"""
META Marketing Agent System - Core Components
Version: 1.0 (Modular Implementation)

This module implements the core API clients, agents, and helper functions.
Operation functions and menu are in operations.py and main.py respectively.
"""

import asyncio
import httpx
import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from dotenv import load_dotenv
from asset_agent import AssetAgent, set_asset_quiet_mode
from ad_agent import AdCreationAgent, set_ad_quiet_mode


# ============================================================================
# GLOBAL CONFIGURATION
# ============================================================================

# Quiet mode flag (suppress debug output)
QUIET_MODE = False

def set_agent_quiet_mode(quiet: bool):
    """Set quiet mode globally in agent module"""
    global QUIET_MODE
    QUIET_MODE = quiet

def log_debug(msg: str):
    """Print debug message only if not in quiet mode"""
    if not QUIET_MODE:
        print(msg)


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """System configuration"""
    META_API_BASE_URL = "https://graph.facebook.com/v24.0"
    API_TIMEOUT = 30
    MAX_RETRIES = 3
    RATE_LIMIT_WINDOW = 3600  # 1 hour
    RATE_LIMIT_MAX_CALLS = 200


# ============================================================================
# DATA MODELS
# ============================================================================

class CampaignObjective(str, Enum):
    """Valid campaign objectives"""
    AWARENESS = "OUTCOME_AWARENESS"
    TRAFFIC = "OUTCOME_TRAFFIC"
    ENGAGEMENT = "OUTCOME_ENGAGEMENT"
    LEADS = "OUTCOME_LEADS"
    APP_PROMOTION = "OUTCOME_APP_PROMOTION"
    SALES = "OUTCOME_SALES"

class CampaignStatus(str, Enum):
    """Campaign status values"""
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DELETED = "DELETED"
    ARCHIVED = "ARCHIVED"


class CampaignParams:
    """Campaign creation parameters - accepts any fields from JSON"""
    
    def __init__(self, **kwargs):
        """
        Initialize with any campaign parameters
        
        Args:
            **kwargs: Any campaign parameters (name, objective, budget, etc.)
        """
        # Required fields
        if "name" not in kwargs:
            raise ValueError("Campaign 'name' is required")
        if "objective" not in kwargs:
            raise ValueError("Campaign 'objective' is required")
        
        # Store all fields
        self.params = kwargs
        
        # Set defaults if not provided
        if "status" not in self.params:
            self.params["status"] = "PAUSED"
        if "special_ad_categories" not in self.params:
            self.params["special_ad_categories"] = ["NONE"]
        
        # Validate budget if present
        if "daily_budget" in self.params and self.params["daily_budget"] < 4000:
            raise ValueError("Daily budget must be at least ₹40 (4000 paisa)")
        if "lifetime_budget" in self.params and self.params["lifetime_budget"] < 4000:
            raise ValueError("Lifetime budget must be at least ₹40 (4000 paisa)")
    
    @property
    def name(self) -> str:
        """Get campaign name"""
        return self.params.get("name")
    
    @property
    def objective(self) -> str:
        """Get campaign objective"""
        return self.params.get("objective")
    
    @property
    def status(self) -> str:
        """Get campaign status"""
        return self.params.get("status", "PAUSED")
    
    def to_api_dict(self) -> Dict:
        """Convert to API request format - pass all fields"""
        return self.params.copy()


class AdSetParams:
    """Flexible Ad set creation parameters - accepts any fields from JSON"""

    def __init__(self, **kwargs):
        # Require minimal identifying fields; campaigns may set campaign_id later
        if "name" not in kwargs:
            raise ValidationError("Ad set 'name' is required")

        # campaign_id is often required; allow creating without it if caller sets later
        if "campaign_id" not in kwargs:
            # We'll allow missing campaign_id here; validation can occur later
            pass

        self.params = kwargs.copy()

        # Defaults
        if "status" not in self.params:
            self.params["status"] = "PAUSED"
        if "billing_event" not in self.params:
            self.params["billing_event"] = "IMPRESSIONS"

        # Validate budgets if present
        if "daily_budget" in self.params and self.params["daily_budget"] is not None:
            try:
                if int(self.params["daily_budget"]) < 4000:
                    raise ValidationError("Ad set 'daily_budget' must be at least 4000 paisa")
            except ValueError:
                raise ValidationError("Ad set 'daily_budget' must be an integer amount in paisa")
        if "lifetime_budget" in self.params and self.params["lifetime_budget"] is not None:
            try:
                if int(self.params["lifetime_budget"]) < 4000:
                    raise ValidationError("Ad set 'lifetime_budget' must be at least 4000 paisa")
            except ValueError:
                raise ValidationError("Ad set 'lifetime_budget' must be an integer amount in paisa")

    @property
    def name(self) -> str:
        return self.params.get("name")

    @property
    def campaign_id(self) -> Optional[str]:
        return self.params.get("campaign_id")

    @campaign_id.setter
    def campaign_id(self, value: str):
        self.params["campaign_id"] = value

    @property
    def optimization_goal(self) -> Optional[str]:
        return self.params.get("optimization_goal")

    @property
    def status(self) -> str:
        return self.params.get("status", "PAUSED")

    def to_api_dict(self) -> Dict:
        """Return a copy of all provided fields to send to the API"""
        return self.params.copy()


@dataclass
class Campaign:
    """Campaign response model"""
    id: str
    name: str
    objective: str
    status: str
    created_time: Optional[str] = None


@dataclass
class AdSet:
    """Ad set response model"""
    id: str
    name: str
    campaign_id: str
    optimization_goal: str
    status: str


# ============================================================================
# EXCEPTIONS
# ============================================================================

class MetaAgentError(Exception):
    """Base exception for all agent errors"""
    pass


class APIError(MetaAgentError):
    """API request failed"""
    def __init__(self, message: str, code: int = None, status_code: int = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(MetaAgentError):
    """Invalid input parameters"""
    pass


class CampaignCreationError(MetaAgentError):
    """Campaign creation failed"""
    pass


class AdSetCreationError(MetaAgentError):
    """Ad set creation failed"""
    pass


# ============================================================================
# API CLIENT
# ============================================================================

class MetaAPIClient:
    """
    HTTP client for Meta Marketing API with rate limiting and error handling
    """
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = Config.META_API_BASE_URL
        self.session = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=Config.API_TIMEOUT
        )
        self.request_count = 0
    
    async def get(self, endpoint: str, params: Dict = None) -> Dict:
        """Execute GET request"""
        params = params or {}
        params["access_token"] = self.access_token
        
        log_debug(f"[API] GET {endpoint}")
        
        try:
            response = await self.session.get(endpoint, params=params)
            return self._handle_response(response)
        except httpx.TimeoutException:
            raise APIError("Request timeout", status_code=408)
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")
    
    async def post(self, endpoint: str, json_data: Dict = None) -> Dict:
        """Execute POST request"""
        json_data = json_data or {}
        json_data["access_token"] = self.access_token
        
        log_debug(f"[API] POST {endpoint}")
        log_debug(f"[API] Data: {json.dumps({k: v for k, v in json_data.items() if k != 'access_token'}, indent=2)}")
        
        try:
            response = await self.session.post(endpoint, json=json_data)
            return self._handle_response(response)
        except httpx.TimeoutException:
            raise APIError("Request timeout", status_code=408)
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}")
    
    def _handle_response(self, response: httpx.Response) -> Dict:
        """Handle API response and errors"""
        log_debug(f"[API] Response Status: {response.status_code}")
        
        if response.status_code >= 400:
            try:
                error_data = response.json()
                # Print full error payload for debugging
                try:
                    log_debug(f"[API] Error Payload: {json.dumps(error_data, indent=2)}")
                except Exception:
                    log_debug(f"[API] Error Payload (raw): {error_data}")

                error_msg = error_data.get("error", {}).get("message", "Unknown error")
                error_code = error_data.get("error", {}).get("code")
                error_subcode = error_data.get("error", {}).get("error_subcode")
                log_debug(f"[API] Error: {error_msg} (Code: {error_code}, Subcode: {error_subcode})")
                # Include the full error_data in the exception message to help diagnosis
                raise APIError(
                    message=f"{error_msg} | payload={error_data}",
                    code=error_code,
                    status_code=response.status_code
                )
            except json.JSONDecodeError:
                raise APIError(
                    message=response.text,
                    status_code=response.status_code
                )
        
        result = response.json()
        log_debug(f"[API] Success: {json.dumps(result, indent=2)}")
        return result
    
    async def close(self):
        """Close HTTP session"""
        await self.session.aclose()


# ============================================================================
# CAMPAIGN AGENT
# ============================================================================

class CampaignAgent:
    """
    Manages campaign and ad set operations
    """
    
    def __init__(self, api_client: MetaAPIClient):
        self.api = api_client
        log_debug("[CampaignAgent] Initialized")
    
    async def create_campaign(
        self,
        ad_account_id: str,
        params: CampaignParams
    ) -> Campaign:
        """
        Create a new advertising campaign
        
        Args:
            ad_account_id: Ad account ID (act_xxxxx)
            params: Campaign parameters
            
        Returns:
            Created campaign with ID
        """
        log_debug(f"\n[CampaignAgent] Creating campaign: {params.name}")
        
        endpoint = f"/act_{ad_account_id}/campaigns"
        data = params.to_api_dict()
        
        try:
            response = await self.api.post(endpoint, json_data=data)
            
            campaign = Campaign(
                id=response["id"],
                name=params.name,
                objective=params.objective,
                status=params.status
            )
            
            log_debug(f"[CampaignAgent] ✓ Campaign created: {campaign.id}")
            return campaign
            
        except APIError as e:
            log_debug(f"[CampaignAgent] ✗ Campaign creation failed: {e.message}")
            raise CampaignCreationError(
                f"Failed to create campaign '{params.name}': {e.message}"
            ) from e
    
    async def create_adset(
        self,
        ad_account_id: str,
        params: AdSetParams
    ) -> AdSet:
        """
        Create a new ad set
        
        Args:
            ad_account_id: Ad account ID
            params: Ad set parameters
            
        Returns:
            Created ad set with ID
        """
        log_debug(f"\n[CampaignAgent] Creating ad set: {params.name}")
        
        endpoint = f"/act_{ad_account_id}/adsets"
        data = params.to_api_dict()
        
        try:
            response = await self.api.post(endpoint, json_data=data)
            
            adset = AdSet(
                id=response["id"],
                name=params.name,
                campaign_id=params.campaign_id,
                optimization_goal=params.optimization_goal,
                status=params.status
            )
            
            log_debug(f"[CampaignAgent] ✓ Ad set created: {adset.id}")
            return adset
            
        except APIError as e:
            log_debug(f"[CampaignAgent] ✗ Ad set creation failed: {e.message}")
            raise AdSetCreationError(
                f"Failed to create ad set '{params.name}': {e.message}"
            ) from e
    
    async def get_campaign(self, campaign_id: str) -> Dict:
        """Get campaign details"""
        endpoint = f"/{campaign_id}"
        # include budget fields so callers can inspect whether campaign-level budget (CBO) is set
        params = {"fields": "id,name,objective,status,created_time,daily_budget,lifetime_budget"}
        return await self.api.get(endpoint, params=params)
    
    async def update_campaign_status(self, campaign_id: str, status: str):
        """Update campaign status"""
        endpoint = f"/{campaign_id}"
        data = {"status": status}
        return await self.api.post(endpoint, json_data=data)
    
    async def pause_campaign(self, campaign_id: str):
        """Pause a campaign"""
        log_debug(f"\n[CampaignAgent] Pausing campaign: {campaign_id}")
        return await self.update_campaign_status(campaign_id, "PAUSED")
    
    async def activate_campaign(self, campaign_id: str):
        """Activate a campaign"""
        log_debug(f"\n[CampaignAgent] Activating campaign: {campaign_id}")
        return await self.update_campaign_status(campaign_id, "ACTIVE")

    async def list_campaigns(self, ad_account_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """List campaigns under an ad account"""
        log_debug(f"\n[CampaignAgent] Listing campaigns for ad account: {ad_account_id}")
        endpoint = f"/act_{ad_account_id}/campaigns"
        params = {"fields": "id,name,objective,status,created_time", "limit": limit}
        response = await self.api.get(endpoint, params=params)
        # Response normally contains 'data' list
        return response.get("data", [])

    async def delete_campaign(self, campaign_id: str):
        """Delete a campaign by setting status to DELETED"""
        log_debug(f"\n[CampaignAgent] Deleting campaign: {campaign_id}")
        return await self.update_campaign_status(campaign_id, "DELETED")


# ============================================================================
# ORCHESTRATOR AGENT
# ============================================================================

class OrchestratorAgent:
    """
    Central coordination agent for META marketing operations
    """
    
    def __init__(self, access_token: str):
        self._access_token = access_token
        self.api = MetaAPIClient(access_token)
        self.campaign_agent = CampaignAgent(self.api)
        self.asset_agent = AssetAgent(self.api)
        self.ad_agent = AdCreationAgent(self.api)
        log_debug("[Orchestrator] Initialized with Campaign Agent and Asset Agent")
    
    @property
    def access_token(self) -> str:
        """Get access token for use by other agents"""
        return self._access_token
    
    async def validate_credentials(self, ad_account_id: str) -> bool:
        """Validate that credentials are valid by making a test API call"""
        try:
            endpoint = f"/act_{ad_account_id}/campaigns"
            params = {"fields": "id", "limit": 1}
            await self.api.get(endpoint, params=params)
            return True
        except Exception as e:
            log_debug(f"[Orchestrator] Credential validation failed: {e}")
            return False
    
    async def list_ad_accounts(self) -> List[Dict[str, Any]]:
        """List all ad accounts accessible with current access token"""
        log_debug(f"\n[Orchestrator] Listing ad accounts")
        endpoint = "/me/adaccounts"
        params = {"fields": "id,name,account_status,created_time,currency,timezone_name"}
        try:
            response = await self.api.get(endpoint, params=params)
            accounts = response.get("data", [])
            log_debug(f"[Orchestrator] Found {len(accounts)} ad account(s)")
            return accounts
        except Exception as e:
            log_debug(f"[Orchestrator] Failed to list ad accounts: {e}")
            raise
    
    async def create_campaign(
        self,
        ad_account_id: str,
        campaign_params: CampaignParams
    ) -> Campaign:
        """
        Create a campaign (orchestrated)
        
        Args:
            ad_account_id: Ad account ID
            campaign_params: Campaign parameters
            
        Returns:
            Created campaign
        """
        print(f"\n{'='*60}")
        log_debug(f"[Orchestrator] Starting campaign creation workflow")
        print(f"{'='*60}")
        
        try:
            campaign = await self.campaign_agent.create_campaign(
                ad_account_id,
                campaign_params
            )
            
            log_debug(f"\n[Orchestrator] ✓ Workflow completed successfully")
            log_debug(f"[Orchestrator] Campaign ID: {campaign.id}")
            return campaign
            
        except Exception as e:
            log_debug(f"\n[Orchestrator] ✗ Workflow failed: {str(e)}")
            raise
    
    async def create_campaign_from_json(
        self,
        ad_account_id: str,
        campaign_json: Dict
    ) -> Campaign:
        """
        Create a campaign from JSON data
        
        Args:
            ad_account_id: Ad account ID
            campaign_json: Campaign parameters in JSON format
            
        Returns:
            Created campaign
        """
        log_debug(f"\n[Orchestrator] Creating campaign from JSON")
        try:
            campaign_params = create_campaign_params_from_json(campaign_json)
            campaign = await self.campaign_agent.create_campaign(
                ad_account_id,
                campaign_params
            )
            return campaign
        except ValidationError as e:
            log_debug(f"[Orchestrator] ✗ Validation failed: {str(e)}")
            raise
    
    async def create_campaign_with_adsets(
        self,
        ad_account_id: str,
        campaign_params: CampaignParams,
        adset_params_list: List[AdSetParams]
    ) -> Dict[str, Any]:
        """
        Create campaign with multiple ad sets
        
        Args:
            ad_account_id: Ad account ID
            campaign_params: Campaign parameters
            adset_params_list: List of ad set parameters
            
        Returns:
            Dict with campaign and ad sets
        """
        print(f"\n{'='*60}")
        log_debug(f"[Orchestrator] Starting full campaign workflow")
        log_debug(f"[Orchestrator] Ad sets to create: {len(adset_params_list)}")
        print(f"{'='*60}")
        
        created_resources = {
            "campaign": None,
            "adsets": []
        }
        
        try:
            # Step 1: Create campaign
            campaign = await self.campaign_agent.create_campaign(
                ad_account_id,
                campaign_params
            )
            created_resources["campaign"] = campaign
            
            # Step 2: Create ad sets
            for adset_params in adset_params_list:
                # Link to campaign
                adset_params.campaign_id = campaign.id
                
                adset = await self.campaign_agent.create_adset(
                    ad_account_id,
                    adset_params
                )
                created_resources["adsets"].append(adset)
            
            log_debug(f"\n[Orchestrator] ✓ Full workflow completed")
            log_debug(f"[Orchestrator] Campaign: {campaign.id}")
            log_debug(f"[Orchestrator] Ad sets: {len(created_resources['adsets'])}")
            
            return created_resources
            
        except Exception as e:
            log_debug(f"\n[Orchestrator] ✗ Workflow failed, initiating rollback")
            await self._rollback(created_resources)
            raise
    
    async def create_campaign_with_adsets_from_json(
        self,
        ad_account_id: str,
        campaign_json: Dict,
        adsets_json_list: List[Dict]
    ) -> Dict[str, Any]:
        """
        Create campaign with multiple ad sets from JSON data
        
        Args:
            ad_account_id: Ad account ID
            campaign_json: Campaign parameters in JSON format
            adsets_json_list: List of ad set parameters in JSON format
            
        Returns:
            Dict with campaign and ad sets
        """
        print(f"\n{'='*60}")
        log_debug(f"[Orchestrator] Starting full campaign workflow from JSON")
        log_debug(f"[Orchestrator] Ad sets to create: {len(adsets_json_list)}")
        print(f"{'='*60}")
        
        try:
            # Convert JSON to params objects
            campaign_params = create_campaign_params_from_json(campaign_json)
            adset_params_list = [create_adset_params_from_json(adset_json) for adset_json in adsets_json_list]
            
            # Create campaign and ad sets
            result = await self.create_campaign_with_adsets(
                ad_account_id,
                campaign_params,
                adset_params_list
            )
            
            return result
            
        except ValidationError as e:
            log_debug(f"[Orchestrator] ✗ Validation failed: {str(e)}")
            raise
    
    async def _rollback(self, created_resources: Dict):
        """Rollback created resources on failure"""
        print("[Orchestrator] Rolling back created resources...")
        
        # Delete ad sets
        for adset in created_resources.get("adsets", []):
            try:
                await self.campaign_agent.update_campaign_status(
                    adset.id,
                    "DELETED"
                )
                log_debug(f"[Orchestrator] Deleted ad set: {adset.id}")
            except Exception as e:
                log_debug(f"[Orchestrator] Failed to delete ad set {adset.id}: {e}")
        
        # Delete campaign
        if campaign := created_resources.get("campaign"):
            try:
                await self.campaign_agent.update_campaign_status(
                    campaign.id,
                    "DELETED"
                )
                log_debug(f"[Orchestrator] Deleted campaign: {campaign.id}")
            except Exception as e:
                log_debug(f"[Orchestrator] Failed to delete campaign {campaign.id}: {e}")
    
    async def close(self):
        """Cleanup resources"""
        await self.api.close()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def build_basic_targeting(
    countries: List[str],
    age_min: int = 18,
    age_max: int = 65,
    genders: List[int] = None
) -> Dict:
    """
    Build basic targeting configuration
    
    Args:
        countries: List of country codes (e.g., ['IN', 'US'])
        age_min: Minimum age
        age_max: Maximum age
        genders: List of genders (1=male, 2=female)
    
    Returns:
        Targeting dictionary
    """
    targeting = {
        "geo_locations": {
            "countries": countries
        },
        "age_min": age_min,
        "age_max": age_max
    }
    
    if genders:
        targeting["genders"] = genders
    
    return targeting


def create_campaign_params_from_json(json_data: Dict) -> CampaignParams:
    """
    Create CampaignParams from JSON data - accepts ALL campaign parameters
    
    Args:
        json_data: Dictionary with campaign parameters
            Required keys:
            - name (str): Campaign name [REQUIRED]
            - objective (str): Campaign objective [REQUIRED]
            
            Optional keys (any of these can be passed):
            - status, special_ad_categories, buying_type, daily_budget, lifetime_budget
            - budget_rebalance_flag, spend_cap, pacing_type, bid_strategy
            - start_time, stop_time
            - promoted_object, is_skadnetwork_attribution, adlabels, optimization_goal
            - attribution_spec, issues_info, source_campaign_id, upstream_events
            - source_campaign, can_create_brand_lift_study, brand_lift_studies
            - configured_status, effective_status, recommendations, topline_id
            - is_dynamic_creative, regulatory_spec, political_content, is_ab_test
            - execution_options, learning_stage_info, smart_promotion_type
            - description, has_secondary_skadnetwork_reporting, buying_type_source
            - ... any other campaign parameters supported by Meta API
    
    Returns:
        CampaignParams object
    
    Raises:
        ValidationError: If required fields are missing or invalid
    """
    try:
        # Validate required fields
        if "name" not in json_data:
            raise ValidationError("Campaign 'name' is required")
        if "objective" not in json_data:
            raise ValidationError("Campaign 'objective' is required")
        
        # Pass all JSON fields to CampaignParams
        # CampaignParams will validate and store them
        campaign_params = CampaignParams(**json_data)
        
        return campaign_params
    
    except ValidationError:
        raise
    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        raise ValidationError(f"Failed to create campaign params from JSON: {str(e)}")


def create_adset_params_from_json(json_data: Dict) -> AdSetParams:
    """
    Create AdSetParams from JSON data
    
    Args:
        json_data: Dictionary with ad set parameters
            Expected keys:
            - name (str): Ad set name [REQUIRED]
            - campaign_id (str): Campaign ID [REQUIRED]
            - optimization_goal (str): Optimization goal [REQUIRED]
            - billing_event (str): Billing event (default: "IMPRESSIONS")
            - targeting (dict): Targeting configuration
            - status (str): Ad set status (default: "PAUSED")
            - daily_budget (int): Daily budget in paisa
            - lifetime_budget (int): Lifetime budget in paisa
            - start_time (str): Start time (ISO format)
            - end_time (str): End time (ISO format)
    
    Returns:
        AdSetParams object
    
    Raises:
        ValidationError: If required fields are missing or invalid
    """
    try:
        # Build a flexible AdSetParams from all provided JSON fields.
        # Only 'name' is strictly required here; campaign_id may be set later
        adset_params = AdSetParams(**json_data)
        return adset_params

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Failed to create ad set params from JSON: {str(e)}")
