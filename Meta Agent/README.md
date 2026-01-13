# Meta Ads Agent - Automated Advertising System

A Python-based agent system for automating Meta (Facebook) advertising operations using the **Meta Marketing Graph API v24.0**.

## 🎯 Overview

Meta Ads Agent provides a modular, asynchronous architecture for managing:
- **Campaigns** — Create, update, pause, activate, list, delete campaigns
- **Ad Sets** — Create, update, manage targeting and budgets
- **Assets** — Upload, validate, and cache images and videos
- **Creatives** — Create ad creatives with flexible specifications
- **Ads** — Create, update, and manage ads linked to creatives
- **Insights** — Fetch, analyze, and export performance data

---

## 📁 Project Structure

### Core Modules (5 files)

| File | Purpose |
|------|---------|
| **main.py** | CLI entry point; handles JSON actions and output modes |
| **campaign_adsets_agent.py** | Campaign & ad set management; includes API client & orchestrator |
| **asset_agent.py** | Image/video upload, validation, and local caching |
| **ad_agent.py** | Ad creative and ad creation/management |
| **insights_agent.py** | Performance data fetching, analysis, and reporting |
| **operations.py** | JSON action handlers and dispatcher |

### Agents Architecture

```
OrchestratorAgent (Main Coordinator)
├── CampaignAgent        → Campaign & ad set CRUD
├── AssetAgent           → Image & video upload/retrieval/cache
├── AdCreationAgent      → Ad creative & ad management
└── InsightsAgent        → Performance data & analytics

MetaAPIClient (Async HTTP wrapper)
```

---

## 🚀 Quick Start

### 1. Setup Environment
Create `.env` file in project root with **access token only**:
```
META_ACCESS_TOKEN=your_access_token_here
```

### 2. Prepare Action JSON
Every action JSON must include `ad_account_id`:
```json
{
  "ad_account_id": "YOUR_AD_ACCOUNT_ID",
  "action": "create_campaign",
  "campaign": {
    "name": "My Campaign",
    "objective": "OUTCOME_LEADS"
  }
}
```

### 3. Run Actions
```bash
# Normal output (friendly format)
python3 main.py create_campaign.json

# JSON-only output (for scripts/APIs)
python3 main.py --json create_campaign.json

# Verbose output (debugging)
python3 main.py --verbose create_campaign.json
```

---

## 📋 Supported Operations (24 Total)

### Account Operations (1)
| Action | Purpose | Returns |
|--------|---------|---------|
| `list_ad_accounts` | List all ad accounts | Array of ad account objects |

### Campaign Operations (7)
| Action | Purpose |
|--------|---------|
| `create_campaign` | Create new advertising campaign |
| `update_campaign` | Update campaign status (pause/active/delete) |
| `get_campaign` | Get campaign details |
| `list_campaigns` | List all campaigns in account |
| `create_adset` | Create ad set with targeting |
| `update_adset` | Update ad set status |
| `get_adset` | Get ad set details |

### Asset Operations (5)
| Action | Purpose | Returns |
|--------|---------|---------|
| `upload_image` | Upload image to ad account | image_hash |
| `upload_video` | Upload video to ad account | video_id |
| `get_image` | Retrieve image by hash | Image metadata |
| `get_video` | Retrieve video by ID | Video metadata |
| `clear_asset_cache` | Clear local asset cache | Success message |

### Ad Operations (5)
| Action | Purpose | Required Fields |
|--------|---------|-----------------|
| `create_creative` | Create ad creative | name, object_story_spec OR asset_feed_spec |
| `get_creative` | Get creative details | creative_id |
| `create_ad` | Create ad | name, adset_id, creative |
| `update_ad` | Update ad fields | ad_id, update object |
| `get_ad` | Get ad details | ad_id |

### Insights Operations (6)
| Action | Purpose | Required Fields |
|--------|---------|-----------------|
| `get_account_insights` | Fetch account-level performance metrics | date_preset |
| `get_campaign_insights` | Fetch campaign-level performance metrics | campaign_id, date_preset |
| `get_adset_insights` | Fetch ad set-level performance metrics | adset_id, date_preset |
| `get_ad_insights` | Fetch ad-level performance metrics | ad_id, date_preset |
| `get_performance_report` | Generate comprehensive performance report | report_type, date_preset |
| `export_insights` | Export insights to JSON or CSV | insights_type, format, date_preset |

---

## 🎯 Common Workflows

### Create Campaign with Ad Sets
```bash
# 1. Create campaign from JSON
python3 main.py create_campaign.json

# Response: campaign_id (use in next step)

# 2. Create ad set linked to campaign
python3 main.py create_adset.json
```

### Create Ad Creative
```bash
# 1. Prepare creative with object_story_spec
python3 main.py create_creative.json

# Response: creative_id

# 2. Use creative_id to create ad
python3 main.py create_ad.json
```

---

## 📚 Detailed Examples

### List Ad Accounts
Get all ad accounts available under your access token:
```json
{
  "action": "list_ad_accounts"
}
```
**Note:** `ad_account_id` not required for this action.

### Create Campaign
```json
{
  "ad_account_id": "120244256006770196",
  "action": "create_campaign",
  "campaign": {
    "name": "JSON Action Campaign",
    "objective": "OUTCOME_LEADS",
    "status": "PAUSED",
    "daily_budget": 100000,
    "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    "description": "Campaign created via JSON action"
  }
}
```

### Create Ad Set
```json
{
  "ad_account_id": "120244256006770196",
  "action": "create_adset",
  "adset": {
    "name": "JSON Action Ad Set",
    "campaign_id": "120244256006770196",
    "optimization_goal": "LEAD_GENERATION",
    "billing_event": "IMPRESSIONS",
    "daily_budget": 20000,
    "status": "PAUSED",
    "targeting": {
      "geo_locations": {
        "countries": ["IN"]
      },
      "age_min": 18,
      "age_max": 65
    }
  }
}
```

### Upload Image
```json
{
  "ad_account_id": "120244256006770196",
  "action": "upload_image",
  "filepath": "/path/to/image.jpg",
  "width": 1200,
  "height": 628
}
```

### Upload Video
```json
{
  "ad_account_id": "120244256006770196",
  "action": "upload_video",
  "filepath": "/path/to/video.mp4",
  "duration": 15,
  "width": 1080,
  "height": 1920,
  "upload_phase": "start"
}
```
**upload_phase options:** `"start"`, `"transfer"`, `"finish"`, `"cancel"`

### Create Creative
```json
{
  "ad_account_id": "120244256006770196",
  "action": "create_creative",
  "creative": {
    "name": "Test Creative - Product Ad",
    "object_story_spec": {
      "page_id": "864501833422699",
      "link_data": {
        "message": "Check out our latest product!",
        "link": "https://example.com/product",
        "caption": "https://example.com/offer",
        "description": "Get 20% off today",
        "picture": "https://www.facebook.com/images/fb_icon_325x325.png"
      }
    }
  }
}
```

### Create Ad
```json
{
  "ad_account_id": "120244256006770196",
  "action": "create_ad",
  "ad": {
    "name": "Test Ad - Product Promotion",
    "adset_id": "120244255421590196",
    "creative": {
      "creative_id": "1534146091157521"
    },
    "status": "PAUSED"
  }
}
```

### Update Ad
```json
{
  "ad_account_id": "120244256006770196",
  "action": "update_ad",
  "ad_id": "YOUR_AD_ID",
  "update": {
    "status": "ACTIVE"
  }
}
```

### Get Campaign
```json
{
  "ad_account_id": "120244256006770196",
  "action": "get_campaign",
  "campaign_id": "120244256006770196"
}
```

### Update Campaign
```json
{
  "ad_account_id": "120244256006770196",
  "action": "update_campaign",
  "campaign_id": "120244256006770196",
  "update_type": "pause"
}
```
**update_type options:** `"pause"`, `"active"`, `"delete"`

---

## 📊 Insights Operations

### Get Account Insights
Retrieve account-level performance metrics:
```json
{
  "ad_account_id": "120244256006770196",
  "action": "get_account_insights",
  "date_preset": "last_7d",
  "fields": ["impressions", "clicks", "spend", "reach", "ctr", "cpc", "cpm"]
}
```

### Get Campaign Insights
Retrieve campaign-level performance metrics with optional breakdowns:
```json
{
  "ad_account_id": "120244256006770196",
  "action": "get_campaign_insights",
  "campaign_id": "120244256006770196",
  "date_preset": "last_30d",
  "breakdowns": ["age", "gender", "country"],
  "fields": ["impressions", "clicks", "spend", "reach", "actions", "ctr"]
}
```

### Get Ad Set Insights
Retrieve ad set-level performance metrics:
```json
{
  "ad_account_id": "120244256006770196",
  "action": "get_adset_insights",
  "adset_id": "120244255421590196",
  "date_preset": "last_14d",
  "breakdowns": ["device", "placement"]
}
```

### Get Ad Insights
Retrieve ad-level performance metrics:
```json
{
  "ad_account_id": "120244256006770196",
  "action": "get_ad_insights",
  "ad_id": "YOUR_AD_ID",
  "date_preset": "last_7d"
}
```

### Get Performance Report
Generate comprehensive performance report:
```json
{
  "ad_account_id": "120244256006770196",
  "action": "get_performance_report",
  "report_type": "campaign",
  "date_preset": "last_30d"
}
```
**report_type options:** `"campaign"`, `"adset"`, `"ad"`

### Export Insights
Export performance data to JSON or CSV:
```json
{
  "ad_account_id": "120244256006770196",
  "action": "export_insights",
  "insights_type": "campaign",
  "format": "csv",
  "date_preset": "last_30d",
  "filename": "campaign_insights_march.csv"
}
```
**format options:** `"json"`, `"csv"`
**insights_type options:** `"campaign"`, `"adset"`, `"ad"`

### Available Date Presets
- `last_7d` - Last 7 days
- `last_14d` - Last 14 days
- `last_28d` - Last 28 days
- `last_30d` - Last 30 days
- `last_90d` - Last 90 days
- `today` - Today
- `yesterday` - Yesterday
- `this_week` - This week
- `last_week` - Last week
- `last_month` - Last month
- `this_quarter` - This quarter
- `last_3m` - Last 3 months
- `lifetime` - All time

### Available Breakdowns
- `age`, `gender`, `country`, `region`, `city`
- `device`, `placement`, `platform`
- `audience_id`, `conversion_device`, `conversion_destination`
- `frequency_value`, `impression_device`

---

## 📊 Asset Specifications

### Images
- **Formats:** JPG, PNG, GIF, WebP, BMP
- **Max Size:** 8 MB
- **Dimensions:** 100×100 to 4096×4096 pixels
- **Aspect Ratios:** 1:1, 4:3, 3:2, 2:1, 1:2, 3:4

### Videos
- **Formats:** MP4, MOV, AVI, FLV, WMV, WebM
- **Max Size:** 2 GB
- **Duration:** 1 to 3600 seconds
- **Dimensions:** 100×100 to 4096×4096 pixels
- **Frame Rates:** 24, 25, 29.97, 30, 50, 59.94, 60 FPS

---

## 🔧 CLI Output Modes

### Default Mode (Clean)
```bash
python3 main.py create_campaign.json
```
User-friendly output with sections and formatted JSON.

### JSON Mode (Single Line)
```bash
python3 main.py --json create_campaign.json
```
Pure JSON output on one line — ideal for scripts and API integrations.

### Verbose Mode (Debug)
```bash
python3 main.py --verbose create_campaign.json
```
Shows API initialization, request/response payloads, and all debug information.

---

## 💾 Asset Caching

Uploaded assets are cached locally in `.asset_cache.json` to prevent re-uploading:
```json
{
  "images": {
    "/path/to/image.jpg": "image_hash_xyz"
  },
  "videos": {
    "/path/to/video.mp4": "video_id_123"
  }
}
```

**Clear cache:**
```bash
python3 main.py clear_asset_cache.json
# Or manually: rm .asset_cache.json
```

---

## 📋 Creative Fields Reference

### object_story_spec (Link Ads)
```json
{
  "page_id": "YOUR_PAGE_ID",
  "link_data": {
    "link": "https://example.com/product",
    "message": "Check this out!",
    "caption": "https://example.com/offer",
    "description": "Limited time offer",
    "picture": "https://example.com/image.jpg"
  }
}
```

### asset_feed_spec (Dynamic Creative)
```json
{
  "images": ["image_hash_1", "image_hash_2"],
  "videos": ["video_id_1", "video_id_2"],
  "bodies": ["Message 1", "Message 2"],
  "titles": ["Title 1", "Title 2"],
  "descriptions": ["Desc 1", "Desc 2"],
  "optimization_type": "AUTO"
}
```

---

## ❌ Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Missing credentials` | `.env` not configured | Create `.env` with `META_ACCESS_TOKEN` |
| `Invalid ad_account_id` | Account ID missing or invalid in JSON | Include valid `ad_account_id` in action JSON |
| `Invalid parameter` | Incorrect caption format | `caption` field must be a URL, not text |
| `Image not downloaded` | Image URL inaccessible to Meta | Use publicly accessible image URL (Meta downloads it) |
| `The parameter creative is required` | Wrong ad structure | Use `"creative": {"creative_id": "..."}` not `"creative_id"` |
| `No payment method` | Account not billed | Add payment method to Meta Ad Manager or use test user |
| `Image validation failed` | File too large or wrong format | Check size < 8MB, format in [JPG, PNG, GIF, WebP, BMP] |
| `Missing Permissions` | Token lacks required scope | Ensure token has `ads_management` scope |

---

## 🗂️ File Structure

```
/Meta Agent
├── main.py                      # CLI entry point
├── campaign_adsets_agent.py     # Campaign & ad set management
├── asset_agent.py               # Image/video upload & caching
├── ad_agent.py                  # Ad creative & ad management
├── insights_agent.py            # Performance insights & analytics
├── operations.py                # Action handlers & dispatcher
├── .env                         # Your credentials
├── .asset_cache.json            # Uploaded assets cache
├── .gitignore                   # Git ignore config
├── README.md                    # This file
├── input_exapmle.txt            # Example : For all operations
└── input.json                   # Input in this file
```

---

## ✅ Features & Status

### ✅ Fully Implemented
- Campaign CRUD operations
- Ad Set creation & management
- Image upload with validation & caching
- Video upload with validation & caching
- Asset retrieval by hash/ID
- Ad creative creation (flexible fields)
- Ad creation & updates
- **Performance insights** (account, campaign, ad set, ad levels)
- **Performance reporting** (comprehensive analytics)
- **Insights export** (JSON and CSV formats)
- Three output modes (default, JSON, verbose)
- Comprehensive error handling
- Async/await architecture
- JSON-based action dispatch

### 🔐 Required Setup
1. Meta Business Account
2. App created in Meta Developer
3. Access token with `ads_management` permission
4. Ad account ID
5. Payment method (optional for testing via test user)
