# Meta Ads API - Complete Technical Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Understanding the Meta Ads API Ecosystem](#understanding-the-meta-ads-api-ecosystem)
3. [Architecture Overview](#architecture-overview)
4. [Core APIs](#core-apis)
5. [Supporting APIs](#supporting-apis)
6. [Tracking and Analytics APIs](#tracking-and-analytics-apis)
7. [Advanced Features](#advanced-features)
8. [API Reference Summary](#api-reference-summary)

---

## Introduction

### What is "Meta Ads API"?

The term "Meta Ads API" does not refer to a single API endpoint, but rather a comprehensive ecosystem of interconnected APIs provided by Meta Platforms. These APIs work together to provide complete advertising functionality across Facebook, Instagram, Messenger, and Audience Network.

All Meta Ads-related APIs are accessed through the **Meta Graph API**, which serves as the foundational layer for all interactions with Meta's platform. The various advertising capabilities are organized into logical modules, each serving specific purposes within the advertising workflow.

### Key Characteristics

- **Unified Access Point**: All APIs use the Graph API as their foundation
- **RESTful Architecture**: Standard HTTP methods (GET, POST, DELETE, UPDATE)
- **Versioned**: APIs use version-specific endpoints (e.g., v24.0, v25.0)
- **OAuth 2.0 Authentication**: Secure token-based authentication
- **Rate Limited**: API calls are subject to rate limiting based on ad account and app

---

## Understanding the Meta Ads API Ecosystem

### Logical Organization

The Meta Ads API ecosystem is organized into several functional categories:

1. **Campaign Management**: Creating and managing advertising campaigns
2. **Business Administration**: Managing business assets and permissions
3. **Audience Management**: Building and targeting audiences
4. **Analytics and Reporting**: Accessing performance metrics
5. **Creative Management**: Uploading and managing ad creatives
6. **Conversion Tracking**: Measuring and attributing conversions
7. **Commerce Integration**: Managing product catalogs for dynamic ads
8. **Lead Generation**: Capturing and retrieving leads
9. **Automation and Webhooks**: Real-time event handling

---

## Architecture Overview

### High-Level Structure

```
Meta Graph API (Foundation)
│
├── Marketing API (Core Ads Management)
│   ├── Campaign Management
│   ├── Ad Set Management
│   ├── Ad Management
│   ├── Creative Management
│   ├── Targeting and Audiences
│   ├── Insights and Reporting
│   ├── Budget and Bidding
│   └── Experiments and Testing
│
├── Business Management API
│   ├── Business Manager
│   ├── Ad Account Management
│   ├── Page Management
│   ├── Instagram Account Management
│   └── Partner and Permission Management
│
├── Commerce and Catalog API
│   ├── Product Catalog Management
│   ├── Product Feed Management
│   └── Dynamic Ad Integration
│
├── Lead Ads API
│   ├── Lead Form Creation
│   └── Lead Retrieval
│
├── Messaging and Engagement APIs
│   ├── Page Messaging
│   ├── WhatsApp Business API
│   └── Instagram Messaging
│
├── Tracking and Conversion APIs
│   ├── Meta Pixel API (Browser-based)
│   └── Conversions API (Server-to-server)
│
└── Creative and Media APIs
    ├── Image Upload
    ├── Video Upload
    └── Creative Preview
```

---

## Core APIs

### 1. Meta Marketing API

**Purpose**: The primary API for creating, managing, and optimizing advertising campaigns across Meta's platforms.

#### Main Objects and Hierarchy

The Marketing API operates on a hierarchical structure:

```
Ad Account
└── Campaign
    └── Ad Set
        └── Ad
            └── Ad Creative
```

#### Object Descriptions

| Object | Purpose | Key Attributes |
|--------|---------|----------------|
| **Campaign** | Top-level organizational container | Objective, status, lifetime budget |
| **Ad Set** | Targeting and budget allocation | Budget, schedule, targeting, placements |
| **Ad** | Individual delivery unit | Status, creative, tracking |
| **Ad Creative** | Content and design | Images, video, text, call-to-action |
| **Ad Account** | Billing and administrative container | Spending limits, payment methods, permissions |
| **Insights** | Performance data and metrics | Impressions, clicks, conversions, spend |

#### Common Endpoints

**Campaign Management**
```http
POST   /v24.0/act_{ad_account_id}/campaigns
GET    /v24.0/{campaign_id}
POST   /v24.0/{campaign_id}
DELETE /v24.0/{campaign_id}
```

**Ad Set Management**
```http
POST   /v24.0/act_{ad_account_id}/adsets
GET    /v24.0/{adset_id}
POST   /v24.0/{adset_id}
DELETE /v24.0/{adset_id}
```

**Ad Management**
```http
POST   /v24.0/act_{ad_account_id}/ads
GET    /v24.0/{ad_id}
POST   /v24.0/{ad_id}
DELETE /v24.0/{ad_id}
```

**Ad Creative Management**
```http
POST   /v24.0/act_{ad_account_id}/adcreatives
GET    /v24.0/{creative_id}
```

**Insights and Reporting**
```http
GET    /v24.0/act_{ad_account_id}/insights
GET    /v24.0/{campaign_id}/insights
GET    /v24.0/{adset_id}/insights
GET    /v24.0/{ad_id}/insights
```

#### Campaign Objectives

The Marketing API supports various campaign objectives:

- **Awareness**: Brand awareness, Reach
- **Consideration**: Traffic, Engagement, App installs, Video views, Lead generation, Messages
- **Conversion**: Conversions, Catalog sales, Store traffic

#### Example: Creating a Campaign

```http
POST /v24.0/act_{ad_account_id}/campaigns
Content-Type: application/json

{
  "name": "Summer Sale Campaign",
  "objective": "OUTCOME_SALES",
  "status": "PAUSED",
  "special_ad_categories": [],
  "access_token": "{access_token}"
}
```

---

### 2. Meta Graph API

**Purpose**: The foundational API that underlies all Meta platform interactions.

#### Core Functions

**Authentication**
- OAuth 2.0 flow
- Access token management
- Permission scoping

**Object Traversal**
- Node-based data structure
- Edge relationships
- Field selection

**Versioning**
- Time-based versioning (quarterly updates)
- Backward compatibility windows
- Version-specific features

#### Basic Endpoints

```http
GET /v24.0/me
GET /v24.0/me/accounts
GET /v24.0/{user_id}
GET /v24.0/{page_id}
GET /v24.0/act_{ad_account_id}
```

#### Field Selection

The Graph API uses field selection to optimize responses:

```http
GET /v24.0/act_{ad_account_id}?fields=name,account_status,currency,timezone_name
```

---

### 3. Business Management API

**Purpose**: Manage business assets, permissions, and organizational structure.

#### Key Capabilities

**Business Portfolio Management**
- Create and manage Business Manager accounts
- Organize multiple ad accounts
- Centralize billing and permissions

**Ad Account Management**
- Create ad accounts
- Transfer ad account ownership
- Manage ad account permissions

**Asset Management**
- Pages
- Instagram accounts
- Pixels
- Catalogs
- Custom audiences

**User and Partner Management**
- Add/remove business users
- Manage partner relationships
- Set role-based permissions
- System users for automation

#### Key Endpoints

**Business Operations**
```http
GET  /v24.0/{business_id}
GET  /v24.0/{business_id}/owned_ad_accounts
POST /v24.0/{business_id}/owned_ad_accounts
GET  /v24.0/{business_id}/owned_pages
POST /v24.0/{business_id}/adaccount
```

**Permission Management**
```http
GET  /v24.0/{business_id}/business_users
POST /v24.0/{business_id}/business_users
POST /v24.0/{ad_account_id}/assigned_users
```

**Partner Management**
```http
GET  /v24.0/{business_id}/partners
POST /v24.0/{business_id}/partners
DELETE /v24.0/{business_id}/partners
```

#### System Users

System users are non-login accounts for automation:

```http
POST /v24.0/{business_id}/system_users
{
  "name": "API Automation User",
  "role": "ADMIN"
}
```

---

## Supporting APIs

### 4. Targeting and Audience APIs

**Purpose**: Build, manage, and optimize audience targeting.

#### Audience Types

**Custom Audiences**
- Customer lists
- Website traffic (Pixel-based)
- App activity
- Engagement audiences

**Lookalike Audiences**
- Based on custom audiences
- Geographic expansion
- Similarity percentage

**Saved Audiences**
- Demographic targeting
- Interest-based targeting
- Behavior targeting
- Location targeting

#### Targeting Search API

Find targeting options:

```http
GET /v24.0/search?type=adinterest&q=fitness
GET /v24.0/search?type=adeducationschool&q=harvard
GET /v24.0/search?type=adlocale
```

#### Custom Audience Endpoints

```http
POST /v24.0/act_{ad_account_id}/customaudiences
{
  "name": "Website Visitors - 30 Days",
  "subtype": "WEBSITE",
  "retention_days": 30,
  "rule": {
    "url": {"i_contains": "example.com"}
  }
}
```

#### Lookalike Audience Creation

```http
POST /v24.0/act_{ad_account_id}/customaudiences
{
  "name": "Lookalike - High Value Customers",
  "subtype": "LOOKALIKE",
  "origin_audience_id": "{custom_audience_id}",
  "lookalike_spec": {
    "type": "similarity",
    "ratio": 0.01,
    "country": "US"
  }
}
```

---

### 5. Insights and Reporting API

**Purpose**: Access detailed performance metrics and analytics.

#### Available Metrics

**Delivery Metrics**
- Impressions
- Reach
- Frequency

**Engagement Metrics**
- Clicks (all)
- Link clicks
- Post engagement
- Video views

**Conversion Metrics**
- Conversions
- Conversion value
- Cost per result
- Return on ad spend (ROAS)

**Cost Metrics**
- Spend
- CPM (Cost per thousand impressions)
- CPC (Cost per click)
- CPA (Cost per action)

#### Time Breakdown Options

- Daily
- Weekly
- Monthly
- Lifetime

#### Attribution Windows

- 1-day click
- 7-day click
- 1-day view
- 7-day view
- 28-day click

#### Example: Insights Query

```http
GET /v24.0/act_{ad_account_id}/insights
  ?fields=campaign_name,impressions,clicks,spend,ctr,cpc,cpp
  &level=campaign
  &time_range={'since':'2024-01-01','until':'2024-01-31'}
  &breakdowns=age,gender
  &time_increment=1
```

#### Async Reporting

For large data requests:

```http
POST /v24.0/act_{ad_account_id}/insights
{
  "level": "ad",
  "fields": ["impressions", "clicks", "spend"],
  "time_range": {"since": "2024-01-01", "until": "2024-12-31"}
}

Response:
{
  "report_run_id": "{report_run_id}"
}

GET /v24.0/{report_run_id}
```

---

### 6. Creative and Media API

**Purpose**: Upload, manage, and preview ad creatives.

#### Image Upload

```http
POST /v24.0/act_{ad_account_id}/adimages
{
  "bytes": "{base64_encoded_image}",
  "name": "summer_sale_banner.jpg"
}
```

#### Video Upload

```http
POST /v24.0/act_{ad_account_id}/advideos
{
  "file_url": "https://example.com/video.mp4"
}
```

#### Creative Preview

Generate preview URLs:

```http
GET /v24.0/{ad_id}/previews
  ?ad_format=DESKTOP_FEED_STANDARD
```

#### Dynamic Creative

Automatically test multiple creative elements:

```http
POST /v24.0/act_{ad_account_id}/adcreatives
{
  "name": "Dynamic Creative Test",
  "object_story_spec": {
    "page_id": "{page_id}",
    "instagram_actor_id": "{instagram_account_id}"
  },
  "asset_feed_spec": {
    "images": [
      {"hash": "{image_hash_1}"},
      {"hash": "{image_hash_2}"},
      {"hash": "{image_hash_3}"}
    ],
    "bodies": [
      {"text": "Shop now and save"},
      {"text": "Limited time offer"}
    ],
    "titles": [
      {"text": "Summer Sale"},
      {"text": "End of Season Clearance"}
    ],
    "call_to_action_types": ["SHOP_NOW", "LEARN_MORE"]
  }
}
```

---

### 7. Commerce and Catalog API

**Purpose**: Manage product catalogs for dynamic ads and commerce experiences.

#### Use Cases

- E-commerce retargeting
- Travel and hotel ads
- Real estate listings
- Automotive inventory

#### Catalog Management

```http
POST /v24.0/{business_id}/owned_product_catalogs
{
  "name": "Main Product Catalog"
}
```

#### Product Feed

```http
POST /v24.0/{catalog_id}/product_feeds
{
  "name": "Daily Product Feed",
  "schedule": {
    "interval": "DAILY",
    "hour": 2
  },
  "feed_url": "https://example.com/products.xml"
}
```

#### Manual Product Upload

```http
POST /v24.0/{catalog_id}/products
{
  "retailer_id": "SKU-12345",
  "name": "Blue Summer Dress",
  "description": "Lightweight cotton dress",
  "price": 4999,
  "currency": "USD",
  "availability": "in stock",
  "condition": "new",
  "brand": "Fashion Brand",
  "url": "https://example.com/products/blue-summer-dress",
  "image_url": "https://example.com/images/dress.jpg"
}
```

---

### 8. Lead Ads API

**Purpose**: Create lead generation forms and retrieve submitted leads.

#### Lead Form Creation

```http
POST /v24.0/{page_id}/leadgen_forms
{
  "name": "Contact Us Form",
  "questions": [
    {
      "type": "FULL_NAME"
    },
    {
      "type": "EMAIL"
    },
    {
      "type": "PHONE"
    }
  ],
  "privacy_policy_url": "https://example.com/privacy"
}
```

#### Lead Retrieval

```http
GET /v24.0/{form_id}/leads
  ?fields=field_data,created_time
```

#### Webhook Integration

Subscribe to real-time lead notifications:

```http
POST /v24.0/{page_id}/subscribed_apps
{
  "subscribed_fields": ["leadgen"]
}
```

---

## Tracking and Analytics APIs

### 9. Meta Pixel API

**Purpose**: Browser-based event tracking for website conversions.

#### Standard Events

- PageView
- ViewContent
- Search
- AddToCart
- InitiateCheckout
- AddPaymentInfo
- Purchase
- Lead
- CompleteRegistration

#### Pixel Implementation

JavaScript integration:

```javascript
fbq('init', '{pixel_id}');
fbq('track', 'PageView');
fbq('track', 'Purchase', {
  value: 99.00,
  currency: 'USD'
});
```

#### Server-Side Pixel Events

```http
POST /v24.0/{pixel_id}/events
{
  "data": [
    {
      "event_name": "Purchase",
      "event_time": 1640000000,
      "action_source": "website",
      "user_data": {
        "em": "{hashed_email}",
        "ph": "{hashed_phone}"
      },
      "custom_data": {
        "value": 99.00,
        "currency": "USD"
      }
    }
  ]
}
```

---

### 10. Conversions API (CAPI)

**Purpose**: Server-to-server conversion tracking for improved accuracy and privacy compliance.

#### Benefits

- iOS 14.5+ privacy compliance
- First-party data integration
- Reduced ad blocker impact
- Offline conversion tracking
- CRM integration

#### Event Sources

- Web
- Mobile app
- Offline (stores, call centers)
- CRM systems
- Third-party platforms

#### Implementation

```http
POST /v24.0/{pixel_id}/events
{
  "data": [
    {
      "event_name": "Purchase",
      "event_time": 1640000000,
      "action_source": "website",
      "event_source_url": "https://example.com/checkout",
      "user_data": {
        "em": "{sha256_hashed_email}",
        "ph": "{sha256_hashed_phone}",
        "client_ip_address": "{ip_address}",
        "client_user_agent": "{user_agent}",
        "fbc": "{facebook_click_id}",
        "fbp": "{facebook_browser_id}"
      },
      "custom_data": {
        "value": 142.50,
        "currency": "USD",
        "content_ids": ["product_123", "product_456"],
        "content_type": "product",
        "num_items": 2
      }
    }
  ],
  "access_token": "{access_token}"
}
```

#### Offline Conversions

```http
POST /v24.0/{offline_event_set_id}/events
{
  "data": [
    {
      "event_name": "Purchase",
      "event_time": 1640000000,
      "match_keys": {
        "email": "{email}",
        "phone": "{phone}"
      },
      "custom_data": {
        "value": 250.00,
        "currency": "USD"
      }
    }
  ]
}
```

---

## Advanced Features

### 11. Experiments and A/B Testing API

**Purpose**: Create and manage split tests for campaigns, ad sets, or creatives.

#### Test Types

- Creative testing
- Audience testing
- Placement testing
- Delivery optimization testing

#### Creating an Experiment

```http
POST /v24.0/act_{ad_account_id}/experiments
{
  "name": "Creative Test - Summer Campaign",
  "description": "Testing 3 different ad creatives",
  "type": "SPLIT_TEST",
  "cells": [
    {
      "name": "Control",
      "adsets": ["{adset_id_1}"],
      "weight": 33
    },
    {
      "name": "Variant A",
      "adsets": ["{adset_id_2}"],
      "weight": 33
    },
    {
      "name": "Variant B",
      "adsets": ["{adset_id_3}"],
      "weight": 34
    }
  ]
}
```

#### Experiment Results

```http
GET /v24.0/{experiment_id}/results
  ?fields=cells,start_time,end_time,winner
```

---

### 12. Reach and Frequency Prediction API

**Purpose**: Forecast campaign performance before launching.

#### Capabilities

- Reach estimation
- Frequency prediction
- Cost forecasting
- Optimal budget allocation

#### Creating a Prediction

```http
POST /v24.0/act_{ad_account_id}/reachestimate
{
  "targeting_spec": {
    "geo_locations": {
      "countries": ["US"]
    },
    "age_min": 18,
    "age_max": 65
  },
  "objective": "REACH",
  "budget": 10000,
  "currency": "USD"
}
```

---

### 13. Policy, Review, and Compliance APIs

**Purpose**: Understand ad review status and policy violations.

#### Ad Review Status

```http
GET /v24.0/{ad_id}
  ?fields=review_feedback,configured_status,effective_status
```

#### Common Review Feedback Fields

- `review_feedback`: Detailed rejection reasons
- `configured_status`: User-set status
- `effective_status`: Actual delivery status
- `issues_info`: Specific policy violations

---

### 14. WhatsApp and Messaging Ads APIs

**Purpose**: Create click-to-message ads for WhatsApp, Messenger, and Instagram.

#### Supported Platforms

- WhatsApp Business
- Facebook Messenger
- Instagram Direct

#### Creating a Click-to-Message Ad

```http
POST /v24.0/act_{ad_account_id}/ads
{
  "name": "WhatsApp Lead Gen Ad",
  "adset_id": "{adset_id}",
  "creative": {
    "object_story_spec": {
      "page_id": "{page_id}",
      "link_data": {
        "message": "Chat with us on WhatsApp",
        "link": "https://wa.me/{phone_number}",
        "call_to_action": {
          "type": "MESSAGE_PAGE"
        }
      }
    }
  }
}
```

---

### 15. Webhooks (Real-Time Updates)

**Purpose**: Receive real-time notifications for important events.

#### Subscription Topics

- Ad account updates
- Campaign status changes
- Ad approval/rejection
- Spend limit warnings
- Lead generation
- Page messaging

#### Setting Up Webhooks

```http
POST /v24.0/{app_id}/subscriptions
{
  "object": "adaccount",
  "callback_url": "https://example.com/webhooks",
  "fields": ["campaign_status", "adset_status", "ad_status"],
  "verify_token": "{your_verify_token}"
}
```

#### Webhook Payload Example

```json
{
  "entry": [
    {
      "id": "act_{ad_account_id}",
      "time": 1640000000,
      "changes": [
        {
          "field": "campaign_status",
          "value": {
            "campaign_id": "{campaign_id}",
            "status": "ACTIVE"
          }
        }
      ]
    }
  ]
}
```

---

## API Reference Summary

### Complete API Inventory

| API | Primary Purpose | Key Objects | Common Use Cases |
|-----|-----------------|-------------|------------------|
| **Marketing API** | Ad campaign management | Campaign, AdSet, Ad, Creative | Creating and optimizing ads |
| **Graph API** | Foundation layer | User, Page, AdAccount | Authentication, data access |
| **Business Management API** | Business operations | Business, AdAccount, Page | Multi-account management |
| **Targeting API** | Audience building | CustomAudience, SavedAudience | Targeting optimization |
| **Insights API** | Performance analytics | Insights, Report | Campaign reporting |
| **Creative API** | Asset management | AdImage, AdVideo | Creative uploads |
| **Catalog API** | Product management | Catalog, Product, ProductFeed | Dynamic ads |
| **Lead Ads API** | Lead generation | LeadgenForm, Lead | Form creation, lead retrieval |
| **Pixel API** | Browser tracking | Pixel, Event | Website conversion tracking |
| **Conversions API** | Server tracking | Event, UserData | Privacy-safe tracking |
| **Experiments API** | A/B testing | Experiment, Cell | Split testing |
| **Reach Prediction API** | Forecasting | ReachEstimate | Budget planning |
| **Policy API** | Compliance | ReviewFeedback, IssuesInfo | Ad review status |
| **Messaging API** | Chat ads | Message, Conversation | Click-to-message campaigns |
| **Webhooks** | Real-time updates | Subscription | Automation and monitoring |

### Authentication Requirements

All API calls require a valid access token with appropriate permissions:

**Required Permissions** (varies by API):
- `ads_management`
- `ads_read`
- `business_management`
- `pages_read_engagement`
- `pages_manage_ads`
- `leads_retrieval`

**Token Types**:
- User Access Token: Short-lived (hours)
- Page Access Token: Long-lived
- System User Token: Non-expiring (for automation)

### Rate Limits

Rate limits are applied at multiple levels:

**Ad Account Level**
- Based on account spend
- Typically 200-400 calls per hour
- Higher limits for larger spenders

**App Level**
- Application-wide limits
- Shared across all users

**API-Specific Limits**
- Insights API: Special async handling
- Bulk operations: Batch API support

### Best Practices

**1. Versioning**
- Always specify API version
- Test before version upgrades
- Monitor deprecation notices

**2. Error Handling**
- Implement exponential backoff
- Handle rate limiting gracefully
- Log errors with context

**3. Performance**
- Use batch requests when possible
- Request only needed fields
- Cache responses appropriately

**4. Security**
- Never expose access tokens
- Use server-side API calls
- Implement token refresh logic
- Follow HTTPS best practices

**5. Data Privacy**
- Hash PII before sending
- Comply with data protection laws
- Implement proper consent mechanisms
- Use Conversions API for sensitive data

---

## Conclusion

The Meta Ads API ecosystem provides comprehensive tools for programmatic advertising across Meta's family of platforms. Understanding the relationship between these APIs and their specific purposes is essential for building robust advertising automation systems.

For the most up-to-date information, always refer to the official Meta for Developers documentation at https://developers.facebook.com/docs/marketing-apis