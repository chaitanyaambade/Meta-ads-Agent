"""
JSON-based Campaign and Ad Set Operations
Handles all operations via JSON action parameter
"""

import json
import os
import asyncio

from ..agents.orchestrator import OrchestratorAgent, create_adset_params_from_json, create_lead_form_params_from_json
from ..core.models import CampaignParams
from ..core.exceptions import ValidationError
from ..agents.asset_agent import AssetValidationError, AssetUploadError
from ..agents.insights_agent import InsightsAgent, validate_date_preset, validate_breakdown

# Global quiet flag for JSON-only output
QUIET_MODE = False


def set_operations_quiet_mode(quiet: bool):
    """Set quiet mode globally for operations"""
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


async def handle_list_ad_accounts(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """List all ad accounts accessible with current access token"""
    log_section("LIST AD ACCOUNTS")
    
    try:
        accounts = await orchestrator.list_ad_accounts()
        
        if not accounts:
            log_info(f"\n✗ No ad accounts found")
            return {"status": "success", "accounts": [], "count": 0}
        
        log_info(f"\n✓ Found {len(accounts)} ad account(s):")
        account_list = []
        for idx, account in enumerate(accounts, 1):
            acc_id = account.get("id")
            acc_name = account.get("name")
            acc_status = account.get("account_status")
            acc_currency = account.get("currency")
            acc_timezone = account.get("timezone_name")
            
            log_info(f"\n  [{idx}] {acc_name}")
            log_info(f"      ID: {acc_id}")
            log_info(f"      Status: {acc_status}")
            log_info(f"      Currency: {acc_currency}")
            log_info(f"      Timezone: {acc_timezone}")
            log_info(f"      Created: {account.get('created_time')}")
            
            account_list.append({
                "id": acc_id,
                "name": acc_name,
                "status": acc_status,
                "currency": acc_currency,
                "timezone": acc_timezone,
                "created_time": account.get("created_time")
            })
        
        return {"status": "success", "accounts": account_list, "count": len(accounts)}
    
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
            await orchestrator.campaign_agent.update_adset_status(adset_id, "PAUSED")
            log_info(f"\n✓ Ad set paused successfully")
            return {"status": "success", "action": "pause"}
        elif update_type == "active":
            await orchestrator.campaign_agent.update_adset_status(adset_id, "ACTIVE")
            log_info(f"\n✓ Ad set activated successfully")
            return {"status": "success", "action": "active"}
        elif update_type == "delete":
            await orchestrator.campaign_agent.update_adset_status(adset_id, "DELETED")
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

        log_info(f"\n[INFO] Fetching ad set: {adset_id}")

        adset_info = await orchestrator.campaign_agent.get_adset(adset_id)

        log_info(f"\n✓ Ad set details:")
        log_info(f"  ID: {adset_info.get('id')}")
        log_info(f"  Name: {adset_info.get('name')}")
        log_info(f"  Campaign ID: {adset_info.get('campaign_id')}")
        log_info(f"  Status: {adset_info.get('status')}")
        log_info(f"  Optimization Goal: {adset_info.get('optimization_goal')}")
        log_info(f"  Created: {adset_info.get('created_time')}")

        return {"status": "success", "adset": adset_info}

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


async def handle_list_adsets(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """List all ad sets in the ad account or under a specific campaign"""
    log_section("LIST AD SETS")

    try:
        campaign_id = payload.get("campaign_id")
        limit = payload.get("limit", 50)

        adsets = await orchestrator.campaign_agent.list_adsets(ad_account_id, campaign_id, limit)

        if not adsets:
            return {"status": "success", "adsets": [], "count": 0}

        adset_list = []
        for adset in adsets:
            # Handle both dict and object formats
            adset_id = adset.get("id") if isinstance(adset, dict) else adset.id
            adset_name = adset.get("name") if isinstance(adset, dict) else adset.name
            adset_status = adset.get("status") if isinstance(adset, dict) else adset.status
            adset_campaign_id = adset.get("campaign_id") if isinstance(adset, dict) else getattr(adset, 'campaign_id', None)
            optimization_goal = adset.get("optimization_goal") if isinstance(adset, dict) else getattr(adset, 'optimization_goal', None)

            adset_list.append({
                "id": adset_id,
                "name": adset_name,
                "status": adset_status,
                "campaign_id": adset_campaign_id,
                "optimization_goal": optimization_goal
            })

        return {"status": "success", "adsets": adset_list, "count": len(adsets)}

    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_list_ads(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """List all ads in the ad account or under a specific ad set"""
    log_section("LIST ADS")

    try:
        adset_id = payload.get("adset_id")
        limit = payload.get("limit", 50)

        ads = await orchestrator.ad_agent.list_ads(ad_account_id, adset_id, limit)

        if not ads:
            return {"status": "success", "ads": [], "count": 0}

        ad_list = []
        for ad in ads:
            # Handle both dict and object formats
            ad_id = ad.get("id") if isinstance(ad, dict) else ad.id
            ad_name = ad.get("name") if isinstance(ad, dict) else ad.name
            ad_status = ad.get("status") if isinstance(ad, dict) else ad.status
            ad_adset_id = ad.get("adset_id") if isinstance(ad, dict) else getattr(ad, 'adset_id', None)
            effective_status = ad.get("effective_status") if isinstance(ad, dict) else getattr(ad, 'effective_status', None)

            ad_list.append({
                "id": ad_id,
                "name": ad_name,
                "status": ad_status,
                "adset_id": ad_adset_id,
                "effective_status": effective_status
            })

        return {"status": "success", "ads": ad_list, "count": len(ads)}

    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_create_creative(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Create an ad creative"""
    log_section("CREATE CREATIVE")
    try:
        creative = payload.get("creative")
        if not creative:
            raise ValidationError("Missing 'creative' object in payload")

        result = await orchestrator.ad_agent.create_creative(ad_account_id, creative)

        log_info(f"\n✓ Creative created: {result.id}")
        return {"status": "success", "creative_id": result.id, "data": result.data}
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_creative(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get creative details"""
    log_section("GET CREATIVE")
    try:
        creative_id = payload.get("creative_id")
        if not creative_id:
            raise ValidationError("Missing 'creative_id' in payload")

        result = await orchestrator.ad_agent.get_creative(creative_id)
        log_info(f"\n✓ Creative retrieved: {creative_id}")
        return {"status": "success", "creative_id": creative_id, "data": result}
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_create_ad(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Create an ad"""
    log_section("CREATE AD")
    try:
        ad = payload.get("ad")
        if not ad:
            raise ValidationError("Missing 'ad' object in payload")

        result = await orchestrator.ad_agent.create_ad(ad_account_id, ad)

        log_info(f"\n✓ Ad created: {result.id}")
        return {"status": "success", "ad_id": result.id, "data": result.data}
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_update_ad(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Update an ad"""
    log_section("UPDATE AD")
    try:
        ad_id = payload.get("ad_id")
        update_fields = payload.get("update")
        if not ad_id:
            raise ValidationError("Missing 'ad_id' in payload")
        if not update_fields:
            raise ValidationError("Missing 'update' object in payload")

        result = await orchestrator.ad_agent.update_ad(ad_id, update_fields)

        log_info(f"\n✓ Ad updated: {ad_id}")
        return {"status": "success", "ad_id": ad_id, "data": result}
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_ad(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get ad details"""
    log_section("GET AD")
    try:
        ad_id = payload.get("ad_id")
        if not ad_id:
            raise ValidationError("Missing 'ad_id' in payload")

        result = await orchestrator.ad_agent.get_ad(ad_id)
        log_info(f"\n✓ Ad retrieved: {ad_id}")
        return {"status": "success", "ad_id": ad_id, "data": result}
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


# ============================================================================
# INSIGHTS OPERATIONS
# ============================================================================

async def handle_get_account_insights(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get account level insights"""
    log_section("GET ACCOUNT INSIGHTS")
    
    try:
        insights_agent = InsightsAgent(orchestrator.access_token)
        
        date_preset = payload.get("date_preset", "last_7d")
        fields = payload.get("fields")
        
        # Validate date preset
        if not validate_date_preset(date_preset):
            raise ValidationError(f"Invalid date_preset: {date_preset}")
        
        log_info(f"\n[INFO] Account ID: {ad_account_id}")
        log_info(f"[INFO] Date preset: {date_preset}")
        
        response = await insights_agent.get_account_insights(ad_account_id, date_preset, fields)
        
        log_info(f"\n✓ Account insights retrieved successfully")
        
        return {
            "status": "success",
            "insights_type": "account",
            "account_id": ad_account_id,
            "data": response
        }
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_campaign_insights(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get campaign level insights with enhanced metrics"""
    log_section("GET CAMPAIGN INSIGHTS")

    try:
        insights_agent = InsightsAgent(orchestrator.access_token)

        campaign_id = payload.get("campaign_id")
        if not campaign_id:
            raise ValidationError("Missing 'campaign_id' in payload")

        date_preset = payload.get("date_preset", "last_7d")
        fields = payload.get("fields")
        breakdowns = payload.get("breakdowns")
        include_enhanced = payload.get("include_enhanced", True)  # Default to True

        # Validate date preset
        if not validate_date_preset(date_preset):
            raise ValidationError(f"Invalid date_preset: {date_preset}")

        # Validate breakdowns if provided
        if breakdowns:
            for breakdown in breakdowns:
                if not validate_breakdown(breakdown):
                    log_info(f"\n[WARNING] Unknown breakdown: {breakdown} (will attempt anyway)")

        log_info(f"\n[INFO] Campaign ID: {campaign_id}")
        log_info(f"[INFO] Date preset: {date_preset}")
        if breakdowns:
            log_info(f"[INFO] Breakdowns: {', '.join(breakdowns)}")

        response = await insights_agent.get_campaign_insights(campaign_id, date_preset, fields, breakdowns)

        result = {
            "status": "success",
            "insights_type": "campaign",
            "campaign_id": campaign_id,
            "data": response
        }

        # Add enhanced metrics if requested
        if include_enhanced:
            # Parse base insights data
            insights_data = response.get("data", [{}])[0] if response.get("data") else {}
            actions = insights_data.get("actions", [])
            primary_result = insights_agent.extract_primary_result(actions)
            spend = float(insights_data.get("spend", 0))
            current_cpr = spend / primary_result["count"] if primary_result["count"] > 0 else 0

            # Initialize enhanced metrics with base data
            result["enhanced_metrics"] = {
                "spend": {
                    "total": spend,
                    "daily_average": spend / 7 if spend > 0 else 0
                },
                "primary_conversion": {
                    "type": primary_result["type"],
                    "count": primary_result["count"]
                },
                "cost_per_result": {
                    "current": round(current_cpr, 2),
                    "rolling_7d": 0.0
                },
                "results_per_day": 0.0,
                "frequency": float(insights_data.get("frequency", 0)),
                "link_ctr": float(insights_data.get("inline_link_click_ctr", 0)),
                "cpm": {
                    "current": float(insights_data.get("cpm", 0)),
                    "trend": "insufficient_data",
                    "change_percent": 0.0
                }
            }

            # Try to get daily insights for rolling calculations
            try:
                daily_insights = await insights_agent.get_daily_insights(campaign_id, "campaign", days=7)
                rolling_cpr = insights_agent.calculate_rolling_cost_per_result(daily_insights)
                results_per_day = insights_agent.calculate_results_per_day(daily_insights)
                cpm_trend = insights_agent.calculate_cpm_trend(daily_insights)

                result["enhanced_metrics"]["cost_per_result"]["rolling_7d"] = round(rolling_cpr, 2)
                result["enhanced_metrics"]["results_per_day"] = round(results_per_day, 2)
                result["enhanced_metrics"]["cpm"]["trend"] = cpm_trend.get("trend")
                result["enhanced_metrics"]["cpm"]["change_percent"] = cpm_trend.get("change_percent", 0)
            except Exception as e:
                log_info(f"[WARNING] Could not fetch daily insights: {e}")

            log_info(f"✓ Enhanced metrics included")

        log_info(f"\n✓ Campaign insights retrieved successfully")

        return result

    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_adset_insights(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get ad set level insights with enhanced metrics including learning phase"""
    log_section("GET AD SET INSIGHTS")

    try:
        insights_agent = InsightsAgent(orchestrator.access_token)

        adset_id = payload.get("adset_id")
        if not adset_id:
            raise ValidationError("Missing 'adset_id' in payload")

        date_preset = payload.get("date_preset", "last_7d")
        fields = payload.get("fields")
        breakdowns = payload.get("breakdowns")
        include_enhanced = payload.get("include_enhanced", True)  # Default to True

        # Validate date preset
        if not validate_date_preset(date_preset):
            raise ValidationError(f"Invalid date_preset: {date_preset}")

        # Validate breakdowns if provided
        if breakdowns:
            for breakdown in breakdowns:
                if not validate_breakdown(breakdown):
                    log_info(f"\n[WARNING] Unknown breakdown: {breakdown} (will attempt anyway)")

        log_info(f"\n[INFO] Ad Set ID: {adset_id}")
        log_info(f"[INFO] Date preset: {date_preset}")
        if breakdowns:
            log_info(f"[INFO] Breakdowns: {', '.join(breakdowns)}")

        response = await insights_agent.get_adset_insights(adset_id, date_preset, fields, breakdowns)

        result = {
            "status": "success",
            "insights_type": "adset",
            "adset_id": adset_id,
            "data": response
        }

        # Add enhanced metrics if requested
        if include_enhanced:
            # Parse base insights data
            insights_data = response.get("data", [{}])[0] if response.get("data") else {}
            actions = insights_data.get("actions", [])
            primary_result = insights_agent.extract_primary_result(actions)
            spend = float(insights_data.get("spend", 0))
            current_cpr = spend / primary_result["count"] if primary_result["count"] > 0 else 0

            # Initialize enhanced metrics with base data
            result["enhanced_metrics"] = {
                "spend": {
                    "total": spend,
                    "daily_average": spend / 7 if spend > 0 else 0
                },
                "primary_conversion": {
                    "type": primary_result["type"],
                    "count": primary_result["count"]
                },
                "cost_per_result": {
                    "current": round(current_cpr, 2),
                    "rolling_7d": 0.0
                },
                "results_per_day": 0.0,
                "learning_phase": {
                    "status": "UNKNOWN",
                    "is_in_learning": False,
                    "actions_remaining": 0
                },
                "frequency": float(insights_data.get("frequency", 0)),
                "link_ctr": float(insights_data.get("inline_link_click_ctr", 0)),
                "cpm": {
                    "current": float(insights_data.get("cpm", 0)),
                    "trend": "insufficient_data",
                    "change_percent": 0.0
                }
            }

            # Try to get learning phase status (separate try/except)
            try:
                learning_phase = await insights_agent.get_adset_learning_phase(adset_id)
                result["enhanced_metrics"]["learning_phase"] = {
                    "status": learning_phase.get("learning_phase_status", "UNKNOWN"),
                    "is_in_learning": learning_phase.get("is_in_learning", False),
                    "actions_remaining": learning_phase.get("actions_remaining", 0)
                }
                log_info(f"✓ Learning phase: {learning_phase.get('learning_phase_status')}")
            except Exception as e:
                log_info(f"[WARNING] Could not fetch learning phase: {e}")

            # Try to get daily insights for rolling calculations (separate try/except)
            try:
                daily_insights = await insights_agent.get_daily_insights(adset_id, "adset", days=7)
                rolling_cpr = insights_agent.calculate_rolling_cost_per_result(daily_insights)
                results_per_day = insights_agent.calculate_results_per_day(daily_insights)
                cpm_trend = insights_agent.calculate_cpm_trend(daily_insights)

                result["enhanced_metrics"]["cost_per_result"]["rolling_7d"] = round(rolling_cpr, 2)
                result["enhanced_metrics"]["results_per_day"] = round(results_per_day, 2)
                result["enhanced_metrics"]["cpm"]["trend"] = cpm_trend.get("trend")
                result["enhanced_metrics"]["cpm"]["change_percent"] = cpm_trend.get("change_percent", 0)
                log_info(f"✓ Rolling metrics calculated")
            except Exception as e:
                log_info(f"[WARNING] Could not fetch daily insights: {e}")

            log_info(f"✓ Enhanced metrics included")

        log_info(f"\n✓ Ad set insights retrieved successfully")

        return result

    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_ad_insights(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get ad level insights with enhanced metrics"""
    log_section("GET AD INSIGHTS")

    try:
        insights_agent = InsightsAgent(orchestrator.access_token)

        ad_id = payload.get("ad_id")
        if not ad_id:
            raise ValidationError("Missing 'ad_id' in payload")

        date_preset = payload.get("date_preset", "last_7d")
        fields = payload.get("fields")
        breakdowns = payload.get("breakdowns")
        include_enhanced = payload.get("include_enhanced", True)  # Default to True

        # Validate date preset
        if not validate_date_preset(date_preset):
            raise ValidationError(f"Invalid date_preset: {date_preset}")

        # Validate breakdowns if provided
        if breakdowns:
            for breakdown in breakdowns:
                if not validate_breakdown(breakdown):
                    log_info(f"\n[WARNING] Unknown breakdown: {breakdown} (will attempt anyway)")

        log_info(f"\n[INFO] Ad ID: {ad_id}")
        log_info(f"[INFO] Date preset: {date_preset}")
        if breakdowns:
            log_info(f"[INFO] Breakdowns: {', '.join(breakdowns)}")

        response = await insights_agent.get_ad_insights(ad_id, date_preset, fields, breakdowns)

        result = {
            "status": "success",
            "insights_type": "ad",
            "ad_id": ad_id,
            "data": response
        }

        # Add enhanced metrics if requested
        if include_enhanced:
            # Parse base insights data
            insights_data = response.get("data", [{}])[0] if response.get("data") else {}
            actions = insights_data.get("actions", [])
            primary_result = insights_agent.extract_primary_result(actions)
            spend = float(insights_data.get("spend", 0))
            current_cpr = spend / primary_result["count"] if primary_result["count"] > 0 else 0

            # Initialize enhanced metrics with base data
            result["enhanced_metrics"] = {
                "spend": {
                    "total": spend,
                    "daily_average": spend / 7 if spend > 0 else 0
                },
                "primary_conversion": {
                    "type": primary_result["type"],
                    "count": primary_result["count"]
                },
                "cost_per_result": {
                    "current": round(current_cpr, 2),
                    "rolling_7d": 0.0
                },
                "results_per_day": 0.0,
                "frequency": float(insights_data.get("frequency", 0)),
                "link_ctr": float(insights_data.get("inline_link_click_ctr", 0)),
                "cpm": {
                    "current": float(insights_data.get("cpm", 0)),
                    "trend": "insufficient_data",
                    "change_percent": 0.0
                }
            }

            # Try to get daily insights for rolling calculations
            try:
                daily_insights = await insights_agent.get_daily_insights(ad_id, "ad", days=7)
                rolling_cpr = insights_agent.calculate_rolling_cost_per_result(daily_insights)
                results_per_day = insights_agent.calculate_results_per_day(daily_insights)
                cpm_trend = insights_agent.calculate_cpm_trend(daily_insights)

                result["enhanced_metrics"]["cost_per_result"]["rolling_7d"] = round(rolling_cpr, 2)
                result["enhanced_metrics"]["results_per_day"] = round(results_per_day, 2)
                result["enhanced_metrics"]["cpm"]["trend"] = cpm_trend.get("trend")
                result["enhanced_metrics"]["cpm"]["change_percent"] = cpm_trend.get("change_percent", 0)
            except Exception as e:
                log_info(f"[WARNING] Could not fetch daily insights: {e}")

            log_info(f"✓ Enhanced metrics included")

        log_info(f"\n✓ Ad insights retrieved successfully")

        return result

    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_performance_report(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Generate performance report from insights"""
    log_section("GET PERFORMANCE REPORT")
    
    try:
        insights_agent = InsightsAgent(orchestrator.access_token)
        
        report_type = payload.get("report_type", "campaign").lower()  # campaign, adset, or ad
        date_preset = payload.get("date_preset", "last_7d")
        breakdowns = payload.get("breakdowns")
        
        if report_type not in ["campaign", "adset", "ad"]:
            raise ValidationError(f"Invalid report_type: {report_type}. Must be 'campaign', 'adset', or 'ad'")
        
        log_info(f"\n[INFO] Report type: {report_type}")
        log_info(f"[INFO] Date preset: {date_preset}")
        
        insights_data = None
        
        if report_type == "campaign":
            # Get all campaigns for the account and get their insights
            log_info(f"\n[INFO] Fetching campaigns insights...")
            campaigns = await orchestrator.campaign_agent.list_campaigns(ad_account_id)
            insights_data = []
            for campaign in campaigns:
                try:
                    response = await insights_agent.get_campaign_insights(
                        campaign.get("id"), date_preset, breakdowns=breakdowns
                    )
                    if "data" in response:
                        insights_data.extend(response["data"])
                except Exception as e:
                    log_info(f"[WARN] Failed to get insights for campaign {campaign.get('id')}: {e}")

        elif report_type == "adset":
            # Get all ad sets and their insights
            log_info(f"\n[INFO] Fetching ad sets insights...")
            adsets = await orchestrator.campaign_agent.list_adsets(ad_account_id)
            insights_data = []
            for adset in adsets:
                try:
                    response = await insights_agent.get_adset_insights(
                        adset.get("id"), date_preset, breakdowns=breakdowns
                    )
                    if "data" in response:
                        insights_data.extend(response["data"])
                except Exception as e:
                    log_info(f"[WARN] Failed to get insights for adset {adset.get('id')}: {e}")

        elif report_type == "ad":
            # Get all ads and their insights
            log_info(f"\n[INFO] Fetching ads insights...")
            ads = await orchestrator.ad_agent.list_ads(ad_account_id)
            insights_data = []
            for ad in ads:
                try:
                    response = await insights_agent.get_ad_insights(
                        ad.get("id"), date_preset, breakdowns=breakdowns
                    )
                    if "data" in response:
                        insights_data.extend(response["data"])
                except Exception as e:
                    log_info(f"[WARN] Failed to get insights for ad {ad.get('id')}: {e}")
        
        # Generate report
        report = insights_agent.generate_performance_report(insights_data, report_type.capitalize())
        
        log_info(f"\n✓ Performance report generated successfully")
        log_info(f"✓ Total records analyzed: {len(insights_data)}")
        
        return {
            "status": "success",
            "report_type": report_type,
            "report": report
        }
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_export_insights(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Export insights to file"""
    log_section("EXPORT INSIGHTS")
    
    try:
        insights_agent = InsightsAgent(orchestrator.access_token)
        
        export_format = payload.get("format", "json").lower()  # json or csv
        insights_type = payload.get("insights_type", "campaign").lower()
        date_preset = payload.get("date_preset", "last_7d")
        filename = payload.get("filename", f"insights_{insights_type}_{date_preset}.{export_format}")
        
        if export_format not in ["json", "csv"]:
            raise ValidationError(f"Invalid format: {export_format}. Must be 'json' or 'csv'")
        
        log_info(f"\n[INFO] Export format: {export_format}")
        log_info(f"\n[INFO] Insights type: {insights_type}")
        log_info(f"\n[INFO] Output file: {filename}")
        
        # Collect insights data based on type
        if insights_type == "campaign":
            campaigns = await orchestrator.campaign_agent.list_campaigns(ad_account_id)
            insights_data = []
            for campaign in campaigns:
                try:
                    response = await insights_agent.get_campaign_insights(campaign.get("id"), date_preset)
                    if "data" in response:
                        insights_data.extend(response["data"])
                except Exception as e:
                    log_info(f"[WARN] Failed to get insights for campaign {campaign.get('id')}: {e}")

        elif insights_type == "adset":
            adsets = await orchestrator.campaign_agent.list_adsets(ad_account_id)
            insights_data = []
            for adset in adsets:
                try:
                    response = await insights_agent.get_adset_insights(adset.get("id"), date_preset)
                    if "data" in response:
                        insights_data.extend(response["data"])
                except Exception as e:
                    log_info(f"[WARN] Failed to get insights for adset {adset.get('id')}: {e}")

        elif insights_type == "ad":
            ads = await orchestrator.ad_agent.list_ads(ad_account_id)
            insights_data = []
            for ad in ads:
                try:
                    response = await insights_agent.get_ad_insights(ad.get("id"), date_preset)
                    if "data" in response:
                        insights_data.extend(response["data"])
                except Exception as e:
                    log_info(f"[WARN] Failed to get insights for ad {ad.get('id')}: {e}")
        
        else:
            raise ValidationError(f"Invalid insights_type: {insights_type}")
        
        # Export data
        if export_format == "json":
            export_path = insights_agent.export_to_json({"insights": insights_data}, filename)
        else:  # csv
            export_path = insights_agent.export_to_csv(insights_data, filename)
        
        log_info(f"\n✓ Insights exported successfully")
        
        return {
            "status": "success",
            "export_format": export_format,
            "filepath": export_path,
            "records_count": len(insights_data)
        }
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================================
# LEAD FORM OPERATIONS
# ============================================================================

async def handle_create_lead_form(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Create a lead form on a Facebook Page"""
    log_section("CREATE LEAD FORM")

    try:
        # IMPORTANT: Lead forms require page_id, not ad_account_id
        page_id = payload.get("page_id")
        if not page_id:
            raise ValidationError("Missing 'page_id' in payload. Lead forms are created on Pages, not Ad Accounts.")

        lead_form_json = payload.get("lead_form")
        if not lead_form_json:
            raise ValidationError("Missing 'lead_form' object in payload")

        log_info(f"\n[INFO] Page ID: {page_id}")
        log_info(f"[INFO] Form name: {lead_form_json.get('name')}")
        log_info(f"[INFO] Questions count: {len(lead_form_json.get('questions', []))}")

        lead_form_params = create_lead_form_params_from_json(lead_form_json)
        lead_form = await orchestrator.business_agent.create_lead_form(page_id, lead_form_params)

        log_info(f"\n✓ Lead form created successfully")
        log_info(f"✓ Form ID: {lead_form.id}")
        log_info(f"✓ Form Name: {lead_form.name}")

        return {
            "status": "success",
            "form_id": lead_form.id,
            "name": lead_form.name,
            "page_id": page_id
        }

    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_lead_form(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get lead form details"""
    log_section("GET LEAD FORM")

    try:
        form_id = payload.get("form_id")
        if not form_id:
            raise ValidationError("Missing 'form_id' in payload")

        log_info(f"\n[INFO] Fetching lead form: {form_id}")

        form_data = await orchestrator.business_agent.get_lead_form(form_id)

        log_info(f"\n✓ Lead form retrieved:")
        log_info(f"  ID: {form_data.get('id')}")
        log_info(f"  Name: {form_data.get('name')}")
        log_info(f"  Status: {form_data.get('status')}")

        return {"status": "success", "lead_form": form_data}

    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_list_lead_forms(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """List all lead forms for a page"""
    log_section("LIST LEAD FORMS")

    try:
        # Lead forms are listed by page_id
        page_id = payload.get("page_id")
        if not page_id:
            raise ValidationError("Missing 'page_id' in payload. Lead forms are listed by Page ID.")

        limit = payload.get("limit", 50)

        log_info(f"\n[INFO] Page ID: {page_id}")

        forms = await orchestrator.business_agent.list_lead_forms(page_id, limit)

        if not forms:
            log_info(f"\n[INFO] No lead forms found for page {page_id}")
            return {"status": "success", "lead_forms": [], "count": 0}

        form_list = []
        for form in forms:
            form_list.append({
                "id": form.get("id"),
                "name": form.get("name"),
                "status": form.get("status"),
                "locale": form.get("locale"),
                "leads_count": form.get("leads_count"),
                "created_time": form.get("created_time")
            })

        log_info(f"\n✓ Found {len(forms)} lead form(s)")

        return {"status": "success", "lead_forms": form_list, "count": len(forms)}

    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_leads(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get leads from a lead form"""
    log_section("GET LEADS")

    try:
        form_id = payload.get("form_id")
        if not form_id:
            raise ValidationError("Missing 'form_id' in payload")

        limit = payload.get("limit", 100)

        log_info(f"\n[INFO] Form ID: {form_id}")
        log_info(f"[INFO] Limit: {limit}")

        leads = await orchestrator.business_agent.get_leads(form_id, limit)

        if not leads:
            log_info(f"\n[INFO] No leads found for form {form_id}")
            return {"status": "success", "leads": [], "count": 0}

        lead_list = []
        for lead in leads:
            # Parse field_data into a more usable format
            field_data = {}
            for field in lead.get("field_data", []):
                field_data[field.get("name")] = field.get("values", [])

            lead_list.append({
                "id": lead.get("id"),
                "created_time": lead.get("created_time"),
                "field_data": field_data,
                "ad_id": lead.get("ad_id"),
                "ad_name": lead.get("ad_name"),
                "adset_id": lead.get("adset_id"),
                "campaign_id": lead.get("campaign_id")
            })

        log_info(f"\n✓ Found {len(leads)} lead(s)")

        return {"status": "success", "leads": lead_list, "count": len(leads)}

    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_lead(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get single lead details"""
    log_section("GET LEAD")

    try:
        lead_id = payload.get("lead_id")
        if not lead_id:
            raise ValidationError("Missing 'lead_id' in payload")

        log_info(f"\n[INFO] Fetching lead: {lead_id}")

        lead_data = await orchestrator.business_agent.get_lead(lead_id)

        # Parse field_data into a more usable format
        field_data = {}
        for field in lead_data.get("field_data", []):
            field_data[field.get("name")] = field.get("values", [])

        result = {
            "id": lead_data.get("id"),
            "created_time": lead_data.get("created_time"),
            "field_data": field_data,
            "form_id": lead_data.get("form_id"),
            "ad_id": lead_data.get("ad_id"),
            "ad_name": lead_data.get("ad_name"),
            "adset_id": lead_data.get("adset_id"),
            "adset_name": lead_data.get("adset_name"),
            "campaign_id": lead_data.get("campaign_id"),
            "campaign_name": lead_data.get("campaign_name"),
            "is_organic": lead_data.get("is_organic")
        }

        log_info(f"\n✓ Lead retrieved: {lead_id}")

        return {"status": "success", "lead": result}

    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================================
# PIXEL OPERATIONS
# ============================================================================

async def handle_create_pixel(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Create a Meta Pixel for an ad account"""
    log_section("CREATE PIXEL")

    try:
        name = payload.get("name")
        if not name:
            raise ValidationError("Missing 'name' in payload")

        log_info(f"\n[INFO] Ad Account ID: {ad_account_id}")
        log_info(f"[INFO] Pixel name: {name}")

        pixel = await orchestrator.business_agent.create_pixel(ad_account_id, name)

        log_info(f"\n✓ Pixel created successfully")
        log_info(f"✓ Pixel ID: {pixel.id}")
        log_info(f"✓ Pixel Name: {pixel.name}")

        return {
            "status": "success",
            "pixel_id": pixel.id,
            "name": pixel.name,
            "ad_account_id": ad_account_id
        }

    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_pixel(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get pixel details"""
    log_section("GET PIXEL")

    try:
        pixel_id = payload.get("pixel_id")
        if not pixel_id:
            raise ValidationError("Missing 'pixel_id' in payload")

        log_info(f"\n[INFO] Fetching pixel: {pixel_id}")

        pixel_data = await orchestrator.business_agent.get_pixel(pixel_id)

        log_info(f"\n✓ Pixel retrieved:")
        log_info(f"  ID: {pixel_data.get('id')}")
        log_info(f"  Name: {pixel_data.get('name')}")

        return {"status": "success", "pixel": pixel_data}

    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_list_pixels(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """List all pixels for an ad account"""
    log_section("LIST PIXELS")

    try:
        limit = payload.get("limit", 50)

        log_info(f"\n[INFO] Ad Account ID: {ad_account_id}")

        pixels = await orchestrator.business_agent.list_pixels(ad_account_id, limit)

        if not pixels:
            log_info(f"\n[INFO] No pixels found for ad account {ad_account_id}")
            return {"status": "success", "pixels": [], "count": 0}

        pixel_list = []
        for pixel in pixels:
            pixel_list.append({
                "id": pixel.get("id"),
                "name": pixel.get("name"),
                "creation_time": pixel.get("creation_time"),
                "last_fired_time": pixel.get("last_fired_time")
            })

        log_info(f"\n✓ Found {len(pixels)} pixel(s)")

        return {"status": "success", "pixels": pixel_list, "count": len(pixels)}

    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_update_pixel(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Update/rename a Meta Pixel"""
    log_section("UPDATE PIXEL")

    try:
        pixel_id = payload.get("pixel_id")
        name = payload.get("name")

        if not pixel_id:
            raise ValidationError("Missing 'pixel_id' in payload")
        if not name:
            raise ValidationError("Missing 'name' in payload")

        log_info(f"\n[INFO] Pixel ID: {pixel_id}")
        log_info(f"[INFO] New name: {name}")

        updated_pixel = await orchestrator.business_agent.update_pixel(pixel_id, name)

        log_info(f"\n✓ Pixel updated successfully")
        log_info(f"✓ Pixel ID: {updated_pixel.get('id')}")
        log_info(f"✓ New Name: {updated_pixel.get('name')}")

        return {
            "status": "success",
            "pixel_id": updated_pixel.get("id"),
            "name": updated_pixel.get("name"),
            "message": "Pixel renamed successfully"
        }

    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def process_action(orchestrator: OrchestratorAgent, ad_account_id: str, action_payload: dict) -> dict:
    """Main action dispatcher - routes to appropriate handler"""
    action = action_payload.get("action", "").lower()
    
    if action == "list_ad_accounts":
        return await handle_list_ad_accounts(orchestrator, ad_account_id, action_payload)
    elif action == "create_campaign":
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
    elif action == "list_adsets":
        return await handle_list_adsets(orchestrator, ad_account_id, action_payload)
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
    elif action == "create_creative":
        return await handle_create_creative(orchestrator, ad_account_id, action_payload)
    elif action == "get_creative":
        return await handle_get_creative(orchestrator, ad_account_id, action_payload)
    elif action == "create_ad":
        return await handle_create_ad(orchestrator, ad_account_id, action_payload)
    elif action == "update_ad":
        return await handle_update_ad(orchestrator, ad_account_id, action_payload)
    elif action == "get_ad":
        return await handle_get_ad(orchestrator, ad_account_id, action_payload)
    elif action == "list_ads":
        return await handle_list_ads(orchestrator, ad_account_id, action_payload)
    elif action == "get_account_insights":
        return await handle_get_account_insights(orchestrator, ad_account_id, action_payload)
    elif action == "get_campaign_insights":
        return await handle_get_campaign_insights(orchestrator, ad_account_id, action_payload)
    elif action == "get_adset_insights":
        return await handle_get_adset_insights(orchestrator, ad_account_id, action_payload)
    elif action == "get_ad_insights":
        return await handle_get_ad_insights(orchestrator, ad_account_id, action_payload)
    elif action == "get_performance_report":
        return await handle_get_performance_report(orchestrator, ad_account_id, action_payload)
    elif action == "export_insights":
        return await handle_export_insights(orchestrator, ad_account_id, action_payload)
    # Lead Form Operations
    elif action == "create_lead_form":
        return await handle_create_lead_form(orchestrator, ad_account_id, action_payload)
    elif action == "get_lead_form":
        return await handle_get_lead_form(orchestrator, ad_account_id, action_payload)
    elif action == "list_lead_forms":
        return await handle_list_lead_forms(orchestrator, ad_account_id, action_payload)
    elif action == "get_leads":
        return await handle_get_leads(orchestrator, ad_account_id, action_payload)
    elif action == "get_lead":
        return await handle_get_lead(orchestrator, ad_account_id, action_payload)
    # Pixel Operations
    elif action == "create_pixel":
        return await handle_create_pixel(orchestrator, ad_account_id, action_payload)
    elif action == "get_pixel":
        return await handle_get_pixel(orchestrator, ad_account_id, action_payload)
    elif action == "list_pixels":
        return await handle_list_pixels(orchestrator, ad_account_id, action_payload)
    elif action == "update_pixel":
        return await handle_update_pixel(orchestrator, ad_account_id, action_payload)
    else:
        supported_actions = [
            "list_ad_accounts",
            "create_campaign", "update_campaign", "get_campaign", "list_campaigns",
            "create_adset", "update_adset", "get_adset", "list_adsets",
            "upload_image", "upload_video", "get_image", "get_video", "clear_asset_cache",
            "create_creative", "get_creative", "create_ad", "update_ad", "get_ad", "list_ads",
            "get_account_insights", "get_campaign_insights", "get_adset_insights",
            "get_ad_insights", "get_performance_report", "export_insights",
            "create_lead_form", "get_lead_form", "list_lead_forms", "get_leads", "get_lead",
            "create_pixel", "get_pixel", "list_pixels", "update_pixel"
        ]
        error_msg = f"Unknown action: {action}. Supported: {', '.join(supported_actions)}"
        log_info(f"\n✗ {error_msg}")
        return {"status": "error", "message": error_msg}
