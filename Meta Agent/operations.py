"""
JSON-based Campaign and Ad Set Operations
Handles all operations via JSON action parameter
"""

import json
import os
import asyncio
from campaign_adsets_agent import OrchestratorAgent, CampaignParams, create_adset_params_from_json, ValidationError
from asset_agent import AssetValidationError, AssetUploadError
from insights_agent import InsightsAgent, validate_date_preset, validate_breakdown

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
    """Get campaign level insights"""
    log_section("GET CAMPAIGN INSIGHTS")
    
    try:
        insights_agent = InsightsAgent(orchestrator.access_token)
        
        campaign_id = payload.get("campaign_id")
        if not campaign_id:
            raise ValidationError("Missing 'campaign_id' in payload")
        
        date_preset = payload.get("date_preset", "last_7d")
        fields = payload.get("fields")
        breakdowns = payload.get("breakdowns")
        
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
        
        log_info(f"\n✓ Campaign insights retrieved successfully")
        
        return {
            "status": "success",
            "insights_type": "campaign",
            "campaign_id": campaign_id,
            "data": response
        }
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_adset_insights(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get ad set level insights"""
    log_section("GET AD SET INSIGHTS")
    
    try:
        insights_agent = InsightsAgent(orchestrator.access_token)
        
        adset_id = payload.get("adset_id")
        if not adset_id:
            raise ValidationError("Missing 'adset_id' in payload")
        
        date_preset = payload.get("date_preset", "last_7d")
        fields = payload.get("fields")
        breakdowns = payload.get("breakdowns")
        
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
        
        log_info(f"\n✓ Ad set insights retrieved successfully")
        
        return {
            "status": "success",
            "insights_type": "adset",
            "adset_id": adset_id,
            "data": response
        }
    
    except Exception as e:
        log_info(f"\n✗ Error: {e}")
        return {"status": "error", "message": str(e)}


async def handle_get_ad_insights(orchestrator: OrchestratorAgent, ad_account_id: str, payload: dict) -> dict:
    """Get ad level insights"""
    log_section("GET AD INSIGHTS")
    
    try:
        insights_agent = InsightsAgent(orchestrator.access_token)
        
        ad_id = payload.get("ad_id")
        if not ad_id:
            raise ValidationError("Missing 'ad_id' in payload")
        
        date_preset = payload.get("date_preset", "last_7d")
        fields = payload.get("fields")
        breakdowns = payload.get("breakdowns")
        
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
        
        log_info(f"\n✓ Ad insights retrieved successfully")
        
        return {
            "status": "success",
            "insights_type": "ad",
            "ad_id": ad_id,
            "data": response
        }
    
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
            campaigns = await orchestrator.list_campaigns(ad_account_id)
            insights_data = []
            for campaign in campaigns:
                try:
                    response = await insights_agent.get_campaign_insights(
                        campaign.get("id"), date_preset, breakdowns=breakdowns
                    )
                    if "data" in response:
                        insights_data.extend(response["data"])
                except:
                    pass
        
        elif report_type == "adset":
            # Get all ad sets and their insights
            log_info(f"\n[INFO] Fetching ad sets insights...")
            adsets = await orchestrator.list_adsets(ad_account_id)
            insights_data = []
            for adset in adsets:
                try:
                    response = await insights_agent.get_adset_insights(
                        adset.get("id"), date_preset, breakdowns=breakdowns
                    )
                    if "data" in response:
                        insights_data.extend(response["data"])
                except:
                    pass
        
        elif report_type == "ad":
            # Get all ads and their insights
            log_info(f"\n[INFO] Fetching ads insights...")
            ads = await orchestrator.list_ads(ad_account_id)
            insights_data = []
            for ad in ads:
                try:
                    response = await insights_agent.get_ad_insights(
                        ad.get("id"), date_preset, breakdowns=breakdowns
                    )
                    if "data" in response:
                        insights_data.extend(response["data"])
                except:
                    pass
        
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
            campaigns = await orchestrator.list_campaigns(ad_account_id)
            insights_data = []
            for campaign in campaigns:
                response = await insights_agent.get_campaign_insights(campaign.get("id"), date_preset)
                if "data" in response:
                    insights_data.extend(response["data"])
        
        elif insights_type == "adset":
            adsets = await orchestrator.list_adsets(ad_account_id)
            insights_data = []
            for adset in adsets:
                response = await insights_agent.get_adset_insights(adset.get("id"), date_preset)
                if "data" in response:
                    insights_data.extend(response["data"])
        
        elif insights_type == "ad":
            ads = await orchestrator.list_ads(ad_account_id)
            insights_data = []
            for ad in ads:
                response = await insights_agent.get_ad_insights(ad.get("id"), date_preset)
                if "data" in response:
                    insights_data.extend(response["data"])
        
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
    else:
        supported_actions = [
            "list_ad_accounts",
            "create_campaign", "update_campaign", "get_campaign", "list_campaigns",
            "create_adset", "update_adset", "get_adset",
            "upload_image", "upload_video", "get_image", "get_video", "clear_asset_cache",
            "create_creative", "get_creative", "create_ad", "update_ad", "get_ad",
            "get_account_insights", "get_campaign_insights", "get_adset_insights", 
            "get_ad_insights", "get_performance_report", "export_insights"
        ]
        error_msg = f"Unknown action: {action}. Supported: {', '.join(supported_actions)}"
        log_info(f"\n✗ {error_msg}")
        return {"status": "error", "message": error_msg}
