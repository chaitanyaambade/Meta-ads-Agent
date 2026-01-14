"""
Orchestrator Agent - Central coordination agent for META marketing operations
"""

from typing import Dict, Any, List

from ..core.api_client import MetaAPIClient
from ..core.models import CampaignParams, AdSetParams, Campaign, LeadFormParams
from ..core.exceptions import ValidationError
from ..core.utils import log_debug

from .campaign_agent import CampaignAgent
from .asset_agent import AssetAgent
from .ad_agent import AdCreationAgent
from .lead_form_agent import LeadFormAgent


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
        self.lead_form_agent = LeadFormAgent(self.api)
        log_debug("[Orchestrator] Initialized with Campaign Agent, Asset Agent, Ad Agent, and Lead Form Agent")

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

            log_debug(f"\n[Orchestrator] Workflow completed successfully")
            log_debug(f"[Orchestrator] Campaign ID: {campaign.id}")
            return campaign

        except Exception as e:
            log_debug(f"\n[Orchestrator] Workflow failed: {str(e)}")
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
            log_debug(f"[Orchestrator] Validation failed: {str(e)}")
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
            campaign = await self.campaign_agent.create_campaign(
                ad_account_id,
                campaign_params
            )
            created_resources["campaign"] = campaign

            for adset_params in adset_params_list:
                adset_params.campaign_id = campaign.id

                adset = await self.campaign_agent.create_adset(
                    ad_account_id,
                    adset_params
                )
                created_resources["adsets"].append(adset)

            log_debug(f"\n[Orchestrator] Full workflow completed")
            log_debug(f"[Orchestrator] Campaign: {campaign.id}")
            log_debug(f"[Orchestrator] Ad sets: {len(created_resources['adsets'])}")

            return created_resources

        except Exception as e:
            log_debug(f"\n[Orchestrator] Workflow failed, initiating rollback")
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
            campaign_params = create_campaign_params_from_json(campaign_json)
            adset_params_list = [create_adset_params_from_json(adset_json) for adset_json in adsets_json_list]

            result = await self.create_campaign_with_adsets(
                ad_account_id,
                campaign_params,
                adset_params_list
            )

            return result

        except ValidationError as e:
            log_debug(f"[Orchestrator] Validation failed: {str(e)}")
            raise

    async def _rollback(self, created_resources: Dict):
        """Rollback created resources on failure"""
        print("[Orchestrator] Rolling back created resources...")

        for adset in created_resources.get("adsets", []):
            try:
                await self.campaign_agent.update_adset_status(
                    adset.id,
                    "DELETED"
                )
                log_debug(f"[Orchestrator] Deleted ad set: {adset.id}")
            except Exception as e:
                log_debug(f"[Orchestrator] Failed to delete ad set {adset.id}: {e}")

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


# Helper functions

def build_basic_targeting(
    countries: List[str],
    age_min: int = 18,
    age_max: int = 65,
    genders: List[int] = None
) -> Dict:
    """
    Build basic targeting configuration

    Args:
        countries: List of country codes
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
    Create CampaignParams from JSON data

    Args:
        json_data: Dictionary with campaign parameters

    Returns:
        CampaignParams object
    """
    try:
        if "name" not in json_data:
            raise ValidationError("Campaign 'name' is required")
        if "objective" not in json_data:
            raise ValidationError("Campaign 'objective' is required")

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

    Returns:
        AdSetParams object
    """
    try:
        adset_params = AdSetParams(**json_data)
        return adset_params

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Failed to create ad set params from JSON: {str(e)}")


def create_lead_form_params_from_json(json_data: Dict) -> LeadFormParams:
    """
    Create LeadFormParams from JSON data

    Args:
        json_data: Dictionary with lead form parameters

    Returns:
        LeadFormParams object
    """
    try:
        lead_form_params = LeadFormParams(**json_data)
        return lead_form_params

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Failed to create lead form params from JSON: {str(e)}")
