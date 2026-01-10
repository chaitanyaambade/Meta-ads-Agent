"""
JSON-based Campaign and Ad Set Operations
Handles all operations via JSON action parameter
"""

import json
import os
from campaign_adsets_agent import OrchestratorAgent, CampaignParams, create_adset_params_from_json, ValidationError
from asset_agent import AssetValidationError, AssetUploadError

# Global quiet flag for JSON-only output
QUIET_MODE = False


def set_quiet_mode(quiet: bool):
    """Set quiet mode globally"""
    global QUIET_MODE
    QUIET_MODE = quiet


def log_info(msg: str):
    """Print info message only if not in quiet mode"""
    if not QUIET_MODE:
        print(msg)


def log_section(title: str):
    """Print section header only if not in quiet mode"""
    if not QUIET_MODE:
        print("\n" + "="*70)
        print(title)
        print("="*70)


async def handle_create_campaign(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Create a campaign"""
    log_section("CREATE CAMPAIGN")
    
    try:
        campaign_json = payload.get("campaign")
        if not campaign_json:
            raise ValidationError("Missing 'campaign' object in payload")
        
        log_info(f"\n[INFO] Campaign name: {campaign_json.get('name')}")
        log_info(f"[INFO] Campaign objective: {campaign_json.get('objective')}")
        
        campaign = await orchestrator.create_campaign_from_json(ad_account_id, campaign_json)
        
        log_info(f"\n✓ Campaign created successfully")
        log_info(f"✓ Campaign ID: {campaign.id}")
        log_info(f"✓ Campaign Name: {campaign.name}")
        
        return {"status": "success", "campaign_id": campaign.id, "name": campaign.name}
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_update_campaign(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Update a campaign status (pause/active/delete)"""
    log_section("UPDATE CAMPAIGN")
    
    try:
        campaign_id = payload.get("campaign_id")
        update_type = payload.get("update_type", "").lower()
        
        if not campaign_id:
            raise ValidationError("Missing 'campaign_id' in payload")
        if not update_type:
            raise ValidationError("Missing 'update_type' in payload (pause/active/delete)")
        
        log_info(f"\n[INFO] Campaign ID: {campaign_id}")
        log_info(f"[INFO] Update type: {update_type}")
        
        if update_type == "pause":
            await orchestrator.campaign_agent.pause_campaign(campaign_id)
            log_info(f"\n✓ Campaign paused successfully")
            return {"status": "success", "action": "pause"}
        elif update_type == "active":
            await orchestrator.campaign_agent.activate_campaign(campaign_id)
            log_info(f"\n✓ Campaign activated successfully")
            return {"status": "success", "action": "active"}
        elif update_type == "delete":
            await orchestrator.campaign_agent.delete_campaign(campaign_id)
            log_info(f"\n✓ Campaign deleted successfully")
            return {"status": "success", "action": "delete"}
        else:
            raise ValidationError(f"Invalid update_type: {update_type}. Use pause/active/delete")
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_campaign(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get campaign details"""
    log_section("GET CAMPAIGN")
    
    try:
        campaign_id = payload.get("campaign_id")
        
        if not campaign_id:
            raise ValidationError("Missing 'campaign_id' in payload")
        
        log_info(f"\n[INFO] Fetching campaign: {campaign_id}")
        
        campaign_info = await orchestrator.campaign_agent.get_campaign(campaign_id)
        
        log_info(f"\n✓ Campaign details:")
        log_info(f"  ID: {campaign_info.get('id')}")
        log_info(f"  Name: {campaign_info.get('name')}")
        log_info(f"  Objective: {campaign_info.get('objective')}")
        log_info(f"  Status: {campaign_info.get('status')}")
        log_info(f"  Created: {campaign_info.get('created_time')}")
        
        return {"status": "success", "campaign": campaign_info}
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_create_adset(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Create an ad set"""
    log_section("CREATE AD SET")
    
    try:
        adset_json = payload.get("adset")
        if not adset_json:
            raise ValidationError("Missing 'adset' object in payload")
        
        log_info(f"\n[INFO] Ad set name: {adset_json.get('name')}")
        log_info(f"[INFO] Campaign ID: {adset_json.get('campaign_id')}")
        log_info(f"[INFO] Optimization goal: {adset_json.get('optimization_goal')}")
        
        # Fetch campaign to validate compatibility and budget rules
        campaign_id = adset_json.get("campaign_id")
        if campaign_id:
            try:
                campaign_info = await orchestrator.campaign_agent.get_campaign(campaign_id)
                campaign_objective = campaign_info.get('objective')
                log_info(f"[INFO] Campaign objective: {campaign_objective}")
                
                # CBO check: if campaign has budget, remove ad set budget
                campaign_has_budget = bool(campaign_info.get('daily_budget') or campaign_info.get('lifetime_budget'))
                if campaign_has_budget:
                    log_info(f"[INFO] Campaign has budget set (CBO). Removing ad set budget fields.")
                    adset_json.pop('daily_budget', None)
                    adset_json.pop('lifetime_budget', None)
            except Exception as e:
                log_info(f"[WARN] Could not fetch campaign info: {e}")
        
        adset_params = create_adset_params_from_json(adset_json)
        adset = await orchestrator.campaign_agent.create_adset(ad_account_id, adset_params)
        
        log_info(f"\n✓ Ad set created successfully")
        log_info(f"✓ Ad Set ID: {adset.id}")
        log_info(f"✓ Ad Set Name: {adset.name}")
        
        return {"status": "success", "adset_id": adset.id, "name": adset.name}
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_update_adset(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Update an ad set status (pause/active/delete)"""
    log_section("UPDATE AD SET")
    
    try:
        adset_id = payload.get("adset_id")
        update_type = payload.get("update_type", "").lower()
        
        if not adset_id:
            raise ValidationError("Missing 'adset_id' in payload")
        if not update_type:
            raise ValidationError("Missing 'update_type' in payload (pause/active/delete)")
        
        log_info(f"\n[INFO] Ad Set ID: {adset_id}")
        log_info(f"[INFO] Update type: {update_type}")
        
        if update_type == "pause":
            await orchestrator.campaign_agent.update_campaign_status(adset_id, "PAUSED")
            log_info(f"\n✓ Ad set paused successfully")
            return {"status": "success", "action": "pause"}
        elif update_type == "active":
            await orchestrator.campaign_agent.update_campaign_status(adset_id, "ACTIVE")
            log_info(f"\n✓ Ad set activated successfully")
            return {"status": "success", "action": "active"}
        elif update_type == "delete":
            await orchestrator.campaign_agent.update_campaign_status(adset_id, "DELETED")
            log_info(f"\n✓ Ad set deleted successfully")
            return {"status": "success", "action": "delete"}
        else:
            raise ValidationError(f"Invalid update_type: {update_type}. Use pause/active/delete")
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_adset(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get ad set details"""
    log_section("GET AD SET")
    
    try:
        adset_id = payload.get("adset_id")
        
        if not adset_id:
            raise ValidationError("Missing 'adset_id' in payload")
        
        log_info(f"\n[INFO] Ad Set ID: {adset_id}")
        log_info(f"[INFO] Listing campaigns for reference...")
        
        campaigns = await orchestrator.campaign_agent.list_campaigns(ad_account_id)
        log_info(f"\n✓ Campaigns in account: {len(campaigns)}")
        
        return {"status": "success", "adset_id": adset_id, "campaigns_count": len(campaigns)}
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_list_campaigns(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """List all campaigns in the ad account"""
    log_section("LIST CAMPAIGNS")
    
    try:
        campaigns = await orchestrator.campaign_agent.list_campaigns(ad_account_id)
        
        if not campaigns:
            return {"status": "success", "campaigns": [], "count": 0}
        
        campaign_list = []
        for idx, campaign in enumerate(campaigns, 1):
            # Handle both dict and object formats
            campaign_id = campaign.get("id") if isinstance(campaign, dict) else campaign.id
            campaign_name = campaign.get("name") if isinstance(campaign, dict) else campaign.name
            campaign_status = campaign.get("status") if isinstance(campaign, dict) else campaign.status
            campaign_objective = campaign.get("objective") if isinstance(campaign, dict) else campaign.objective
            
            campaign_list.append({
                "id": campaign_id,
                "name": campaign_name,
                "status": campaign_status,
                "objective": campaign_objective
            })
        
        return {"status": "success", "campaigns": campaign_list, "count": len(campaigns)}
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================================
# ASSET OPERATIONS
# ============================================================================

async def handle_upload_image(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Upload image to ad account"""
    log_section("UPLOAD IMAGE")
    
    try:
        filepath = payload.get("filepath")
        if not filepath:
            raise ValidationError("Missing 'filepath' in payload")
        
        width = payload.get("width")
        height = payload.get("height")
        
        log_info(f"\n[INFO] Image file: {filepath}")
        if width and height:
            log_info(f"[INFO] Image dimensions: {width}x{height}")
        
        image_asset = await orchestrator.asset_agent.upload_image(ad_account_id, filepath, width, height)
        
        log_info(f"\n✓ Image uploaded successfully")
        log_info(f"✓ Image Hash: {image_asset.image_hash}")
        log_info(f"✓ Filename: {image_asset.filename}")
        log_info(f"✓ Size: {image_asset.size_bytes / 1024:.2f}KB")
        
        return {
            "status": "success",
            "asset_type": "image",
            "image_hash": image_asset.image_hash,
            "filename": image_asset.filename,
            "size_bytes": image_asset.size_bytes,
            "width": width,
            "height": height
        }
    
    except AssetValidationError as e:
        log_info(f"\n✗ Validation Error: {e}")
        return {"status": "error", "type": "validation", "message": str(e)}
    except AssetUploadError as e:
        log_info(f"\n✗ Upload Error: {e}")
        return {"status": "error", "type": "upload", "message": str(e)}
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_upload_video(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Upload video to ad account"""
    log_section("UPLOAD VIDEO")
    
    try:
        filepath = payload.get("filepath")
        if not filepath:
            raise ValidationError("Missing 'filepath' in payload")
        
        duration = payload.get("duration")
        width = payload.get("width")
        height = payload.get("height")
        upload_phase = payload.get("upload_phase", "init")
        
        log_info(f"\n[INFO] Video file: {filepath}")
        if duration:
            log_info(f"[INFO] Duration: {duration}s")
        if width and height:
            log_info(f"[INFO] Dimensions: {width}x{height}")
        
        video_asset = await orchestrator.asset_agent.upload_video(
            ad_account_id, filepath, duration, width, height, upload_phase
        )
        
        log_info(f"\n✓ Video uploaded successfully")
        log_info(f"✓ Video ID: {video_asset.video_id}")
        log_info(f"✓ Filename: {video_asset.filename}")
        log_info(f"✓ Size: {video_asset.size_bytes / 1024 / 1024:.2f}MB")
        log_info(f"✓ Status: {video_asset.status}")
        
        return {
            "status": "success",
            "asset_type": "video",
            "video_id": video_asset.video_id,
            "filename": video_asset.filename,
            "size_bytes": video_asset.size_bytes,
            "duration": duration,
            "width": width,
            "height": height,
            "upload_status": video_asset.status
        }
    
    except AssetValidationError as e:
        log_info(f"\n✗ Validation Error: {e}")
        return {"status": "error", "type": "validation", "message": str(e)}
    except AssetUploadError as e:
        log_info(f"\n✗ Upload Error: {e}")
        return {"status": "error", "type": "upload", "message": str(e)}
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_image(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get image details by hash"""
    log_section("GET IMAGE")
    
    try:
        image_hash = payload.get("image_hash")
        if not image_hash:
            raise ValidationError("Missing 'image_hash' in payload")
        
        log_info(f"\n[INFO] Image hash: {image_hash}")
        
        image_data = await orchestrator.asset_agent.get_image(ad_account_id, image_hash)
        
        log_info(f"\n✓ Image retrieved successfully")
        
        return {
            "status": "success",
            "asset_type": "image",
            "image_hash": image_hash,
            "data": image_data
        }
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_video(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get video details by ID"""
    log_section("GET VIDEO")
    
    try:
        video_id = payload.get("video_id")
        if not video_id:
            raise ValidationError("Missing 'video_id' in payload")
        
        log_info(f"\n[INFO] Video ID: {video_id}")
        
        video_data = await orchestrator.asset_agent.get_video(ad_account_id, video_id)
        
        log_info(f"\n✓ Video retrieved successfully")
        
        return {
            "status": "success",
            "asset_type": "video",
            "video_id": video_id,
            "data": video_data
        }
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_clear_asset_cache(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Clear the asset cache"""
    log_section("CLEAR ASSET CACHE")
    
    try:
        orchestrator.asset_agent.clear_cache()
        log_info(f"\n✓ Asset cache cleared successfully")
        return {"status": "success", "message": "Asset cache cleared"}
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def process_action(orchestrator: OrchestratorAgent, ad_account_id: str, action_payload: dict) -> dict:
    """Main action dispatcher - routes to appropriate handler"""
    action = action_payload.get("action", "").lower()
    
    if action == "create_campaign":
        return await handle_create_campaign(orchestrator, ad_account_id, action_payload)
    elif action == "update_campaign":
        return await handle_update_campaign(orchestrator, ad_account_id, action_payload)
    elif action == "get_campaign":
        return await handle_get_campaign(orchestrator, ad_account_id, action_payload)
    elif action == "list_campaigns":
        return await handle_list_campaigns(orchestrator, ad_account_id, action_payload)
    elif action == "create_adset":
        return await handle_create_adset(orchestrator, ad_account_id, action_payload)
    elif action == "update_adset":
        return await handle_update_adset(orchestrator, ad_account_id, action_payload)
    elif action == "get_adset":
        return await handle_get_adset(orchestrator, ad_account_id, action_payload)
    elif action == "upload_image":
        return await handle_upload_image(orchestrator, ad_account_id, action_payload)
    elif action == "upload_video":
        return await handle_upload_video(orchestrator, ad_account_id, action_payload)
    elif action == "get_image":
        return await handle_get_image(orchestrator, ad_account_id, action_payload)
    elif action == "get_video":
        return await handle_get_video(orchestrator, ad_account_id, action_payload)
    elif action == "clear_asset_cache":
        return await handle_clear_asset_cache(orchestrator, ad_account_id, action_payload)
    else:
        supported_actions = [
            "create_campaign", "update_campaign", "get_campaign", "list_campaigns",
            "create_adset", "update_adset", "get_adset",
            "upload_image", "upload_video", "get_image", "get_video", "clear_asset_cache"
        ]
        error_msg = f"Unknown action: {action}. Supported: {', '.join(supported_actions)}"
        log_info(f"\n✗ {error_msg}")
        return {"status": "error", "message": error_msg}
