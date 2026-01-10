# Meta Marketing API - Complete Capabilities Reference

> **API Version**: v24.0 (Latest as of January 2025)
> **Platforms**: Facebook, Instagram, Messenger, WhatsApp, Audience Network, Threads
> **Documentation**: https://developers.facebook.com/docs/marketing-api

---

## Table of Contents

1. [API Overview](#1-api-overview)
2. [Campaigns](#2-campaigns)
3. [Ad Sets](#3-ad-sets)
4. [Ads & Creatives](#4-ads--creatives)
5. [Targeting](#5-targeting)
6. [Audiences](#6-audiences)
7. [Analytics & Reporting](#7-analytics--reporting)
8. [Optimization](#8-optimization)
9. [Conversions API (CAPI)](#9-conversions-api-capi)
10. [Organic Publishing](#10-organic-publishing)
11. [Organic Insights](#11-organic-insights)
12. [API Examples](#12-api-examples)

---

## 1. API Overview

### Base Information

| Property | Value |
|----------|-------|
| **API Name** | Meta Marketing API (Facebook Marketing API) |
| **Current Version** | v24.0 (Released October 8, 2025) |
| **Base URL** | `https://graph.facebook.com/v24.0/` |
| **Authentication** | OAuth 2.0 Bearer Token |
| **Rate Limits** | ~200 calls/user/hour (varies by tier) |

### Required Permissions

| Permission | Purpose |
|------------|---------|
| `ads_management` | Create and manage ads |
| `ads_read` | Read ad data and insights |
| `business_management` | Manage business assets |
| `pages_read_engagement` | Read page insights |
| `pages_manage_posts` | Publish to pages |
| `instagram_basic` | Instagram account info |
| `instagram_content_publish` | Publish to Instagram |
| `instagram_manage_insights` | Read Instagram insights |

### Authentication Headers

```http
Authorization: Bearer {ACCESS_TOKEN}
Content-Type: application/json
```

### Token Types

| Type | Use Case | Expiry |
|------|----------|--------|
| User Access Token | Interactive apps | 1-2 hours (short-lived), 60 days (long-lived) |
| System User Token | Server-to-server automation | Never (recommended for production) |
| Page Access Token | Page operations | Never (if using long-lived user token) |

### Ad Hierarchy Structure

```
Ad Account (act_{AD_ACCOUNT_ID})
└── Campaign (Objective, Budget Type)
    └── Ad Set (Targeting, Placement, Schedule, Budget)
        └── Ad (Creative, Call-to-Action)
```

---

## 2. Campaigns

### Endpoint

```http
POST https://graph.facebook.com/v24.0/act_{AD_ACCOUNT_ID}/campaigns
GET https://graph.facebook.com/v24.0/{CAMPAIGN_ID}
```

### Campaign Objectives (ODAX Framework)

Meta uses **Outcome-Driven Ad Experiences (ODAX)** with 6 unified objectives:

| Objective | API Value | Funnel Stage | Use Case |
|-----------|-----------|--------------|----------|
| **Awareness** | `OUTCOME_AWARENESS` | Top | Brand recognition, reach |
| **Traffic** | `OUTCOME_TRAFFIC` | Middle | Website/app visits |
| **Engagement** | `OUTCOME_ENGAGEMENT` | Middle | Likes, comments, shares, messages |
| **Leads** | `OUTCOME_LEADS` | Middle | Lead forms, calls |
| **App Promotion** | `OUTCOME_APP_PROMOTION` | Middle | App installs, events |
| **Sales** | `OUTCOME_SALES` | Bottom | Purchases, conversions |

> **Note**: Old objectives like `LEAD_GENERATION`, `CONVERSIONS`, `REACH` are deprecated. Use `OUTCOME_*` values.

### Campaign Parameters

#### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Campaign name (internal) |
| `objective` | enum | Marketing goal (`OUTCOME_*`) |

#### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `status` | enum | `PAUSED` | `PAUSED`, `ACTIVE` |
| `special_ad_categories` | array | `["NONE"]` | `NONE`, `HOUSING`, `EMPLOYMENT`, `CREDIT`, `ISSUES_ELECTIONS_POLITICS` |
| `buying_type` | enum | `AUCTION` | `AUCTION`, `RESERVED` |
| `campaign_budget_optimization` | boolean | false | Enable CBO |
| `daily_budget` | integer | - | Daily budget in cents (requires CBO) |
| `lifetime_budget` | integer | - | Total budget in cents (requires CBO + end_time) |
| `bid_strategy` | enum | `LOWEST_COST_WITHOUT_CAP` | Bidding approach |
| `spend_cap` | integer | - | Maximum total spend in cents |
| `start_time` | datetime | - | ISO 8601 format |
| `stop_time` | datetime | - | ISO 8601 format |
| `pacing_type` | array | `["standard"]` | `standard`, `day_parting` |

### Bid Strategies

| Strategy | API Value | Description |
|----------|-----------|-------------|
| Lowest Cost | `LOWEST_COST_WITHOUT_CAP` | Meta auto-bids for maximum results |
| Bid Cap | `LOWEST_COST_WITH_BID_CAP` | Auto-bid with maximum bid limit |
| Cost Cap | `COST_CAP` | Target average cost per result |
| Target Cost | `TARGET_COST` | Stable cost per action (deprecated) |

### Special Ad Categories

| Category | When Required |
|----------|---------------|
| `HOUSING` | Real estate, rentals, home insurance |
| `EMPLOYMENT` | Job listings, recruitment |
| `CREDIT` | Loans, credit cards, financial services |
| `ISSUES_ELECTIONS_POLITICS` | Political ads, social issues |

### Advantage+ Campaigns (2025)

Meta's AI-powered campaign automation using three automation levers:

| Automation | Description |
|------------|-------------|
| **Advantage+ Budget** | Auto-manages spending across ad sets |
| **Advantage+ Audience** | AI-driven audience targeting |
| **Advantage+ Placements** | Optimal placement selection |

**Performance**: 22% average ROAS improvement, 9% lower CPA

**Supported Objectives**:
- `OUTCOME_SALES` → Advantage+ Sales Campaigns (formerly ASC)
- `OUTCOME_APP_PROMOTION` → Advantage+ App Campaigns
- `OUTCOME_LEADS` → Advantage+ Leads Campaigns

> **Important**: Legacy ASC/AAC APIs deprecated October 8, 2025. Full removal in v25.0 (Q1 2026).

---

## 3. Ad Sets

### Endpoint

```http
POST https://graph.facebook.com/v24.0/act_{AD_ACCOUNT_ID}/adsets
GET https://graph.facebook.com/v24.0/{ADSET_ID}
```

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Ad set name |
| `campaign_id` | string | Parent campaign ID |
| `billing_event` | enum | When you're charged |
| `optimization_goal` | enum | What to optimize for |
| `targeting` | object | Audience definition |
| `status` | enum | `PAUSED` or `ACTIVE` |

### Billing Events

| Event | API Value | Description |
|-------|-----------|-------------|
| Impressions | `IMPRESSIONS` | Charged per 1,000 views (CPM) |
| Link Clicks | `LINK_CLICKS` | Charged per outbound click |
| ThruPlay | `THRUPLAY` | Charged per 15s video view |
| App Installs | `APP_INSTALLS` | Charged per install |
| Conversions | `CONVERSIONS` | Charged per conversion |

### Optimization Goals

| Goal | API Value | Compatible Billing | Use Case |
|------|-----------|-------------------|----------|
| Reach | `REACH` | IMPRESSIONS | Brand awareness |
| Impressions | `IMPRESSIONS` | IMPRESSIONS | Maximum visibility |
| Link Clicks | `LINK_CLICKS` | IMPRESSIONS, LINK_CLICKS | Traffic |
| Landing Page Views | `LANDING_PAGE_VIEWS` | IMPRESSIONS, LINK_CLICKS | Quality traffic |
| Conversions | `OFFSITE_CONVERSIONS` | IMPRESSIONS | Website actions |
| Value | `VALUE` | IMPRESSIONS | ROAS optimization |
| App Installs | `APP_INSTALLS` | IMPRESSIONS, APP_INSTALLS | App growth |
| Lead Generation | `LEAD_GENERATION` | IMPRESSIONS | Lead forms |
| Messages | `MESSAGES` | IMPRESSIONS | Messenger/WhatsApp |
| Video Views | `VIDEO_VIEWS` | IMPRESSIONS, THRUPLAY | Video engagement |

### Budget Configuration

**Currency**: Values in **cents** (smallest unit)

| Currency | ₹500/day | $10/day |
|----------|----------|---------|
| API Value | `50000` | `1000` |

**Budget Types**:

```json
// Daily Budget (ongoing campaigns)
{
  "daily_budget": 50000,
  "start_time": "2026-01-10T00:00:00+0530"
}

// Lifetime Budget (fixed duration)
{
  "lifetime_budget": 500000,
  "start_time": "2026-01-10T00:00:00+0530",
  "end_time": "2026-01-20T23:59:59+0530"
}
```

**Minimum Budgets (India)**:
- Awareness: ₹40/day
- Traffic: ₹100/day
- Conversions: ₹200/day

### Attribution Settings

```json
"attribution_spec": [
  {"event_type": "CLICK_THROUGH", "window_days": 7},
  {"event_type": "VIEW_THROUGH", "window_days": 1}
]
```

| Window | Description |
|--------|-------------|
| 7-day click, 1-day view | Default (recommended) |
| 1-day click, 1-day view | Impulse purchases |
| 28-day click, 7-day view | High-consideration |

### Promoted Object

Required for conversion-based campaigns:

```json
// Website Conversions
"promoted_object": {
  "pixel_id": "123456789012345",
  "custom_event_type": "PURCHASE"
}

// App Events
"promoted_object": {
  "application_id": "123456789012345",
  "object_store_url": "https://play.google.com/store/apps/details?id=com.example"
}

// Lead Forms
"promoted_object": {
  "page_id": "123456789012345"
}
```

**Custom Event Types**:
- `VIEW_CONTENT` - Product views
- `ADD_TO_CART` - Cart additions
- `INITIATE_CHECKOUT` - Checkout started
- `PURCHASE` - Completed purchase
- `LEAD` - Lead submission
- `COMPLETE_REGISTRATION` - Sign-ups

### Destination Types

| Type | Description |
|------|-------------|
| `WEBSITE` | External website |
| `APP` | Mobile app |
| `MESSENGER` | Messenger conversation |
| `WHATSAPP` | WhatsApp chat |
| `INSTAGRAM_DIRECT` | Instagram DM |
| `FACEBOOK` | On-Facebook destination |

---

## 4. Ads & Creatives

### Endpoints

```http
POST https://graph.facebook.com/v24.0/act_{AD_ACCOUNT_ID}/ads
POST https://graph.facebook.com/v24.0/act_{AD_ACCOUNT_ID}/adcreatives
POST https://graph.facebook.com/v24.0/act_{AD_ACCOUNT_ID}/adimages
POST https://graph.facebook.com/v24.0/act_{AD_ACCOUNT_ID}/advideos
```

### Ad Creation Workflow

1. Upload assets (images/videos) → Get `image_hash` or `video_id`
2. Create ad creative → Get `creative_id`
3. Create ad using `creative_id` + `adset_id`

### Ad Formats

| Format | Description | Specs |
|--------|-------------|-------|
| **Single Image** | Static image ad | 1080x1080 (1:1), 1200x628 (1.91:1) |
| **Single Video** | Video ad | Up to 240 min, 4GB max |
| **Carousel** | 2-10 swipeable cards | 1080x1080 per card |
| **Collection** | Hero + product grid | Mobile only |
| **Instant Experience** | Full-screen interactive | Mobile only |
| **Slideshow** | Images as video | 3-10 images |

### Image Specifications

| Placement | Recommended Size | Aspect Ratio |
|-----------|------------------|--------------|
| Feed | 1080x1080 | 1:1 |
| Stories/Reels | 1080x1920 | 9:16 |
| Right Column | 1200x628 | 1.91:1 |
| Marketplace | 1200x628 | 1.91:1 |

### Video Specifications

| Property | Requirement |
|----------|-------------|
| Format | MP4, MOV recommended |
| Resolution | 1080p+ recommended |
| Aspect Ratios | 1:1 (Feed), 9:16 (Stories/Reels), 16:9 (In-stream) |
| Duration | 1s - 240 min |
| File Size | Up to 4GB |
| Captions | Recommended (.srt file) |

### Carousel Ad Structure

```json
{
  "name": "Carousel Ad Creative",
  "object_story_spec": {
    "page_id": "PAGE_ID",
    "link_data": {
      "link": "https://example.com",
      "child_attachments": [
        {
          "link": "https://example.com/product1",
          "image_hash": "abc123",
          "name": "Product 1",
          "description": "Description 1"
        },
        {
          "link": "https://example.com/product2",
          "image_hash": "def456",
          "name": "Product 2",
          "description": "Description 2"
        }
      ]
    }
  }
}
```

### Call-to-Action Types

| CTA | API Value |
|-----|-----------|
| Shop Now | `SHOP_NOW` |
| Learn More | `LEARN_MORE` |
| Sign Up | `SIGN_UP` |
| Book Now | `BOOK_TRAVEL` |
| Contact Us | `CONTACT_US` |
| Download | `DOWNLOAD` |
| Get Offer | `GET_OFFER` |
| Get Quote | `GET_QUOTE` |
| Subscribe | `SUBSCRIBE` |
| Apply Now | `APPLY_NOW` |
| Send Message | `MESSAGE_PAGE` |
| Send WhatsApp | `WHATSAPP_MESSAGE` |

### Flexible Ad Format (2025)

AI-powered format selection:
- Upload up to 10 images/videos
- Meta automatically determines optimal format per viewer
- Supports single image, video, and carousel variations

---

## 5. Targeting

### Targeting Object Structure

```json
"targeting": {
  "geo_locations": {...},
  "age_min": 18,
  "age_max": 65,
  "genders": [1, 2],
  "publisher_platforms": ["facebook", "instagram"],
  "facebook_positions": ["feed", "story"],
  "instagram_positions": ["stream", "story", "reels"],
  "flexible_spec": [...],
  "custom_audiences": [...],
  "excluded_custom_audiences": [...]
}
```

### Geographic Targeting

```json
"geo_locations": {
  "countries": ["IN", "US"],
  "regions": [{"key": "4030"}],
  "cities": [
    {
      "key": "2422341",
      "radius": 25,
      "distance_unit": "kilometer"
    }
  ],
  "location_types": ["home", "recent"]
}
```

**Location Types**:
- `home` - People who live here
- `recent` - Recently in location
- `travel_in` - Traveling to location

**Finding Location IDs**:
```http
GET /v24.0/search?type=adgeolocation&q=Mumbai&location_types=["city"]
```

### Demographic Targeting

```json
{
  "age_min": 18,
  "age_max": 45,
  "genders": [2]
}
```

| Gender ID | Value |
|-----------|-------|
| 1 | Male |
| 2 | Female |
| [1, 2] | All |

### Interest & Behavior Targeting

```json
"flexible_spec": [
  {
    "interests": [
      {"id": "6003139266461", "name": "Online shopping"},
      {"id": "6003107902433", "name": "Fashion"}
    ],
    "behaviors": [
      {"id": "6002714895372", "name": "Engaged Shoppers"}
    ]
  }
]
```

**Logic**:
- Objects in array = OR
- Properties within object = AND

**Finding Interest/Behavior IDs**:
```http
GET /v24.0/search?type=adinterest&q=fitness
GET /v24.0/search?type=adTargetingCategory&class=behaviors
```

### Placement Options

#### Automatic Placements (Recommended)

```json
"publisher_platforms": ["facebook", "instagram", "audience_network", "messenger"]
```

#### Manual Placements

**Facebook**:
```json
"facebook_positions": ["feed", "right_hand_column", "video_feeds", "marketplace", "story", "search", "instream_video"]
```

**Instagram**:
```json
"instagram_positions": ["stream", "story", "explore", "reels", "profile_feed", "search"]
```

**Messenger**:
```json
"messenger_positions": ["messenger_home", "story", "sponsored_messages"]
```

**Audience Network**:
```json
"audience_network_positions": ["classic", "instream_video", "rewarded_video"]
```

**Threads** (NEW 2025):
```json
"threads_positions": ["threads_feed"]
```

#### Device Targeting

```json
"device_platforms": ["mobile", "desktop"]
```

---

## 6. Audiences

### Audience Types

| Type | Description | API Endpoint |
|------|-------------|--------------|
| **Custom Audience** | Your data (pixel, CRM, engagement) | `/act_{id}/customaudiences` |
| **Lookalike Audience** | Similar to source audience | `/act_{id}/customaudiences` |
| **Saved Audience** | Saved targeting criteria | `/act_{id}/savedaudiences` |

### Custom Audience Sources

| Source | Description |
|--------|-------------|
| Website Traffic | Pixel-based visitors |
| Customer List | Uploaded emails/phones |
| App Activity | SDK events |
| Engagement | FB/IG interactions |
| Video | Video viewers |
| Lead Form | Lead form interactions |
| Shopping | Catalog engagement |
| Offline Activity | Offline conversions |

### Creating Custom Audiences

#### Website Custom Audience

```json
{
  "name": "Website Visitors - Last 30 Days",
  "subtype": "WEBSITE",
  "rule": {
    "inclusions": {
      "operator": "or",
      "rules": [
        {
          "event_sources": [{"id": "PIXEL_ID", "type": "pixel"}],
          "retention_seconds": 2592000,
          "filter": {
            "operator": "and",
            "filters": [
              {"field": "url", "operator": "i_contains", "value": "/product"}
            ]
          }
        }
      ]
    }
  }
}
```

#### Customer List Upload

```json
{
  "name": "Email Subscribers",
  "subtype": "CUSTOM",
  "customer_file_source": "USER_PROVIDED_ONLY"
}
```

**Supported Identifiers** (hashed SHA-256):
- Email addresses
- Phone numbers (E.164 format)
- Mobile Advertiser IDs (IDFA/GAID)
- First/Last name + location

### Lookalike Audiences

```json
{
  "name": "Lookalike - Top Customers 1%",
  "subtype": "LOOKALIKE",
  "origin_audience_id": "SOURCE_CUSTOM_AUDIENCE_ID",
  "lookalike_spec": {
    "ratio": 0.01,
    "country": "IN",
    "type": "similarity"
  }
}
```

**Ratio Values**:
- `0.01` (1%) - Most similar, smallest
- `0.05` (5%) - Medium similarity
- `0.10` (10%) - Least similar, largest

### Using Audiences in Ad Sets

```json
"targeting": {
  "custom_audiences": [
    {"id": "23851234567890123"}
  ],
  "excluded_custom_audiences": [
    {"id": "23859876543210987"}
  ]
}
```

---

## 7. Analytics & Reporting

### Insights Endpoint

```http
GET https://graph.facebook.com/v24.0/{OBJECT_ID}/insights
GET https://graph.facebook.com/v24.0/act_{AD_ACCOUNT_ID}/insights
```

**Object Levels**: Ad Account, Campaign, Ad Set, Ad

### Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `level` | Aggregation level | `campaign`, `adset`, `ad` |
| `fields` | Metrics to return | `impressions,clicks,spend` |
| `date_preset` | Predefined date range | `last_30d`, `this_month` |
| `time_range` | Custom date range | `{"since":"2025-01-01","until":"2025-01-31"}` |
| `time_increment` | Granularity | `1` (daily), `7` (weekly), `monthly` |
| `breakdowns` | Segmentation | `age,gender,country` |
| `action_breakdowns` | Action segmentation | `action_type,action_device` |

### Performance Metrics

| Metric | API Field | Description |
|--------|-----------|-------------|
| Impressions | `impressions` | Times ad was displayed |
| Reach | `reach` | Unique people who saw ad |
| Frequency | `frequency` | Avg views per person |
| Clicks | `clicks` | All clicks |
| Link Clicks | `inline_link_clicks` | Outbound clicks |
| CTR | `ctr` | Click-through rate |
| CPC | `cpc` | Cost per click |
| CPM | `cpm` | Cost per 1,000 impressions |
| Spend | `spend` | Total spend |

### Engagement Metrics

| Metric | API Field | Description |
|--------|-----------|-------------|
| Post Reactions | `actions[action_type=post_reaction]` | Likes, loves, etc. |
| Post Comments | `actions[action_type=comment]` | Comments |
| Post Shares | `actions[action_type=post]` | Shares |
| Post Saves | `actions[action_type=onsite_conversion.post_save]` | Saves |
| Page Likes | `actions[action_type=like]` | Page follows |
| Video Views | `video_views` | 3s+ views |
| ThruPlays | `video_thruplay_actions` | 15s+ or complete |

### Conversion Metrics

| Metric | API Field | Description |
|--------|-----------|-------------|
| Conversions | `actions` | All conversion actions |
| Purchases | `actions[action_type=purchase]` | Purchase events |
| Leads | `actions[action_type=lead]` | Lead submissions |
| Add to Cart | `actions[action_type=add_to_cart]` | Cart additions |
| Conv. Value | `action_values` | Conversion values |
| ROAS | `purchase_roas` | Return on ad spend |
| Cost/Result | `cost_per_action_type` | Cost per action |

### Video Metrics

| Metric | API Field | Description |
|--------|-----------|-------------|
| 3s Views | `video_view_3_second_actions` | 3+ second views |
| 10s Views | `video_view_10_second_actions` | 10+ second views |
| ThruPlay | `video_thruplay_actions` | 15s+ or complete |
| 25% Watched | `video_p25_watched_actions` | Quartile completion |
| 50% Watched | `video_p50_watched_actions` | Quartile completion |
| 75% Watched | `video_p75_watched_actions` | Quartile completion |
| 100% Watched | `video_p100_watched_actions` | Complete views |
| Avg Watch Time | `video_avg_time_watched_actions` | Avg seconds |

### Breakdowns (Segmentation)

| Category | Breakdowns |
|----------|------------|
| **Demographics** | `age`, `gender` |
| **Geography** | `country`, `region`, `dma` |
| **Placement** | `publisher_platform`, `platform_position`, `device_platform` |
| **Time** | `hourly_stats_aggregated_by_advertiser_time_zone` |
| **Product** | `product_id` (catalog campaigns) |

### 2025 API Changes

**Reach Breakdown Limitation (June 2025)**:
- Reach data limited to 13 months with breakdowns
- Beyond 13 months: fetch without breakdowns, merge manually

**Attribution Update (June 2025)**:
- Unified attribution settings
- On-Facebook conversions counted at impression time
- Aligns API with Ads Manager reporting

**Metrics Terminology**:
- `impressions` → `views` (for non-video content)
- `page_likes` → `page_followers`

---

## 8. Optimization

### Smart Bidding Strategies

| Strategy | When to Use | Control Level |
|----------|-------------|---------------|
| `LOWEST_COST_WITHOUT_CAP` | Starting out, learning | Low (Meta controls) |
| `LOWEST_COST_WITH_BID_CAP` | Cost control needed | Medium |
| `COST_CAP` | Scaling with CPA goals | High |

### Campaign Budget Optimization (CBO)

```json
{
  "campaign_budget_optimization": true,
  "daily_budget": 100000,
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP"
}
```

**Benefits**:
- Automatic budget distribution
- Optimal ad set allocation
- Reduced manual management

### Ad Set Spend Controls (with CBO)

```json
{
  "daily_min_spend_target": 20000,
  "daily_spend_cap": 100000
}
```

### Learning Phase

**Requirements**:
- ~50 optimization events per week
- 7-14 days typical duration
- Avoid significant changes during learning

**Best Practices**:
- Days 1-3: Don't make changes
- Days 4-7: Minor adjustments only (±20% budget)
- Days 8+: Scale 20-30% every 3 days

### Optimization Timeline

| Phase | Days | Actions |
|-------|------|---------|
| Learning | 1-7 | Monitor only, let algorithm learn |
| Optimization | 8-14 | Refine targeting, adjust budgets |
| Scaling | 15+ | Increase budget, expand audiences |

---

## 9. Conversions API (CAPI)

### Overview

Server-side event tracking that bypasses browser limitations.

### Endpoint

```http
POST https://graph.facebook.com/v24.0/{PIXEL_ID}/events
```

### Event Structure

```json
{
  "data": [
    {
      "event_name": "Purchase",
      "event_time": 1704067200,
      "action_source": "website",
      "event_source_url": "https://example.com/checkout",
      "user_data": {
        "em": ["SHA256_HASHED_EMAIL"],
        "ph": ["SHA256_HASHED_PHONE"],
        "client_ip_address": "1.2.3.4",
        "client_user_agent": "Mozilla/5.0...",
        "fbc": "fb.1.1234567890.CLICK_ID",
        "fbp": "fb.1.1234567890.BROWSER_ID"
      },
      "custom_data": {
        "currency": "INR",
        "value": 1500.00,
        "content_ids": ["SKU123"],
        "content_type": "product"
      }
    }
  ]
}
```

### Standard Events

| Event | Description |
|-------|-------------|
| `PageView` | Page load |
| `ViewContent` | Product/content view |
| `Search` | Search query |
| `AddToCart` | Cart addition |
| `AddToWishlist` | Wishlist addition |
| `InitiateCheckout` | Checkout started |
| `AddPaymentInfo` | Payment info added |
| `Purchase` | Completed purchase |
| `Lead` | Lead submission |
| `CompleteRegistration` | Sign-up completed |
| `Subscribe` | Subscription started |
| `Contact` | Contact request |

### User Data Parameters

| Parameter | Description | Format |
|-----------|-------------|--------|
| `em` | Email | SHA-256 hash |
| `ph` | Phone | SHA-256 hash (E.164) |
| `fn` | First name | SHA-256 hash (lowercase) |
| `ln` | Last name | SHA-256 hash (lowercase) |
| `ct` | City | SHA-256 hash (lowercase) |
| `st` | State | SHA-256 hash (2-letter) |
| `zp` | Zip code | SHA-256 hash |
| `country` | Country | SHA-256 hash (2-letter) |
| `external_id` | Customer ID | SHA-256 hash |
| `client_ip_address` | IP address | Plain text |
| `client_user_agent` | User agent | Plain text |
| `fbc` | Click ID | Plain text |
| `fbp` | Browser ID | Plain text |

### Event Match Quality (EMQ)

**Target**: 6.0+ out of 10

**Improve EMQ**:
1. Send more user identifiers
2. Include `fbc` and `fbp` cookies
3. Hash data correctly (SHA-256, lowercase)
4. Send events in real-time

### Deduplication

Use same `event_id` for Pixel and CAPI events:

```json
{
  "event_name": "Purchase",
  "event_id": "unique_order_12345"
}
```

### Implementation Options

| Method | Complexity | Maintenance |
|--------|------------|-------------|
| CAPI Gateway | Low (no-code) | Meta-managed |
| Partner Integration | Low | Partner-managed |
| Server-Side GTM | Medium | Self-managed |
| Direct API | High | Full control |

---

## 10. Organic Publishing

### Facebook Page Publishing

#### Endpoint

```http
POST https://graph.facebook.com/v24.0/{PAGE_ID}/feed
POST https://graph.facebook.com/v24.0/{PAGE_ID}/photos
POST https://graph.facebook.com/v24.0/{PAGE_ID}/videos
```

#### Content Types

| Type | Endpoint | Parameters |
|------|----------|------------|
| Text Post | `/feed` | `message` |
| Link Post | `/feed` | `message`, `link` |
| Photo Post | `/photos` | `url` or `source`, `caption` |
| Video Post | `/videos` | `file_url` or `source`, `description` |
| Stories | `/stories` | `photo_url` or `video_url` |

#### Scheduling Posts

```json
{
  "message": "Scheduled post content",
  "published": false,
  "scheduled_publish_time": 1704067200
}
```

### Instagram Publishing

#### Endpoint

```http
POST https://graph.facebook.com/v24.0/{IG_USER_ID}/media
POST https://graph.facebook.com/v24.0/{IG_USER_ID}/media_publish
```

#### Two-Step Publishing Process

**Step 1**: Create media container
```json
// Image Post
{
  "image_url": "https://example.com/image.jpg",
  "caption": "Post caption #hashtag"
}

// Video/Reel
{
  "media_type": "REELS",
  "video_url": "https://example.com/video.mp4",
  "caption": "Reel caption"
}

// Carousel
{
  "media_type": "CAROUSEL",
  "children": ["CONTAINER_ID_1", "CONTAINER_ID_2"],
  "caption": "Carousel caption"
}

// Story
{
  "media_type": "STORIES",
  "image_url": "https://example.com/story.jpg"
}
```

**Step 2**: Publish container
```http
POST /{IG_USER_ID}/media_publish?creation_id={CONTAINER_ID}
```

#### Supported Content Types

| Type | `media_type` | Max Duration | Aspect Ratio |
|------|--------------|--------------|--------------|
| Image Post | (default) | - | 1:1, 4:5, 1.91:1 |
| Video Post | `VIDEO` | 60 min | Various |
| Reel | `REELS` | 90 seconds | 9:16 |
| Carousel | `CAROUSEL` | - | 1:1 |
| Story | `STORIES` | 60 seconds | 9:16 |

#### Requirements

- Instagram Business or Creator account
- Connected to Facebook Page
- 1,000+ followers for some features

---

## 11. Organic Insights

### Facebook Page Insights

#### Endpoint

```http
GET https://graph.facebook.com/v24.0/{PAGE_ID}/insights
GET https://graph.facebook.com/v24.0/{POST_ID}/insights
```

#### Page-Level Metrics

| Metric | API Field | Description |
|--------|-----------|-------------|
| Page Views | `page_views_total` | Total page views |
| Page Followers | `page_follows` | New followers |
| Page Unfollows | `page_unfollows` | Lost followers |
| Page Reach | `page_impressions_unique` | Unique reach |
| Page Impressions | `page_impressions` | Total impressions |
| Engaged Users | `page_engaged_users` | Users who engaged |
| Post Engagements | `page_post_engagements` | All engagements |

#### Post-Level Metrics

| Metric | API Field | Description |
|--------|-----------|-------------|
| Post Reach | `post_impressions_unique` | Unique reach |
| Post Impressions | `post_impressions` | Total impressions |
| Engagements | `post_engaged_users` | Total engagements |
| Reactions | `post_reactions_by_type_total` | By type |
| Comments | `post_comments` | Comments |
| Shares | `post_shares` | Shares |
| Clicks | `post_clicks` | Clicks |
| Video Views | `post_video_views` | 3s+ views |

### Instagram Insights

#### Endpoint

```http
GET https://graph.facebook.com/v24.0/{IG_USER_ID}/insights
GET https://graph.facebook.com/v24.0/{IG_MEDIA_ID}/insights
```

#### Account-Level Metrics

| Metric | API Field | Description |
|--------|-----------|-------------|
| Impressions | `impressions` | Total impressions |
| Reach | `reach` | Unique accounts reached |
| Profile Views | `profile_views` | Profile visits |
| Follower Count | `follower_count` | Total followers |
| Website Clicks | `website_clicks` | Bio link clicks |

#### Media-Level Metrics

| Metric | API Field | Description |
|--------|-----------|-------------|
| Impressions | `impressions` | Total impressions |
| Reach | `reach` | Unique accounts |
| Engagement | `engagement` | Total engagement |
| Likes | `like_count` | Likes |
| Comments | `comments_count` | Comments |
| Saves | `saved` | Saves |
| Shares | `shares` | Shares |

#### Reels Metrics

| Metric | API Field | Description |
|--------|-----------|-------------|
| Plays | `plays` | Total plays |
| Reach | `reach` | Unique accounts |
| Likes | `likes` | Likes |
| Comments | `comments` | Comments |
| Shares | `shares` | Shares |
| Saves | `saved` | Saves |

#### Stories Metrics

| Metric | API Field | Description |
|--------|-----------|-------------|
| Impressions | `impressions` | Total views |
| Reach | `reach` | Unique viewers |
| Exits | `exits` | Story exits |
| Replies | `replies` | DM replies |
| Taps Forward | `taps_forward` | Skip taps |
| Taps Back | `taps_back` | Replay taps |

### 2025 Metric Deprecations

**Deprecated (v21+)**:
- `video_views` (non-Reels)
- `email_contacts`
- `profile_views` (time series)
- `website_clicks` (time series)
- `phone_call_clicks`
- `text_message_clicks`

**November 2025 Changes**:
- `impressions` → `views` (for non-video)
- `page_likes` → `page_followers`

---

## 12. API Examples

### Example 1: Create Lead Generation Campaign

```json
// POST /act_{AD_ACCOUNT_ID}/campaigns
{
  "name": "Lead Gen Campaign - Jan 2026",
  "objective": "OUTCOME_LEADS",
  "status": "PAUSED",
  "special_ad_categories": ["NONE"],
  "buying_type": "AUCTION",
  "campaign_budget_optimization": true,
  "daily_budget": 50000,
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP"
}
```

### Example 2: Create E-commerce Ad Set

```json
// POST /act_{AD_ACCOUNT_ID}/adsets
{
  "name": "AdSet - Purchase - Fashion - India",
  "campaign_id": "120209876543210",
  "status": "PAUSED",
  "billing_event": "IMPRESSIONS",
  "optimization_goal": "OFFSITE_CONVERSIONS",
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
  "daily_budget": 100000,
  "start_time": "2026-01-10T00:00:00+0530",
  "promoted_object": {
    "pixel_id": "123456789012345",
    "custom_event_type": "PURCHASE"
  },
  "attribution_spec": [
    {"event_type": "CLICK_THROUGH", "window_days": 7},
    {"event_type": "VIEW_THROUGH", "window_days": 1}
  ],
  "targeting": {
    "geo_locations": {
      "countries": ["IN"]
    },
    "age_min": 18,
    "age_max": 45,
    "genders": [2],
    "publisher_platforms": ["facebook", "instagram"],
    "flexible_spec": [
      {
        "interests": [
          {"id": "6003107902433", "name": "Fashion"},
          {"id": "6003139266461", "name": "Online shopping"}
        ],
        "behaviors": [
          {"id": "6002714895372", "name": "Engaged Shoppers"}
        ]
      }
    ]
  }
}
```

### Example 3: Create Retargeting Ad Set

```json
// POST /act_{AD_ACCOUNT_ID}/adsets
{
  "name": "AdSet - Retarget - Cart Abandoners",
  "campaign_id": "120209876543213",
  "status": "PAUSED",
  "billing_event": "IMPRESSIONS",
  "optimization_goal": "OFFSITE_CONVERSIONS",
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
  "daily_budget": 75000,
  "promoted_object": {
    "pixel_id": "123456789012345",
    "custom_event_type": "PURCHASE"
  },
  "targeting": {
    "geo_locations": {"countries": ["IN"]},
    "publisher_platforms": ["facebook", "instagram"],
    "custom_audiences": [
      {"id": "23851234567890123"}
    ],
    "excluded_custom_audiences": [
      {"id": "23859876543210987"}
    ]
  }
}
```

### Example 4: Get Campaign Insights

```http
GET /act_{AD_ACCOUNT_ID}/insights?
  level=campaign&
  date_preset=last_30d&
  fields=campaign_name,impressions,reach,clicks,spend,actions,cost_per_action_type&
  breakdowns=publisher_platform
```

### Example 5: Get Ad Set Performance by Demographics

```http
GET /{ADSET_ID}/insights?
  date_preset=last_7d&
  fields=impressions,reach,clicks,spend,actions&
  breakdowns=age,gender&
  time_increment=1
```

### Example 6: Send Conversion Event (CAPI)

```json
// POST /{PIXEL_ID}/events
{
  "data": [
    {
      "event_name": "Purchase",
      "event_time": 1704067200,
      "event_id": "order_12345",
      "action_source": "website",
      "event_source_url": "https://example.com/thank-you",
      "user_data": {
        "em": ["a1b2c3d4e5f6..."],
        "ph": ["1234567890..."],
        "client_ip_address": "1.2.3.4",
        "client_user_agent": "Mozilla/5.0...",
        "fbc": "fb.1.1234567890.abcdefg",
        "fbp": "fb.1.1234567890.hijklmn"
      },
      "custom_data": {
        "currency": "INR",
        "value": 2499.00,
        "content_ids": ["SKU123", "SKU456"],
        "content_type": "product",
        "num_items": 2
      }
    }
  ],
  "access_token": "{ACCESS_TOKEN}"
}
```

### Example 7: Create Custom Audience from Website Visitors

```json
// POST /act_{AD_ACCOUNT_ID}/customaudiences
{
  "name": "Website Visitors - Add to Cart - 30 Days",
  "subtype": "WEBSITE",
  "retention_days": 30,
  "rule": {
    "inclusions": {
      "operator": "or",
      "rules": [
        {
          "event_sources": [
            {"id": "123456789012345", "type": "pixel"}
          ],
          "retention_seconds": 2592000,
          "filter": {
            "operator": "and",
            "filters": [
              {"field": "event", "operator": "eq", "value": "AddToCart"}
            ]
          }
        }
      ]
    }
  }
}
```

### Example 8: Publish Instagram Reel

```json
// Step 1: Create container
// POST /{IG_USER_ID}/media
{
  "media_type": "REELS",
  "video_url": "https://example.com/reel.mp4",
  "caption": "Check out our new product! #newproduct #launch",
  "share_to_feed": true
}

// Response: {"id": "CONTAINER_ID"}

// Step 2: Publish
// POST /{IG_USER_ID}/media_publish
{
  "creation_id": "CONTAINER_ID"
}
```

---

## Quick Reference

### API Endpoints Summary

| Resource | Endpoint |
|----------|----------|
| Campaigns | `/act_{id}/campaigns` |
| Ad Sets | `/act_{id}/adsets` |
| Ads | `/act_{id}/ads` |
| Creatives | `/act_{id}/adcreatives` |
| Images | `/act_{id}/adimages` |
| Videos | `/act_{id}/advideos` |
| Insights | `/{object_id}/insights` |
| Custom Audiences | `/act_{id}/customaudiences` |
| Pixels | `/act_{id}/adspixels` |
| Conversions | `/{pixel_id}/events` |
| Page Posts | `/{page_id}/feed` |
| IG Media | `/{ig_user_id}/media` |

### Currency Conversion (INR)

```
₹1 = 100 paisa = 100 (API value)
₹100 = 10000
₹500 = 50000
₹1,000 = 100000
₹10,000 = 1000000
```

### Common Objective + Optimization Combinations

| Goal | Objective | Optimization |
|------|-----------|--------------|
| Brand Awareness | `OUTCOME_AWARENESS` | `REACH` |
| Website Traffic | `OUTCOME_TRAFFIC` | `LINK_CLICKS` |
| Quality Traffic | `OUTCOME_TRAFFIC` | `LANDING_PAGE_VIEWS` |
| Engagement | `OUTCOME_ENGAGEMENT` | `POST_ENGAGEMENT` |
| Messages | `OUTCOME_ENGAGEMENT` | `MESSAGES` |
| Lead Forms | `OUTCOME_LEADS` | `LEAD_GENERATION` |
| Website Conversions | `OUTCOME_SALES` | `OFFSITE_CONVERSIONS` |
| ROAS Optimization | `OUTCOME_SALES` | `VALUE` |
| App Installs | `OUTCOME_APP_PROMOTION` | `APP_INSTALLS` |

### Minimum Budgets

| Objective | India (INR/day) | US (USD/day) |
|-----------|-----------------|--------------|
| Awareness | ₹40 | $1 |
| Traffic | ₹100 | $5 |
| Engagement | ₹100 | $5 |
| Leads | ₹200 | $10 |
| Conversions | ₹200 | $10 |

---

## Sources

### Official Documentation
- [Meta Marketing API](https://developers.facebook.com/docs/marketing-api)
- [Graph API Reference](https://developers.facebook.com/docs/graph-api)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [Conversions API](https://developers.facebook.com/docs/marketing-api/conversions-api)

### 2025 Updates
- [Meta API v24.0 Release](https://uamaster.net/facebook-launches-graph-api-v24-0-and-marketing-api-v24-0-for-developers/)
- [Advantage+ Campaign Changes](https://ppc.land/meta-deprecates-legacy-campaign-apis-for-advantage-structure/)
- [Facebook Ads Reporting API Guide](https://magicbrief.com/post/comprehensive-guide-to-the-facebook-ads-reporting-api)
- [Meta Ads API Complete Guide](https://admanage.ai/blog/meta-ads-api)
- [ODAX Campaign Objectives](https://bir.ch/blog/facebook-ad-objectives)
- [Instagram Graph API 2025](https://elfsight.com/blog/instagram-graph-api-complete-developer-guide-for-2025/)
- [Meta Conversions API Guide](https://www.didomi.io/blog/meta-conversions-api-capi-tracking)
- [Facebook Insights Deprecation](https://www.yext.com/blog/2025/10/facebook-is-deprecating-metrics-what-to-know)
