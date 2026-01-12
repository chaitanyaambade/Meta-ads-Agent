"""
Ad Creation Agent
Responsible for creating and managing ad creatives and ads.

Endpoints used:
- Create Creative: POST /act_{ad_account_id}/adcreatives
- Get Creative: GET /{creative_id}
- Create Ad: POST /act_{ad_account_id}/ads
- Update Ad: POST /{ad_id}
- Get Ad: GET /{ad_id}

This module expects to receive an `api_client` object with async `get` and `post`
methods that accept (endpoint, params) and (endpoint, json_data) respectively.
Typically this will be the `MetaAPIClient` instance from `campaign_adsets_agent`.
"""

from dataclasses import dataclass
from typing import Dict, Any


class AdAgentError(Exception):
    """Base exception for ad agent"""
    pass


class CreativeError(AdAgentError):
    pass


class AdCreationError(AdAgentError):
    pass


@dataclass
class Creative:
    id: str
    name: str
    data: Dict[str, Any]


@dataclass
class Ad:
    id: str
    name: str
    data: Dict[str, Any]


class AdCreationAgent:
    """Agent for ad creative and ad management"""

    def __init__(self, api_client):
        self.api = api_client

    async def create_creative(self, ad_account_id: str, creative_payload: Dict[str, Any]) -> Creative:
        """Create an ad creative for an ad account.

        Args:
            ad_account_id: numeric ad account id (without `act_` prefix)
            creative_payload: dict of creative fields as required by Meta API

        Returns:
            Creative dataclass with id and original payload
        """
        endpoint = f"/act_{ad_account_id}/adcreatives"
        try:
            response = await self.api.post(endpoint, json_data=creative_payload)
            creative_id = response.get("id")
            if not creative_id:
                raise CreativeError("No creative id returned from API")
            return Creative(id=creative_id, name=creative_payload.get("name", ""), data=response)
        except Exception as e:
            raise CreativeError(str(e)) from e

    async def get_creative(self, creative_id: str) -> Dict[str, Any]:
        """Retrieve a creative by its id"""
        endpoint = f"/{creative_id}"
        params = {"fields": "id,name,object_story_spec,thumbnail_url,body,title,call_to_action_type"}
        try:
            response = await self.api.get(endpoint, params=params)
            return response
        except Exception as e:
            raise CreativeError(str(e)) from e

    async def create_ad(self, ad_account_id: str, ad_payload: Dict[str, Any]) -> Ad:
        """Create an ad under an ad account"""
        endpoint = f"/act_{ad_account_id}/ads"
        try:
            response = await self.api.post(endpoint, json_data=ad_payload)
            ad_id = response.get("id")
            if not ad_id:
                raise AdCreationError("No ad id returned from API")
            return Ad(id=ad_id, name=ad_payload.get("name", ""), data=response)
        except Exception as e:
            raise AdCreationError(str(e)) from e

    async def update_ad(self, ad_id: str, update_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing ad by ID"""
        endpoint = f"/{ad_id}"
        try:
            response = await self.api.post(endpoint, json_data=update_fields)
            return response
        except Exception as e:
            raise AdCreationError(str(e)) from e

    async def get_ad(self, ad_id: str) -> Dict[str, Any]:
        """Retrieve an ad by id"""
        endpoint = f"/{ad_id}"
        params = {"fields": "id,name,status,effective_status,creative,insights"}
        try:
            response = await self.api.get(endpoint, params=params)
            return response
        except Exception as e:
            raise AdCreationError(str(e)) from e


def set_ad_quiet_mode(quiet: bool):
    """Placeholder for symmetry with other agents; kept for API compatibility"""
    # This module intentionally keeps quiet handling in the orchestrator
    return
