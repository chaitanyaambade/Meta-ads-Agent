# Meta Ads Agent - Complete System

## 🎯 Quick Start

**New to this project?** Start with these files in order:

1. **[AGENT_QUICK_REFERENCE.md](AGENT_QUICK_REFERENCE.md)** ⭐ START HERE
   - All 12 actions at a glance
   - Command examples (default, --json, --verbose)
   - Common file paths and setup

2. **[ASSET_AGENT_GUIDE.md](ASSET_AGENT_GUIDE.md)** (if using assets)
   - Image & video upload specs
   - Validation rules
   - Caching system

3. **[JSON_ACTION_GUIDE.md](JSON_ACTION_GUIDE.md)** (if customizing)
   - Campaign & ad set fields
   - Targeting configuration
   - Budget and status values

---

## 📁 Project Structure

### Core Implementation
```
main.py                     Entry point (handles CLI flags & execution)
campaign_adsets_agent.py    Campaign & ad set operations
asset_agent.py              Image & video upload & management
operations.py               JSON action dispatcher & handlers
```

### Agents Available
- **OrchestratorAgent** — Main orchestrator (campaigns + assets)
  - **CampaignAgent** — Campaign & ad set CRUD
  - **AssetAgent** — Image/video upload, validation, cache

### Example JSON Action Files
```
upload_image.json           Upload image to ad account
upload_video.json           Upload video to ad account
get_image.json              Get image details by hash
get_video.json              Get video details by ID
clear_asset_cache.json      Clear local asset cache
create_campaign.json        Create new campaign
create_adset.json           Create new ad set
```

---

## 🚀 Usage

### Setup
1. Create `.env` file in project root:
   ```
   META_ACCESS_TOKEN=your_token_here
   META_AD_ACCOUNT_ID=your_account_id_here
   ```

### Run with Default Output (clean)
```bash
python3 main.py upload_image.json
python3 main.py create_campaign.json
```

### Run with JSON-Only Output (for scripts/APIs)
```bash
python3 main.py --json upload_image.json
```

### Run with Verbose Output (debugging)
```bash
python3 main.py --verbose upload_image.json
```

---

## 📋 All 12 Supported Actions

### Campaign Operations (7)
| Action | Purpose | Example File |
|--------|---------|---|
| `create_campaign` | Create new campaign | create_campaign.json |
| `update_campaign` | Update campaign | update_campaign.json |
| `get_campaign` | Get campaign details | get_campaign.json |
| `list_campaigns` | List all campaigns | input.json |
| `create_adset` | Create ad set | create_adset.json |
| `update_adset` | Update ad set | update_adset.json |
| `get_adset` | Get ad set details | get_adset.json |

### Asset Operations (5)
| Action | Purpose | Returns | Example File |
|--------|---------|---------|---|
| `upload_image` | Upload image | image_hash | upload_image.json |
| `upload_video` | Upload video | video_id | upload_video.json |
| `get_image` | Get image details | Image data | get_image.json |
| `get_video` | Get video details | Video data | get_video.json |
| `clear_asset_cache` | Clear cache | Success msg | clear_asset_cache.json |

---

## 🎯 Common Workflows

### Upload Image & Use Hash
```bash
# 1. Upload image (get image_hash from response)
python3 main.py upload_image.json

# Response includes: "image_hash": "abc123..."

# 2. Use image_hash when creating ads/creatives
```

### Upload Video & Check Status
```bash
# 1. Upload video
python3 main.py upload_video.json
# Returns: "video_id": "123456", "upload_status": "PROCESSING"

# 2. Check status later
python3 main.py get_video.json
# Wait for status to change to "READY" before using in ads
```

### Create Campaign with Ad Sets
```bash
# 1. Create campaign
python3 main.py create_campaign.json

# 2. Create ad sets (need campaign_id from step 1)
python3 main.py create_adset.json
```

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

## 📚 Documentation Map

| Need | File | Focus |
|------|------|-------|
| Quick overview | [AGENT_QUICK_REFERENCE.md](AGENT_QUICK_REFERENCE.md) | All actions & commands |
| Asset details | [ASSET_AGENT_GUIDE.md](ASSET_AGENT_GUIDE.md) | Upload, validation, caching |
| Campaign/AdSet | [JSON_ACTION_GUIDE.md](JSON_ACTION_GUIDE.md) | Fields, targeting, budgets |
| Asset quick ref | [ASSET_AGENT_QUICK_REFERENCE.md](ASSET_AGENT_QUICK_REFERENCE.md) | Images/videos at a glance |

---

## 🔧 Output Modes

### Default Mode (Clean)
```bash
python3 main.py action.json
```
Output:
```
======================================================================
RESULT
======================================================================
{
  "status": "success",
  "asset_type": "image",
  "image_hash": "abc123..."
}
```

### JSON Mode (Single Line)
```bash
python3 main.py --json action.json
```
Output:
```
{"status": "success", "asset_type": "image", "image_hash": "abc123..."}
```

### Verbose Mode (Debug)
```bash
python3 main.py --verbose action.json
```
Shows all initialization, API calls, and processing steps.

---

## 💾 Asset Caching

Uploaded assets are cached in `.asset_cache.json`:
```json
{
  "images": {
    "/path/to/image.jpg": "image_hash_abc123"
  },
  "videos": {
    "/path/to/video.mp4": "video_id_123456"
  }
}
```

**To clear cache:**
```bash
python3 main.py clear_asset_cache.json
# Or manually: rm .asset_cache.json
```

---

## ❌ Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| Missing credentials | `.env` not found or empty | Create `.env` with TOKEN and ACCOUNT_ID |
| Image not found | Wrong filepath | Use absolute path or verify file exists |
| Image validation failed | Size/format issue | Check file size < 8MB, format is JPG/PNG/GIF/WebP/BMP |
| API error 100 | Invalid parameters | Check upload_phase is one of: start, transfer, finish, cancel |
| No image_hash returned | API response parse error | Check API response structure (shouldn't happen now) |

---

## 🗂️ Project Files Summary

### Python Modules
- `main.py` — CLI entry point with --json, --verbose flags
- `campaign_adsets_agent.py` — Campaign & ad set agents
- `asset_agent.py` — Asset upload, validation, caching
- `operations.py` — Action dispatcher & handlers

### Config
- `.env` — Your META_ACCESS_TOKEN and META_AD_ACCOUNT_ID
- `.asset_cache.json` — Local cache of uploaded assets

### Documentation
- `AGENT_QUICK_REFERENCE.md` — Start here! All actions & commands
- `ASSET_AGENT_GUIDE.md` — Complete asset specs & usage
- `JSON_ACTION_GUIDE.md` — Campaign/adset field reference
- `CHANGES.md` — What was changed/added

### Example Actions
- `upload_image.json`, `upload_video.json` — Asset uploads
- `get_image.json`, `get_video.json` — Asset retrieval
- `create_campaign.json`, `create_adset.json` — Campaign/adset creation

---

## ✅ What Works

✅ Campaign creation with JSON
✅ Campaign updates
✅ Campaign listing
✅ Ad set creation with targeting
✅ Ad set updates
✅ Image upload with validation
✅ Video upload with validation
✅ Asset caching (prevents re-uploads)
✅ Image/video retrieval by hash/ID
✅ Three output modes (default, JSON, verbose)
✅ Comprehensive error handling
✅ Full documentation

---

## 🎓 Next Steps

1. Read [AGENT_QUICK_REFERENCE.md](AGENT_QUICK_REFERENCE.md)
2. Set up `.env` with your credentials
3. Try one of the example actions:
   ```bash
   python3 main.py upload_image.json
   python3 main.py create_campaign.json
   ```
4. Check the response and adjust parameters as needed
5. For help with specific fields, see [JSON_ACTION_GUIDE.md](JSON_ACTION_GUIDE.md)

---

**Status:** ✅ Production Ready | All 12 actions tested and working
