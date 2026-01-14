"""
Lead Form Agent - Manages lead form operations
Handles creating, retrieving, and managing lead forms and leads
"""

from typing import Dict, Any, List

from ..core.models import LeadFormParams, LeadForm, Lead
from ..core.exceptions import LeadFormError
from ..core.utils import log_debug


class LeadFormAgent:
    """Agent for lead form management"""

    def __init__(self, api_client):
        """
        Initialize Lead Form Agent

        Args:
            api_client: MetaAPIClient instance
        """
        self.api = api_client
        log_debug("[LeadFormAgent] Initialized")

    async def create_lead_form(self, page_id: str, params: LeadFormParams) -> LeadForm:
        """
        Create a new lead form on a page

        Args:
            page_id: Facebook Page ID (NOT ad_account_id!)
            params: Lead form parameters

        Returns:
            LeadForm dataclass with form details
        """
        log_debug(f"\n[LeadFormAgent] Creating lead form: {params.name}")

        # NOTE: Lead forms are created on PAGE_ID, not ad_account_id
        endpoint = f"/{page_id}/leadgen_forms"
        data = params.to_api_dict()

        try:
            response = await self.api.post(endpoint, json_data=data)

            form_id = response.get("id")
            if not form_id:
                raise LeadFormError("No form id returned from API")

            lead_form = LeadForm(
                id=form_id,
                name=params.name,
                status="ACTIVE",  # Default status on creation
                page_id=page_id,
                locale=params.locale,
                questions=params.questions
            )

            log_debug(f"[LeadFormAgent] Lead form created: {lead_form.id}")
            return lead_form

        except Exception as e:
            log_debug(f"[LeadFormAgent] Lead form creation failed: {e}")
            raise LeadFormError(f"Failed to create lead form '{params.name}': {str(e)}") from e

    async def get_lead_form(self, form_id: str) -> Dict[str, Any]:
        """
        Get lead form details by ID

        Args:
            form_id: Lead form ID

        Returns:
            Dict with form details
        """
        log_debug(f"\n[LeadFormAgent] Getting lead form: {form_id}")

        endpoint = f"/{form_id}"
        params = {
            "fields": "id,name,status,locale,questions,privacy_policy,thank_you_page,created_time,page"
        }

        try:
            response = await self.api.get(endpoint, params=params)
            log_debug(f"[LeadFormAgent] Lead form retrieved: {form_id}")
            return response
        except Exception as e:
            log_debug(f"[LeadFormAgent] Failed to get lead form: {e}")
            raise LeadFormError(f"Failed to get lead form '{form_id}': {str(e)}") from e

    async def list_lead_forms(self, page_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List all lead forms for a page

        Args:
            page_id: Facebook Page ID
            limit: Maximum forms to return

        Returns:
            List of form dictionaries
        """
        log_debug(f"\n[LeadFormAgent] Listing lead forms for page: {page_id}")

        # NOTE: Uses PAGE_ID endpoint
        endpoint = f"/{page_id}/leadgen_forms"
        params = {
            "fields": "id,name,status,locale,created_time,leads_count",
            "limit": limit
        }

        try:
            response = await self.api.get(endpoint, params=params)
            forms = response.get("data", [])
            log_debug(f"[LeadFormAgent] Found {len(forms)} lead forms")
            return forms
        except Exception as e:
            log_debug(f"[LeadFormAgent] Failed to list lead forms: {e}")
            raise LeadFormError(f"Failed to list lead forms for page '{page_id}': {str(e)}") from e

    async def get_leads(self, form_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all leads from a lead form

        Args:
            form_id: Lead form ID
            limit: Maximum leads to return

        Returns:
            List of lead dictionaries
        """
        log_debug(f"\n[LeadFormAgent] Getting leads from form: {form_id}")

        endpoint = f"/{form_id}/leads"
        params = {
            "fields": "id,created_time,field_data,ad_id,ad_name,adset_id,campaign_id",
            "limit": limit
        }

        try:
            response = await self.api.get(endpoint, params=params)
            leads = response.get("data", [])
            log_debug(f"[LeadFormAgent] Found {len(leads)} leads")
            return leads
        except Exception as e:
            log_debug(f"[LeadFormAgent] Failed to get leads: {e}")
            raise LeadFormError(f"Failed to get leads from form '{form_id}': {str(e)}") from e

    async def get_lead(self, lead_id: str) -> Dict[str, Any]:
        """
        Get a single lead's details

        Args:
            lead_id: Lead ID

        Returns:
            Dict with lead details
        """
        log_debug(f"\n[LeadFormAgent] Getting lead: {lead_id}")

        endpoint = f"/{lead_id}"
        params = {
            "fields": "id,created_time,field_data,ad_id,ad_name,adset_id,adset_name,campaign_id,campaign_name,form_id,is_organic"
        }

        try:
            response = await self.api.get(endpoint, params=params)
            log_debug(f"[LeadFormAgent] Lead retrieved: {lead_id}")
            return response
        except Exception as e:
            log_debug(f"[LeadFormAgent] Failed to get lead: {e}")
            raise LeadFormError(f"Failed to get lead '{lead_id}': {str(e)}") from e

    async def update_lead_form_status(self, form_id: str, status: str) -> Dict[str, Any]:
        """
        Update lead form status (archive/activate)

        Args:
            form_id: Lead form ID
            status: New status (ACTIVE, ARCHIVED)

        Returns:
            API response
        """
        log_debug(f"\n[LeadFormAgent] Updating form {form_id} status to: {status}")

        endpoint = f"/{form_id}"
        data = {"status": status}

        try:
            response = await self.api.post(endpoint, json_data=data)
            log_debug(f"[LeadFormAgent] Form status updated")
            return response
        except Exception as e:
            log_debug(f"[LeadFormAgent] Failed to update form status: {e}")
            raise LeadFormError(f"Failed to update form '{form_id}': {str(e)}") from e
