# Meta Marketing API v24.0 - Create Ad Set Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Authentication](#authentication)
4. [Endpoint Reference](#endpoint-reference)
5. [CREATE Ad Set - Required Parameters](#required-parameters)
6. [CREATE Ad Set - Optional Parameters](#optional-parameters)
7. [Targeting Specifications](#targeting-specifications)
8. [Placement Options](#placement-options)
9. [Optimization & Bidding](#optimization-bidding)
10. [Budget Configuration](#budget-configuration)
11. [Attribution Settings](#attribution-settings)
12. [READ Ad Sets - GET Operations](#read-ad-sets)
13. [Complete Examples](#complete-examples)
14. [Best Practices](#best-practices)
15. [Common Errors](#common-errors)

---

## Overview

The Create Ad Set endpoint allows you to create an ad set within an existing campaign in Meta's advertising platform. An ad set is the middle layer of Meta's advertising structure:

**Campaign** → **Ad Set** (Targeting, Budget, Schedule) → **Ad** (Creative)

**API Endpoint:**
```
POST https://graph.facebook.com/v24.0/act_<AD_ACCOUNT_ID>/adsets
```

**Purpose:** Define where, when, and to whom your ads will be shown, along with budget allocation and optimization goals.

---

## Prerequisites

### Non-Negotiable Requirements

Before you can successfully create an ad set, ensure the following exist:

| Requirement | Description | How to Verify |
|-------------|-------------|---------------|
| **Ad Account** | Active Meta Ads Account | `GET /act_{ad_account_id}` |
| **Campaign** | Parent campaign with valid objective | `GET /{campaign_id}` |
| **Page/Instagram Account** | For traffic, conversions, or sales campaigns | Account settings |
| **Pixel/App/Offline Event Set** | Required for conversion-based campaigns | `GET /{ad_account_id}/adspixels` |
| **Access Token** | Valid token with `ads_management` and `business_management` permissions | Token debugger |

### Permission Scopes Required
- `ads_management` - Create and manage ads
- `business_management` - Manage business assets

---

## Authentication

### Headers Required

```http
Content-Type: application/json
Authorization: Bearer {USER_ACCESS_TOKEN}
```

### Token Types
- **User Access Token:** Most common, requires user permissions
- **System User Token:** For automated systems
- **App Access Token:** Limited use cases

**Token Generation:** Use Facebook Login or Business Manager to generate tokens with appropriate scopes.

---

## Endpoint Reference

### Base Request Structure

```http
POST https://graph.facebook.com/v24.0/act_{AD_ACCOUNT_ID}/adsets
Content-Type: application/json
Authorization: Bearer {ACCESS_TOKEN}

{
  "name": "string",
  "campaign_id": "string",
  "billing_event": "enum",
  "optimization_goal": "enum",
  "bid_strategy": "enum",
  "daily_budget": integer,
  "targeting": {...},
  "status": "enum"
}
```

---

## Required Parameters

### 1. name (string)
**Description:** Internal identifier for the ad set. Not visible to end users.

**Format:** Descriptive string that helps you identify the ad set.

**Best Practice Naming Convention:**
```
AdSet - [Objective] - [Location] - [Demographics] - [Date]
```

**Examples:**
```json
"name": "AdSet - Purchase - India - 18-45 - Jan2026"
"name": "AdSet - Traffic - Mumbai - Women 25-34"
"name": "AdSet - LeadGen - Delhi NCR - Homeowners"
```

**Constraints:**
- Maximum 200 characters
- Avoid special characters that might cause parsing issues

---

### 2. campaign_id (string)
**Description:** The ID of the parent campaign under which this ad set will be created.

**Format:** Numeric string

**Example:**
```json
"campaign_id": "120209876543210"
```

**How to Get Campaign ID:**
```bash
GET /v24.0/act_{ad_account_id}/campaigns
```

**Important Notes:**
- Campaign must already exist
- Campaign's objective determines available optimization goals
- Cannot be changed after creation

---

### 3. billing_event (enum)
**Description:** Determines when you're charged for the ad.

**Available Values:**

| Value | Description | When to Use | Compatible Objectives |
|-------|-------------|-------------|----------------------|
| `IMPRESSIONS` | Charged per 1,000 impressions (CPM) | Most common, brand awareness | All objectives |
| `CLICKS` | Charged per click on ad | When clicks are valuable | Traffic, Conversions |
| `LINK_CLICKS` | Charged per outbound link click | Website traffic focus | Traffic, Conversions |
| `THRUPLAY` | Charged per 15-second video view | Video campaigns | Video Views, Engagement |
| `APP_INSTALLS` | Charged per app installation | App campaigns | App Installs |
| `CONVERSIONS` | Charged per conversion event | Performance campaigns | Conversions, Sales |

**Example:**
```json
"billing_event": "IMPRESSIONS"
```

**Critical Rule:** Must align with `optimization_goal` (see compatibility matrix below).

---

### 4. optimization_goal (enum)
**Description:** What Meta's algorithm should optimize delivery for.

**Most Common Values:**

| Goal | Description | Use Case | Compatible Billing Events |
|------|-------------|----------|---------------------------|
| `REACH` | Maximize unique users reached | Brand awareness | IMPRESSIONS |
| `IMPRESSIONS` | Maximize total impressions | Broad awareness | IMPRESSIONS |
| `LINK_CLICKS` | Maximize link clicks | Website traffic | IMPRESSIONS, LINK_CLICKS |
| `LANDING_PAGE_VIEWS` | Maximize landing page loads | Quality traffic | IMPRESSIONS, LINK_CLICKS |
| `OFFSITE_CONVERSIONS` | Maximize website conversions | E-commerce, lead gen | IMPRESSIONS, CONVERSIONS |
| `VALUE` | Maximize conversion value | E-commerce ROAS | IMPRESSIONS |
| `APP_INSTALLS` | Maximize app installs | Mobile apps | IMPRESSIONS, APP_INSTALLS |
| `VIDEO_VIEWS` | Maximize video plays | Video content | IMPRESSIONS, THRUPLAY |
| `LEAD_GENERATION` | Maximize lead form submissions | Lead generation | IMPRESSIONS |
| `MESSAGES` | Maximize messaging conversations | Customer engagement | IMPRESSIONS |

**Example:**
```json
"optimization_goal": "OFFSITE_CONVERSIONS"
```

**Campaign Objective Compatibility:**
The optimization goal must be compatible with your campaign's objective. For example:
- **SALES** campaign → `OFFSITE_CONVERSIONS`, `VALUE`
- **TRAFFIC** campaign → `LINK_CLICKS`, `LANDING_PAGE_VIEWS`
- **AWARENESS** campaign → `REACH`, `IMPRESSIONS`

---

### 5. bid_strategy (enum)
**Description:** How Meta should manage bidding in the auction.

**Available Strategies:**

| Strategy | Description | When to Use | Control Level |
|----------|-------------|-------------|---------------|
| `LOWEST_COST_WITHOUT_CAP` | Meta auto-bids for best results | Starting out, stable campaigns | Low (Meta controls) |
| `LOWEST_COST_WITH_BID_CAP` | Auto-bid with maximum bid limit | Control costs, mature campaigns | Medium |
| `COST_CAP` | Target average cost per action | Scaling with CPA goals | Medium-High |
| `TARGET_COST` | Stable cost per action | Consistent CPA needed | High |

**Detailed Explanations:**

**LOWEST_COST_WITHOUT_CAP (Recommended for Most):**
```json
"bid_strategy": "LOWEST_COST_WITHOUT_CAP"
```
- Meta has full control
- Bids as needed to maximize results
- Best for: Learning phase, new campaigns, unstable delivery

**LOWEST_COST_WITH_BID_CAP:**
```json
"bid_strategy": "LOWEST_COST_WITH_BID_CAP",
"bid_amount": 5000  // ₹50 max bid in cents
```
- Set maximum bid you're willing to pay
- Meta bids up to this cap
- Best for: Controlling costs, avoiding overspend

**COST_CAP:**
```json
"bid_strategy": "COST_CAP",
"bid_amount": 3000  // Target ₹30 average cost
```
- Meta maintains average cost around your target
- Individual results may cost more/less
- Best for: Scaling while maintaining efficiency

**TARGET_COST (Deprecated but available):**
```json
"bid_strategy": "TARGET_COST",
"bid_amount": 2500  // Target ₹25 per result
```
- Stricter than COST_CAP
- Meta tries to deliver at exactly this cost
- Best for: When you need predictable costs

---

### 6. daily_budget OR lifetime_budget (integer)
**Description:** How much you're willing to spend on this ad set.

**Critical:** Values are in **CENTS** (smallest currency unit).

**Format:**
```json
"daily_budget": 50000  // ₹500 per day (in paisa)
```

OR

```json
"lifetime_budget": 500000  // ₹5,000 total (in paisa)
```

**Conversion Examples (INR):**
- ₹100/day → `10000`
- ₹500/day → `50000`
- ₹1,000/day → `100000`
- ₹10,000/day → `1000000`

**Rules:**
1. **Use ONLY ONE** - Either `daily_budget` OR `lifetime_budget`, not both
2. **Campaign Budget Optimization (CBO):** If campaign uses CBO, do NOT set ad set budget
3. **Minimum Budget:** Depends on billing event and location (typically ₹40-₹100/day for India)
4. **Lifetime Budget:** Requires `end_time` to be set

**Example Daily Budget:**
```json
{
  "daily_budget": 50000,
  "start_time": "2026-01-10T00:00:00+0530"
}
```

**Example Lifetime Budget:**
```json
{
  "lifetime_budget": 700000,
  "start_time": "2026-01-10T00:00:00+0530",
  "end_time": "2026-01-17T23:59:59+0530"
}
```

---

### 7. targeting (object)
**Description:** Defines who will see your ads. This is the most complex and important parameter.

**Overview:** Targeting is a nested JSON object containing multiple sub-parameters for demographics, geography, interests, behaviors, and more.

**Basic Structure:**
```json
"targeting": {
  "geo_locations": {...},
  "age_min": 18,
  "age_max": 65,
  "genders": [1, 2],
  "publisher_platforms": ["facebook", "instagram"],
  "flexible_spec": [...],
  "custom_audiences": [...],
  "excluded_custom_audiences": [...]
}
```

**See [Targeting Specifications](#targeting-specifications) section for complete details.**

---

## Optional Parameters

### Time & Delivery Controls

#### start_time (datetime string)
**Description:** When the ad set should start running.

**Format:** ISO-8601 with timezone
```json
"start_time": "2026-01-10T00:00:00+0530"
```

**Rules:**
- If omitted, starts immediately when set to ACTIVE
- Must be in future
- Timezone format: `+0530` for IST, `+0000` for UTC

#### end_time (datetime string)
**Description:** When the ad set should stop running.

**Format:** Same as `start_time`
```json
"end_time": "2026-01-20T23:59:59+0530"
```

**Rules:**
- Optional (runs indefinitely if omitted with daily budget)
- Required if using `lifetime_budget`
- Must be after `start_time`

#### status (enum)
**Description:** Initial state of the ad set.

**Values:**
- `PAUSED` - Created but not running (RECOMMENDED for testing)
- `ACTIVE` - Running immediately

**Example:**
```json
"status": "PAUSED"
```

**Best Practice:** Always create as `PAUSED`, review everything, then activate separately.

---

### Advanced Delivery Options

#### pacing_type (array of enum)
**Description:** Controls how budget is spent throughout the day.

**Values:**
- `standard` - Spend evenly throughout the day (default)
- `day_parting` - Spend only during specific hours

**Example:**
```json
"pacing_type": ["standard"]
```

#### destination_type (enum)
**Description:** Where people go when they click your ad.

**Values:**
- `WEBSITE` - External website
- `APP` - Mobile app
- `MESSENGER` - Messenger conversation
- `WHATSAPP` - WhatsApp conversation
- `INSTAGRAM_DIRECT` - Instagram DM
- `FACEBOOK` - On-Facebook destination

**Example:**
```json
"destination_type": "WEBSITE"
```

---

## Targeting Specifications

### Geographic Targeting (geo_locations)

#### Structure:
```json
"geo_locations": {
  "countries": ["IN", "US"],
  "regions": [
    {"key": "4030"}  // Maharashtra, India
  ],
  "cities": [
    {
      "key": "2418779",  // Pune
      "radius": 25,
      "distance_unit": "kilometer"
    }
  ],
  "zips": [
    {"key": "US:10001"}  // US only
  ],
  "location_types": ["home", "recent"]
}
```

#### Finding Geographic IDs:

**Countries:** Use ISO 3166-1 alpha-2 codes
```
IN = India
US = United States
GB = United Kingdom
AE = United Arab Emirates
```

**Regions/Cities:** Use the geolocation search endpoint
```bash
GET /v24.0/search?type=adgeolocation&q=Mumbai&location_types=["city"]
```

**Response Example:**
```json
{
  "data": [
    {
      "key": "2422341",
      "name": "Mumbai, Maharashtra, India",
      "type": "city",
      "country_code": "IN"
    }
  ]
}
```

#### Location Types:
- `home` - People who live in this location
- `recent` - People recently in this location
- `travel_in` - People traveling to this location

**Example - Multiple Locations:**
```json
"geo_locations": {
  "countries": ["IN"],
  "cities": [
    {"key": "2418779", "radius": 15, "distance_unit": "kilometer"},
    {"key": "2422341", "radius": 20, "distance_unit": "kilometer"}
  ],
  "location_types": ["home", "recent"]
}
```

---

### Demographic Targeting

#### Age
```json
"age_min": 18,
"age_max": 45
```

**Rules:**
- Minimum: 13 (18 for alcohol, gambling, financial services)
- Maximum: 65+
- Both must be specified together

#### Gender
```json
"genders": [1]  // Male only
"genders": [2]  // Female only
"genders": [1, 2]  // All genders
```

**Gender IDs:**
- `1` = Male
- `2` = Female
- `[1, 2]` = All genders (default if omitted)

---

### Interest & Behavior Targeting (flexible_spec)

**Structure:** Array of objects containing interests, behaviors, demographics, or connections.

**Logic:** Objects within array are OR'd, properties within objects are AND'd.

#### Basic Example - Interests:
```json
"flexible_spec": [
  {
    "interests": [
      {"id": "6003139266461", "name": "Online shopping"},
      {"id": "6003107902433", "name": "Fashion"}
    ]
  }
]
```

**Meaning:** People interested in Online Shopping OR Fashion

#### Complex Example - Interests AND Behaviors:
```json
"flexible_spec": [
  {
    "interests": [
      {"id": "6003139266461", "name": "Online shopping"}
    ],
    "behaviors": [
      {"id": "6002714895372", "name": "Engaged Shoppers"}
    ]
  }
]
```

**Meaning:** People interested in Online Shopping AND are Engaged Shoppers

#### Multiple Audience Segments:
```json
"flexible_spec": [
  {
    "interests": [{"id": "6003139266461"}]
  },
  {
    "behaviors": [{"id": "6015559470583"}]
  }
]
```

**Meaning:** (People interested in Online Shopping) OR (People with specific behavior)

#### Finding Interest/Behavior IDs:

**Interests:**
```bash
GET /v24.0/search?type=adinterest&q=fitness&limit=10
```

**Response:**
```json
{
  "data": [
    {
      "id": "6003139266461",
      "name": "Physical fitness",
      "audience_size_lower_bound": 290000000,
      "audience_size_upper_bound": 340000000,
      "path": ["Interests", "Fitness and wellness"]
    }
  ]
}
```

**Behaviors:**
```bash
GET /v24.0/search?type=adTargetingCategory&class=behaviors
```

**Demographics:**
```bash
GET /v24.0/search?type=adTargetingCategory&class=demographics
```

---

### Custom Audiences

#### Including Custom Audiences:
```json
"custom_audiences": [
  {"id": "23851234567890123"},
  {"id": "23851234567890456"}
]
```

**Meaning:** Target people in these custom audiences (Website visitors, customer lists, etc.)

#### Excluding Custom Audiences:
```json
"excluded_custom_audiences": [
  {"id": "23859876543210987"}
]
```

**Meaning:** Exclude people in this audience (e.g., existing customers)

#### Lookalike Audiences:
```json
"custom_audiences": [
  {"id": "23851234567890123"}
],
"lookalike_spec": {
  "ratio": 0.01,
  "country": "IN",
  "starting_ratio": 0.00
}
```

**Ratio Values:**
- `0.01` = 1% lookalike (most similar, smallest audience)
- `0.05` = 5% lookalike
- `0.10` = 10% lookalike (least similar, largest audience)

---

### Connections

#### Targeting Connected Users:
```json
"connections": [
  {"id": "123456789012345"}  // Page ID
]
```

**Meaning:** People who like this page

#### Excluding Connected Users:
```json
"excluded_connections": [
  {"id": "123456789012345"}
]
```

**Meaning:** People who don't like this page

#### Friend Connections:
```json
"friends_of_connections": [
  {"id": "123456789012345"}
]
```

**Meaning:** Friends of people who like this page

---

## Placement Options

### Automatic Placements (Recommended)

**Description:** Let Meta show ads across all available placements.

```json
"targeting": {
  "publisher_platforms": ["facebook", "instagram", "audience_network", "messenger"]
}
```

**Advantages:**
- Lower costs (more inventory)
- Better optimization
- Simpler setup

**Best For:** Most campaigns, especially when starting

---

### Manual Placement Selection

**Structure:** Specify platforms and specific positions.

```json
"targeting": {
  "publisher_platforms": ["facebook", "instagram"],
  "facebook_positions": ["feed", "video_feeds", "marketplace"],
  "instagram_positions": ["stream", "story", "explore"]
}
```

#### Available Platform & Position Combinations:

**Facebook:**
```json
"publisher_platforms": ["facebook"],
"facebook_positions": [
  "feed",               // News Feed
  "right_hand_column",  // Desktop sidebar
  "video_feeds",        // Video Feed
  "marketplace",        // Marketplace
  "story",              // Stories
  "search"              // Search results
]
```

**Instagram:**
```json
"publisher_platforms": ["instagram"],
"instagram_positions": [
  "stream",    // Feed
  "story",     // Stories
  "explore",   // Explore tab
  "reels"      // Reels
]
```

**Messenger:**
```json
"publisher_platforms": ["messenger"],
"messenger_positions": [
  "messenger_home",  // Messenger home
  "story"            // Messenger Stories
]
```

**Audience Network:**
```json
"publisher_platforms": ["audience_network"],
"audience_network_positions": [
  "classic",         // Banner/interstitial
  "instream_video",  // In-stream video
  "rewarded_video"   // Rewarded video
]
```

#### Device Targeting:
```json
"device_platforms": ["mobile", "desktop"],
"publisher_platforms": ["facebook"]
```

**Values:**
- `mobile` - Smartphones and tablets
- `desktop` - Desktop computers

---

## Optimization & Bidding

### Promoted Object (Conversion Setup)

**Description:** Specifies what conversion event to optimize for.

**Required for:** Conversion-based campaigns (SALES, LEAD_GENERATION)

#### Website Conversions with Pixel:
```json
"promoted_object": {
  "pixel_id": "123456789012345",
  "custom_event_type": "PURCHASE"
}
```

**Custom Event Types:**
- `VIEW_CONTENT` - Product page views
- `ADD_TO_CART` - Add to cart events
- `INITIATE_CHECKOUT` - Checkout started
- `PURCHASE` - Completed purchases
- `LEAD` - Lead form submissions
- `COMPLETE_REGISTRATION` - Account registrations
- `ADD_PAYMENT_INFO` - Payment info added
- `ADD_TO_WISHLIST` - Wishlist additions

#### App Events:
```json
"promoted_object": {
  "application_id": "123456789012345",
  "object_store_url": "https://play.google.com/store/apps/details?id=com.example",
  "custom_event_type": "PURCHASE"
}
```

#### Offline Events:
```json
"promoted_object": {
  "offline_conversion_data_set_id": "123456789012345",
  "custom_event_type": "PURCHASE"
}
```

#### Page Engagement:
```json
"promoted_object": {
  "page_id": "123456789012345"
}
```

---

### Attribution Settings

**Description:** Defines the conversion window for attributing conversions to ads.

```json
"attribution_spec": [
  {
    "event_type": "CLICK_THROUGH",
    "window_days": 7
  },
  {
    "event_type": "VIEW_THROUGH",
    "window_days": 1
  }
]
```

**Event Types:**
- `CLICK_THROUGH` - User clicked ad then converted
- `VIEW_THROUGH` - User saw ad then converted without clicking

**Common Window Configurations:**

**Default (Recommended):**
- 7-day click
- 1-day view

**E-commerce:**
- 7-day click
- 1-day view

**Long Purchase Cycle:**
- 28-day click
- 7-day view

**Short Attention:**
- 1-day click
- 1-day view

---

### Conversion Optimization

#### Conversion Location:
```json
"conversion_domain": "www.example.com"
```

**Use When:** Optimizing for conversions on specific domain

#### Deep Link:
```json
"deep_link": "myapp://product/12345"
```

**Use When:** Driving to specific in-app content

---

## Budget Configuration

### Daily Budget
```json
"daily_budget": 50000,  // ₹500/day
"start_time": "2026-01-10T00:00:00+0530"
```

**Best For:**
- Ongoing campaigns
- Flexible end date
- Testing and learning

---

### Lifetime Budget
```json
"lifetime_budget": 500000,  // ₹5,000 total
"start_time": "2026-01-10T00:00:00+0530",
"end_time": "2026-01-20T23:59:59+0530"
```

**Best For:**
- Fixed campaign duration
- Event-based promotions
- Fixed total spend

---

### Budget Spend Limits (Advanced)

**Only works with Campaign Budget Optimization (CBO)**

#### Minimum Daily Spend:
```json
"daily_min_spend_target": 20000  // ₹200 minimum per day
```

#### Maximum Daily Spend:
```json
"daily_spend_cap": 100000  // ₹1,000 maximum per day
```

**Use Cases:**
- Control ad set within CBO campaigns
- Prevent overspend on specific audiences
- Ensure minimum exposure

---

## READ Ad Sets - GET Operations

### Overview

The GET endpoints allow you to retrieve ad set data, monitor performance, check status, and audit configurations. This is essential for:
- Monitoring campaign performance
- Auditing ad set configurations
- Building dashboards and reports
- Automated optimization systems
- Troubleshooting delivery issues

---

### GET Endpoints

#### 1. Get Single Ad Set
```
GET https://graph.facebook.com/v24.0/{adset_id}
```

**Use Case:** Retrieve detailed information about a specific ad set.

**Example Request:**
```bash
GET /v24.0/120209876543210?fields=id,name,status,daily_budget,targeting&access_token=YOUR_TOKEN
```

---

#### 2. Get All Ad Sets in Ad Account
```
GET https://graph.facebook.com/v24.0/act_{AD_ACCOUNT_ID}/adsets
```

**Use Case:** List all ad sets in an ad account, with optional filtering.

**Example Request:**
```bash
GET /v24.0/act_123456789012345/adsets?fields=id,name,status,effective_status&access_token=YOUR_TOKEN
```

---

### Query Parameters

#### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `access_token` | string | Valid access token with ads_management permission | `EAABsb...` |
| `fields` | string | Comma-separated list of fields to retrieve | `id,name,status` |

#### Optional Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `limit` | integer | Number of results per page (default: 25, max: 100) | `50` |
| `after` | string | Pagination cursor for next page | `encoded_cursor` |
| `filtering` | array | Filter results by specific criteria | `[{field:"status",operator:"EQUAL",value:"ACTIVE"}]` |
| `date_preset` | enum | Date range for insights | `last_7d`, `last_30d` |

---

### Complete Field Reference

#### 🔹 Core Identification Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `id` | string | Unique ad set identifier | `"120209876543210"` |
| `account_id` | string | Parent ad account ID | `"act_123456789012345"` |
| `campaign_id` | string | Parent campaign ID | `"120208765432100"` |
| `name` | string | Ad set name (internal label) | `"AdSet - Purchase - India"` |
| `created_time` | datetime | When ad set was created | `"2026-01-08T10:30:00+0000"` |
| `updated_time` | datetime | Last modification time | `"2026-01-09T15:45:00+0000"` |
| `start_time` | datetime | Scheduled start time | `"2026-01-10T00:00:00+0530"` |
| `end_time` | datetime | Scheduled end time (if set) | `"2026-01-20T23:59:59+0530"` |

**Example Request:**
```bash
GET /v24.0/120209876543210?fields=id,name,campaign_id,created_time,updated_time&access_token=TOKEN
```

**Example Response:**
```json
{
  "id": "120209876543210",
  "name": "AdSet - Purchase - India - 18-45",
  "campaign_id": "120208765432100",
  "created_time": "2026-01-08T10:30:00+0000",
  "updated_time": "2026-01-09T15:45:00+0000"
}
```

---

#### 🔹 Status & Delivery Fields

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `status` | enum | Current configured status | `ACTIVE`, `PAUSED`, `DELETED`, `ARCHIVED` |
| `configured_status` | enum | Explicitly set status | Same as `status` |
| `effective_status` | enum | Real-time delivery status | See detailed list below |
| `issues_info` | array | Delivery problems and blocks | Array of issue objects |
| `recommendations` | array | Meta's optimization suggestions | Array of recommendation objects |

**Status Enum Values:**

| Value | Meaning |
|-------|---------|
| `ACTIVE` | Ad set is turned on |
| `PAUSED` | Ad set is paused by user |
| `DELETED` | Ad set is deleted (soft delete) |
| `ARCHIVED` | Ad set is archived |

**Effective Status Values (Real Delivery State):**

| Value | Meaning | Action Needed |
|-------|---------|---------------|
| `ACTIVE` | Currently delivering | None - running normally |
| `PAUSED` | Manually paused | Unpause to resume |
| `IN_PROCESS` | Being reviewed or processing | Wait for approval |
| `WITH_ISSUES` | Has delivery problems | Check `issues_info` |
| `CAMPAIGN_PAUSED` | Parent campaign is paused | Activate campaign |
| `DELETED` | Soft deleted | Restore or create new |
| `ARCHIVED` | Archived for historical record | Duplicate if needed |
| `ADSET_PAUSED` | This specific ad set paused | Change status to ACTIVE |

**Example Request:**
```bash
GET /v24.0/120209876543210?fields=id,name,status,configured_status,effective_status,issues_info&access_token=TOKEN
```

**Example Response:**
```json
{
  "id": "120209876543210",
  "name": "AdSet - Purchase - India",
  "status": "ACTIVE",
  "configured_status": "ACTIVE",
  "effective_status": "WITH_ISSUES",
  "issues_info": [
    {
      "level": "WARNING",
      "message": "Your ad set is not delivering because your payment method failed"
    }
  ]
}
```

---

#### 🔹 Budget & Bidding Fields (Critical)

| Field | Type | Description | Format |
|-------|------|-------------|--------|
| `daily_budget` | string | Daily budget in minor currency units | `"50000"` = ₹500 |
| `lifetime_budget` | string | Total lifetime budget | `"500000"` = ₹5,000 |
| `budget_remaining` | string | Remaining budget (lifetime only) | `"250000"` = ₹2,500 |
| `bid_amount` | string | Manual bid amount (if applicable) | `"5000"` = ₹50 |
| `bid_strategy` | enum | Bidding strategy used | See values below |
| `billing_event` | enum | When you're charged | See values below |
| `optimization_goal` | enum | What Meta optimizes for | See values below |
| `use_new_app_click` | boolean | Uses new app click attribution | `true` or `false` |
| `pacing_type` | array | How budget is spent | `["standard"]` or `["day_parting"]` |

**Bid Strategy Values:**

| Value | Description |
|-------|-------------|
| `LOWEST_COST_WITHOUT_CAP` | Automatic bidding, no cap |
| `LOWEST_COST_WITH_BID_CAP` | Automatic with max bid limit |
| `COST_CAP` | Target average cost per result |
| `LOWEST_COST_WITH_MIN_ROAS` | Minimum ROAS bidding |

**Billing Event Values:**

| Value | Charged For |
|-------|-------------|
| `IMPRESSIONS` | Per 1,000 impressions |
| `CLICKS` | Per click |
| `LINK_CLICKS` | Per outbound link click |
| `APP_INSTALLS` | Per app install |
| `THRUPLAY` | Per video ThruPlay |
| `CONVERSIONS` | Per conversion |

**Optimization Goal Values:**

| Value | Optimizes For |
|-------|---------------|
| `REACH` | Maximum unique reach |
| `IMPRESSIONS` | Maximum impressions |
| `LINK_CLICKS` | Maximum link clicks |
| `APP_INSTALLS` | Maximum app installs |
| `CONVERSIONS` | Maximum conversions |
| `OFFSITE_CONVERSIONS` | Maximum website conversions |
| `VALUE` | Maximum conversion value |
| `LEAD_GENERATION` | Maximum leads |
| `LANDING_PAGE_VIEWS` | Maximum landing page views |
| `THRUPLAY` | Maximum ThruPlays |

**Example Request:**
```bash
GET /v24.0/120209876543210?fields=id,name,daily_budget,bid_strategy,billing_event,optimization_goal,budget_remaining&access_token=TOKEN
```

**Example Response:**
```json
{
  "id": "120209876543210",
  "name": "AdSet - Purchase - India",
  "daily_budget": "50000",
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
  "billing_event": "IMPRESSIONS",
  "optimization_goal": "OFFSITE_CONVERSIONS",
  "budget_remaining": null
}
```

---

#### 🔹 Targeting (Critical Section)

**Field:** `targeting` (object)

**Description:** Complete targeting specification showing who sees your ads.

**Sub-Fields in Targeting Object:**

| Sub-Field | Type | Description |
|-----------|------|-------------|
| `geo_locations` | object | Geographic targeting (countries, regions, cities) |
| `age_min` | integer | Minimum age |
| `age_max` | integer | Maximum age |
| `genders` | array | Gender targeting (1=male, 2=female) |
| `interests` | array | Interest-based targeting IDs |
| `behaviors` | array | Behavior-based targeting IDs |
| `custom_audiences` | array | Custom audience IDs to include |
| `excluded_custom_audiences` | array | Custom audience IDs to exclude |
| `publisher_platforms` | array | Platforms (facebook, instagram, audience_network, messenger) |
| `facebook_positions` | array | FB placements (feed, stories, reels, etc.) |
| `instagram_positions` | array | IG placements (stream, story, explore, reels) |
| `device_platforms` | array | Device types (mobile, desktop) |
| `user_os` | array | Operating systems (iOS, Android, Windows) |
| `wireless_carrier` | array | Mobile carrier targeting |
| `education_statuses` | array | Education level targeting |
| `work_employers` | array | Employer targeting |
| `work_positions` | array | Job title targeting |
| `flexible_spec` | array | Combined interest/behavior/demographic targeting |
| `exclusions` | object | Audience exclusions |
| `connections` | array | Page/app connection targeting |
| `excluded_connections` | array | Exclude page/app connections |
| `friends_of_connections` | array | Friends of page likers |

**Example Request:**
```bash
GET /v24.0/120209876543210?fields=id,name,targeting&access_token=TOKEN
```

**Example Response:**
```json
{
  "id": "120209876543210",
  "name": "AdSet - Purchase - India",
  "targeting": {
    "geo_locations": {
      "countries": ["IN"],
      "location_types": ["home"]
    },
    "age_min": 18,
    "age_max": 45,
    "genders": [1, 2],
    "publisher_platforms": ["facebook", "instagram"],
    "facebook_positions": ["feed", "video_feeds"],
    "instagram_positions": ["stream", "story"],
    "device_platforms": ["mobile", "desktop"],
    "flexible_spec": [
      {
        "interests": [
          {
            "id": "6003139266461",
            "name": "Online shopping"
          }
        ],
        "behaviors": [
          {
            "id": "6002714895372",
            "name": "Engaged Shoppers"
          }
        ]
      }
    ],
    "custom_audiences": [
      {
        "id": "23851234567890123",
        "name": "Website Visitors - 30 Days"
      }
    ],
    "excluded_custom_audiences": [
      {
        "id": "23859876543210987",
        "name": "Existing Customers"
      }
    ]
  }
}
```

---

#### 🔹 Dynamic Creative & Automation

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `is_dynamic_creative` | boolean | Using dynamic creative optimization | `true`, `false` |
| `use_new_app_click` | boolean | New app click attribution method | `true`, `false` |
| `smart_promotion_type` | enum | Smart automation type | `GUIDED_CREATION`, `SMART_APP_PROMOTION` |
| `multi_optimization_goal_weight` | string | Weight for multiple optimization goals | Percentage string |

**Example Request:**
```bash
GET /v24.0/120209876543210?fields=id,name,is_dynamic_creative,smart_promotion_type&access_token=TOKEN
```

**Example Response:**
```json
{
  "id": "120209876543210",
  "name": "AdSet - Purchase - India",
  "is_dynamic_creative": true,
  "smart_promotion_type": "GUIDED_CREATION"
}
```

---

#### 🔹 Attribution & Conversion

| Field | Type | Description |
|-------|------|-------------|
| `attribution_spec` | array | Attribution windows for conversions |
| `conversion_window_days` | integer | Conversion window in days |
| `promoted_object` | object | What's being promoted (pixel, app, page) |

**Promoted Object Sub-Fields:**

| Sub-Field | Type | Description |
|-----------|------|-------------|
| `pixel_id` | string | Facebook Pixel ID |
| `custom_event_type` | enum | Event to optimize for (PURCHASE, LEAD, etc.) |
| `application_id` | string | Mobile app ID |
| `product_set_id` | string | Product catalog set ID |
| `page_id` | string | Facebook Page ID |
| `object_store_url` | string | App store URL |

**Example Request:**
```bash
GET /v24.0/120209876543210?fields=id,name,promoted_object,attribution_spec&access_token=TOKEN
```

**Example Response:**
```json
{
  "id": "120209876543210",
  "name": "AdSet - Purchase - India",
  "promoted_object": {
    "pixel_id": "123456789012345",
    "custom_event_type": "PURCHASE"
  },
  "attribution_spec": [
    {
      "event_type": "CLICK_THROUGH",
      "window_days": 7
    },
    {
      "event_type": "VIEW_THROUGH",
      "window_days": 1
    }
  ]
}
```

---

#### 🔹 Delivery Controls

| Field | Type | Description |
|-------|------|-------------|
| `frequency_control_specs` | array | Frequency capping rules |
| `delivery_estimate` | object | Estimated reach and results |
| `daily_min_spend_target` | string | Minimum daily spend (CBO only) |
| `daily_spend_cap` | string | Maximum daily spend (CBO only) |
| `lifetime_min_spend_target` | string | Minimum lifetime spend |
| `lifetime_spend_cap` | string | Maximum lifetime spend |

**Example Request:**
```bash
GET /v24.0/120209876543210?fields=id,name,frequency_control_specs,daily_spend_cap&access_token=TOKEN
```

**Example Response:**
```json
{
  "id": "120209876543210",
  "name": "AdSet - Purchase - India",
  "frequency_control_specs": [
    {
      "event": "IMPRESSIONS",
      "interval_days": 7,
      "max_frequency": 2
    }
  ],
  "daily_spend_cap": "100000"
}
```

---

#### 🔹 Special Ad Categories (Compliance)

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `special_ad_categories` | array | Restricted ad categories | See below |
| `special_ad_category_country` | array | Countries where restrictions apply | Country codes |

**Special Ad Category Values:**

| Value | Applies To |
|-------|------------|
| `HOUSING` | Real estate, rentals |
| `EMPLOYMENT` | Job postings, recruitment |
| `CREDIT` | Financial services, loans |
| `ISSUES_ELECTIONS_POLITICS` | Political ads, social issues |

**Example Request:**
```bash
GET /v24.0/120209876543210?fields=id,name,special_ad_categories,special_ad_category_country&access_token=TOKEN
```

**Example Response:**
```json
{
  "id": "120209876543210",
  "name": "AdSet - Employment - India",
  "special_ad_categories": ["EMPLOYMENT"],
  "special_ad_category_country": ["IN", "US"]
}
```

---

#### 🔹 A/B Testing & Labeling

| Field | Type | Description |
|-------|------|-------------|
| `is_experiment` | boolean | Part of A/B test |
| `adlabels` | array | Labels for organization |
| `source_adset_id` | string | Original ad set if duplicated |
| `creative_sequence` | array | Creative rotation sequence |

**Example Request:**
```bash
GET /v24.0/120209876543210?fields=id,name,is_experiment,adlabels,source_adset_id&access_token=TOKEN
```

**Example Response:**
```json
{
  "id": "120209876543210",
  "name": "AdSet - Purchase - Test A",
  "is_experiment": true,
  "adlabels": [
    {
      "id": "12345",
      "name": "Q1-2026-Campaign"
    }
  ],
  "source_adset_id": "120209876543200"
}
```

---

#### 🔹 Review & Quality Scores

| Field | Type | Description |
|-------|------|-------------|
| `review_feedback` | object | Ad review status and feedback |
| `rf_prediction_id` | string | Reach & frequency prediction ID |
| `quality_score_ectr` | string | Expected click-through rate score |
| `quality_score_ecvr` | string | Expected conversion rate score |
| `quality_score_organic` | string | Organic engagement quality score |

**Example Request:**
```bash
GET /v24.0/120209876543210?fields=id,name,review_feedback,quality_score_ectr&access_token=TOKEN
```

**Example Response:**
```json
{
  "id": "120209876543210",
  "name": "AdSet - Purchase - India",
  "review_feedback": {
    "global": {
      "can_use_creative": true
    }
  },
  "quality_score_ectr": "ABOVE_AVERAGE"
}
```

---

### Full Fields String for Postman

**Copy-Paste Ready - All Available Fields:**

```
id,account_id,campaign_id,name,status,configured_status,effective_status,created_time,updated_time,start_time,end_time,daily_budget,lifetime_budget,budget_remaining,bid_amount,bid_strategy,billing_event,optimization_goal,pacing_type,targeting,promoted_object,attribution_spec,frequency_control_specs,delivery_estimate,is_dynamic_creative,use_new_app_click,smart_promotion_type,multi_optimization_goal_weight,special_ad_categories,special_ad_category_country,daily_spend_cap,daily_min_spend_target,lifetime_spend_cap,lifetime_min_spend_target,adlabels,issues_info,recommendations,review_feedback,source_adset_id,is_experiment,rf_prediction_id,quality_score_ectr,quality_score_ecvr,quality_score_organic,creative_sequence
```

**Usage in Postman:**
```
GET https://graph.facebook.com/v24.0/120209876543210?fields=id,account_id,campaign_id,name,status,configured_status,effective_status,created_time,updated_time,start_time,end_time,daily_budget,lifetime_budget,budget_remaining,bid_amount,bid_strategy,billing_event,optimization_goal,pacing_type,targeting,promoted_object,attribution_spec,frequency_control_specs,delivery_estimate,is_dynamic_creative,use_new_app_click,smart_promotion_type,multi_optimization_goal_weight,special_ad_categories,special_ad_category_country,daily_spend_cap,daily_min_spend_target,lifetime_spend_cap,lifetime_min_spend_target,adlabels,issues_info,recommendations,review_feedback,source_adset_id,is_experiment&access_token=YOUR_TOKEN
```

---

### Practical GET Examples

#### Example 1: Basic Ad Set Info
```bash
GET /v24.0/120209876543210?fields=id,name,status,daily_budget,campaign_id&access_token=TOKEN
```

**Response:**
```json
{
  "id": "120209876543210",
  "name": "AdSet - Purchase - India - 18-45",
  "status": "ACTIVE",
  "daily_budget": "50000",
  "campaign_id": "120208765432100"
}
```

---

#### Example 2: Status Check with Issues
```bash
GET /v24.0/120209876543210?fields=id,name,effective_status,issues_info,recommendations&access_token=TOKEN
```

**Response:**
```json
{
  "id": "120209876543210",
  "name": "AdSet - Purchase - India",
  "effective_status": "WITH_ISSUES",
  "issues_info": [
    {
      "level": "ERROR",
      "message": "This ad set is not delivering because all ads in this ad set have been disapproved"
    }
  ],
  "recommendations": [
    {
      "message": "Edit your ads to comply with our policies"
    }
  ]
}
```

---

#### Example 3: Complete Budget & Bid Info
```bash
GET /v24.0/120209876543210?fields=id,name,daily_budget,lifetime_budget,budget_remaining,bid_strategy,bid_amount,billing_event,optimization_goal&access_token=TOKEN
```

**Response:**
```json
{
  "id": "120209876543210",
  "name": "AdSet - Purchase - India",
  "daily_budget": "50000",
  "bid_strategy": "LOWEST_COST_WITH_BID_CAP",
  "bid_amount": "5000",
  "billing_event": "IMPRESSIONS",
  "optimization_goal": "OFFSITE_CONVERSIONS"
}
```

---

#### Example 4: Full Targeting Details
```bash
GET /v24.0/120209876543210?fields=id,name,targeting&access_token=TOKEN
```

**Response:** (See targeting section example above)

---

#### Example 5: Conversion Setup Audit
```bash
GET /v24.0/120209876543210?fields=id,name,promoted_object,attribution_spec,optimization_goal&access_token=TOKEN
```

**Response:**
```json
{
  "id": "120209876543210",
  "name": "AdSet - Purchase - India",
  "promoted_object": {
    "pixel_id": "123456789012345",
    "custom_event_type": "PURCHASE"
  },
  "attribution_spec": [
    {
      "event_type": "CLICK_THROUGH",
      "window_days": 7
    },
    {
      "event_type": "VIEW_THROUGH",
      "window_days": 1
    }
  ],
  "optimization_goal": "OFFSITE_CONVERSIONS"
}
```

---

#### Example 6: List All Active Ad Sets
```bash
GET /v24.0/act_123456789012345/adsets?fields=id,name,status,effective_status,daily_budget&filtering=[{"field":"effective_status","operator":"IN","value":["ACTIVE"]}]&limit=50&access_token=TOKEN
```

**Response:**
```json
{
  "data": [
    {
      "id": "120209876543210",
      "name": "AdSet - Purchase - India - 18-45",
      "status": "ACTIVE",
      "effective_status": "ACTIVE",
      "daily_budget": "50000"
    },
    {
      "id": "120209876543211",
      "name": "AdSet - Traffic - Mumbai - Women",
      "status": "ACTIVE",
      "effective_status": "ACTIVE",
      "daily_budget": "30000"
    }
  ],
  "paging": {
    "cursors": {
      "before": "MAZDZD",
      "after": "MjQZD"
    },
    "next": "https://graph.facebook.com/v24.0/act_123456789012345/adsets?after=MjQZD"
  }
}
```

---

### Filtering Ad Sets

**Filter Structure:**
```json
[
  {
    "field": "field_name",
    "operator": "OPERATOR",
    "value": "value_or_array"
  }
]
```

**Common Filters:**

#### Filter by Status:
```bash
filtering=[{"field":"effective_status","operator":"IN","value":["ACTIVE","PAUSED"]}]
```

#### Filter by Campaign:
```bash
filtering=[{"field":"campaign_id","operator":"EQUAL","value":"120208765432100"}]
```

#### Filter by Date Range:
```bash
filtering=[{"field":"created_time","operator":"GREATER_THAN","value":"2026-01-01"}]
```

**Available Operators:**
- `EQUAL`
- `NOT_EQUAL`
- `IN`
- `NOT_IN`
- `GREATER_THAN`
- `LESS_THAN`
- `CONTAIN`
- `NOT_CONTAIN`

---

### Pagination

**Automatic Pagination:**
```bash
# First request
GET /v24.0/act_123456789012345/adsets?fields=id,name&limit=25&access_token=TOKEN
```

**Response includes pagination:**
```json
{
  "data": [...],
  "paging": {
    "cursors": {
      "before": "MAZDZD",
      "after": "MjQZD"
    },
    "next": "https://graph.facebook.com/v24.0/act_123456789012345/adsets?after=MjQZD"
  }
}
```

**Next Page Request:**
```bash
GET /v24.0/act_123456789012345/adsets?fields=id,name&limit=25&after=MjQZD&access_token=TOKEN
```

---

### Performance Insights (Separate Endpoint)

**Note:** Performance metrics are NOT available through standard GET fields. Use the insights endpoint:

```bash
GET /v24.0/{adset_id}/insights?fields=impressions,clicks,spend,cpc,cpm,ctr,conversions,cost_per_conversion&date_preset=last_7d&access_token=TOKEN
```

**Available Insight Metrics:**
- `impressions` - Total impressions
- `clicks` - Total clicks
- `spend` - Total spend
- `reach` - Unique reach
- `frequency` - Average frequency
- `cpc` - Cost per click
- `cpm` - Cost per 1,000 impressions
- `ctr` - Click-through rate
- `conversions` - Total conversions
- `cost_per_conversion` - Average cost per conversion
- `roas` - Return on ad spend (requires value data)

**See [Meta Insights API Documentation](https://developers.facebook.com/docs/marketing-api/insights) for complete metrics list.**

---

### Use Cases for GET Operations

#### 1. **Monitoring Dashboard**
Retrieve all ad sets with status and budget:
```bash
GET /v24.0/act_{account_id}/adsets?fields=id,name,effective_status,daily_budget,budget_remaining,spend&access_token=TOKEN
```

#### 2. **Delivery Troubleshooting**
Check why ad sets aren't delivering:
```bash
GET /v24.0/{adset_id}?fields=id,name,effective_status,issues_info,recommendations&access_token=TOKEN
```

#### 3. **Budget Audit**
Review budget allocation across ad sets:
```bash
GET /v24.0/act_{account_id}/adsets?fields=id,name,daily_budget,lifetime_budget,budget_remaining&access_token=TOKEN
```

#### 4. **Targeting Audit**
Review targeting configurations:
```bash
GET /v24.0/{adset_id}?fields=id,name,targeting&access_token=TOKEN
```

#### 5. **Conversion Setup Verification**
Ensure pixels and events are configured:
```bash
GET /v24.0/{adset_id}?fields=id,name,promoted_object,optimization_goal,attribution_spec&access_token=TOKEN
```

#### 6. **Campaign Structure Export**
Export complete campaign structure:
```bash
GET /v24.0/act_{account_id}/adsets?fields=id,campaign_id,name,status,targeting,daily_budget,optimization_goal&limit=100&access_token=TOKEN
```

---

### GET Best Practices

#### 1. **Request Only Needed Fields**
❌ **Don't:**
```bash
GET /v24.0/{adset_id}?fields=id,account_id,campaign_id,name,status,configured_status,effective_status,created_time,updated_time,start_time,end_time,daily_budget,lifetime_budget,...[50 more fields]
```

✅ **Do:**
```bash
GET /v24.0/{adset_id}?fields=id,name,status,effective_status,daily_budget
```

**Reason:** Reduces response size, improves speed, lowers API quota usage.

---

#### 2. **Use Filtering for Large Accounts**
Always filter when listing ad sets:
```bash
GET /v24.0/act_{account_id}/adsets?fields=id,name&filtering=[{"field":"effective_status","operator":"IN","value":["ACTIVE"]}]
```

---

#### 3. **Implement Pagination Properly**
For accounts with 100+ ad sets:
```python
# Pseudo-code
all_adsets = []
url = f"/v24.0/act_{account_id}/adsets?fields=id,name&limit=100"

while url:
    response = requests.get(url)
    data = response.json()
    all_adsets.extend(data['data'])
    url = data.get('paging', {}).get('next')
```

---

#### 4. **Cache Static Data**
Fields that rarely change:
- `id`, `name`, `campaign_id`
- `created_time`, `targeting` (unless modified)

Cache these and refresh periodically rather than requesting every time.

---

#### 5. **Monitor Rate Limits**
- **Per User:** 200 calls per hour per user
- **Per App:** 200 calls per hour per app per user

Implement exponential backoff and retry logic.

---

#### 6. **Error Handling**
```javascript
try {
  const response = await fetch(apiUrl);
  const data = await response.json();
  
  if (data.error) {
    console.error('API Error:', data.error.message);
    // Handle specific error codes
    if (data.error.code === 100) {
      // Invalid parameter
    } else if (data.error.code === 190) {
      // Invalid access token
    }
  }
} catch (error) {
  console.error('Request failed:', error);
}
```

---

### Complete Postman Collection Example

**Collection Structure:**

```
Meta Marketing API - Ad Sets
│
├── 1. GET Single Ad Set
│   └── GET /v24.0/{adset_id}
│
├── 2. GET All Ad Sets (Basic)
│   └── GET /v24.0/act_{account_id}/adsets
│
├── 3. GET Active Ad Sets Only
│   └── GET /v24.0/act_{account_id}/adsets (with filtering)
│
├── 4. GET Ad Set with Full Details
│   └── GET /v24.0/{adset_id} (all fields)
│
├── 5. GET Ad Set Targeting
│   └── GET /v24.0/{adset_id}?fields=targeting
│
└── 6. GET Ad Set Insights
    └── GET /v24.0/{adset_id}/insights
```

**Environment Variables:**
- `ad_account_id`: Your ad account ID
- `access_token`: Your access token
- `adset_id`: Specific ad set ID for testing

---

## Complete Examples

### Example 1: E-commerce Purchase Campaign - India

**Scenario:** Selling products online, targeting Indian shoppers interested in fashion.

```json
{
  "name": "AdSet - Purchase - Fashion Lovers - India - Jan2026",
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

---

### Example 2: Lead Generation - Local Business

**Scenario:** Dental clinic in Mumbai targeting local residents.

```json
{
  "name": "AdSet - LeadGen - Mumbai - Dental - Jan2026",
  "campaign_id": "120209876543211",
  "status": "PAUSED",
  
  "billing_event": "IMPRESSIONS",
  "optimization_goal": "LEAD_GENERATION",
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
  
  "daily_budget": 30000,
  "start_time": "2026-01-10T00:00:00+0530",
  "end_time": "2026-01-31T23:59:59+0530",
  
  "targeting": {
    "geo_locations": {
      "cities": [
        {
          "key": "2422341",
          "radius": 10,
          "distance_unit": "kilometer"
        }
      ],
      "location_types": ["home"]
    },
    "age_min": 25,
    "age_max": 55,
    "publisher_platforms": ["facebook", "instagram"],
    "facebook_positions": ["feed", "marketplace"],
    "instagram_positions": ["stream"]
  }
}
```

---

### Example 3: App Install Campaign

**Scenario:** Mobile game targeting gamers worldwide.

```json
{
  "name": "AdSet - AppInstall - Global - Gamers - Jan2026",
  "campaign_id": "120209876543212",
  "status": "PAUSED",
  
  "billing_event": "IMPRESSIONS",
  "optimization_goal": "APP_INSTALLS",
  "bid_strategy": "LOWEST_COST_WITH_BID_CAP",
  "bid_amount": 15000,
  
  "daily_budget": 200000,
  "start_time": "2026-01-10T00:00:00+0530",
  
  "promoted_object": {
    "application_id": "987654321098765",
    "object_store_url": "https://play.google.com/store/apps/details?id=com.game.awesome"
  },
  
  "targeting": {
    "geo_locations": {
      "countries": ["IN", "US", "GB", "CA", "AU"]
    },
    "age_min": 18,
    "age_max": 35,
    "publisher_platforms": ["facebook", "instagram", "audience_network"],
    "device_platforms": ["mobile"],
    "flexible_spec": [
      {
        "interests": [
          {"id": "6003348954433", "name": "Mobile games"},
          {"id": "6003050466278", "name": "Video games"}
        ]
      }
    ]
  }
}
```

---

### Example 4: Retargeting Website Visitors

**Scenario:** Retarget people who visited but didn't purchase, exclude existing customers.

```json
{
  "name": "AdSet - Retarget - Cart Abandoners - Jan2026",
  "campaign_id": "120209876543213",
  "status": "PAUSED",
  
  "billing_event": "IMPRESSIONS",
  "optimization_goal": "OFFSITE_CONVERSIONS",
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
  
  "daily_budget": 75000,
  "start_time": "2026-01-10T00:00:00+0530",
  
  "promoted_object": {
    "pixel_id": "123456789012345",
    "custom_event_type": "PURCHASE"
  },
  
  "targeting": {
    "geo_locations": {
      "countries": ["IN"]
    },
    "age_min": 18,
    "age_max": 65,
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

---

### Example 5: Lookalike Audience - High-Value Customers

**Scenario:** Find people similar to your best customers.

```json
{
  "name": "AdSet - Lookalike - TopCustomers 1% - Jan2026",
  "campaign_id": "120209876543214",
  "status": "PAUSED",
  
  "billing_event": "IMPRESSIONS",
  "optimization_goal": "VALUE",
  "bid_strategy": "COST_CAP",
  "bid_amount": 25000,
  
  "daily_budget": 150000,
  "start_time": "2026-01-10T00:00:00+0530",
  
  "promoted_object": {
    "pixel_id": "123456789012345",
    "custom_event_type": "PURCHASE"
  },
  
  "targeting": {
    "geo_locations": {
      "countries": ["IN"]
    },
    "age_min": 25,
    "age_max": 55,
    "publisher_platforms": ["facebook", "instagram"],
    "custom_audiences": [
      {"id": "23851234567890123"}
    ],
    "lookalike_spec": {
      "ratio": 0.01,
      "country": "IN",
      "starting_ratio": 0.00
    },
    "excluded_custom_audiences": [
      {"id": "23859876543210987"}
    ]
  }
}
```

---

## Best Practices

### 1. Initial Testing Phase

**Start Conservative:**
```json
{
  "status": "PAUSED",
  "daily_budget": 10000,
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
  "optimization_goal": "LINK_CLICKS"
}
```

**Why:**
- Test creative performance
- Validate targeting
- Check technical setup
- Minimize risk

**Duration:** 3-7 days minimum

---

### 2. Targeting Strategy

**Broad → Narrow:**

**Phase 1 - Broad (Learning):**
```json
"targeting": {
  "geo_locations": {"countries": ["IN"]},
  "age_min": 18,
  "age_max": 65
}
```

**Phase 2 - Refined (Optimizing):**
```json
"targeting": {
  "geo_locations": {
    "countries": ["IN"],
    "regions": [{"key": "4030"}]
  },
  "age_min": 25,
  "age_max": 45,
  "flexible_spec": [...]
}
```

---

### 3. Budget Allocation

**Minimum Recommended Budgets:**

| Objective | Minimum Daily (India) | Learning Phase |
|-----------|----------------------|----------------|
| Awareness | ₹200 | 3-5 days |
| Traffic | ₹300 | 3-7 days |
| Conversions | ₹500 | 7-14 days |
| App Installs | ₹400 | 7-10 days |

**Formula:** Minimum = (Target CPA) × 50 conversions ÷ 7 days

---

### 4. Placement Strategy

**Start:** Automatic Placements
```json
"publisher_platforms": ["facebook", "instagram", "audience_network", "messenger"]
```

**After Learning:** Review Placement Performance
- Remove underperforming placements
- Allocate more to top performers
- Create placement-specific ad sets

---

### 5. Optimization Timeline

**Days 1-3: Learning**
- Don't make changes
- Let algorithm learn
- Monitor delivery

**Days 4-7: Initial Optimization**
- Review metrics
- Adjust budget ±20%
- Refine targeting slightly

**Days 8-14: Scaling**
- Increase budget 20-30% every 3 days
- Expand to similar audiences
- Test new creatives

**Days 15+: Mature**
- Maintain winning combinations
- Continuous testing
- Expand to new markets

---

### 6. Attribution Best Practices

**E-commerce Standard:**
```json
"attribution_spec": [
  {"event_type": "CLICK_THROUGH", "window_days": 7},
  {"event_type": "VIEW_THROUGH", "window_days": 1}
]
```

**High-Consideration Products (Cars, Real Estate):**
```json
"attribution_spec": [
  {"event_type": "CLICK_THROUGH", "window_days": 28},
  {"event_type": "VIEW_THROUGH", "window_days": 7}
]
```

**Impulse Purchases:**
```json
"attribution_spec": [
  {"event_type": "CLICK_THROUGH", "window_days": 1},
  {"event_type": "VIEW_THROUGH", "window_days": 1}
]
```

---

### 7. Naming Conventions

**Template:**
```
AdSet - [Objective] - [Audience] - [Location] - [Demo] - [Date/Version]
```

**Examples:**
```
AdSet - Purchase - Lookalike1% - India - 25-45F - Jan2026
AdSet - Traffic - InterestFitness - Mumbai - 18-35 - V2
AdSet - LeadGen - Retarget-Visitors - Delhi - Homeowners
```

---

### 8. Testing Framework

**Variables to Test (One at a Time):**

1. **Audiences:**
   - Interest targeting
   - Behavior targeting
   - Custom audiences
   - Lookalike %

2. **Demographics:**
   - Age ranges
   - Gender
   - Location radius

3. **Placements:**
   - Automatic vs Manual
   - Specific positions
   - Device types

4. **Bidding:**
   - Bid strategies
   - Bid amounts
   - Budget levels

**Test Structure:**
- Control ad set (winning combination)
- Test ad set (one variable changed)
- Equal budgets
- Run simultaneously
- 7-day minimum

---

## Common Errors

### Error 1: Budget Too Low

**Error Message:**
```json
{
  "error": {
    "message": "(#100) The budget is too low for this ad set",
    "code": 100
  }
}
```

**Solution:**
- Increase `daily_budget` to at least ₹40-100 (4000-10000 cents)
- Check minimum budget requirements for your billing event

---

### Error 2: Invalid Campaign Objective

**Error Message:**
```json
{
  "error": {
    "message": "The optimization goal is not compatible with this campaign objective",
    "code": 100
  }
}
```

**Solution:**
- Verify campaign's `objective`
- Match `optimization_goal` to compatible value
- See optimization goal compatibility matrix above

---

### Error 3: Missing Promoted Object

**Error Message:**
```json
{
  "error": {
    "message": "promoted_object is required for this optimization goal",
    "code": 100
  }
}
```

**Solution:**
Add `promoted_object`:
```json
"promoted_object": {
  "pixel_id": "YOUR_PIXEL_ID",
  "custom_event_type": "PURCHASE"
}
```

---

### Error 4: Invalid Targeting ID

**Error Message:**
```json
{
  "error": {
    "message": "Invalid parameter: targeting",
    "code": 100
  }
}
```

**Solution:**
- Verify interest/behavior IDs using search endpoint
- Check geo location keys are correct
- Ensure custom audience IDs exist and you have access

---

### Error 5: Overlapping Budget Settings

**Error Message:**
```json
{
  "error": {
    "message": "Cannot set ad set budget when campaign uses CBO",
    "code": 100
  }
}
```

**Solution:**
- Remove `daily_budget` and `lifetime_budget` from ad set
- Campaign Budget Optimization handles budget at campaign level

---

### Error 6: Attribution Spec Invalid

**Error Message:**
```json
{
  "error": {
    "message": "Invalid attribution_spec format",
    "code": 100
  }
}
```

**Solution:**
Use correct format:
```json
"attribution_spec": [
  {"event_type": "CLICK_THROUGH", "window_days": 7},
  {"event_type": "VIEW_THROUGH", "window_days": 1}
]
```

---

### Error 7: Missing Permissions

**Error Message:**
```json
{
  "error": {
    "message": "Insufficient permissions to create ad set",
    "code": 200
  }
}
```

**Solution:**
- Verify access token has `ads_management` permission
- Check you have ADMIN or ADVERTISER role on ad account
- Regenerate token with proper scopes

---

### Error 8: Invalid Time Format

**Error Message:**
```json
{
  "error": {
    "message": "Invalid start_time format",
    "code": 100
  }
}
```

**Solution:**
Use ISO-8601 format:
```json
"start_time": "2026-01-10T00:00:00+0530"
```

Not: `"2026-01-10"` or `"01/10/2026"`

---

## Testing Checklist

Before launching an ad set, verify:

- [ ] Campaign ID is valid and objective matches
- [ ] Budget is in CENTS (multiply by 100)
- [ ] `billing_event` matches `optimization_goal`
- [ ] Pixel is installed and firing (for conversions)
- [ ] Targeting isn't too narrow (>1,000 potential reach)
- [ ] Targeting isn't too broad (unless intentional)
- [ ] `promoted_object` included for conversion campaigns
- [ ] Status set to `PAUSED` for review
- [ ] `start_time` in correct timezone format
- [ ] Access token has required permissions
- [ ] Custom audience IDs exist and accessible
- [ ] Interest/behavior IDs validated via search
- [ ] Attribution windows appropriate for business
- [ ] Naming convention followed for tracking

---

## Quick Reference

### API Endpoints Summary

**CREATE Ad Set:**
```
POST /v24.0/act_{AD_ACCOUNT_ID}/adsets
```

**GET Single Ad Set:**
```
GET /v24.0/{adset_id}?fields=FIELD_LIST
```

**GET All Ad Sets:**
```
GET /v24.0/act_{AD_ACCOUNT_ID}/adsets?fields=FIELD_LIST
```

**GET Ad Set Insights:**
```
GET /v24.0/{adset_id}/insights?fields=METRIC_LIST&date_preset=PRESET
```

---

### Currency Conversion (INR)
```
₹1 = 100 paisa = 100 (in API)
₹10 = 1000
₹100 = 10000
₹500 = 50000
₹1,000 = 100000
₹10,000 = 1000000
```

---

### Status Values Quick Reference

**Status (Configured):**
- `ACTIVE` - Ad set turned on
- `PAUSED` - Ad set paused

**Effective Status (Real Delivery):**
- `ACTIVE` - Delivering
- `PAUSED` - Manually paused
- `WITH_ISSUES` - Has problems
- `CAMPAIGN_PAUSED` - Parent campaign paused
- `IN_PROCESS` - Under review

---

### Common Optimization Goals
```
Traffic → LINK_CLICKS or LANDING_PAGE_VIEWS
Conversions → OFFSITE_CONVERSIONS
Value → VALUE
Leads → LEAD_GENERATION
Apps → APP_INSTALLS
Awareness → REACH or IMPRESSIONS
Video → THRUPLAY
Messages → MESSAGES
```

---

### Bid Strategies
```
LOWEST_COST_WITHOUT_CAP → Full automation (Recommended)
LOWEST_COST_WITH_BID_CAP → Capped automation
COST_CAP → Target average cost
TARGET_COST → Stable cost (deprecated)
```

---

### Minimum Budgets (India)
```
Awareness: ₹40-100/day
Traffic: ₹100-200/day
Conversions: ₹200-500/day
App Installs: ₹300-400/day
```

---

### Learning Phase
```
Needs ~50 optimization events per week
7-14 days typical duration
Avoid changes during learning
Reset triggers: Major targeting/budget changes
```

---

### Essential GET Fields by Use Case

**Monitoring:**
```
fields=id,name,effective_status,daily_budget,spend
```

**Troubleshooting:**
```
fields=id,name,effective_status,issues_info,recommendations
```

**Budget Audit:**
```
fields=id,name,daily_budget,lifetime_budget,budget_remaining
```

**Targeting Audit:**
```
fields=id,name,targeting
```

**Performance Check:**
```
Use /insights endpoint with metrics like impressions,clicks,spend,conversions
```

---

### Common Filter Examples

**Active Ad Sets:**
```
filtering=[{"field":"effective_status","operator":"EQUAL","value":"ACTIVE"}]
```

**By Campaign:**
```
filtering=[{"field":"campaign_id","operator":"EQUAL","value":"CAMPAIGN_ID"}]
```

**Created After Date:**
```
filtering=[{"field":"created_time","operator":"GREATER_THAN","value":"2026-01-01"}]
```

---

## Additional Resources

### Official Documentation
- Meta Marketing API Docs: https://developers.facebook.com/docs/marketing-api
- Ad Set Reference: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign
- Targeting Specs: https://developers.facebook.com/docs/marketing-api/audiences/reference/targeting-specs

### Tools
- **Graph API Explorer:** Test API calls - https://developers.facebook.com/tools/explorer
- **Access Token Debugger:** Verify permissions - https://developers.facebook.com/tools/debug/accesstoken
- **Targeting Search:** Find IDs - https://developers.facebook.com/tools/explorer (search endpoint)

### Support
- Developer Community: https://developers.facebook.com/community
- Business Help Center: https://www.facebook.com/business/help

---

## Version History

**v24.0** - Current
- Latest stable version
- All features documented above

**Backwards Compatibility:**
- Most parameters work across versions
- Check changelog for deprecations
- Test thoroughly when upgrading

---

## Conclusion

This comprehensive guide covers all aspects of creating ad sets via the Meta Marketing API v24.0. Remember:

1. **Start Paused** - Always review before activating
2. **Test Small** - Begin with low budgets
3. **Learn Phase** - Give algorithm time to optimize
4. **Monitor Closely** - Check performance daily initially
5. **Iterate** - Continuous testing and improvement

For complex implementations, consider:
- Using Meta's Business SDK (Python, PHP, Node.js)
- Implementing error handling and retry logic
- Building automated rules and alerts
- Regular backup of configurations

**Need Help?** Consult Meta's official documentation or reach out to their developer support.