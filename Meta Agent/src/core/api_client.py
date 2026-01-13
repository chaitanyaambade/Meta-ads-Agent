"""
Meta API Client for HTTP communication
"""

import json
import httpx
from typing import Dict

from .config import Config
from .exceptions import APIError
from .utils import log_debug


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
                try:
                    log_debug(f"[API] Error Payload: {json.dumps(error_data, indent=2)}")
                except Exception:
                    log_debug(f"[API] Error Payload (raw): {error_data}")

                error_msg = error_data.get("error", {}).get("message", "Unknown error")
                error_code = error_data.get("error", {}).get("code")
                error_subcode = error_data.get("error", {}).get("error_subcode")
                log_debug(f"[API] Error: {error_msg} (Code: {error_code}, Subcode: {error_subcode})")
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
