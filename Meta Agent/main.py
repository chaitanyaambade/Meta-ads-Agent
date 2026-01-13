"""
Main entry point for Meta Ads Agent
Reads JSON action file and processes it
"""

import asyncio
import json
import os
import sys

# Parse command line BEFORE imports to set quiet mode early
QUIET_MODE = "--json" in sys.argv
VERBOSE_MODE = "--verbose" in sys.argv

# Now import modules
from dotenv import load_dotenv
from src.agents.orchestrator import OrchestratorAgent
from src.core.utils import set_quiet_mode
from src.handlers.operations import process_action, set_operations_quiet_mode

# Set quiet mode immediately after imports
if not VERBOSE_MODE:
    set_quiet_mode(True)
    set_operations_quiet_mode(True)
else:
    set_quiet_mode(QUIET_MODE)
    set_operations_quiet_mode(QUIET_MODE)


async def main():
    """Main async function - reads JSON action file and executes it"""
    global QUIET_MODE
    
    # Load environment variables
    load_dotenv()
    
    # Get access token from environment (.env file)
    access_token = os.getenv('META_ACCESS_TOKEN')
    
    if not access_token:
        if VERBOSE_MODE:
            print("\n✗ Error: Missing required environment variable")
            print("   Please set META_ACCESS_TOKEN in .env file")
        else:
            print(json.dumps({"status": "error", "message": "Missing META_ACCESS_TOKEN in .env"}))
        return
    
    # Parse command line arguments
    action_file = None
    if len(sys.argv) > 1:
        # Remove flags from argv for processing
        args = [arg for arg in sys.argv[1:] if arg not in ["--json", "--verbose"]]
        if args:
            action_file = args[0]
        else:
            action_file = "action.json"
    else:
        action_file = "action.json"
    
    # Load and parse action JSON
    if not os.path.exists(action_file):
        if VERBOSE_MODE:
            print(f"\n✗ Error: Action file not found: {action_file}")
            print(f"   Usage: python3 main.py [--json] [--verbose] <action_file.json>")
            print(f"   Example: python3 main.py action.json")
            print(f"   Example (JSON only): python3 main.py --json action.json")
            print(f"   Example (Verbose): python3 main.py --verbose action.json")
        else:
            print(json.dumps({"status": "error", "message": f"Action file not found: {action_file}"}))
        return
    
    try:
        with open(action_file, 'r') as f:
            action_payload = json.load(f)
    except json.JSONDecodeError as e:
        if VERBOSE_MODE:
            print(f"\n✗ Error: Invalid JSON in {action_file}: {e}")
        else:
            print(json.dumps({"status": "error", "message": f"Invalid JSON: {e}"}))
        return
    except Exception as e:
        if VERBOSE_MODE:
            print(f"\n✗ Error reading {action_file}: {e}")
        else:
            print(json.dumps({"status": "error", "message": f"Error reading file: {e}"}))
        return
    
    # Extract ad_account_id from action payload
    ad_account_id = action_payload.get('ad_account_id')
    action = action_payload.get('action', '').lower()
    
    # For list_ad_accounts, ad_account_id can be placeholder (not used)
    if action != 'list_ad_accounts' and not ad_account_id:
        if VERBOSE_MODE:
            print(f"\n✗ Error: Missing 'ad_account_id' in action JSON")
            print(f"   Every action must include 'ad_account_id' field")
        else:
            print(json.dumps({"status": "error", "message": "Missing 'ad_account_id' in action JSON"}))
        return
    
    # For list_ad_accounts, use placeholder if not provided
    if not ad_account_id:
        ad_account_id = "placeholder"
    
    # Initialize orchestrator
    if VERBOSE_MODE:
        print("\n[INFO] Initializing Meta Ads Agent...")
    orchestrator = OrchestratorAgent(access_token)
    
    try:
        # Skip credential validation for list_ad_accounts action
        if action != 'list_ad_accounts':
            # Validate credentials with API
            is_valid = await orchestrator.validate_credentials(ad_account_id)
            if not is_valid:
                if VERBOSE_MODE:
                    print("\n✗ Error: Invalid credentials. Please check your META_ACCESS_TOKEN and META_AD_ACCOUNT_ID")
                else:
                    print(json.dumps({"status": "error", "message": "Invalid credentials"}))
                return
        
        if VERBOSE_MODE:
            print("✓ Credentials validated successfully" if action != 'list_ad_accounts' else "✓ Access token verified")
            if action != 'list_ad_accounts':
                print(f"✓ Using ad account: {ad_account_id}\n")
        
            # Process the action
            print(f"[INFO] Processing action from: {action_file}")
            print(f"[INFO] Action: {action_payload.get('action')}\n")
        
        result = await process_action(orchestrator, ad_account_id, action_payload)
        
        # Output result
        if QUIET_MODE:
            print(json.dumps(result))
        else:
            print(f"\n{'='*70}")
            print("RESULT")
            print(f"{'='*70}")
            print(json.dumps(result, indent=2))
        
    finally:
        await orchestrator.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        if VERBOSE_MODE:
            print("\n\n[INFO] Agent interrupted by user. Goodbye!")
    except Exception as e:
        if VERBOSE_MODE:
            print(f"\n✗ Unexpected error: {e}")
        else:
            print(json.dumps({"status": "error", "message": str(e)}))
