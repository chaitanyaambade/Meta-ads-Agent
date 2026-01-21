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
    # New fields for enhanced insights
    link_ctr: float = 0.0  # Link Click-Through Rate (fatigue signal)
    inline_link_clicks: int = 0  # Link clicks for CTR calculation
    learning_phase_status: Optional[str] = None  # Learning phase status
    results_per_day: float = 0.0  # Daily results average
    rolling_7d_cost_per_result: float = 0.0  # 7-day rolling cost per result
    cpm_trend: Optional[str] = None  # CPM trend direction (increasing/decreasing/stable)
    cpm_change_percent: float = 0.0  # CPM change percentage
    daily_spend: float = 0.0  # Average daily spend
    primary_result_type: Optional[str] = None  # Lead, Call, or WhatsApp
    primary_result_count: int = 0  # Primary conversion count

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
                "ctr", "cpc", "cpm", "actions", "action_values",
                "inline_link_clicks", "inline_link_click_ctr",
                "date_start", "date_stop"
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
                "inline_link_clicks", "inline_link_click_ctr",
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
                "inline_link_clicks", "inline_link_click_ctr",
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
                "inline_link_clicks", "inline_link_click_ctr",
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

    async def get_adset_learning_phase(self, adset_id: str) -> Dict[str, Any]:
        """
        Fetch ad set learning phase status

        Args:
            adset_id: Ad set ID

        Returns:
            Learning phase status data including:
            - learning_phase_info: Current learning phase status
            - effective_status: Overall effective status
        """
        log_debug(f"\n[DEBUG] Fetching learning phase for ad set: {adset_id}")

        url = f"{self.api_url}/{adset_id}"
        params = {
            "fields": "id,name,status,effective_status,learning_phase_info"
        }

        try:
            response = await self._make_request("GET", url, params=params)
            learning_info = response.get("learning_phase_info", {})

            result = {
                "adset_id": adset_id,
                "adset_name": response.get("name"),
                "status": response.get("status"),
                "effective_status": response.get("effective_status"),
                "learning_phase_status": learning_info.get("status", "UNKNOWN"),
                "is_in_learning": learning_info.get("status") == "LEARNING",
                "actions_remaining": learning_info.get("actions_remaining_to_exit", 0)
            }

            log_debug(f"Learning phase status: {result['learning_phase_status']}")
            return result
        except Exception as e:
            log_debug(f"Error fetching learning phase: {e}")
            raise

    async def get_daily_insights(self, entity_id: str, entity_type: str = "campaign",
                                  days: int = 7,
                                  fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Fetch daily insights for rolling calculations

        Args:
            entity_id: Campaign, Ad Set, or Ad ID
            entity_type: Type of entity (campaign, adset, ad)
            days: Number of days to fetch (default 7)
            fields: Specific fields to retrieve

        Returns:
            List of daily insights data
        """
        log_debug(f"\n[DEBUG] Fetching daily insights for {entity_type}: {entity_id}")

        if not fields:
            fields = [
                "impressions", "clicks", "spend", "reach", "frequency",
                "ctr", "cpc", "cpm", "actions", "action_values",
                "inline_link_clicks", "inline_link_click_ctr",
                "date_start", "date_stop"
            ]

        url = f"{self.api_url}/{entity_id}/insights"
        params = {
            "date_preset": f"last_{days}d",
            "time_increment": "1",  # Daily breakdown
            "fields": ",".join(fields)
        }

        try:
            response = await self._make_request("GET", url, params=params)
            daily_data = response.get("data", [])
            log_debug(f"Retrieved {len(daily_data)} days of insights")
            return daily_data
        except Exception as e:
            log_debug(f"Error fetching daily insights: {e}")
            raise

    def calculate_rolling_cost_per_result(self, daily_insights: List[Dict[str, Any]],
                                          result_action_types: List[str] = None) -> float:
        """
        Calculate 7-day rolling cost per result

        Args:
            daily_insights: List of daily insight data
            result_action_types: Action types to count as results (leads, calls, etc.)

        Returns:
            Rolling cost per result value
        """
        if not result_action_types:
            result_action_types = [
                "lead", "onsite_conversion.lead_grouped",
                "contact_call_click", "onsite_web_call",
                "onsite_conversion.messaging_conversation_started_7d",
                "onsite_conversion.messaging_first_reply"
            ]

        total_spend = 0.0
        total_results = 0

        for day_data in daily_insights:
            total_spend += float(day_data.get("spend", 0))

            actions = day_data.get("actions", [])
            for action in actions:
                if action.get("action_type") in result_action_types:
                    total_results += int(action.get("value", 0))

        if total_results > 0:
            return total_spend / total_results
        return 0.0

    def calculate_results_per_day(self, daily_insights: List[Dict[str, Any]],
                                  result_action_types: List[str] = None) -> float:
        """
        Calculate average results per day

        Args:
            daily_insights: List of daily insight data
            result_action_types: Action types to count as results

        Returns:
            Average results per day
        """
        if not result_action_types:
            result_action_types = [
                "lead", "onsite_conversion.lead_grouped",
                "contact_call_click", "onsite_web_call",
                "onsite_conversion.messaging_conversation_started_7d",
                "onsite_conversion.messaging_first_reply"
            ]

        total_results = 0
        days_with_data = len(daily_insights)

        for day_data in daily_insights:
            actions = day_data.get("actions", [])
            for action in actions:
                if action.get("action_type") in result_action_types:
                    total_results += int(action.get("value", 0))

        if days_with_data > 0:
            return total_results / days_with_data
        return 0.0

    def calculate_cpm_trend(self, daily_insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate CPM trend over the period

        Args:
            daily_insights: List of daily insight data

        Returns:
            Dictionary with trend direction and percentage change
        """
        if len(daily_insights) < 2:
            return {"trend": "insufficient_data", "change_percent": 0.0}

        # Sort by date
        sorted_data = sorted(daily_insights, key=lambda x: x.get("date_start", ""))

        # Get CPM values
        cpm_values = [float(d.get("cpm", 0)) for d in sorted_data if float(d.get("cpm", 0)) > 0]

        if len(cpm_values) < 2:
            return {"trend": "insufficient_data", "change_percent": 0.0}

        # Calculate trend using first half vs second half comparison
        mid_point = len(cpm_values) // 2
        first_half_avg = sum(cpm_values[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(cpm_values[mid_point:]) / (len(cpm_values) - mid_point) if (len(cpm_values) - mid_point) > 0 else 0

        if first_half_avg > 0:
            change_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        else:
            change_percent = 0.0

        # Determine trend direction
        if change_percent > 10:
            trend = "increasing"
        elif change_percent < -10:
            trend = "decreasing"
        else:
            trend = "stable"

        return {
            "trend": trend,
            "change_percent": round(change_percent, 2),
            "first_period_avg": round(first_half_avg, 2),
            "second_period_avg": round(second_half_avg, 2)
        }

    def extract_primary_result(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract primary conversion result (Leads, Calls, or WhatsApp)

        Args:
            actions: List of action data

        Returns:
            Dictionary with result type and count
        """
        # Priority order for primary results
        result_mappings = {
            "lead": ("Lead", ["lead", "onsite_conversion.lead_grouped"]),
            "call": ("Call", ["contact_call_click", "onsite_web_call", "phone_call"]),
            "whatsapp": ("WhatsApp", [
                "onsite_conversion.messaging_conversation_started_7d",
                "onsite_conversion.messaging_first_reply",
                "onsite_conversion.messaging_welcome_message_view"
            ])
        }

        results = {"Lead": 0, "Call": 0, "WhatsApp": 0}

        for action in actions:
            action_type = action.get("action_type", "")
            value = int(action.get("value", 0))

            for result_name, action_types in result_mappings.values():
                if action_type in action_types:
                    results[result_name] += value

        # Find primary result (highest count)
        primary_type = max(results, key=results.get)
        primary_count = results[primary_type]

        if primary_count == 0:
            return {"type": None, "count": 0, "all_results": results}

        return {
            "type": primary_type,
            "count": primary_count,
            "all_results": results
        }

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

        # Parse Link CTR (fatigue signal)
        metrics.inline_link_clicks = int(insight_data.get("inline_link_clicks", 0))
        metrics.link_ctr = float(insight_data.get("inline_link_click_ctr", 0.0))

        if "actions" in insight_data:
            metrics.actions = insight_data["actions"]
        if "action_values" in insight_data:
            metrics.action_values = insight_data["action_values"]

        if metrics.actions:
            for action in metrics.actions:
                if action.get("action_type") == "offsite_conversion.post_click":
                    metrics.conversions = int(action.get("value", 0))

            # Extract primary result (Lead, Call, or WhatsApp)
            primary_result = self.extract_primary_result(metrics.actions)
            metrics.primary_result_type = primary_result["type"]
            metrics.primary_result_count = primary_result["count"]

        # Parse learning phase status if available
        if "learning_phase_info" in insight_data:
            learning_info = insight_data["learning_phase_info"]
            metrics.learning_phase_status = learning_info.get("status", "UNKNOWN")

        metrics.campaign_name = insight_data.get("campaign_name")
        metrics.adset_name = insight_data.get("adset_name")
        metrics.ad_name = insight_data.get("ad_name")
        metrics.date_start = insight_data.get("date_start", "")
        metrics.date_stop = insight_data.get("date_stop", "")

        # Calculate daily spend if date range is available
        if metrics.date_start and metrics.date_stop:
            try:
                start = datetime.strptime(metrics.date_start, "%Y-%m-%d")
                stop = datetime.strptime(metrics.date_stop, "%Y-%m-%d")
                days = (stop - start).days + 1
                if days > 0:
                    metrics.daily_spend = metrics.spend / days
            except ValueError:
                metrics.daily_spend = metrics.spend

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

        # Add new enhanced metrics
        calculated["link_ctr"] = metrics.link_ctr
        calculated["primary_result_type"] = metrics.primary_result_type
        calculated["primary_result_count"] = metrics.primary_result_count
        calculated["daily_spend"] = metrics.daily_spend
        calculated["learning_phase_status"] = metrics.learning_phase_status

        return calculated

    async def get_enhanced_insights(self, entity_id: str, entity_type: str = "campaign",
                                    adset_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch comprehensive enhanced insights including all new metrics

        This method retrieves:
        - Standard insights (spend, impressions, clicks, etc.)
        - Link CTR (fatigue signal)
        - Learning Phase Status (from adset)
        - 7-day Rolling Cost per Result
        - Results per Day
        - CPM Trend
        - Primary Conversion Count (Lead/Call/WhatsApp)
        - Daily Spend

        Args:
            entity_id: Campaign, Ad Set, or Ad ID
            entity_type: Type of entity (campaign, adset, ad)
            adset_id: Optional adset ID for learning phase (if entity is ad or campaign)

        Returns:
            Enhanced insights dictionary with all metrics
        """
        log_debug(f"\n[DEBUG] Fetching enhanced insights for {entity_type}: {entity_id}")

        # Fetch standard insights
        if entity_type == "campaign":
            standard_insights = await self.get_campaign_insights(entity_id)
        elif entity_type == "adset":
            standard_insights = await self.get_adset_insights(entity_id)
            adset_id = entity_id  # Use the entity ID for learning phase
        elif entity_type == "ad":
            standard_insights = await self.get_ad_insights(entity_id)
        else:
            raise ValueError(f"Invalid entity type: {entity_type}")

        insights_data = standard_insights.get("data", [{}])[0] if standard_insights.get("data") else {}

        # Fetch daily insights for rolling calculations
        daily_insights = await self.get_daily_insights(entity_id, entity_type, days=7)

        # Calculate rolling metrics
        rolling_cost_per_result = self.calculate_rolling_cost_per_result(daily_insights)
        results_per_day = self.calculate_results_per_day(daily_insights)
        cpm_trend = self.calculate_cpm_trend(daily_insights)

        # Fetch learning phase status if adset_id is provided
        learning_phase = None
        if adset_id:
            try:
                learning_phase = await self.get_adset_learning_phase(adset_id)
            except Exception as e:
                log_debug(f"Could not fetch learning phase: {e}")
                learning_phase = {"learning_phase_status": "UNKNOWN", "is_in_learning": False}

        # Parse standard metrics
        metrics = self.parse_insight_metrics(insights_data)

        # Add rolling and trend metrics
        metrics.rolling_7d_cost_per_result = rolling_cost_per_result
        metrics.results_per_day = results_per_day
        metrics.cpm_trend = cpm_trend.get("trend")
        metrics.cpm_change_percent = cpm_trend.get("change_percent", 0.0)

        # Add learning phase if available
        if learning_phase:
            metrics.learning_phase_status = learning_phase.get("learning_phase_status", "UNKNOWN")

        # Build enhanced response
        enhanced_insights = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "date_range": {
                "start": metrics.date_start,
                "end": metrics.date_stop
            },
            # Budget & Spend
            "spend": {
                "total": metrics.spend,
                "daily_average": metrics.daily_spend
            },
            # Primary Conversion
            "primary_conversion": {
                "type": metrics.primary_result_type,
                "count": metrics.primary_result_count
            },
            # Cost Metrics
            "cost_per_result": {
                "current": metrics.spend / metrics.primary_result_count if metrics.primary_result_count > 0 else 0,
                "rolling_7d": metrics.rolling_7d_cost_per_result
            },
            # Performance Stability
            "results_per_day": metrics.results_per_day,
            # Learning Phase
            "learning_phase": {
                "status": metrics.learning_phase_status,
                "is_in_learning": learning_phase.get("is_in_learning", False) if learning_phase else False,
                "actions_remaining": learning_phase.get("actions_remaining", 0) if learning_phase else 0
            },
            # Fatigue Signals
            "frequency": metrics.frequency,
            "link_ctr": metrics.link_ctr,
            # Audience/Competition Signals
            "cpm": {
                "current": metrics.cpm,
                "trend": metrics.cpm_trend,
                "change_percent": metrics.cpm_change_percent
            },
            # Additional Standard Metrics
            "impressions": metrics.impressions,
            "clicks": metrics.clicks,
            "reach": metrics.reach,
            "ctr": metrics.ctr,
            "cpc": metrics.cpc,
            # Raw metrics object for further processing
            "raw_metrics": asdict(metrics)
        }

        log_debug(f"Enhanced insights generated successfully")
        return enhanced_insights

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
