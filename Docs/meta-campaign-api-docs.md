# Meta Marketing API - Campaign Creation Documentation

## Endpoint Overview

**POST** `https://graph.facebook.com/v24.0/act_<AD_ACCOUNT_ID>/campaigns`

### Purpose
Creates a Campaign (top level of Meta Ads hierarchy)

### Ad Hierarchy Structure
```
Campaign
 └── Ad Set
      └── Ad
```

---

## Authentication & Headers

### Required Headers (Postman)
- **Authorization**: `Bearer <SYSTEM_USER_ACCESS_TOKEN>`
- **Content-Type**: `application/json`

### Required Token Permissions
- `ads_management`
- `business_management`
- Access to the Ad Account

---

## Required Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | ✅ | Campaign name |
| `objective` | string | ✅ | Marketing goal |
| `status` | string | ❌ (default: PAUSED) | Campaign delivery status |
| `special_ad_categories` | array | ❌ (required in some cases) | Compliance categories |

---

## Complete Parameter Reference

### 1. name
- **Type**: `string`
- **Description**: Human-readable campaign name
- **Example**:
```json
"name": "Axgen Lead Gen Campaign Jan 2026"
```

---

### 2. objective ⚠️ VERY IMPORTANT
- **Type**: `string`
- **Description**: Defines the marketing goal for the campaign

#### Allowed Values (v24.0 - Stable)

| Objective | Meaning |
|-----------|---------|
| `OUTCOME_AWARENESS` | Reach & Brand awareness |
| `OUTCOME_TRAFFIC` | Website / app traffic |
| `OUTCOME_ENGAGEMENT` | Likes, comments, shares |
| `OUTCOME_LEADS` | Lead forms, calls |
| `OUTCOME_APP_PROMOTION` | App installs |
| `OUTCOME_SALES` | Conversions, purchases |

⚠️ **Note**: Old objectives like `LEAD_GENERATION`, `CONVERSIONS` are deprecated

**Example**:
```json
"objective": "OUTCOME_LEADS"
```

---

### 3. status
- **Type**: `string`
- **Description**: Controls campaign delivery state

| Value | Meaning |
|-------|---------|
| `PAUSED` | Campaign created but not delivering |
| `ACTIVE` | Campaign starts delivering |

⚠️ **BEST PRACTICE**: Always create as `PAUSED`

**Example**:
```json
"status": "PAUSED"
```

---

### 4. special_ad_categories
- **Type**: `array<string>`
- **Required**: If campaign involves regulated content

#### Allowed Values

| Value | Used For |
|-------|----------|
| `NONE` | Normal ads |
| `HOUSING` | Property, rentals |
| `EMPLOYMENT` | Jobs |
| `CREDIT` | Loans, credit cards |
| `ISSUES_ELECTIONS_POLITICS` | Political |

**Example (Normal business)**:
```json
"special_ad_categories": ["NONE"]
```

---

### 5. buying_type
- **Type**: `string`
- **Default**: `AUCTION`

| Value | Meaning |
|-------|---------|
| `AUCTION` | Standard Meta auction ads |
| `RESERVED` | Reach & frequency (rare) |

**Example**:
```json
"buying_type": "AUCTION"
```

---

### 6. budget_rebalance_flag
- **Type**: `boolean`
- **Description**: Allows Meta to shift budget between ad sets automatically

**Example**:
```json
"budget_rebalance_flag": true
```

---

### 7. campaign_budget_optimization (CBO)
- **Type**: `boolean`

| Value | Meaning |
|-------|---------|
| `true` | Campaign Budget Optimization ON |
| `false` | Budget controlled at Ad Set level |

**Example**:
```json
"campaign_budget_optimization": true
```

---

### 8. daily_budget
- **Type**: `integer` (in minor units)
- **Currency Conversion**:
  - ₹500/day → `50000`
  - $10/day → `1000`

⚠️ **Note**: Only allowed if CBO = `true`

**Example**:
```json
"daily_budget": 50000
```

---

### 9. lifetime_budget
- **Type**: `integer` (in minor units)
- **Description**: Used instead of daily budget

**Example**:
```json
"lifetime_budget": 300000
```

---

### 10. start_time
- **Type**: ISO 8601 datetime

**Example**:
```json
"start_time": "2026-01-10T00:00:00+0530"
```

---

### 11. stop_time
- **Type**: ISO 8601 datetime

**Example**:
```json
"stop_time": "2026-01-31T23:59:59+0530"
```

---

### 12. bid_strategy
- **Type**: `string`

| Value | Meaning |
|-------|---------|
| `LOWEST_COST_WITHOUT_CAP` | Default |
| `LOWEST_COST_WITH_BID_CAP` | Manual bid |
| `COST_CAP` | Cost control |
| `BID_CAP` | Hard bid |

**Example**:
```json
"bid_strategy": "LOWEST_COST_WITHOUT_CAP"
```

---

### 13. spend_cap
- **Type**: `integer` (in minor units)
- **Description**: Maximum total spend allowed

**Example**:
```json
"spend_cap": 1000000
```

---

### 14. pacing_type
- **Type**: `array<string>`

| Value | Meaning |
|-------|---------|
| `standard` | Spend evenly |
| `accelerated` | Spend faster |

**Example**:
```json
"pacing_type": ["standard"]
```

---

### 15. promoted_object
- **Type**: `object`
- **Required**: For Sales / App / Leads objectives

#### Example: Website Conversion
```json
"promoted_object": {
  "pixel_id": "123456789",
  "custom_event_type": "LEAD"
}
```

#### Example: App Install
```json
"promoted_object": {
  "application_id": "987654321"
}
```

---

### 16. source_campaign_id
- **Type**: `string`
- **Description**: Used for duplication or A/B testing

**Example**:
```json
"source_campaign_id": "2385xxxxxxxx"
```

---

### 17. is_skadnetwork_attribution
- **Type**: `boolean`
- **Description**: iOS 14+ attribution support

**Example**:
```json
"is_skadnetwork_attribution": true
```

---

## Complete Postman Example

### Recommended First API Test (Safe)

```json
{
  "name": "Axgen Test Campaign v24",
  "objective": "OUTCOME_LEADS",
  "status": "PAUSED",
  "special_ad_categories": ["NONE"],
  "buying_type": "AUCTION",
  "campaign_budget_optimization": true,
  "daily_budget": 50000,
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP"
}
```

---

## Expected Response

### Success Response
```json
{
  "id": "120213456789012"
}
```

🎉 **Campaign created successfully (PAUSED)**

---

## Quick Reference

### Minimum Required Body
```json
{
  "name": "Campaign Name",
  "objective": "OUTCOME_LEADS"
}
```

### Common Production Body
```json
{
  "name": "Production Campaign Name",
  "objective": "OUTCOME_LEADS",
  "status": "PAUSED",
  "special_ad_categories": ["NONE"],
  "buying_type": "AUCTION",
  "campaign_budget_optimization": true,
  "daily_budget": 50000,
  "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
  "start_time": "2026-01-10T00:00:00+0530",
  "stop_time": "2026-01-31T23:59:59+0530"
}
```

---

## Best Practices

1. ✅ Always create campaigns in `PAUSED` status initially
2. ✅ Use new objective values (OUTCOME_*) instead of deprecated ones
3. ✅ Convert currency to minor units (multiply by 100)
4. ✅ Set `special_ad_categories` appropriately for compliance
5. ✅ Enable CBO for better budget optimization
6. ✅ Use ISO 8601 format for datetime values
7. ✅ Test with small budgets first

---

---

# GET Campaign Details

## Endpoint Overview

**GET** `https://graph.facebook.com/v24.0/{campaign_id}`

**OR**

**GET** `https://graph.facebook.com/v24.0/act_<AD_ACCOUNT_ID>/campaigns`

### Purpose
Retrieve campaign information and settings

---

## Required Query Parameters (Postman)

| Key | Value | Description |
|-----|-------|-------------|
| `access_token` | SYSTEM_USER_ACCESS_TOKEN | Authentication token |
| `fields` | comma-separated list | Fields to retrieve |

---

## Core Identifiers (Always Available)

| Field | Type | Meaning |
|-------|------|---------|
| `id` | string | Campaign ID |
| `account_id` | string | Ad account ID |
| `name` | string | Campaign name |
| `objective` | enum | Campaign objective |
| `status` | enum | Configured status |
| `effective_status` | enum | Real delivery status |
| `created_time` | datetime | Creation time |
| `updated_time` | datetime | Last update time |
| `start_time` | datetime | Campaign start |
| `stop_time` | datetime | Campaign end |

---

## Status Enum Values

### status
- `ACTIVE`
- `PAUSED`
- `DELETED`
- `ARCHIVED`

### effective_status
- `ACTIVE`
- `PAUSED`
- `IN_PROCESS`
- `WITH_ISSUES`
- `DELETED`
- `ARCHIVED`

---

## Objective Enum Values (v24.0)

| Objective |
|-----------|
| `AWARENESS` |
| `TRAFFIC` |
| `ENGAGEMENT` |
| `LEADS` |
| `APP_PROMOTION` |
| `SALES` |
| `OUTCOME_AWARENESS` |
| `OUTCOME_TRAFFIC` |
| `OUTCOME_ENGAGEMENT` |
| `OUTCOME_LEADS` |
| `OUTCOME_APP_PROMOTION` |
| `OUTCOME_SALES` |

⚠️ **Note**: Legacy objectives are auto-mapped to OUTCOME_* versions

---

## Budget & Bid Control Fields

| Field | Type | Description |
|-------|------|-------------|
| `daily_budget` | string | Daily budget (minor units) |
| `lifetime_budget` | string | Lifetime budget |
| `budget_remaining` | string | Remaining budget |
| `buying_type` | enum | `AUCTION` |
| `bid_strategy` | enum | Bidding logic |

### bid_strategy Values
- `LOWEST_COST_WITHOUT_CAP`
- `LOWEST_COST_WITH_BID_CAP`
- `COST_CAP`
- `LOWEST_COST_WITH_MIN_ROAS`

---

## Campaign Budget Optimization (CBO)

| Field | Type | Meaning |
|-------|------|---------|
| `is_skadnetwork_attribution` | bool | SKAN attribution |
| `smart_promotion_type` | enum | Automated boost |
| `topline_id` | string | Budget group ID |

---

## Special Ad Category (Legal/Compliance)

| Field | Type | Notes |
|-------|------|-------|
| `special_ad_categories` | array | Housing, Credit, Employment |
| `special_ad_category_country` | array | ISO country codes |

### Category Values
- `HOUSING`
- `EMPLOYMENT`
- `CREDIT`
- `ISSUES_ELECTIONS_POLITICS`

---

## Attribution & Delivery

| Field | Type | Description |
|-------|------|-------------|
| `attribution_spec` | array | Conversion attribution |
| `optimization_goal` | string | Delivery optimization |
| `delivery_estimate` | object | Reach estimate |
| `pacing_type` | array | Spend pacing |

---

## A/B Testing & Experiments

| Field | Type | Meaning |
|-------|------|---------|
| `is_experiment` | bool | Part of experiment |
| `adlabels` | array | Labels |
| `can_use_spend_cap` | bool | Spend cap allowed |
| `spend_cap` | string | Max spend |

---

## Promoted Object (VERY IMPORTANT)

The `promoted_object` field may contain:
- `pixel_id` - Meta Pixel ID
- `custom_event_type` - Event type (e.g., LEAD)
- `application_id` - App ID
- `object_store_url` - Store URL
- `product_set_id` - Product catalog ID
- `page_id` - Facebook Page ID

---

## Publishing & Review

| Field | Type |
|-------|------|
| `configured_status` | enum |
| `issues_info` | array |
| `recommendations` | array |
| `source_campaign_id` | string |

---

## Insights (Read-only via Edge)

Not directly returned unless using `/insights` endpoint:

```
GET /v24.0/{campaign_id}/insights
```

---

## Full "Everything" Field String (Postman Ready)

Copy this into the `fields` parameter to get all available data:

```
id,account_id,name,objective,status,effective_status,configured_status,buying_type,bid_strategy,daily_budget,lifetime_budget,budget_remaining,spend_cap,created_time,updated_time,start_time,stop_time,special_ad_categories,special_ad_category_country,promoted_object,pacing_type,attribution_spec,is_experiment,adlabels,issues_info,recommendations,source_campaign_id,topline_id,can_use_spend_cap,smart_promotion_type
```

---

## Sample Postman GET Requests

### Get Single Campaign
```
GET https://graph.facebook.com/v24.0/1209XXXXXXXX?fields=id,name,objective,status,daily_budget,lifetime_budget,promoted_object&access_token=EAAB...
```

### Get All Campaigns for Ad Account
```
GET https://graph.facebook.com/v24.0/act_123456789/campaigns?fields=id,name,objective,status,effective_status,daily_budget&access_token=EAAB...
```

### Get Campaign with Full Details
```
GET https://graph.facebook.com/v24.0/1209XXXXXXXX?fields=id,account_id,name,objective,status,effective_status,configured_status,buying_type,bid_strategy,daily_budget,lifetime_budget,budget_remaining,spend_cap,created_time,updated_time,start_time,stop_time,special_ad_categories,promoted_object&access_token=EAAB...
```

---

## API Version
This documentation is for **Meta Marketing API v24.0**