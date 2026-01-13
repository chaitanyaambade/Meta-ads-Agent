"""
Campaign Agent - Manages campaign and ad set operations
"""

from typing import Dict, Any, List

from ..core.api_client import MetaAPIClient
from ..core.models import CampaignParams, AdSetParams, Campaign, AdSet
from ..core.exceptions import CampaignCreationError, AdSetCreationError, APIError
from ..core.utils import log_debug


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

            log_debug(f"[CampaignAgent] Campaign created: {campaign.id}")
            return campaign

        except APIError as e:
            log_debug(f"[CampaignAgent] Campaign creation failed: {e.message}")
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

            log_debug(f"[CampaignAgent] Ad set created: {adset.id}")
            return adset

        except APIError as e:
            log_debug(f"[CampaignAgent] Ad set creation failed: {e.message}")
            raise AdSetCreationError(
                f"Failed to create ad set '{params.name}': {e.message}"
            ) from e

    async def get_campaign(self, campaign_id: str) -> Dict:
        """Get campaign details"""
        endpoint = f"/{campaign_id}"
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
        return response.get("data", [])

    async def list_adsets(self, ad_account_id: str, campaign_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List ad sets under an ad account or specific campaign

        Args:
            ad_account_id: Ad account ID (without act_ prefix)
            campaign_id: Optional campaign ID to filter ad sets
            limit: Maximum number of ad sets to return

        Returns:
            List of ad set dictionaries
        """
        log_debug(f"\n[CampaignAgent] Listing ad sets for ad account: {ad_account_id}")

        if campaign_id:
            endpoint = f"/{campaign_id}/adsets"
        else:
            endpoint = f"/act_{ad_account_id}/adsets"

        params = {
            "fields": "id,name,campaign_id,status,optimization_goal,billing_event,daily_budget,lifetime_budget,created_time",
            "limit": limit
        }
        response = await self.api.get(endpoint, params=params)
        return response.get("data", [])

    async def get_adset(self, adset_id: str) -> Dict:
        """Get ad set details"""
        endpoint = f"/{adset_id}"
        params = {"fields": "id,name,campaign_id,status,optimization_goal,billing_event,daily_budget,lifetime_budget,targeting,created_time"}
        return await self.api.get(endpoint, params=params)

    async def update_adset_status(self, adset_id: str, status: str):
        """Update ad set status"""
        endpoint = f"/{adset_id}"
        data = {"status": status}
        return await self.api.post(endpoint, json_data=data)

    async def delete_campaign(self, campaign_id: str):
        """Delete a campaign by setting status to DELETED"""
        log_debug(f"\n[CampaignAgent] Deleting campaign: {campaign_id}")
        return await self.update_campaign_status(campaign_id, "DELETED")
