# META Marketing Agent Architecture
## Complete Technical Documentation

**Version:** 1.0  
**Last Updated:** January 2026  
**API Version:** Meta Marketing API v24.0  
**Author:** System Architecture Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Architecture Design](#3-architecture-design)
4. [Agent Specifications](#4-agent-specifications)
5. [Workflow Orchestration](#5-workflow-orchestration)
6. [API Integration](#6-api-integration)
7. [Data Models](#7-data-models)
8. [Error Handling](#8-error-handling)
9. [Performance & Scalability](#9-performance--scalability)
10. [Security & Authentication](#10-security--authentication)
11. [Monitoring & Logging](#11-monitoring--logging)
12. [Deployment Guide](#12-deployment-guide)

---

## 1. Executive Summary

### 1.1 Purpose

This document defines the architecture for an automated META Marketing Agent system that integrates with Meta's Marketing API to manage end-to-end advertising operations on Facebook, Instagram, Messenger, WhatsApp, and Audience Network platforms.

### 1.2 Key Objectives

- **Automation**: Eliminate manual ad creation and management processes
- **Efficiency**: Minimize agent count while maximizing functionality
- **Scalability**: Support high-volume campaign operations
- **Reliability**: Ensure robust error handling and recovery
- **Integration**: Seamless connection with Ambient Agent orchestrator

### 1.3 Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Minimal Complexity** | 4 specialized agents (not 10+) |
| **Single Responsibility** | Each agent has one clear purpose |
| **Loose Coupling** | Agents communicate via orchestrator |
| **High Cohesion** | Related operations grouped together |
| **Fail-Safe** | Comprehensive error handling & rollback |

---

## 2. System Overview

### 2.1 High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      EXTERNAL SYSTEMS                         │
├──────────────────────────────────────────────────────────────┤
│  • Ambient Agent (Request Initiator)                         │
│  • Meta Marketing API (v24.0)                                │
│  • Asset Storage (Images/Videos)                             │
│  • Analytics Dashboard                                       │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              META MARKETING AGENT SYSTEM                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │         ORCHESTRATOR AGENT (Central Hub)           │     │
│  │  • Request routing & validation                    │     │
│  │  • Workflow coordination                           │     │
│  │  • Dependency management                           │     │
│  │  • Response aggregation                            │     │
│  └───┬──────────┬──────────┬──────────┬───────────────┘     │
│      │          │          │          │                      │
│      ▼          ▼          ▼          ▼                      │
│  ┌──────┐  ┌────────┐  ┌───────┐  ┌──────────┐            │
│  │ASSET │  │CAMPAIGN│  │  AD   │  │ INSIGHTS │            │
│  │AGENT │  │ AGENT  │  │CREATION│  │  AGENT   │            │
│  └──────┘  └────────┘  └───────┘  └──────────┘            │
│                                                               │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    DATA & STORAGE LAYER                       │
├──────────────────────────────────────────────────────────────┤
│  • Campaign Database                                         │
│  • Asset Cache                                               │
│  • Performance Metrics                                       │
│  • Audit Logs                                                │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Component Interaction Flow

```
Request Flow:
Ambient Agent → Orchestrator → Specialized Agent → Meta API

Response Flow:
Meta API → Specialized Agent → Orchestrator → Ambient Agent

Monitoring Flow:
All Agents → Logger → Monitoring Dashboard
```

### 2.3 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Runtime** | Python 3.10+ | Agent execution |
| **API Client** | `requests` / `httpx` | HTTP communication |
| **Async Processing** | `asyncio` | Parallel operations |
| **Data Validation** | `pydantic` | Schema validation |
| **Caching** | `redis` | Performance optimization |
| **Logging** | `structlog` | Structured logging |
| **Monitoring** | `prometheus` | Metrics collection |

---

## 3. Architecture Design

### 3.1 Agent Ecosystem

The system employs a **4-agent architecture** optimized for minimal complexity and maximum efficiency:

#### Agent Distribution

```
┌─────────────────────────────────────────────────────────┐
│  ORCHESTRATOR AGENT (1)                                 │
│  └─ Request routing, validation, workflow management    │
└─────────────────────────────────────────────────────────┘
           │
           ├─────────────────┬─────────────┬──────────────┐
           ▼                 ▼             ▼              ▼
┌──────────────┐  ┌─────────────────┐  ┌────────┐  ┌──────────┐
│ ASSET AGENT  │  │ CAMPAIGN AGENT  │  │AD AGENT│  │ INSIGHTS │
│              │  │                 │  │        │  │  AGENT   │
│ • Images     │  │ • Campaigns     │  │• Creats│  │• Reports │
│ • Videos     │  │ • Ad Sets       │  │• Ads   │  │• Metrics │
└──────────────┘  └─────────────────┘  └────────┘  └──────────┘
```

### 3.2 Design Rationale

#### Why 4 Agents (Not More)?

**Asset Agent (Separate)**
- Upload operations are I/O intensive
- Can run in parallel with other operations
- Asset reuse across multiple campaigns
- Independent failure domain

**Campaign Agent (Combined: Campaigns + Ad Sets)**
- Tightly coupled in Meta's hierarchy
- Always created together
- Share 90% of configuration logic
- Reduces inter-agent communication

**Ad Creation Agent (Combined: Creatives + Ads)**
- Creative is always needed for an ad
- Created in sequence (creative → ad)
- Simplifies dependency management
- Reduces API calls

**Insights Agent (Separate)**
- Read-only operations
- Different access patterns
- Can operate independently
- No dependencies on creation agents

#### Why Not 3 Agents?

Merging Asset + Ad Creation would create:
- ❌ Upload bottlenecks
- ❌ Tight coupling between unrelated operations
- ❌ Reduced parallelization opportunities
- ❌ Complex error handling

#### Why Not 5+ Agents?

Additional agents would introduce:
- ❌ Communication overhead
- ❌ Complex orchestration
- ❌ Harder debugging
- ❌ Increased latency

### 3.3 Communication Patterns

#### Request-Response Pattern

```python
# Synchronous request-response
request = OrchestatorRequest(action="create_campaign", data=...)
response = orchestrator.execute(request)

# Asynchronous with callback
await orchestrator.execute_async(request, callback=handle_response)
```

#### Event-Driven Pattern

```python
# Event emission
event_bus.emit("campaign_created", campaign_id="123")

# Event subscription
@event_bus.on("campaign_created")
def on_campaign_created(campaign_id):
    insights_agent.start_tracking(campaign_id)
```

---

## 4. Agent Specifications

### 4.1 Orchestrator Agent

**Role:** Central coordination and workflow management

#### Responsibilities

| Category | Functions |
|----------|-----------|
| **Validation** | Credential verification, parameter validation, schema checking |
| **Routing** | Request classification, agent selection, load balancing |
| **Coordination** | Workflow execution, dependency management, state tracking |
| **Aggregation** | Response collection, data merging, result formatting |
| **Error Handling** | Exception catching, rollback orchestration, retry logic |

#### Core Operations

```python
class OrchestratorAgent:
    """
    Central orchestration agent for META marketing operations.
    """
    
    def __init__(self):
        self.asset_agent = AssetAgent()
        self.campaign_agent = CampaignAgent()
        self.ad_creation_agent = AdCreationAgent()
        self.insights_agent = InsightsAgent()
        self.validator = RequestValidator()
        self.logger = StructuredLogger("orchestrator")
    
    async def execute(self, request: OrchestratorRequest) -> Response:
        """
        Main execution method for handling requests.
        
        Args:
            request: Validated orchestrator request
            
        Returns:
            Consolidated response from executed workflow
            
        Raises:
            ValidationError: Invalid request parameters
            ExecutionError: Workflow execution failure
        """
        # Validate request
        self.validator.validate(request)
        
        # Route to appropriate workflow
        workflow = self._get_workflow(request.action)
        
        # Execute with error handling
        try:
            result = await workflow.execute(request.data)
            return Response(status="success", data=result)
        except Exception as e:
            await self._handle_error(e, workflow)
            raise
    
    def _get_workflow(self, action: str) -> Workflow:
        """Select workflow based on action type."""
        workflows = {
            "create_full_campaign": FullCampaignWorkflow,
            "create_campaign": CampaignOnlyWorkflow,
            "update_campaign": UpdateCampaignWorkflow,
            "get_insights": InsightsWorkflow,
            "optimize_campaign": OptimizationWorkflow,
        }
        return workflows[action](self)
    
    async def _handle_error(self, error: Exception, workflow: Workflow):
        """Centralized error handling with rollback."""
        self.logger.error("workflow_failed", error=str(error))
        await workflow.rollback()
```

#### Workflow Definitions

**Full Campaign Creation Workflow**

```python
class FullCampaignWorkflow:
    """
    Complete campaign creation: assets → campaign → adsets → ads
    """
    
    async def execute(self, data: dict) -> dict:
        results = {
            "assets": [],
            "campaign": None,
            "adsets": [],
            "ads": []
        }
        
        try:
            # Step 1: Upload assets (parallel)
            if data.get("assets"):
                results["assets"] = await self._upload_assets(data["assets"])
            
            # Step 2: Create campaign
            results["campaign"] = await self._create_campaign(data["campaign"])
            
            # Step 3: Create ad sets (parallel)
            results["adsets"] = await self._create_adsets(
                data["adsets"],
                results["campaign"]["id"]
            )
            
            # Step 4: Create ads (parallel)
            results["ads"] = await self._create_ads(
                data["ads"],
                results["adsets"],
                results["assets"]
            )
            
            return results
            
        except Exception as e:
            await self.rollback(results)
            raise
    
    async def _upload_assets(self, assets: list) -> list:
        """Upload all assets in parallel."""
        tasks = [
            orchestrator.asset_agent.upload(asset)
            for asset in assets
        ]
        return await asyncio.gather(*tasks)
    
    async def _create_adsets(self, adsets: list, campaign_id: str) -> list:
        """Create ad sets in parallel."""
        tasks = [
            orchestrator.campaign_agent.create_adset({
                **adset,
                "campaign_id": campaign_id
            })
            for adset in adsets
        ]
        return await asyncio.gather(*tasks)
    
    async def rollback(self, results: dict):
        """Rollback created resources on failure."""
        # Delete in reverse order
        for ad in results.get("ads", []):
            await orchestrator.ad_creation_agent.delete_ad(ad["id"])
        
        for adset in results.get("adsets", []):
            await orchestrator.campaign_agent.delete_adset(adset["id"])
        
        if results.get("campaign"):
            await orchestrator.campaign_agent.delete_campaign(
                results["campaign"]["id"]
            )
```

---

### 4.2 Asset Agent

**Role:** Upload and manage advertising assets (images, videos)

#### Responsibilities

- Upload images to ad account
- Upload videos to ad account
- Validate asset specifications
- Manage asset cache
- Return asset identifiers

#### API Endpoints

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Upload Image | POST | `/act_{id}/adimages` |
| Upload Video | POST | `/act_{id}/advideos` |
| Get Image | GET | `/{image_hash}` |
| Get Video | GET | `/{video_id}` |

#### Implementation

```python
class AssetAgent:
    """
    Manages upload and validation of advertising assets.
    """
    
    def __init__(self, api_client: MetaAPIClient):
        self.api = api_client
        self.cache = AssetCache()
        self.validator = AssetValidator()
        self.logger = StructuredLogger("asset_agent")
    
    async def upload_image(
        self,
        ad_account_id: str,
        image_data: bytes | str,
        filename: str
    ) -> ImageAsset:
        """
        Upload image to Meta ad account.
        
        Args:
            ad_account_id: Ad account ID (act_xxxxx)
            image_data: Image bytes or URL
            filename: Image filename
            
        Returns:
            ImageAsset with hash and metadata
            
        Raises:
            AssetValidationError: Invalid image specs
            AssetUploadError: Upload failed
        """
        # Check cache first
        cache_key = f"{ad_account_id}:{filename}"
        if cached := self.cache.get(cache_key):
            self.logger.info("cache_hit", filename=filename)
            return cached
        
        # Validate specifications
        self.validator.validate_image(image_data)
        
        # Prepare upload
        endpoint = f"/act_{ad_account_id}/adimages"
        files = {"filename": (filename, image_data)}
        
        try:
            response = await self.api.post(endpoint, files=files)
            
            asset = ImageAsset(
                hash=response["images"][filename]["hash"],
                filename=filename,
                url=response["images"][filename].get("url")
            )
            
            # Cache result
            self.cache.set(cache_key, asset, ttl=3600)
            
            self.logger.info(
                "image_uploaded",
                hash=asset.hash,
                filename=filename
            )
            
            return asset
            
        except APIError as e:
            self.logger.error("upload_failed", error=str(e))
            raise AssetUploadError(f"Failed to upload {filename}") from e
    
    async def upload_video(
        self,
        ad_account_id: str,
        video_url: str,
        title: str,
        description: str = ""
    ) -> VideoAsset:
        """
        Upload video to Meta ad account.
        
        Args:
            ad_account_id: Ad account ID
            video_url: Accessible video URL
            title: Video title
            description: Video description
            
        Returns:
            VideoAsset with ID and metadata
        """
        # Validate video
        self.validator.validate_video_url(video_url)
        
        endpoint = f"/act_{ad_account_id}/advideos"
        data = {
            "file_url": video_url,
            "title": title,
            "description": description
        }
        
        try:
            response = await self.api.post(endpoint, json=data)
            
            asset = VideoAsset(
                id=response["id"],
                title=title,
                url=video_url
            )
            
            self.logger.info("video_uploaded", video_id=asset.id)
            return asset
            
        except APIError as e:
            raise AssetUploadError(f"Failed to upload video") from e
    
    async def batch_upload(
        self,
        ad_account_id: str,
        assets: list[dict]
    ) -> list[Asset]:
        """
        Upload multiple assets in parallel.
        
        Args:
            ad_account_id: Ad account ID
            assets: List of asset definitions
            
        Returns:
            List of uploaded assets
        """
        tasks = []
        
        for asset in assets:
            if asset["type"] == "image":
                task = self.upload_image(
                    ad_account_id,
                    asset["data"],
                    asset["filename"]
                )
            elif asset["type"] == "video":
                task = self.upload_video(
                    ad_account_id,
                    asset["url"],
                    asset.get("title", asset["filename"])
                )
            tasks.append(task)
        
        return await asyncio.gather(*tasks)
```

#### Asset Validation

```python
class AssetValidator:
    """Validates asset specifications against Meta requirements."""
    
    IMAGE_SPECS = {
        "feed": {
            "min_width": 600,
            "min_height": 600,
            "aspect_ratios": [(1, 1), (1.91, 1), (4, 5)]
        },
        "story": {
            "min_width": 1080,
            "min_height": 1920,
            "aspect_ratios": [(9, 16)]
        }
    }
    
    VIDEO_SPECS = {
        "max_size_mb": 4096,
        "max_duration_sec": 14400,  # 240 minutes
        "formats": ["MP4", "MOV", "AVI"]
    }
    
    def validate_image(self, image_data: bytes):
        """Validate image meets Meta requirements."""
        from PIL import Image
        import io
        
        img = Image.open(io.BytesIO(image_data))
        width, height = img.size
        
        # Check minimum dimensions
        if width < 600 or height < 600:
            raise AssetValidationError(
                f"Image too small: {width}x{height}. Minimum 600x600"
            )
        
        # Check file size
        size_mb = len(image_data) / (1024 * 1024)
        if size_mb > 30:
            raise AssetValidationError(
                f"Image too large: {size_mb:.1f}MB. Maximum 30MB"
            )
    
    def validate_video_url(self, url: str):
        """Validate video URL is accessible."""
        import requests
        
        try:
            response = requests.head(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            raise AssetValidationError(
                f"Video URL not accessible: {url}"
            ) from e
```

---

### 4.3 Campaign Agent

**Role:** Manage campaigns and ad sets

#### Responsibilities

- Create and update campaigns
- Create and update ad sets
- Configure targeting
- Manage budgets and schedules
- Handle campaign optimization settings

#### API Endpoints

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Create Campaign | POST | `/act_{id}/campaigns` |
| Update Campaign | POST | `/{campaign_id}` |
| Get Campaign | GET | `/{campaign_id}` |
| Create Ad Set | POST | `/act_{id}/adsets` |
| Update Ad Set | POST | `/{adset_id}` |
| Get Ad Set | GET | `/{adset_id}` |

#### Implementation

```python
class CampaignAgent:
    """
    Manages campaign and ad set operations.
    """
    
    def __init__(self, api_client: MetaAPIClient):
        self.api = api_client
        self.validator = CampaignValidator()
        self.targeting_helper = TargetingHelper()
        self.logger = StructuredLogger("campaign_agent")
    
    async def create_campaign(
        self,
        ad_account_id: str,
        params: CampaignParams
    ) -> Campaign:
        """
        Create a new advertising campaign.
        
        Args:
            ad_account_id: Ad account ID
            params: Campaign parameters
            
        Returns:
            Created campaign with ID
        """
        # Validate parameters
        self.validator.validate_campaign(params)
        
        # Prepare API request
        endpoint = f"/act_{ad_account_id}/campaigns"
        data = {
            "name": params.name,
            "objective": params.objective,
            "status": params.status or "PAUSED",
            "special_ad_categories": params.special_ad_categories or ["NONE"]
        }
        
        # Add optional parameters
        if params.daily_budget:
            data["daily_budget"] = params.daily_budget
            data["campaign_budget_optimization"] = True
        
        if params.lifetime_budget:
            data["lifetime_budget"] = params.lifetime_budget
            data["campaign_budget_optimization"] = True
        
        if params.bid_strategy:
            data["bid_strategy"] = params.bid_strategy
        
        try:
            response = await self.api.post(endpoint, json=data)
            
            campaign = Campaign(
                id=response["id"],
                name=params.name,
                objective=params.objective,
                status=data["status"]
            )
            
            self.logger.info(
                "campaign_created",
                campaign_id=campaign.id,
                name=campaign.name
            )
            
            return campaign
            
        except APIError as e:
            self.logger.error("campaign_creation_failed", error=str(e))
            raise CampaignCreationError(
                f"Failed to create campaign: {params.name}"
            ) from e
    
    async def create_adset(
        self,
        ad_account_id: str,
        params: AdSetParams
    ) -> AdSet:
        """
        Create a new ad set.
        
        Args:
            ad_account_id: Ad account ID
            params: Ad set parameters
            
        Returns:
            Created ad set with ID
        """
        # Validate parameters
        self.validator.validate_adset(params)
        
        # Build targeting
        targeting = await self.targeting_helper.build_targeting(
            params.targeting
        )
        
        # Prepare API request
        endpoint = f"/act_{ad_account_id}/adsets"
        data = {
            "name": params.name,
            "campaign_id": params.campaign_id,
            "billing_event": params.billing_event or "IMPRESSIONS",
            "optimization_goal": params.optimization_goal,
            "targeting": targeting,
            "status": params.status or "PAUSED"
        }
        
        # Budget configuration
        if params.daily_budget:
            data["daily_budget"] = params.daily_budget
        elif params.lifetime_budget:
            data["lifetime_budget"] = params.lifetime_budget
            data["end_time"] = params.end_time
        
        # Start time
        if params.start_time:
            data["start_time"] = params.start_time
        
        # Promoted object (for conversion campaigns)
        if params.promoted_object:
            data["promoted_object"] = params.promoted_object
        
        # Attribution settings
        if params.attribution_spec:
            data["attribution_spec"] = params.attribution_spec
        
        try:
            response = await self.api.post(endpoint, json=data)
            
            adset = AdSet(
                id=response["id"],
                name=params.name,
                campaign_id=params.campaign_id,
                optimization_goal=params.optimization_goal
            )
            
            self.logger.info(
                "adset_created",
                adset_id=adset.id,
                name=adset.name
            )
            
            return adset
            
        except APIError as e:
            self.logger.error("adset_creation_failed", error=str(e))
            raise AdSetCreationError(
                f"Failed to create ad set: {params.name}"
            ) from e
    
    async def update_campaign_budget(
        self,
        campaign_id: str,
        daily_budget: int
    ):
        """Update campaign daily budget."""
        endpoint = f"/{campaign_id}"
        data = {"daily_budget": daily_budget}
        
        await self.api.post(endpoint, json=data)
        self.logger.info(
            "budget_updated",
            campaign_id=campaign_id,
            daily_budget=daily_budget
        )
    
    async def pause_campaign(self, campaign_id: str):
        """Pause a campaign."""
        await self._update_status(campaign_id, "PAUSED")
    
    async def resume_campaign(self, campaign_id: str):
        """Resume a paused campaign."""
        await self._update_status(campaign_id, "ACTIVE")
    
    async def _update_status(self, object_id: str, status: str):
        """Update campaign or ad set status."""
        endpoint = f"/{object_id}"
        await self.api.post(endpoint, json={"status": status})
        
        self.logger.info(
            "status_updated",
            object_id=object_id,
            status=status
        )
```

#### Targeting Helper

```python
class TargetingHelper:
    """Builds and validates targeting configurations."""
    
    def __init__(self, api_client: MetaAPIClient):
        self.api = api_client
        self.interest_cache = {}
    
    async def build_targeting(self, params: dict) -> dict:
        """
        Build complete targeting object.
        
        Args:
            params: Targeting parameters
            
        Returns:
            Meta-formatted targeting object
        """
        targeting = {}
        
        # Geographic targeting
        if geo := params.get("geo_locations"):
            targeting["geo_locations"] = await self._build_geo(geo)
        
        # Demographics
        if age_min := params.get("age_min"):
            targeting["age_min"] = age_min
        if age_max := params.get("age_max"):
            targeting["age_max"] = age_max
        if genders := params.get("genders"):
            targeting["genders"] = genders
        
        # Interests & behaviors
        if interests := params.get("interests"):
            targeting["flexible_spec"] = await self._build_interests(interests)
        
        # Custom audiences
        if custom_audiences := params.get("custom_audiences"):
            targeting["custom_audiences"] = [
                {"id": aud_id} for aud_id in custom_audiences
            ]
        
        # Excluded audiences
        if excluded := params.get("excluded_custom_audiences"):
            targeting["excluded_custom_audiences"] = [
                {"id": aud_id} for aud_id in excluded
            ]
        
        # Placements
        if platforms := params.get("publisher_platforms"):
            targeting["publisher_platforms"] = platforms
        
        return targeting
    
    async def _build_geo(self, geo_params: dict) -> dict:
        """Build geographic targeting."""
        geo = {}
        
        if countries := geo_params.get("countries"):
            geo["countries"] = countries
        
        if cities := geo_params.get("cities"):
            geo["cities"] = [
                {
                    "key": city["key"],
                    "radius": city.get("radius", 25),
                    "distance_unit": city.get("unit", "kilometer")
                }
                for city in cities
            ]
        
        if location_types := geo_params.get("location_types"):
            geo["location_types"] = location_types
        
        return geo
    
    async def _build_interests(self, interest_names: list) -> list:
        """
        Convert interest names to IDs.
        
        Uses caching to minimize API calls.
        """
        interests = []
        
        for name in interest_names:
            if name not in self.interest_cache:
                # Search for interest ID
                interest_id = await self._search_interest(name)
                self.interest_cache[name] = interest_id
            
            interests.append({
                "id": self.interest_cache[name],
                "name": name
            })
        
        return [{"interests": interests}]
    
    async def _search_interest(self, query: str) -> str:
        """Search for interest ID by name."""
        endpoint = "/search"
        params = {
            "type": "adinterest",
            "q": query,
            "limit": 1
        }
        
        response = await self.api.get(endpoint, params=params)
        
        if not response.get("data"):
            raise TargetingError(f"Interest not found: {query}")
        
        return response["data"][0]["id"]
```

---

### 4.4 Ad Creation Agent

**Role:** Create and manage ads and creatives

#### Responsibilities

- Create ad creatives (all formats)
- Create ads
- Link creatives to ads
- Manage creative variations
- Handle format-specific logic

#### API Endpoints

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Create Creative | POST | `/act_{id}/adcreatives` |
| Get Creative | GET | `/{creative_id}` |
| Create Ad | POST | `/act_{id}/ads` |
| Update Ad | POST | `/{ad_id}` |
| Get Ad | GET | `/{ad_id}` |

#### Implementation

```python
class AdCreationAgent:
    """
    Manages ad and creative creation.
    """
    
    def __init__(self, api_client: MetaAPIClient):
        self.api = api_client
        self.validator = CreativeValidator()
        self.logger = StructuredLogger("ad_creation_agent")
    
    async def create_image_creative(
        self,
        ad_account_id: str,
        params: ImageCreativeParams
    ) -> Creative:
        """
        Create single image ad creative.
        
        Args:
            ad_account_id: Ad account ID
            params: Creative parameters
            
        Returns:
            Created creative with ID
        """
        self.validator.validate_image_creative(params)
        
        endpoint = f"/act_{ad_account_id}/adcreatives"
        data = {
            "name": params.name,
            "object_story_spec": {
                "page_id": params.page_id,
                "link_data": {
                    "image_hash": params.image_hash,
                    "link": params.link,
                    "message": params.message,
                    "call_to_action": {
                        "type": params.cta_type
                    }
                }
            }
        }
        
        try:
            response = await self.api.post(endpoint, json=data)
            
            creative = Creative(
                id=response["id"],
                name=params.name,
                format="single_image"
            )
            
            self.logger.info(
                "creative_created",
                creative_id=creative.id,
                format="single_image"
            )
            
            return creative
            
        except APIError as e:
            raise CreativeCreationError(
                f"Failed to create creative: {params.name}"
            ) from e
    
    async def create_video_creative(
        self,
        ad_account_id: str,
        params: VideoCreativeParams
    ) -> Creative:
        """Create video ad creative."""
        self.validator.validate_video_creative(params)
        
        endpoint = f"/act_{ad_account_id}/adcreatives"
        data = {
            "name": params.name,
            "object_story_spec": {
                "page_id": params.page_id,
                "video_data": {
                    "video_id": params.video_id,
                    "message": params.message,
                    "call_to_action": {
                        "type": params.cta_type,
                        "value": {"link": params.link}
                    }
                }
            }
        }
        
        response = await self.api.post(endpoint, json=data)
        
        return Creative(
            id=response["id"],
            name=params.name,
            format="video"
        )
    
    async def create_carousel_creative(
        self,
        ad_account_id: str,
        params: CarouselCreativeParams
    ) -> Creative:
        """Create carousel ad creative."""
        self.validator.validate_carousel_creative(params)
        
        # Build child attachments
        child_attachments = []
        for card in params.cards:
            child_attachments.append({
                "link": card.link,
                "image_hash": card.image_hash,
                "name": card.headline,
                "description": card.description
            })
        
        endpoint = f"/act_{ad_account_id}/adcreatives"
        data = {
            "name": params.name,
            "object_story_spec": {
                "page_id": params.page_id,
                "link_data": {
                    "link": params.link,
                    "child_attachments": child_attachments,
                    "call_to_action": {
                        "type": params.cta_type
                    }
                }
            }
        }
        
        response = await self.api.post(endpoint, json=data)
        
        return Creative(
            id=response["id"],
            name=params.name,
            format="carousel"
        )
    
    async def create_ad(
        self,
        ad_account_id: str,
        params: AdParams
    ) -> Ad:
        """
        Create an ad.
        
        Args:
            ad_account_id: Ad account ID
            params: Ad parameters
            
        Returns:
            Created ad with ID
        """
        self.validator.validate_ad(params)
        
        endpoint = f"/act_{ad_account_id}/ads"
        data = {
            "name": params.name,
            "adset_id": params.adset_id,
            "creative": {"creative_id": params.creative_id},
            "status": params.status or "PAUSED"
        }
        
        try:
            response = await self.api.post(endpoint, json=data)
            
            ad = Ad(
                id=response["id"],
                name=params.name,
                adset_id=params.adset_id,
                creative_id=params.creative_id
            )
            
            self.logger.info(
                "ad_created",
                ad_id=ad.id,
                name=ad.name
            )
            
            return ad
            
        except APIError as e:
            raise AdCreationError(
                f"Failed to create ad: {params.name}"
            ) from e
    
    async def create_ad_with_creative(
        self,
        ad_account_id: str,
        adset_id: str,
        creative_params: CreativeParams,
        ad_name: str
    ) -> tuple[Creative, Ad]:
        """
        Create creative and ad in one operation.
        
        Returns:
            Tuple of (creative, ad)
        """
        # Step 1: Create creative
        creative = await self._create_creative_by_type(
            ad_account_id,
            creative_params
        )
        
        # Step 2: Create ad
        ad_params = AdParams(
            name=ad_name,
            adset_id=adset_id,
            creative_id=creative.id,
            status="PAUSED"
        )
        
        ad = await self.create_ad(ad_account_id, ad_params)
        
        return creative, ad
    
    async def _create_creative_by_type(
        self,
        ad_account_id: str,
        params: CreativeParams
    ) -> Creative:
        """Route to appropriate creative creation method."""
        if params.format == "image":
            return await self.create_image_creative(ad_account_id, params)
        elif params.format == "video":
            return await self.create_video_creative(ad_account_id, params)
        elif params.format == "carousel":
            return await self.create_carousel_creative(ad_account_id, params)
        else:
            raise CreativeCreationError(f"Unknown format: {params.format}")
```

---

### 4.5 Insights Agent

**Role:** Fetch and analyze performance data

#### Responsibilities

- Fetch campaign/adset/ad insights
- Generate performance reports
- Handle metrics and breakdowns
- Export analytics data
- Performance comparisons

#### API Endpoints

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Account Insights | GET | `/act_{id}/insights` |
| Campaign Insights | GET | `/{campaign_id}/insights` |
| Ad Set Insights | GET | `/{adset_id}/insights` |
| Ad Insights | GET | `/{ad_id}/insights` |

#### Implementation

```python
class InsightsAgent:
    """
    Fetches and processes performance insights.
    """
    
    def __init__(self, api_client: MetaAPIClient):
        self.api = api_client
        self.formatter = InsightsFormatter()
        self.logger = StructuredLogger("insights_agent")
    
    async def get_campaign_insights(
        self,
        campaign_id: str,
        params: InsightsParams
    ) -> CampaignInsights:
        """
        Get performance insights for a campaign.
        
        Args:
            campaign_id: Campaign ID
            params: Insights parameters
            
        Returns:
            Formatted campaign insights
        """
        endpoint = f"/{campaign_id}/insights"
        query_params = self._build_query_params(params)
        
        try:
            response = await self.api.get(endpoint, params=query_params)
            
            insights = self.formatter.format_campaign_insights(
                response["data"]
            )
            
            self.logger.info(
                "insights_fetched",
                campaign_id=campaign_id,
                date_range=params.date_preset
            )
            
            return insights
            
        except APIError as e:
            raise InsightsFetchError(
                f"Failed to fetch insights for campaign {campaign_id}"
            ) from e
    
    async def get_adset_insights(
        self,
        adset_id: str,
        params: InsightsParams
    ) -> AdSetInsights:
        """Get insights for an ad set."""
        endpoint = f"/{adset_id}/insights"
        query_params = self._build_query_params(params)
        
        response = await self.api.get(endpoint, params=query_params)
        
        return self.formatter.format_adset_insights(response["data"])
    
    async def get_ad_insights(
        self,
        ad_id: str,
        params: InsightsParams
    ) -> AdInsights:
        """Get insights for an ad."""
        endpoint = f"/{ad_id}/insights"
        query_params = self._build_query_params(params)
        
        response = await self.api.get(endpoint, params=query_params)
        
        return self.formatter.format_ad_insights(response["data"])
    
    async def generate_performance_report(
        self,
        campaign_id: str,
        date_preset: str = "last_30d"
    ) -> PerformanceReport:
        """
        Generate comprehensive performance report.
        
        Args:
            campaign_id: Campaign ID
            date_preset: Date range preset
            
        Returns:
            Complete performance report
        """
        params = InsightsParams(
            date_preset=date_preset,
            fields=[
                "campaign_name",
                "impressions",
                "reach",
                "clicks",
                "inline_link_clicks",
                "spend",
                "actions",
                "action_values",
                "ctr",
                "cpc",
                "cpm",
                "frequency"
            ],
            breakdowns=["publisher_platform", "age", "gender"]
        )
        
        insights = await self.get_campaign_insights(campaign_id, params)
        
        # Generate report
        report = PerformanceReport(
            campaign_id=campaign_id,
            campaign_name=insights.campaign_name,
            date_range=date_preset,
            summary=self._calculate_summary(insights),
            platform_breakdown=self._breakdown_by_platform(insights),
            demographic_breakdown=self._breakdown_by_demographics(insights),
            recommendations=self._generate_recommendations(insights)
        )
        
        return report
    
    def _build_query_params(self, params: InsightsParams) -> dict:
        """Build API query parameters."""
        query = {
            "fields": ",".join(params.fields)
        }
        
        if params.date_preset:
            query["date_preset"] = params.date_preset
        elif params.time_range:
            query["time_range"] = json.dumps(params.time_range)
        
        if params.breakdowns:
            query["breakdowns"] = ",".join(params.breakdowns)
        
        if params.time_increment:
            query["time_increment"] = params.time_increment
        
        if params.level:
            query["level"] = params.level
        
        return query
    
    def _calculate_summary(self, insights: dict) -> dict:
        """Calculate summary metrics."""
        return {
            "total_impressions": sum(i.get("impressions", 0) for i in insights),
            "total_reach": sum(i.get("reach", 0) for i in insights),
            "total_clicks": sum(i.get("clicks", 0) for i in insights),
            "total_spend": sum(i.get("spend", 0) for i in insights),
            "avg_ctr": self._calculate_avg_ctr(insights),
            "avg_cpc": self._calculate_avg_cpc(insights)
        }
    
    def _generate_recommendations(self, insights: dict) -> list[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        # Check CTR
        avg_ctr = self._calculate_avg_ctr(insights)
        if avg_ctr < 1.0:
            recommendations.append(
                "CTR below 1% - consider refreshing ad creatives"
            )
        
        # Check frequency
        avg_frequency = self._calculate_avg_frequency(insights)
        if avg_frequency > 3:
            recommendations.append(
                "High frequency detected - expand audience to reduce ad fatigue"
            )
        
        # Check CPC
        avg_cpc = self._calculate_avg_cpc(insights)
        if avg_cpc > 500:  # ₹5
            recommendations.append(
                "High CPC - review targeting and bid strategy"
            )
        
        return recommendations
```

---

## 5. Workflow Orchestration

### 5.1 Workflow Types

| Workflow | Description | Agents Involved |
|----------|-------------|-----------------|
| **Full Campaign** | Create complete campaign from scratch | All 4 agents |
| **Campaign Only** | Create campaign and ad sets only | Campaign agent |
| **Creative Update** | Update existing ad creatives | Ad Creation agent |
| **Performance Analysis** | Fetch and analyze insights | Insights agent |
| **Bulk Operations** | Process multiple campaigns | All agents (parallel) |
| **Optimization** | Auto-optimize based on performance | Campaign + Insights agents |

### 5.2 Workflow Execution Engine

```python
class WorkflowEngine:
    """
    Manages workflow execution with state tracking.
    """
    
    def __init__(self, orchestrator: OrchestratorAgent):
        self.orchestrator = orchestrator
        self.state_manager = WorkflowStateManager()
        self.logger = StructuredLogger("workflow_engine")
    
    async def execute_workflow(
        self,
        workflow_type: str,
        data: dict,
        request_id: str
    ) -> WorkflowResult:
        """
        Execute a workflow with state management.
        
        Args:
            workflow_type: Type of workflow to execute
            data: Workflow input data
            request_id: Unique request identifier
            
        Returns:
            Workflow execution result
        """
        # Initialize workflow state
        state = WorkflowState(
            request_id=request_id,
            workflow_type=workflow_type,
            status="running",
            created_resources=[]
        )
        
        self.state_manager.save(state)
        
        try:
            # Execute workflow steps
            workflow = self._get_workflow_class(workflow_type)
            result = await workflow.execute(data, state)
            
            # Update state
            state.status = "completed"
            state.result = result
            self.state_manager.save(state)
            
            return WorkflowResult(
                success=True,
                data=result,
                request_id=request_id
            )
            
        except Exception as e:
            # Handle failure
            self.logger.error(
                "workflow_failed",
                request_id=request_id,
                error=str(e)
            )
            
            # Rollback if needed
            await self._rollback_workflow(state)
            
            state.status = "failed"
            state.error = str(e)
            self.state_manager.save(state)
            
            return WorkflowResult(
                success=False,
                error=str(e),
                request_id=request_id
            )
    
    async def _rollback_workflow(self, state: WorkflowState):
        """Rollback created resources on failure."""
        self.logger.info(
            "rolling_back",
            request_id=state.request_id,
            resources=len(state.created_resources)
        )
        
        # Delete in reverse order
        for resource in reversed(state.created_resources):
            try:
                await self._delete_resource(resource)
            except Exception as e:
                self.logger.error(
                    "rollback_failed",
                    resource=resource,
                    error=str(e)
                )
    
    async def _delete_resource(self, resource: dict):
        """Delete a created resource."""
        resource_type = resource["type"]
        resource_id = resource["id"]
        
        endpoint = f"/{resource_id}"
        params = {"status": "DELETED"}
        
        await self.orchestrator.api.post(endpoint, json=params)
```

### 5.3 State Management

```python
class WorkflowState:
    """Represents workflow execution state."""
    
    def __init__(
        self,
        request_id: str,
        workflow_type: str,
        status: str,
        created_resources: list
    ):
        self.request_id = request_id
        self.workflow_type = workflow_type
        self.status = status  # running, completed, failed
        self.created_resources = created_resources
        self.started_at = datetime.utcnow()
        self.completed_at = None
        self.result = None
        self.error = None
    
    def add_resource(self, resource_type: str, resource_id: str):
        """Track created resource for potential rollback."""
        self.created_resources.append({
            "type": resource_type,
            "id": resource_id,
            "created_at": datetime.utcnow().isoformat()
        })
    
    def to_dict(self) -> dict:
        """Serialize state to dictionary."""
        return {
            "request_id": self.request_id,
            "workflow_type": self.workflow_type,
            "status": self.status,
            "created_resources": self.created_resources,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error
        }


class WorkflowStateManager:
    """Manages persistence of workflow states."""
    
    def __init__(self, storage_backend="redis"):
        self.storage = self._get_storage(storage_backend)
    
    def save(self, state: WorkflowState):
        """Persist workflow state."""
        key = f"workflow:{state.request_id}"
        self.storage.set(key, json.dumps(state.to_dict()), ex=86400)
    
    def get(self, request_id: str) -> WorkflowState:
        """Retrieve workflow state."""
        key = f"workflow:{request_id}"
        data = self.storage.get(key)
        
        if not data:
            raise StateNotFoundError(f"State not found: {request_id}")
        
        return WorkflowState.from_dict(json.loads(data))
    
    def delete(self, request_id: str):
        """Delete workflow state."""
        key = f"workflow:{request_id}"
        self.storage.delete(key)
```

---

## 6. API Integration

### 6.1 API Client Implementation

```python
class MetaAPIClient:
    """
    HTTP client for Meta Marketing API.
    """
    
    BASE_URL = "https://graph.facebook.com/v24.0"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.session = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0
        )
        self.rate_limiter = RateLimiter(max_calls=200, window=3600)
        self.logger = StructuredLogger("api_client")
    
    async def get(
        self,
        endpoint: str,
        params: dict = None
    ) -> dict:
        """Execute GET request."""
        await self.rate_limiter.acquire()
        
        params = params or {}
        params["access_token"] = self.access_token
        
        self.logger.debug("api_request", method="GET", endpoint=endpoint)
        
        response = await self.session.get(endpoint, params=params)
        
        return self._handle_response(response)
    
    async def post(
        self,
        endpoint: str,
        json: dict = None,
        files: dict = None
    ) -> dict:
        """Execute POST request."""
        await self.rate_limiter.acquire()
        
        data = json or {}
        data["access_token"] = self.access_token
        
        self.logger.debug("api_request", method="POST", endpoint=endpoint)
        
        if files:
            response = await self.session.post(endpoint, data=data, files=files)
        else:
            response = await self.session.post(endpoint, json=data)
        
        return self._handle_response(response)
    
    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and errors."""
        self.logger.debug(
            "api_response",
            status_code=response.status_code,
            duration=response.elapsed.total_seconds()
        )
        
        if response.status_code >= 400:
            error_data = response.json()
            raise APIError(
                message=error_data.get("error", {}).get("message", "Unknown error"),
                code=error_data.get("error", {}).get("code"),
                status_code=response.status_code
            )
        
        return response.json()
    
    async def close(self):
        """Close HTTP session."""
        await self.session.aclose()
```

### 6.2 Rate Limiting

```python
class RateLimiter:
    """
    Token bucket rate limiter.
    """
    
    def __init__(self, max_calls: int, window: int):
        self.max_calls = max_calls
        self.window = window
        self.calls = []
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make API call."""
        async with self.lock:
            now = time.time()
            
            # Remove expired calls
            self.calls = [
                call_time for call_time in self.calls
                if now - call_time < self.window
            ]
            
            # Check if we can make a call
            if len(self.calls) >= self.max_calls:
                # Calculate wait time
                oldest_call = min(self.calls)
                wait_time = self.window - (now - oldest_call)
                
                logger.warning(
                    "rate_limit_hit",
                    wait_time=wait_time
                )
                
                await asyncio.sleep(wait_time)
                
                # Retry acquisition
                return await self.acquire()
            
            # Record this call
            self.calls.append(now)
```

### 6.3 Error Handling

```python
class APIError(Exception):
    """Base exception for API errors."""
    
    def __init__(self, message: str, code: int = None, status_code: int = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class RetryableAPIError(APIError):
    """API error that can be retried."""
    pass


class NonRetryableAPIError(APIError):
    """API error that should not be retried."""
    pass


async def retry_on_error(
    func,
    max_retries: int = 3,
    backoff_base: float = 2.0
):
    """
    Retry function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum retry attempts
        backoff_base: Exponential backoff base
        
    Returns:
        Function result
        
    Raises:
        Exception after max retries exceeded
    """
    for attempt in range(max_retries):
        try:
            return await func()
        except RetryableAPIError as e:
            if attempt == max_retries - 1:
                raise
            
            wait_time = backoff_base ** attempt
            logger.warning(
                "retrying_request",
                attempt=attempt + 1,
                wait_time=wait_time,
                error=str(e)
            )
            
            await asyncio.sleep(wait_time)
        except NonRetryableAPIError:
            raise
```

---

## 7. Data Models

### 7.1 Request Models

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class OrchestratorRequest(BaseModel):
    """Main request to orchestrator."""
    agent_id: str
    request_id: str
    timestamp: datetime
    action: str
    credentials: dict
    data: dict
    options: Optional[dict] = {}


class CampaignParams(BaseModel):
    """Campaign creation parameters."""
    name: str = Field(..., min_length=1, max_length=200)
    objective: str = Field(..., regex="^OUTCOME_")
    status: Optional[str] = "PAUSED"
    special_ad_categories: Optional[List[str]] = ["NONE"]
    daily_budget: Optional[int] = Field(None, gt=0)
    lifetime_budget: Optional[int] = Field(None, gt=0)
    bid_strategy: Optional[str] = "LOWEST_COST_WITHOUT_CAP"
    start_time: Optional[datetime] = None
    stop_time: Optional[datetime] = None
    
    @validator("objective")
    def validate_objective(cls, v):
        valid_objectives = [
            "OUTCOME_AWARENESS",
            "OUTCOME_TRAFFIC",
            "OUTCOME_ENGAGEMENT",
            "OUTCOME_LEADS",
            "OUTCOME_APP_PROMOTION",
            "OUTCOME_SALES"
        ]
        if v not in valid_objectives:
            raise ValueError(f"Invalid objective: {v}")
        return v
    
    @validator("daily_budget", "lifetime_budget")
    def validate_budget(cls, v):
        if v and v < 4000:  # ₹40 minimum
            raise ValueError("Budget must be at least ₹40 (4000 paisa)")
        return v


class AdSetParams(BaseModel):
    """Ad set creation parameters."""
    name: str
    campaign_id: str
    billing_event: str = "IMPRESSIONS"
    optimization_goal: str
    targeting: dict
    status: Optional[str] = "PAUSED"
    daily_budget: Optional[int] = None
    lifetime_budget: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    promoted_object: Optional[dict] = None
    attribution_spec: Optional[List[dict]] = None


class ImageCreativeParams(BaseModel):
    """Image creative parameters."""
    name: str
    page_id: str
    image_hash: str
    link: str
    message: str
    cta_type: str = "LEARN_MORE"


class AdParams(BaseModel):
    """Ad creation parameters."""
    name: str
    adset_id: str
    creative_id: str
    status: Optional[str] = "PAUSED"


class InsightsParams(BaseModel):
    """Insights query parameters."""
    date_preset: Optional[str] = "last_30d"
    time_range: Optional[dict] = None
    fields: List[str] = [
        "impressions",
        "clicks",
        "spend",
        "actions"
    ]
    breakdowns: Optional[List[str]] = None
    time_increment: Optional[str] = None
    level: Optional[str] = None
```

### 7.2 Response Models

```python
class Campaign(BaseModel):
    """Campaign response model."""
    id: str
    name: str
    objective: str
    status: str
    created_time: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class AdSet(BaseModel):
    """Ad set response model."""
    id: str
    name: str
    campaign_id: str
    optimization_goal: str
    status: str
    daily_budget: Optional[int] = None
    
    class Config:
        orm_mode = True


class Creative(BaseModel):
    """Creative response model."""
    id: str
    name: str
    format: str
    
    class Config:
        orm_mode = True


class Ad(BaseModel):
    """Ad response model."""
    id: str
    name: str
    adset_id: str
    creative_id: str
    status: str
    
    class Config:
        orm_mode = True


class ImageAsset(BaseModel):
    """Image asset response model."""
    hash: str
    filename: str
    url: Optional[str] = None


class VideoAsset(BaseModel):
    """Video asset response model."""
    id: str
    title: str
    url: str


class CampaignInsights(BaseModel):
    """Campaign insights model."""
    campaign_id: str
    campaign_name: str
    date_start: str
    date_stop: str
    impressions: int
    reach: int
    clicks: int
    spend: float
    actions: Optional[List[dict]] = None
    
    class Config:
        orm_mode = True
```

---

## 8. Error Handling

### 8.1 Error Taxonomy

```python
# Base Errors
class MetaAgentError(Exception):
    """Base exception for all agent errors."""
    pass

class ValidationError(MetaAgentError):
    """Invalid input parameters."""
    pass

class AuthenticationError(MetaAgentError):
    """Authentication/authorization failed."""
    pass

# Asset Errors
class AssetError(MetaAgentError):
    """Base asset error."""
    pass

class AssetValidationError(AssetError):
    """Asset doesn't meet specifications."""
    pass

class AssetUploadError(AssetError):
    """Asset upload failed."""
    pass

# Campaign Errors
class CampaignError(MetaAgentError):
    """Base campaign error."""
    pass

class CampaignCreationError(CampaignError):
    """Campaign creation failed."""
    pass

class CampaignUpdateError(CampaignError):
    """Campaign update failed."""
    pass

# Ad Errors
class AdError(MetaAgentError):
    """Base ad error."""
    pass

class CreativeCreationError(AdError):
    """Creative creation failed."""
    pass

class AdCreationError(AdError):
    """Ad creation failed."""
    pass

# Insights Errors
class InsightsError(MetaAgentError):
    """Base insights error."""
    pass

class InsightsFetchError(InsightsError):
    """Failed to fetch insights."""
    pass

# Workflow Errors
class WorkflowError(MetaAgentError):
    """Base workflow error."""
    pass

class WorkflowExecutionError(WorkflowError):
    """Workflow execution failed."""
    pass

class StateNotFoundError(WorkflowError):
    """Workflow state not found."""
    pass
```

### 8.2 Error Recovery Strategies

```python
class ErrorRecoveryManager:
    """
    Manages error recovery strategies.
    """
    
    def __init__(self):
        self.logger = StructuredLogger("error_recovery")
        self.strategies = {
            "rate_limit": self.handle_rate_limit,
            "timeout": self.handle_timeout,
            "server_error": self.handle_server_error,
            "validation": self.handle_validation,
            "auth": self.handle_auth
        }
    
    async def recover(self, error: Exception, context: dict):
        """
        Attempt error recovery.
        
        Args:
            error: Exception that occurred
            context: Error context
            
        Returns:
            Recovery result
        """
        error_type = self._classify_error(error)
        
        if strategy := self.strategies.get(error_type):
            return await strategy(error, context)
        
        # No recovery strategy
        self.logger.error(
            "no_recovery_strategy",
            error_type=error_type,
            error=str(error)
        )
        raise error
    
    def _classify_error(self, error: Exception) -> str:
        """Classify error type."""
        if isinstance(error, APIError):
            if error.code == 17:  # Rate limit
                return "rate_limit"
            elif error.status_code >= 500:
                return "server_error"
            elif error.status_code == 401:
                return "auth"
        
        if isinstance(error, ValidationError):
            return "validation"
        
        if isinstance(error, TimeoutError):
            return "timeout"
        
        return "unknown"
    
    async def handle_rate_limit(self, error, context):
        """Handle rate limit errors."""
        self.logger.warning("rate_limit_exceeded")
        
        # Wait and retry
        await asyncio.sleep(60)
        
        return await context["retry_func"]()
    
    async def handle_timeout(self, error, context):
        """Handle timeout errors."""
        self.logger.warning("request_timeout")
        
        # Retry with longer timeout
        context["timeout"] *= 2
        return await context["retry_func"]()
    
    async def handle_server_error(self, error, context):
        """Handle server errors."""
        self.logger.warning("server_error")
        
        # Exponential backoff retry
        attempts = context.get("attempts", 0)
        if attempts < 3:
            wait_time = 2 ** attempts
            await asyncio.sleep(wait_time)
            
            context["attempts"] = attempts + 1
            return await context["retry_func"]()
        
        raise error
    
    async def handle_validation(self, error, context):
        """Handle validation errors."""
        self.logger.error("validation_failed", error=str(error))
        
        # No recovery for validation errors
        raise error
    
    async def handle_auth(self, error, context):
        """Handle authentication errors."""
        self.logger.error("authentication_failed")
        
        # Attempt token refresh if available
        if refresh_func := context.get("refresh_token_func"):
            new_token = await refresh_func()
            context["access_token"] = new_token
            return await context["retry_func"]()
        
        raise error
```

---

## 9. Performance & Scalability

### 9.1 Caching Strategy

```python
class CacheManager:
    """
    Multi-level caching system.
    """
    
    def __init__(self):
        self.redis = redis.Redis(decode_responses=True)
        self.local_cache = {}
        self.logger = StructuredLogger("cache")
    
    def get(self, key: str, level: str = "redis"):
        """
        Get value from cache.
        
        Args:
            key: Cache key
            level: Cache level (local, redis)
            
        Returns:
            Cached value or None
        """
        # Try local cache first
        if level in ["local", "both"]:
            if value := self.local_cache.get(key):
                self.logger.debug("cache_hit", key=key, level="local")
                return value
        
        # Try Redis
        if level in ["redis", "both"]:
            if value := self.redis.get(key):
                self.logger.debug("cache_hit", key=key, level="redis")
                
                # Populate local cache
                if level == "both":
                    self.local_cache[key] = value
                
                return value
        
        self.logger.debug("cache_miss", key=key)
        return None
    
    def set(
        self,
        key: str,
        value: any,
        ttl: int = 3600,
        level: str = "redis"
    ):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            level: Cache level
        """
        if level in ["local", "both"]:
            self.local_cache[key] = value
        
        if level in ["redis", "both"]:
            self.redis.setex(key, ttl, value)
        
        self.logger.debug(
            "cache_set",
            key=key,
            level=level,
            ttl=ttl
        )
    
    def invalidate(self, pattern: str):
        """Invalidate cache entries matching pattern."""
        # Invalidate Redis
        for key in self.redis.scan_iter(match=pattern):
            self.redis.delete(key)
        
        # Invalidate local cache
        self.local_cache = {
            k: v for k, v in self.local_cache.items()
            if not fnmatch.fnmatch(k, pattern)
        }
        
        self.logger.info("cache_invalidated", pattern=pattern)
```

### 9.2 Parallel Processing

```python
async def process_in_batches(
    items: list,
    processor: callable,
    batch_size: int = 10
):
    """
    Process items in parallel batches.
    
    Args:
        items: Items to process
        processor: Async function to process each item
        batch_size: Number of items per batch
        
    Returns:
        List of processed results
    """
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        batch_results = await asyncio.gather(
            *[processor(item) for item in batch],
            return_exceptions=True
        )
        
        results.extend(batch_results)
    
    return results
```

### 9.3 Performance Monitoring

```python
class PerformanceMonitor:
    """
    Tracks agent performance metrics.
    """
    
    def __init__(self):
        self.metrics = {
            "request_count": Counter("requests_total"),
            "request_duration": Histogram("request_duration_seconds"),
            "error_count": Counter("errors_total"),
            "api_calls": Counter("api_calls_total")
        }
    
    @contextmanager
    def track_request(self, operation: str):
        """Track request timing."""
        start = time.time()
        
        try:
            yield
            self.metrics["request_count"].inc()
        except Exception:
            self.metrics["error_count"].inc()
            raise
        finally:
            duration = time.time() - start
            self.metrics["request_duration"].observe(duration)
    
    def record_api_call(self, endpoint: str):
        """Record API call."""
        self.metrics["api_calls"].labels(endpoint=endpoint).inc()
```

---

## 10. Security & Authentication

### 10.1 Credential Management

```python
class CredentialManager:
    """
    Secure credential storage and retrieval.
    """
    
    def __init__(self, vault_url: str):
        self.vault = hvac.Client(url=vault_url)
        self.cache = {}
        self.logger = StructuredLogger("credentials")
    
    def get_access_token(self, ad_account_id: str) -> str:
        """
        Retrieve access token for ad account.
        
        Args:
            ad_account_id: Ad account ID
            
        Returns:
            Valid access token
        """
        # Check cache
        if token := self.cache.get(ad_account_id):
            if not self._is_token_expired(token):
                return token["value"]
        
        # Retrieve from vault
        secret_path = f"meta/tokens/{ad_account_id}"
        
        try:
            secret = self.vault.secrets.kv.v2.read_secret_version(
                path=secret_path
            )
            
            token_data = secret["data"]["data"]
            
            # Cache token
            self.cache[ad_account_id] = {
                "value": token_data["access_token"],
                "expires_at": token_data["expires_at"]
            }
            
            return token_data["access_token"]
            
        except Exception as e:
            self.logger.error(
                "token_retrieval_failed",
                ad_account_id=ad_account_id,
                error=str(e)
            )
            raise AuthenticationError(
                f"Failed to retrieve token for {ad_account_id}"
            ) from e
    
    def _is_token_expired(self, token: dict) -> bool:
        """Check if token is expired."""
        expires_at = datetime.fromisoformat(token["expires_at"])
        return datetime.utcnow() >= expires_at
    
    def rotate_token(self, ad_account_id: str, new_token: str):
        """Rotate access token."""
        secret_path = f"meta/tokens/{ad_account_id}"
        
        self.vault.secrets.kv.v2.create_or_update_secret(
            path=secret_path,
            secret={
                "access_token": new_token,
                "expires_at": (
                    datetime.utcnow() + timedelta(days=60)
                ).isoformat()
            }
        )
        
        # Invalidate cache
        self.cache.pop(ad_account_id, None)
        
        self.logger.info("token_rotated", ad_account_id=ad_account_id)
```

### 10.2 Request Validation

```python
class RequestValidator:
    """
    Validates incoming requests.
    """
    
    def validate(self, request: OrchestratorRequest):
        """
        Validate orchestrator request.
        
        Args:
            request: Request to validate
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate required fields
        if not request.credentials.get("ad_account_id"):
            raise ValidationError("Missing ad_account_id")
        
        if not request.credentials.get("access_token"):
            raise ValidationError("Missing access_token")
        
        # Validate action
        valid_actions = [
            "create_full_campaign",
            "create_campaign",
            "update_campaign",
            "get_insights"
        ]
        
        if request.action not in valid_actions:
            raise ValidationError(f"Invalid action: {request.action}")
        
        # Validate data based on action
        if request.action == "create_full_campaign":
            self._validate_campaign_data(request.data)
    
    def _validate_campaign_data(self, data: dict):
        """Validate campaign creation data."""
        if not data.get("campaign"):
            raise ValidationError("Missing campaign data")
        
        campaign = data["campaign"]
        
        if not campaign.get("name"):
            raise ValidationError("Missing campaign name")
        
        if not campaign.get("objective"):
            raise ValidationError("Missing campaign objective")
```

---

## 11. Monitoring & Logging

### 11.1 Structured Logging

```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


class StructuredLogger:
    """
    Structured logging wrapper.
    """
    
    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)
    
    def info(self, event: str, **kwargs):
        """Log info event."""
        self.logger.info(event, **kwargs)
    
    def warning(self, event: str, **kwargs):
        """Log warning event."""
        self.logger.warning(event, **kwargs)
    
    def error(self, event: str, **kwargs):
        """Log error event."""
        self.logger.error(event, **kwargs)
    
    def debug(self, event: str, **kwargs):
        """Log debug event."""
        self.logger.debug(event, **kwargs)
```

### 11.2 Metrics Collection

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
REQUEST_COUNT = Counter(
    "meta_agent_requests_total",
    "Total requests",
    ["agent", "action"]
)

REQUEST_DURATION = Histogram(
    "meta_agent_request_duration_seconds",
    "Request duration",
    ["agent", "action"]
)

ACTIVE_WORKFLOWS = Gauge(
    "meta_agent_active_workflows",
    "Active workflows"
)

API_CALLS = Counter(
    "meta_agent_api_calls_total",
    "Total API calls",
    ["endpoint", "method"]
)

ERROR_COUNT = Counter(
    "meta_agent_errors_total",
    "Total errors",
    ["agent", "error_type"]
)
```

### 11.3 Health Checks

```python
class HealthCheck:
    """
    System health monitoring.
    """
    
    def __init__(self, orchestrator: OrchestratorAgent):
        self.orchestrator = orchestrator
    
    async def check_health(self) -> dict:
        """
        Perform health check.
        
        Returns:
            Health status
        """
        checks = {
            "api_connectivity": await self._check_api(),
            "database": await self._check_database(),
            "cache": await self._check_cache(),
            "agents": await self._check_agents()
        }
        
        overall_status = all(
            check["status"] == "healthy"
            for check in checks.values()
        )
        
        return {
            "status": "healthy" if overall_status else "unhealthy",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _check_api(self) -> dict:
        """Check Meta API connectivity."""
        try:
            # Simple API call
            response = await self.orchestrator.api.get("/me")
            
            return {
                "status": "healthy",
                "response_time": response.get("response_time")
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_database(self) -> dict:
        """Check database connectivity."""
        # Implement database check
        return {"status": "healthy"}
    
    async def _check_cache(self) -> dict:
        """Check cache connectivity."""
        # Implement cache check
        return {"status": "healthy"}
    
    async def _check_agents(self) -> dict:
        """Check agent availability."""
        return {
            "status": "healthy",
            "agents": {
                "orchestrator": "active",
                "asset": "active",
                "campaign": "active",
                "ad_creation": "active",
                "insights": "active"
            }
        }
```

---

## 12. Deployment Guide

### 12.1 Environment Configuration

```yaml
# config/production.yaml

api:
  base_url: "https://graph.facebook.com/v24.0"
  timeout: 30
  max_retries: 3

agents:
  orchestrator:
    workers: 4
  asset:
    workers: 8
    upload_timeout: 300
  campaign:
    workers: 4
  ad_creation:
    workers: 4
  insights:
    workers: 2

cache:
  backend: "redis"
  host: "redis.example.com"
  port: 6379
  ttl: 3600

database:
  url: "postgresql://user:pass@db.example.com/meta_agent"

monitoring:
  enabled: true
  prometheus_port: 9090
  log_level: "INFO"

security:
  vault_url: "https://vault.example.com"
  encrypt_at_rest: true
```

### 12.2 Docker Deployment

```dockerfile
# Dockerfile

FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose ports
EXPOSE 8000 9090

# Run application
CMD ["python", "-m", "meta_agent.main"]
```

```yaml
# docker-compose.yml

version: '3.8'

services:
  orchestrator:
    build: .
    environment:
      - AGENT_TYPE=orchestrator
      - CONFIG_PATH=/app/config/production.yaml
    ports:
      - "8000:8000"
      - "9090:9090"
    depends_on:
      - redis
      - postgres
  
  asset-agent:
    build: .
    environment:
      - AGENT_TYPE=asset
      - CONFIG_PATH=/app/config/production.yaml
    depends_on:
      - redis
  
  campaign-agent:
    build: .
    environment:
      - AGENT_TYPE=campaign
      - CONFIG_PATH=/app/config/production.yaml
    depends_on:
      - redis
  
  ad-creation-agent:
    build: .
    environment:
      - AGENT_TYPE=ad_creation
      - CONFIG_PATH=/app/config/production.yaml
    depends_on:
      - redis
  
  insights-agent:
    build: .
    environment:
      - AGENT_TYPE=insights
      - CONFIG_PATH=/app/config/production.yaml
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=meta_agent
      - POSTGRES_USER=agent_user
      - POSTGRES_PASSWORD=secure_password
    ports:
      - "5432:5432"
```

---

## Conclusion

This architecture provides a robust, scalable, and maintainable solution for automating META marketing operations with **minimal agent complexity** (4 agents) while maximizing functionality and reliability.

**Key Achievements:**
- ✅ Complete campaign automation
- ✅ Efficient agent design
- ✅ Comprehensive error handling
- ✅ High performance & scalability
- ✅ Production-ready deployment

**Next Steps:**
1. Implement core agents
2. Set up monitoring infrastructure
3. Deploy to staging environment
4. Conduct load testing
5. Production rollout