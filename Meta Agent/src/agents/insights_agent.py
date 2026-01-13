"""
META Marketing Agent System - Insights Agent
Handles fetching and analyzing performance data from Meta Ads API.
"""

import asyncio
import httpx
import json
import csv
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict

from ..core.config import Config
from ..core.utils import log_debug


@dataclass
class InsightMetrics:
    """Insight metrics data"""
    impressions: int = 0
    clicks: int = 0
    spend: float = 0.0
    reach: int = 0
    frequency: float = 0.0
    ctr: float = 0.0
    cpc: float = 0.0
    cpm: float = 0.0
    cpp: float = 0.0
    actions: List[Dict[str, Any]] = None
    action_values: List[Dict[str, Any]] = None
    conversions: int = 0
    conversion_value: float = 0.0
    roas: float = 0.0
    date_start: str = ""
    date_stop: str = ""
    campaign_name: Optional[str] = None
    adset_name: Optional[str] = None
    ad_name: Optional[str] = None

    def __post_init__(self):
        if self.actions is None:
            self.actions = []
        if self.action_values is None:
            self.action_values = []


class InsightsAgent:
    """Agent for fetching and analyzing ad performance insights"""

    def __init__(self, access_token: str):
        """
        Initialize InsightsAgent

        Args:
            access_token: Meta API access token
        """
        self.access_token = access_token
        self.api_url = Config.META_API_BASE_URL

    async def _make_request(self, method: str, url: str, params: Optional[Dict] = None,
                           json_data: Optional[Dict] = None, retry_count: int = 0) -> Dict[str, Any]:
        """Make API request with retry logic"""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": "MetaAdsAgent/1.0"
        }

        try:
            async with httpx.AsyncClient(timeout=Config.API_TIMEOUT) as client:
                if params is None:
                    params = {}
                params["access_token"] = self.access_token

                response = await client.request(method, url, params=params, json=json_data, headers=headers)
                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and retry_count < Config.MAX_RETRIES:
                log_debug(f"Rate limited, retrying in {2 ** retry_count} seconds...")
                await asyncio.sleep(2 ** retry_count)
                return await self._make_request(method, url, params, json_data, retry_count + 1)
            raise

    async def get_account_insights(self, account_id: str,
                                   date_preset: str = "last_7d",
                                   fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fetch account level insights

        Args:
            account_id: Ad account ID (without 'act_' prefix)
            date_preset: Date range preset
            fields: Specific fields to retrieve

        Returns:
            Account insights data
        """
        log_debug(f"\n[DEBUG] Fetching account insights for: {account_id}")

        if not fields:
            fields = [
                "impressions", "clicks", "spend", "reach", "frequency",
                "ctr", "cpc", "cpm", "actions", "action_values", "date_start", "date_stop"
            ]

        url = f"{self.api_url}/act_{account_id}/insights"
        params = {
            "date_preset": date_preset,
            "fields": ",".join(fields)
        }

        try:
            response = await self._make_request("GET", url, params=params)
            log_debug(f"Account insights retrieved successfully")
            return response
        except Exception as e:
            log_debug(f"Error fetching account insights: {e}")
            raise

    async def get_campaign_insights(self, campaign_id: str,
                                   date_preset: str = "last_7d",
                                   fields: Optional[List[str]] = None,
                                   breakdowns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fetch campaign level insights

        Args:
            campaign_id: Campaign ID
            date_preset: Date range preset
            fields: Specific fields to retrieve
            breakdowns: Data breakdowns

        Returns:
            Campaign insights data
        """
        log_debug(f"\n[DEBUG] Fetching campaign insights for: {campaign_id}")

        if not fields:
            fields = [
                "impressions", "clicks", "spend", "reach", "frequency",
                "ctr", "cpc", "cpm", "actions", "action_values",
                "campaign_id", "campaign_name", "date_start", "date_stop"
            ]

        url = f"{self.api_url}/{campaign_id}/insights"
        params = {
            "date_preset": date_preset,
            "fields": ",".join(fields)
        }

        if breakdowns:
            params["breakdowns"] = ",".join(breakdowns)

        try:
            response = await self._make_request("GET", url, params=params)
            log_debug(f"Campaign insights retrieved successfully")
            return response
        except Exception as e:
            log_debug(f"Error fetching campaign insights: {e}")
            raise

    async def get_adset_insights(self, adset_id: str,
                                date_preset: str = "last_7d",
                                fields: Optional[List[str]] = None,
                                breakdowns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fetch ad set level insights

        Args:
            adset_id: Ad set ID
            date_preset: Date range preset
            fields: Specific fields to retrieve
            breakdowns: Data breakdowns

        Returns:
            Ad set insights data
        """
        log_debug(f"\n[DEBUG] Fetching ad set insights for: {adset_id}")

        if not fields:
            fields = [
                "impressions", "clicks", "spend", "reach", "frequency",
                "ctr", "cpc", "cpm", "actions", "action_values",
                "adset_id", "adset_name", "date_start", "date_stop"
            ]

        url = f"{self.api_url}/{adset_id}/insights"
        params = {
            "date_preset": date_preset,
            "fields": ",".join(fields)
        }

        if breakdowns:
            params["breakdowns"] = ",".join(breakdowns)

        try:
            response = await self._make_request("GET", url, params=params)
            log_debug(f"Ad set insights retrieved successfully")
            return response
        except Exception as e:
            log_debug(f"Error fetching ad set insights: {e}")
            raise

    async def get_ad_insights(self, ad_id: str,
                             date_preset: str = "last_7d",
                             fields: Optional[List[str]] = None,
                             breakdowns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Fetch ad level insights

        Args:
            ad_id: Ad ID
            date_preset: Date range preset
            fields: Specific fields to retrieve
            breakdowns: Data breakdowns

        Returns:
            Ad insights data
        """
        log_debug(f"\n[DEBUG] Fetching ad insights for: {ad_id}")

        if not fields:
            fields = [
                "impressions", "clicks", "spend", "reach", "frequency",
                "ctr", "cpc", "cpm", "actions", "action_values",
                "ad_id", "adcreative", "date_start", "date_stop"
            ]

        url = f"{self.api_url}/{ad_id}/insights"
        params = {
            "date_preset": date_preset,
            "fields": ",".join(fields)
        }

        if breakdowns:
            params["breakdowns"] = ",".join(breakdowns)

        try:
            response = await self._make_request("GET", url, params=params)
            log_debug(f"Ad insights retrieved successfully")
            return response
        except Exception as e:
            log_debug(f"Error fetching ad insights: {e}")
            raise

    def parse_insight_metrics(self, insight_data: Dict[str, Any]) -> InsightMetrics:
        """Parse raw insight data into InsightMetrics object"""
        metrics = InsightMetrics()

        metrics.impressions = int(insight_data.get("impressions", 0))
        metrics.clicks = int(insight_data.get("clicks", 0))
        metrics.spend = float(insight_data.get("spend", 0.0))
        metrics.reach = int(insight_data.get("reach", 0))
        metrics.frequency = float(insight_data.get("frequency", 0.0))
        metrics.ctr = float(insight_data.get("ctr", 0.0))
        metrics.cpc = float(insight_data.get("cpc", 0.0))
        metrics.cpm = float(insight_data.get("cpm", 0.0))
        metrics.cpp = float(insight_data.get("cpp", 0.0))

        if "actions" in insight_data:
            metrics.actions = insight_data["actions"]
        if "action_values" in insight_data:
            metrics.action_values = insight_data["action_values"]

        if metrics.actions:
            for action in metrics.actions:
                if action.get("action_type") == "offsite_conversion.post_click":
                    metrics.conversions = int(action.get("value", 0))

        metrics.campaign_name = insight_data.get("campaign_name")
        metrics.adset_name = insight_data.get("adset_name")
        metrics.ad_name = insight_data.get("ad_name")
        metrics.date_start = insight_data.get("date_start", "")
        metrics.date_stop = insight_data.get("date_stop", "")

        return metrics

    def calculate_performance_metrics(self, metrics: InsightMetrics) -> Dict[str, Any]:
        """Calculate additional performance metrics"""
        calculated = {}

        if metrics.conversion_value > 0 and metrics.spend > 0:
            calculated["roi"] = ((metrics.conversion_value - metrics.spend) / metrics.spend) * 100
        else:
            calculated["roi"] = 0

        if metrics.conversions > 0:
            calculated["cost_per_conversion"] = metrics.spend / metrics.conversions
        else:
            calculated["cost_per_conversion"] = 0

        if metrics.impressions > 0:
            calculated["engagement_rate"] = (metrics.clicks / metrics.impressions) * 100
        else:
            calculated["engagement_rate"] = 0

        if metrics.conversions > 0:
            calculated["cost_per_result"] = metrics.spend / metrics.conversions

        return calculated

    def generate_performance_report(self, insights_list: List[Dict[str, Any]],
                                   metric_name: str = "Campaign") -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        log_debug(f"\n[DEBUG] Generating {metric_name} performance report...")

        report = {
            "report_type": f"{metric_name} Performance Report",
            "generated_at": datetime.now().isoformat(),
            "total_records": len(insights_list),
            "summary": {
                "total_spend": 0.0,
                "total_impressions": 0,
                "total_clicks": 0,
                "total_conversions": 0,
                "average_ctr": 0.0,
                "average_cpc": 0.0,
                "average_cpm": 0.0,
                "average_roas": 0.0
            },
            "details": []
        }

        if not insights_list:
            return report

        total_ctr = 0
        total_cpc = 0
        total_cpm = 0
        total_roas = 0

        for insight in insights_list:
            metrics = self.parse_insight_metrics(insight)
            calc_metrics = self.calculate_performance_metrics(metrics)

            report["summary"]["total_spend"] += metrics.spend
            report["summary"]["total_impressions"] += metrics.impressions
            report["summary"]["total_clicks"] += metrics.clicks
            report["summary"]["total_conversions"] += metrics.conversions

            total_ctr += metrics.ctr
            total_cpc += metrics.cpc
            total_cpm += metrics.cpm
            if "roi" in calc_metrics:
                total_roas += calc_metrics["roi"]

            detail = asdict(metrics)
            detail.update(calc_metrics)
            report["details"].append(detail)

        count = len(insights_list)
        report["summary"]["average_ctr"] = total_ctr / count if count > 0 else 0
        report["summary"]["average_cpc"] = total_cpc / count if count > 0 else 0
        report["summary"]["average_cpm"] = total_cpm / count if count > 0 else 0
        report["summary"]["average_roas"] = total_roas / count if count > 0 else 0

        log_debug(f"Report generated successfully")
        return report

    def export_to_json(self, data: Dict[str, Any], filename: str) -> str:
        """Export data to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            log_debug(f"Data exported to {filename}")
            return filename
        except Exception as e:
            log_debug(f"Error exporting data: {e}")
            raise

    def export_to_csv(self, insights_list: List[Dict[str, Any]], filename: str) -> str:
        """Export insights to CSV file"""
        try:
            if not insights_list:
                log_debug("No data to export")
                return None

            fieldnames = set()
            for insight in insights_list:
                fieldnames.update(insight.keys())
            fieldnames = sorted(list(fieldnames))

            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(insights_list)

            log_debug(f"Data exported to {filename}")
            return filename
        except Exception as e:
            log_debug(f"Error exporting to CSV: {e}")
            raise


def validate_date_preset(date_preset: str) -> bool:
    """Validate date preset value"""
    valid_presets = [
        "last_7d", "last_14d", "last_28d", "last_30d", "last_90d",
        "today", "yesterday", "this_week", "last_week", "last_month",
        "this_quarter", "last_3m", "lifetime"
    ]
    return date_preset in valid_presets


def validate_breakdown(breakdown: str) -> bool:
    """Validate breakdown value"""
    valid_breakdowns = [
        "age", "gender", "country", "region", "city", "device",
        "placement", "platform", "audience_id", "conversion_device",
        "conversion_destination", "frequency_value", "impression_device"
    ]
    return breakdown in valid_breakdowns
