# META Marketing Agent Architecture
## Complete Logic Documentation

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Agent Specifications](#agent-specifications)
4. [Workflow Logic](#workflow-logic)
5. [Communication Protocol](#communication-protocol)
6. [Error Handling & Recovery](#error-handling--recovery)
7. [Design Decisions](#design-decisions)
8. [Scalability & Performance](#scalability--performance)
9. [Monitoring & Observability](#monitoring--observability)
10. [Best Practices](#best-practices)

---

## Executive Summary

### System Purpose
Automate the complete META (Facebook/Instagram) advertising lifecycle including campaign creation, ad management, asset handling, and performance analytics through an intelligent multi-agent system.

### Key Objectives
- **Minimize human intervention** in META ad operations
- **Optimize agent count** for efficiency (4 specialized agents)
- **Ensure data consistency** across the ad hierarchy
- **Enable parallel processing** where possible
- **Provide comprehensive insights** and reporting

### Architecture Philosophy
**Separation of Concerns with Minimal Overhead**: Each agent handles a distinct domain while the orchestrator manages dependencies and workflows, minimizing inter-agent communication complexity.

---

## Architecture Overview

### System Hierarchy

```
External Layer (Input)
└── Ambient Agent
    └── Provides all parameters and initiates requests

Orchestration Layer
└── META Orchestrator Agent
    ├── Validates inputs
    ├── Manages workflows
    ├── Coordinates specialized agents
    └── Returns consolidated responses

Execution Layer (4 Specialized Agents)
├── Asset Agent (Media Upload)
├── Campaign Agent (Campaigns + Ad Sets)
├── Ad Creation Agent (Creatives + Ads)
└── Insights Agent (Analytics + Reporting)
```

### Agent Count Rationale

**4 Agents** is the optimal number because:
- **Too few (2-3)**: Creates bottlenecks and tight coupling
- **Too many (6+)**: Increases coordination overhead exponentially
- **Just right (4)**: Balances specialization with communication efficiency

### Data Flow Pattern

**Sequential Dependencies**:
1. Assets must be uploaded before creative creation
2. Campaigns must exist before ad sets
3. Ad sets must exist before ads
4. Creatives must exist before ads
5. All entities must exist before insights retrieval

**Parallel Opportunities**:
- Multiple assets can upload simultaneously
- Multiple ad sets can be created in parallel
- Multiple ads can be created concurrently
- Multiple insight queries can run together

---

## Agent Specifications

### 1. META Orchestrator Agent

**Role**: Central coordinator and workflow manager

#### Primary Responsibilities

**Input Processing**:
- Receives requests from Ambient Agent
- Validates all required parameters
- Checks credential validity (access tokens, ad account IDs)
- Validates API version compatibility
- Preprocesses data into agent-specific formats

**Workflow Management**:
- Determines execution order based on dependencies
- Decides which operations can run in parallel
- Manages state across multi-step operations
- Tracks progress of long-running workflows
- Coordinates rollback operations on failures

**Response Consolidation**:
- Collects results from all specialized agents
- Aggregates data into unified response format
- Adds metadata (execution time, warnings, recommendations)
- Formats errors with actionable guidance

**Error Recovery**:
- Implements retry logic with exponential backoff
- Performs cleanup of partially created resources
- Maintains transaction logs for debugging
- Provides detailed failure context to Ambient Agent

#### Key Capabilities

**Validation Functions**:
- Verify access token validity and permissions
- Check ad account status and spending limits
- Validate budget amounts against minimums
- Confirm objective-optimization goal compatibility
- Verify targeting parameters are valid

**Routing Logic**:
- Map request types to appropriate agents
- Determine parallel vs sequential execution
- Allocate resources based on request complexity
- Queue low-priority operations

**Dependency Management**:
- Track entity relationships (campaign → ad set → ad)
- Ensure parent entities exist before children
- Maintain ID mappings across creation steps
- Handle cascading updates and deletions

**State Management**:
- Store intermediate results during workflows
- Enable resume from failure points
- Track which steps completed successfully
- Maintain audit trail of all operations

---

### 2. Asset Agent

**Role**: Media file upload and management specialist

#### Primary Responsibilities

**Asset Upload**:
- Accept images and videos from URLs or binary data
- Validate file specifications before upload
- Handle multiple image formats (JPG, PNG, GIF)
- Process video files (MP4, MOV) up to 4GB
- Return asset hashes for images and IDs for videos

**Validation Logic**:
- Check file sizes against META limits
- Verify aspect ratios match placement requirements
- Validate resolution meets minimum standards
- Ensure video duration is within allowed range
- Confirm file formats are supported

**Batch Processing**:
- Upload multiple assets concurrently
- Track progress of each upload
- Handle partial batch failures gracefully
- Return results with success/failure status per asset

**Asset Tracking**:
- Maintain cache of uploaded asset hashes
- Enable asset reuse across multiple ads
- Track which assets are used in which campaigns
- Support asset lifecycle management

#### Operations

**Upload Image**:
- Input: Image URL or binary data, filename
- Process: Validate specs → Upload to ad account → Retrieve hash
- Output: Image hash, dimensions, file size
- Error scenarios: Invalid format, size exceeded, upload failure

**Upload Video**:
- Input: Video URL or binary data, filename
- Process: Validate specs → Upload to ad account → Poll status → Retrieve ID
- Output: Video ID, duration, resolution, thumbnail
- Error scenarios: Encoding failure, duration exceeded, upload timeout

**Validate Specifications**:
- Check against placement requirements
- Verify aspect ratio compatibility
- Confirm resolution meets standards
- Validate file size limits

**Batch Upload**:
- Accept array of asset definitions
- Process uploads in parallel (up to 10 concurrent)
- Track individual upload progress
- Return consolidated results with per-asset status

**Get Asset Status**:
- Query upload completion status
- Retrieve processing progress for videos
- Check if asset is ready for use in ads
- Return error details if upload failed

#### Asset Lifecycle

**Upload Phase**:
1. Receive asset from orchestrator
2. Validate specifications
3. Initiate upload to META API
4. Poll for completion (videos only)
5. Return hash/ID to orchestrator

**Reuse Phase**:
- Check cache for existing hash
- Skip upload if already exists
- Return cached hash immediately
- Update usage tracking

**Cleanup Phase**:
- Remove unused assets after campaign deletion
- Handle orphaned assets from failed creations
- Maintain asset inventory for auditing

---

### 3. Campaign Agent

**Role**: Campaign and ad set creation/management specialist

#### Primary Responsibilities

**Campaign Management**:
- Create campaigns with specified objectives
- Configure campaign-level budgets (CBO)
- Set campaign schedules and spending limits
- Manage campaign status (active, paused, archived)
- Update campaign parameters

**Ad Set Management**:
- Create ad sets under campaigns
- Configure detailed targeting parameters
- Set ad set budgets and schedules
- Define optimization goals and billing events
- Manage placement selections

**Targeting Configuration**:
- Process geographic targeting (countries, regions, cities, radius)
- Configure demographic filters (age, gender)
- Set interest and behavior targeting
- Handle custom and lookalike audience assignments
- Apply exclusion criteria

**Budget Management**:
- Calculate budget in API format (currency smallest unit)
- Validate against minimum budget requirements
- Configure daily vs lifetime budgets
- Set spend caps and pacing
- Manage budget distribution with CBO

#### Operations

**Create Campaign**:
- Input: Campaign parameters from orchestrator
- Process: Validate objective → Check special ad categories → Create via API
- Output: Campaign ID, creation timestamp
- Dependencies: None (top of hierarchy)

**Create Ad Set**:
- Input: Ad set parameters + parent campaign ID
- Process: Validate targeting → Configure optimization → Link to campaign → Create via API
- Output: Ad set ID, creation timestamp
- Dependencies: Campaign must exist

**Update Campaign**:
- Input: Campaign ID + updated parameters
- Process: Validate changes → Update via API → Verify success
- Output: Updated campaign details
- Constraints: Cannot change objective after creation

**Update Ad Set**:
- Input: Ad set ID + updated parameters
- Process: Validate changes → Update via API → Handle learning phase reset if major change
- Output: Updated ad set details
- Constraints: Budget changes trigger learning phase restart

**Pause/Resume Campaign**:
- Input: Campaign ID + desired status
- Process: Update status field → Cascade to child ad sets → Verify state change
- Output: New status confirmation
- Impact: All child ad sets and ads inherit status

**Pause/Resume Ad Set**:
- Input: Ad set ID + desired status
- Process: Update status field → Cascade to child ads → Verify state change
- Output: New status confirmation
- Impact: All child ads inherit status

**Configure Targeting**:
- Input: Targeting specification object
- Process: Validate location IDs → Check interest/behavior IDs → Build targeting JSON
- Output: Validated targeting configuration
- Validation: Check all IDs exist in META catalog

**Set Budget**:
- Input: Budget amount, budget type (daily/lifetime), currency
- Process: Convert to smallest unit → Validate minimums → Apply to campaign/ad set
- Output: Budget configuration confirmation
- Validation: Check against objective-specific minimums

#### Targeting Logic

**Geographic Targeting Processing**:
- Country level: Use ISO country codes
- Region level: Look up region keys via search API
- City level: Look up city keys + radius configuration
- Location type: Filter by home, recent, or traveling

**Demographic Filtering**:
- Age range: Validate min/max between 13-65
- Gender: Map to numeric codes (1=male, 2=female, [1,2]=all)
- Language: Apply language preference filters

**Interest and Behavior Logic**:
- Interest targeting: Use flexible_spec array with OR logic
- Behavior targeting: Combine with interests in same object for AND logic
- Multiple flexible_spec objects create OR conditions between groups

**Audience Assignment**:
- Custom audiences: Add to inclusion list
- Excluded audiences: Add to exclusion list
- Lookalike audiences: Treated as custom audiences
- Multiple audiences combine with OR logic

**Placement Configuration**:
- Automatic: Let META optimize placements
- Manual: Specify exact platforms and positions
- Platform options: Facebook, Instagram, Messenger, Audience Network, Threads
- Position granularity: Feed, Stories, Reels, Search, etc.

---

### 4. Ad Creation Agent

**Role**: Creative and ad entity specialist

#### Primary Responsibilities

**Creative Management**:
- Build creative objects using uploaded assets
- Configure creative format (single image, video, carousel, collection)
- Set ad copy (headline, description, call-to-action)
- Link creative to destination URLs
- Handle platform-specific creative requirements

**Ad Management**:
- Create ad entities linked to ad sets
- Associate creatives with ads
- Manage ad status and delivery
- Handle ad updates and variations
- Support A/B testing configurations

**Format Handling**:
- Single image ads: Simple image + copy
- Single video ads: Video + copy with playback options
- Carousel ads: Multiple cards with individual links
- Collection ads: Hero image + product grid
- Instant Experience: Full-screen mobile experience

#### Operations

**Create Image Creative**:
- Input: Asset hash + ad copy + destination URL + CTA
- Process: Build object_story_spec → Create creative via API
- Output: Creative ID
- Requirements: Image hash from Asset Agent

**Create Video Creative**:
- Input: Video ID + ad copy + destination URL + CTA
- Process: Build object_story_spec → Configure video options → Create creative via API
- Output: Creative ID
- Requirements: Video ID from Asset Agent

**Create Carousel Creative**:
- Input: Multiple asset hashes + individual card details + CTA
- Process: Build child_attachments array → Create parent creative → Link cards
- Output: Creative ID
- Requirements: 2-10 asset hashes from Asset Agent

**Create Collection Creative**:
- Input: Hero image hash + product catalog ID + template
- Process: Build collection spec → Link catalog → Create creative
- Output: Creative ID
- Requirements: Catalog setup in Business Manager

**Create Ad**:
- Input: Ad set ID + creative ID + ad name + status
- Process: Link to ad set → Associate creative → Set status → Create via API
- Output: Ad ID, creation timestamp
- Dependencies: Ad set exists, creative exists

**Update Ad**:
- Input: Ad ID + updated parameters
- Process: Validate changes → Update via API → Reset learning if major change
- Output: Updated ad details
- Constraints: Cannot change ad set after creation

**Pause/Resume Ad**:
- Input: Ad ID + desired status
- Process: Update status field → Verify state change
- Output: New status confirmation

**Duplicate Ad**:
- Input: Source ad ID + new name + optional modifications
- Process: Fetch original ad → Clone parameters → Create new ad → Copy creative
- Output: New ad ID
- Use case: A/B testing, scaling successful ads

#### Creative Building Logic

**Object Story Spec Structure**:
- Page ID: Facebook page that owns the ad
- Link data: Contains URL, image/video, copy, CTA
- Template data: For dynamic creative formats
- Instagram actor ID: For Instagram placements

**Call-to-Action Configuration**:
- Type selection based on campaign objective
- Shop Now, Learn More, Sign Up, etc.
- Different CTAs for different placements
- CTA button vs link click tracking

**Creative Variation Handling**:
- Dynamic Creative: Multiple assets automatically tested
- Flexible Format: AI-optimized format selection
- Manual variations: Create separate ads for A/B testing

**Platform-Specific Requirements**:
- Instagram: Requires Instagram Actor ID
- Stories: 9:16 aspect ratio mandatory
- Feed: 1:1 or 1.91:1 aspect ratios
- Reels: 9:16 vertical video only

---

### 5. Insights Agent

**Role**: Analytics, reporting, and performance monitoring specialist

#### Primary Responsibilities

**Data Retrieval**:
- Fetch campaign-level metrics
- Retrieve ad set performance data
- Get ad-level analytics
- Query account-wide insights
- Support custom date ranges and breakdowns

**Report Generation**:
- Aggregate metrics across entities
- Calculate derived metrics (CTR, CPA, ROAS)
- Format data for presentation
- Support multiple export formats
- Generate comparative analyses

**Performance Monitoring**:
- Track key performance indicators
- Identify underperforming entities
- Flag anomalies and trends
- Compare against benchmarks
- Provide optimization recommendations

**Breakdown Analysis**:
- Demographic segmentation (age, gender)
- Geographic performance (country, region, city)
- Placement analysis (platform, position)
- Time-based trends (hourly, daily, weekly)
- Device type breakdowns

#### Operations

**Get Campaign Insights**:
- Input: Campaign ID + date range + metrics + breakdowns
- Process: Query insights API → Parse response → Calculate derived metrics
- Output: Performance data object with summary and breakdowns
- Aggregation: Rolls up all ad sets and ads under campaign

**Get Ad Set Insights**:
- Input: Ad set ID + date range + metrics + breakdowns
- Process: Query insights API → Parse response → Segment data
- Output: Performance data with demographic/geographic splits
- Aggregation: Rolls up all ads under ad set

**Get Ad Insights**:
- Input: Ad ID + date range + metrics + breakdowns
- Process: Query insights API → Parse response → Format results
- Output: Granular ad-level performance data
- Granularity: Lowest level of reporting

**Get Account Insights**:
- Input: Ad account ID + date range + level (campaign/adset/ad)
- Process: Query all entities → Aggregate results → Generate summary
- Output: Account-wide performance overview
- Use case: Portfolio analysis, budget allocation

**Generate Report**:
- Input: Entity IDs + template + date range + metrics
- Process: Fetch all relevant data → Apply calculations → Format per template
- Output: Structured report (JSON, CSV, or formatted text)
- Templates: Performance summary, demographic analysis, placement comparison

**Compare Performance**:
- Input: Two or more entity IDs + metrics
- Process: Fetch data for all entities → Calculate differences → Rank performance
- Output: Comparative analysis with winners/losers
- Use case: A/B test analysis, ad set optimization

**Export Data**:
- Input: Query parameters + export format
- Process: Fetch data → Transform to format → Generate file
- Output: Downloadable file (CSV, JSON, Excel)
- Formats: Support multiple export formats

#### Metrics Processing Logic

**Core Performance Metrics**:
- Impressions: Total ad views
- Reach: Unique users who saw ad
- Frequency: Average views per user (impressions/reach)
- Clicks: All click types
- Link clicks: Outbound clicks only
- CTR: (clicks/impressions) × 100
- CPC: spend/clicks
- CPM: (spend/impressions) × 1000

**Engagement Metrics**:
- Reactions: Likes, loves, wow, etc.
- Comments: All comment interactions
- Shares: Post share count
- Saves: Post save count
- Video views: 3-second+ views
- ThruPlays: 15-second+ or complete views

**Conversion Metrics**:
- Actions: All conversion events
- Purchase events: Completed transactions
- Lead events: Form submissions
- Add to cart: Cart addition events
- Conversion value: Monetary value of conversions
- ROAS: (conversion value/spend) × 100
- CPA: spend/conversions

**Video-Specific Metrics**:
- 3-second views: Quick engagement metric
- 10-second views: Deeper engagement
- 25%, 50%, 75%, 100% completion rates
- Average watch time: Mean seconds viewed
- ThruPlay rate: Completion percentage

#### Breakdown Logic

**Demographic Breakdowns**:
- Age buckets: 18-24, 25-34, 35-44, 45-54, 55-64, 65+
- Gender: Male, Female, Unknown
- Combined: Age-gender intersections

**Geographic Breakdowns**:
- Country: ISO country codes
- Region: State/province level
- DMA: Designated Market Areas (US)
- City: Urban area level

**Placement Breakdowns**:
- Publisher platform: Facebook, Instagram, Messenger, etc.
- Platform position: Feed, Stories, Reels, etc.
- Device platform: Mobile, desktop, tablet

**Time Breakdowns**:
- Hourly: 24-hour segments
- Daily: Day-by-day performance
- Weekly: 7-day aggregations
- Monthly: Calendar month totals

#### Report Generation Logic

**Template Processing**:
1. Load report template configuration
2. Identify required metrics and breakdowns
3. Fetch all necessary data from insights API
4. Apply calculations and transformations
5. Format according to template specification
6. Add visualizations if requested
7. Return structured report object

**Performance Analysis**:
- Calculate period-over-period changes
- Identify statistically significant trends
- Flag performance anomalies
- Compare against account benchmarks
- Generate optimization recommendations

**Data Aggregation**:
- Roll up ad-level data to ad set level
- Roll up ad set data to campaign level
- Roll up campaign data to account level
- Maintain granular data for drill-down
- Handle data gaps and missing values

---

## Workflow Logic

### Workflow 1: Create Complete Campaign

**Objective**: Create a full campaign from scratch with assets, campaigns, ad sets, and ads

**Input from Ambient Agent**:
- Campaign details (name, objective, budget)
- Ad set configurations (targeting, optimization)
- Ad specifications (copy, links, CTAs)
- Asset files (images/videos)

**Execution Sequence**:

**Step 1: Asset Upload (Parallel)**
- Orchestrator extracts all asset references from request
- Routes asset array to Asset Agent
- Asset Agent uploads all assets concurrently
- Returns hash/ID mapping for each asset
- Orchestrator stores asset mappings

**Step 2: Campaign Creation (Sequential)**
- Orchestrator extracts campaign parameters
- Routes to Campaign Agent
- Campaign Agent creates campaign entity
- Returns campaign ID
- Orchestrator stores campaign ID

**Step 3: Ad Set Creation (Parallel)**
- Orchestrator injects campaign ID into each ad set config
- Routes all ad set configs to Campaign Agent
- Campaign Agent creates ad sets concurrently
- Returns array of ad set IDs
- Orchestrator stores ad set ID mappings

**Step 4: Creative Creation (Sequential per ad)**
- Orchestrator processes each ad definition
- Injects asset hashes from Step 1 mapping
- Routes to Ad Creation Agent
- Ad Creation Agent builds creative with assets
- Returns creative ID for each ad
- Orchestrator stores creative ID mappings

**Step 5: Ad Creation (Parallel)**
- Orchestrator injects ad set IDs and creative IDs
- Routes all ad configs to Ad Creation Agent
- Ad Creation Agent creates all ads concurrently
- Returns array of ad IDs
- Orchestrator stores ad ID mappings

**Step 6: Response Compilation**
- Orchestrator aggregates all created entity IDs
- Formats response with hierarchical structure
- Adds metadata (creation timestamps, status)
- Returns to Ambient Agent

**Success Criteria**:
- All assets uploaded successfully
- Campaign created with correct objective
- All ad sets created under campaign
- All creatives created with correct assets
- All ads created and linked properly

**Failure Handling**:
- If asset upload fails: Abort workflow, return error
- If campaign creation fails: Cleanup assets, abort
- If ad set creation fails: Cleanup campaign and assets
- If creative creation fails: Cleanup hierarchy, retry once
- If ad creation fails: Mark failed ads, return partial success

---

### Workflow 2: Update Campaign Budget

**Objective**: Modify budget for existing campaign or ad set

**Input from Ambient Agent**:
- Entity ID (campaign or ad set)
- New budget amount
- Budget type (daily or lifetime)

**Execution Sequence**:

**Step 1: Validation**
- Orchestrator validates entity ID exists
- Checks new budget against minimums
- Verifies budget type compatibility
- Confirms user has update permissions

**Step 2: Learning Phase Check**
- Orchestrator queries current status via Campaign Agent
- Determines if entity is in learning phase
- Calculates budget change percentage
- Assesses learning phase impact

**Step 3: Update Execution**
- If change > 20%: Warn about learning phase reset
- Route update to Campaign Agent
- Campaign Agent performs API update
- Returns confirmation of new budget

**Step 4: Verification**
- Orchestrator queries entity to confirm change
- Checks that budget was applied correctly
- Verifies no unintended side effects

**Step 5: Response**
- Return success with new budget details
- Include warning if learning phase was reset
- Provide recommendation for monitoring period

**Edge Cases**:
- Budget decrease below minimum: Reject with error
- Campaign at spending limit: Warn before applying
- Lifetime budget without end date: Require end date
- CBO campaign: Cannot set ad set budgets

---

### Workflow 3: Generate Performance Report

**Objective**: Create comprehensive performance analysis

**Input from Ambient Agent**:
- Entity IDs (campaigns, ad sets, or ads)
- Date range
- Metrics to include
- Breakdowns to apply
- Report format

**Execution Sequence**:

**Step 1: Query Planning**
- Orchestrator analyzes request complexity
- Determines if single or multiple API calls needed
- Plans breakdown strategy to avoid rate limits
- Identifies parallel query opportunities

**Step 2: Data Retrieval (Parallel)**
- Route all queries to Insights Agent
- Insights Agent fetches data concurrently
- Each query targets specific breakdown
- Results stream back as they complete

**Step 3: Data Aggregation**
- Orchestrator collects all query results
- Insights Agent merges data from multiple sources
- Resolves any data conflicts or duplicates
- Handles missing data gracefully

**Step 4: Calculation & Analysis**
- Calculate derived metrics (CTR, CPA, ROAS)
- Perform period-over-period comparisons
- Identify top/bottom performers
- Flag statistical anomalies
- Generate optimization insights

**Step 5: Formatting**
- Structure data according to requested format
- Apply visualization hints if applicable
- Add executive summary
- Include recommendations
- Attach raw data appendix

**Step 6: Response Delivery**
- Return formatted report to Ambient Agent
- Include metadata (generation time, data freshness)
- Provide export options if applicable

**Optimization Logic**:
- Cache frequently requested metrics
- Use date presets when possible (faster)
- Limit breakdowns to essential dimensions
- Batch related queries together
- Stream results for large reports

---

### Workflow 4: Pause Underperforming Ads

**Objective**: Automatically identify and pause ads not meeting performance thresholds

**Input from Ambient Agent**:
- Campaign ID or ad set ID
- Performance thresholds (CPA, ROAS, CTR)
- Date range for evaluation
- Minimum spend before evaluation

**Execution Sequence**:

**Step 1: Data Collection**
- Orchestrator queries all ads under specified entity
- Routes insights request to Insights Agent
- Retrieve performance metrics for evaluation period
- Filter out ads below minimum spend threshold

**Step 2: Performance Evaluation**
- Insights Agent calculates key metrics per ad
- Compare each ad against thresholds
- Identify ads failing any threshold
- Rank ads by performance score
- Generate list of ads to pause

**Step 3: Impact Analysis**
- Calculate total reach of ads to be paused
- Estimate budget reallocation opportunity
- Predict campaign impact of pausing
- Generate recommendation report

**Step 4: Execution (if auto-approved)**
- Route pause commands to Ad Creation Agent
- Ad Creation Agent pauses identified ads
- Confirm status change for each ad
- Log all paused ad IDs

**Step 5: Optimization Recommendations**
- Identify top-performing ads for budget increase
- Suggest new targeting based on winners
- Recommend creative variations to test
- Calculate optimal budget reallocation

**Step 6: Response**
- Return list of paused ads with reasons
- Include performance comparison
- Provide optimization action items
- Attach detailed analysis report

**Safety Checks**:
- Never pause all ads (keep at least one active)
- Require minimum 7 days of data
- Ensure statistical significance
- Flag manual review if pausing >50% of ads

---

### Workflow 5: A/B Test Campaign

**Objective**: Create controlled experiment with variations

**Input from Ambient Agent**:
- Base campaign configuration
- Test variations (audiences, creatives, placements)
- Split percentage
- Success metric
- Test duration

**Execution Sequence**:

**Step 1: Test Design**
- Orchestrator validates test parameters
- Calculates budget split based on percentages
- Determines sample size requirements
- Plans entity creation sequence

**Step 2: Control Group Creation**
- Create base campaign with 50% budget
- Create ad sets for control variant
- Upload control assets via Asset Agent
- Create control creatives and ads
- Label all entities with "Control" tag

**Step 3: Test Group Creation (Parallel)**
- Create variation campaigns with remaining budget
- Apply test variations (different targeting, creative, etc.)
- Upload test assets concurrently
- Create test creatives and ads
- Label all entities with "Variant A", "Variant B", etc.

**Step 4: Synchronization**
- Ensure all variants launch simultaneously
- Set identical start times
- Verify budget parity or intended split
- Activate all groups at once

**Step 5: Monitoring Setup**
- Configure automated performance tracking
- Set up alerts for significant differences
- Schedule interim check-ins
- Prepare stopping rules (early winner detection)

**Step 6: Response**
- Return all campaign/ad set/ad IDs
- Provide test tracking dashboard
- Include success criteria
- Set automated report schedule

**Test Monitoring**:
- Daily automated performance checks
- Statistical significance testing
- Early stopping if clear winner emerges
- Final analysis at test conclusion

---

## Communication Protocol

### Request Structure

**Standard Request Format**:

Every request from Ambient Agent to Orchestrator includes:

**Header Section**:
- Agent ID: Unique identifier for Ambient Agent instance
- Request ID: UUID for tracking and idempotency
- Timestamp: ISO 8601 format with timezone
- Priority: High, medium, or low (affects queue position)

**Authentication Section**:
- Ad account ID: Target META ad account
- Access token: OAuth bearer token
- Pixel ID: For conversion tracking (if applicable)
- Business ID: For business-scoped operations (if applicable)

**Action Section**:
- Action type: Specific operation to perform
- Target entities: IDs of entities to operate on
- Parameters: Operation-specific configuration

**Data Section**:
- Payload: Complete data for creation/update operations
- Nested objects follow META API structure
- All IDs use string format
- Currency values in smallest unit (cents)

**Options Section**:
- Auto-publish: Whether to activate immediately
- Validation only: Run validation without execution
- Dry run: Simulate without creating entities
- Notifications: Whether to send completion alerts
- Timeout: Maximum execution time in seconds

### Response Structure

**Standard Response Format**:

Every response from Orchestrator to Ambient Agent includes:

**Status Section**:
- Status code: Success, partial success, or failure
- Request ID: Matches original request for correlation
- Timestamp: When response was generated
- Execution time: Total processing duration

**Results Section**:
- Created entities: Array of newly created entity IDs with types
- Updated entities: Array of modified entity IDs with changes
- Failed operations: Array of operations that failed with reasons
- Metadata: Additional context about execution

**Data Section**:
- Entity details: Full object representations if requested
- Performance metrics: Insights data if applicable
- Related entities: Connected entities affected by operation

**Warnings Section**:
- Non-critical issues encountered
- Best practice violations
- Recommendations for improvement
- Future deprecation notices

**Next Steps Section**:
- Suggested follow-up actions
- Required manual interventions
- Optimization opportunities
- Monitoring recommendations

### Inter-Agent Communication

**Orchestrator to Specialized Agent**:

**Task Assignment Format**:
- Task ID: Unique identifier for this specific task
- Task type: Specific operation to perform
- Priority: Execution priority level
- Dependencies: IDs of prerequisite tasks
- Payload: Complete data needed for execution
- Timeout: Maximum execution time
- Retry policy: Number of retries and backoff strategy

**Specialized Agent to Orchestrator**:

**Task Completion Format**:
- Task ID: Matches original assignment
- Status: Success or failure
- Result data: Created IDs, hashes, or retrieved data
- Execution time: How long task took
- Warnings: Any issues encountered
- Metadata: Additional context

**Event Notifications**:
- Progress updates for long-running operations
- Milestone completions
- Error conditions requiring attention
- State changes requiring coordination

### Idempotency Handling

**Request Deduplication**:
- Every request includes unique request ID
- Orchestrator maintains request cache (1 hour TTL)
- Duplicate requests return cached response
- Prevents accidental double-creation
- Safe retry mechanism for clients

**Entity Conflict Resolution**:
- Check if entity with same name exists
- Compare parameters to detect duplicates
- Return existing ID if exact match
- Fail with error if similar but different
- Provide override option for intentional duplicates

---

## Error Handling & Recovery

### Error Classification

**Level 1: Input Validation Errors**
- Invalid parameters
- Missing required fields
- Out-of-range values
- Incompatible combinations
- **Recovery**: Return error immediately, no cleanup needed

**Level 2: Authentication Errors**
- Expired access token
- Insufficient permissions
- Invalid ad account ID
- Rate limit exceeded
- **Recovery**: Pause operation, request token refresh, retry

**Level 3: Resource Creation Errors**
- Asset upload failure
- Campaign creation failure
- API quota exceeded
- **Recovery**: Cleanup created resources, retry with backoff

**Level 4: State Inconsistency Errors**
- Parent entity doesn't exist
- Budget conflict with CBO
- Learning phase conflicts
- **Recovery**: Synchronize state, retry operation

**Level 5: Partial Success Scenarios**
- Some ads created, others failed
- Batch upload with failures
- Multi-step workflow interrupted
- **Recovery**: Return partial results, enable resume

### Retry Logic

**Exponential Backoff Strategy**:

**Attempt 1**:
- Wait: 0 seconds
- Action: Execute immediately

**Attempt 2**:
- Wait: 2 seconds
- Action: Retry after brief pause

**Attempt 3**:
- Wait: 4 seconds
- Action: Retry with longer pause

**Attempt 4**:
- Wait: 8 seconds
- Action: Final retry attempt

**Attempt 5**:
- Wait: 16 seconds
- Action: Last attempt before failure

**Max Attempts**: 5
**Max Total Wait**: 30 seconds
**Jitter**: Add random 0-1 second to prevent thundering herd

**Retry Conditions**:
- Network timeouts: Always retry
- Rate limits: Retry with exponential backoff
- Server errors (5xx): Retry up to 3 times
- Client errors (4xx): Do not retry (except 429)
- Validation errors: Do not retry

### Rollback Mechanisms

**Transaction Log**:
- Record every entity creation with timestamp
- Store entity IDs and types in order
- Maintain parent-child relationships
- Enable reverse-order cleanup

**Cleanup Process**:

**Step 1: Identify Scope**
- Determine which entities were created
- Build dependency tree
- Identify orphaned resources

**Step 2: Delete in Reverse Order**
- Delete ads first
- Then delete creatives
- Then delete ad sets
- Then delete campaigns
- Finally cleanup assets if unused

**Step 3: Verification**
- Confirm each deletion succeeded
- Handle deletion failures gracefully
- Log all cleanup actions
- Return cleanup summary

**Partial Cleanup**:
- If some entities should be kept, mark them
- Only cleanup unmarked entities
- Update transaction log
- Enable manual review of kept entities

### State Recovery

**Checkpoint System**:
- Save state after each major step
- Include all created entity IDs
- Store in durable storage
- Enable resume from any checkpoint

**Resume Logic**:
1. Load checkpoint data
2. Verify entities still exist via API
3. Determine which step failed
4. Resume from failed step
5. Skip already-completed steps
6. Continue workflow to completion

**Conflict Resolution**:
- Detect if state changed during downtime
- Merge manual changes with planned changes
- Resolve conflicts conservatively
- Flag conflicts for manual review

---

## Design Decisions

### Why 4 Agents?

**Agent 1: Orchestrator**
- **Rationale**: Central coordination is essential
- **Alternative considered**: Peer-to-peer agent communication
- **Rejected because**: Creates O(n²) communication complexity
- **Benefits**: Single point of control, easier debugging

**Agent 2: Asset Agent**
- **Rationale**: Asset upload is I/O-bound and parallelizable
- **Alternative considered**: Combine with Ad Creation Agent
- **Rejected because**: Creates bottleneck, can't parallelize effectively
- **Benefits**: Parallel upload, asset reuse across campaigns

**Agent 3: Campaign Agent**
- **Rationale**: Campaigns and ad sets are tightly coupled
- **Alternative considered**: Separate campaign and ad set agents
- **Rejected because**: Always created together, 90% shared logic
- **Benefits**: Fewer handoffs, atomic campaign creation

**Agent 4: Ad Creation Agent**
- **Rationale**: Creatives and ads must be created together
- **Alternative considered**: Separate creative and ad agents
- **Rejected because**: Always created in sequence, tight coupling
- **Benefits**: Atomic ad creation, easier creative management

**Agent 5: Insights Agent**
- **Rationale**: Completely separate concern (read vs write)
- **Alternative considered**: Combine with Orchestrator
- **Rejected because**: Complex metric processing, different scaling needs
- **Benefits**: Specialized analytics logic, independent scaling

### Data Flow Patterns

**Sequential Dependencies**:
- Used when: Later step requires output from earlier step
- Example: Creative creation requires asset hash from upload
- Implementation: Step B waits for Step A completion
- Benefit: Data consistency guaranteed

**Parallel Execution**:
- Used when: Steps have no dependencies
- Example: Uploading multiple images simultaneously
- Implementation: Async/await with gather/Promise.all
- Benefit: Reduced total execution time

**Pipeline Processing**:
- Used when: Streaming data through transformations
- Example: Report generation with multiple data sources
- Implementation: Process data as it arrives, don't wait for all
- Benefit: Lower memory usage, faster time-to-first-byte

### Caching Strategy

**What to Cache**:

**Targeting Catalog Data**:
- Interest IDs and names (30-day TTL)
- Behavior IDs and names (30-day TTL)
- Location keys (90-day TTL)
- Rationale: Rarely changes, frequently reused

**Asset Hashes**:
- Image hash to file mapping (24-hour TTL)
- Video ID to file mapping (24-hour TTL)
- Rationale: Enable asset reuse, reduce uploads

**Access Tokens**:
- Token validity status (5-minute TTL)
- Permission scopes (15-minute TTL)
- Rationale: Reduce auth API calls

**What Not to Cache**:

**Performance Metrics**:
- Insights data (always fetch fresh)
- Campaign status (may change frequently)
- Budget usage (real-time critical)
- Rationale: Stale data causes bad decisions

**Entity Configuration**:
- Targeting settings (may be updated)
- Creative content (may be modified)
- Budget amounts (may be changed)
- Rationale: Must reflect current state

### Rate Limiting Strategy

**API Call Budgeting**:
- Total limit: 200 calls per user per hour
- Reserve 20% for critical operations
- Allocate 50% to insights (heaviest use)
- Allocate 30% to creation operations
- Rationale: Prevent exhaustion during peak loads

**Throttling Logic**:
- Track calls in sliding 1-hour window
- Pause new requests at 90% capacity
- Queue non-urgent requests
- Prioritize critical operations
- Alert when consistently hitting limits

**Batch Optimization**:
- Combine related API calls when possible
- Use bulk endpoints for multiple entities
- Fetch multiple metrics in single insights call
- Upload multiple images in one request
- Rationale: Reduce total API call count

---

## Scalability & Performance

### Horizontal Scaling

**Orchestrator Agent**:
- Deployment: Multiple instances behind load balancer
- State: Stateless design, stores nothing locally
- Coordination: Use distributed locks for conflicts
- Benefit: Linear scaling with load

**Specialized Agents**:
- Deployment: Auto-scaling based on queue depth
- State: Stateless, pull tasks from queue
- Coordination: No inter-agent coordination needed
- Benefit: Scale independently based on demand

**Queue-Based Architecture**:
- Orchestrator publishes tasks to queues
- Specialized agents consume from queues
- Multiple consumers per queue for parallelism
- Dead letter queue for failed tasks
- Benefit: Decouples components, enables auto-scaling

### Performance Optimization

**Parallel Processing**:

**Asset Upload**:
- Upload up to 10 assets concurrently
- Monitor bandwidth and throttle if needed
- Use connection pooling
- Benefit: 10x faster than sequential

**Ad Set Creation**:
- Create up to 5 ad sets in parallel
- Respect API rate limits
- Use batch API when available
- Benefit: 5x faster campaign setup

**Insights Queries**:
- Fetch multiple date ranges in parallel
- Query different breakdowns concurrently
- Stream results as they arrive
- Benefit: Report generation 3-5x faster

**Caching Effectiveness**:

**L1 Cache (In-Memory)**:
- Duration: 5-15 minutes
- Contents: Targeting IDs, token validation
- Size: <100MB per instance
- Hit rate target: >80%

**L2 Cache (Distributed)**:
- Duration: 1-24 hours
- Contents: Asset hashes, catalog data
- Size: <1GB total
- Hit rate target: >60%

**Cache Invalidation**:
- Time-based expiry (TTL)
- Event-based invalidation (on updates)
- Manual purge option
- Stale-while-revalidate pattern

### Database Design

**Entity Storage**:
- Store all created entity IDs
- Maintain parent-child relationships
- Index by ad account ID
- Enable fast lookups and traversals

**Transaction Log**:
- Append-only log of all operations
- Include timestamps and actors
- Store request and response payloads
- Enable audit trails and debugging

**Metrics Cache**:
- Store frequently accessed insights
- Aggregate at multiple levels (ad, ad set, campaign)
- Update incrementally
- Reduce API call volume

---

## Monitoring & Observability

### Metrics Collection

**Request Metrics**:
- Total requests per minute
- Request latency (p50, p95, p99)
- Success rate percentage
- Error rate by type
- Active concurrent requests

**Agent Metrics**:
- Task queue depth per agent
- Task processing time per agent
- Agent error rate
- Agent resource utilization
- Task completion rate

**API Metrics**:
- META API calls per minute
- API error rate by endpoint
- API latency distribution
- Rate limit proximity (% used)
- Quota consumption rate

**Business Metrics**:
- Campaigns created per hour
- Total ad spend under management
- Average campaign setup time
- Insights queries per day
- Asset upload success rate

### Logging Strategy

**Structured Logging**:

**Log Entry Format**:
- Timestamp (ISO 8601 with microseconds)
- Request ID (for correlation)
- Agent name (which component)
- Action (what operation)
- Entity IDs (what entities involved)
- Duration (how long it took)
- Status (success/failure)
- Error details (if failed)
- Metadata (additional context)

**Log Levels**:

**DEBUG**:
- Detailed execution flow
- Parameter values
- API request/response payloads
- Use: Development and troubleshooting

**INFO**:
- Request received
- Task started/completed
- Entity created/updated
- Use: Normal operation tracking

**WARN**:
- Retry attempts
- Rate limit approaching
- Configuration issues
- Use: Potential problems

**ERROR**:
- Operation failures
- API errors
- Validation failures
- Use: Actual problems

**CRITICAL**:
- System-wide failures
- Data corruption
- Security issues
- Use: Immediate attention required

### Alerting Rules

**P0 (Critical) Alerts**:
- Orchestrator down
- >50% error rate for 5 minutes
- Security breach detected
- Data corruption detected
- Response: Page on-call immediately

**P1 (High) Alerts**:
- Single agent unresponsive
- >25% error rate for 15 minutes
- Rate limit exceeded
- API quota exhausted
- Response: Notify within 15 minutes

**P2 (Medium) Alerts**:
- High latency (p95 >10s for 30 min)
- Error rate >10% for 1 hour
- Cache hit rate <50%
- Queue depth >1000 tasks
- Response: Notify within 1 hour

**P3 (Low) Alerts**:
- Increased retry rate
- Slow drift in metrics
- Configuration drift
- Deprecation warnings
- Response: Daily review

### Health Checks

**Agent Health**:
- Heartbeat every 30 seconds
- Process basic test request
- Verify API connectivity
- Check queue accessibility
- Report resource usage

**Dependency Health**:
- META API reachability
- Authentication token validity
- Database connectivity
- Cache availability
- Queue service status

**End-to-End Health**:
- Create test campaign (canary)
- Upload test asset
- Fetch test insights
- Verify complete workflow
- Run every 5 minutes
- Clean up test entities

---

## Best Practices

### Request Optimization

**Batch Operations**:
- Group related entities when possible
- Create multiple ad sets in one request
- Upload multiple assets together
- Fetch multiple metrics simultaneously
- Benefit: Fewer API calls, faster execution

**Parameter Validation**:
- Validate all inputs before API calls
- Check against known constraints
- Verify ID formats and existence
- Catch errors early
- Benefit: Reduce wasted API calls

**Selective Field Retrieval**:
- Only request needed fields
- Use field projection in queries
- Avoid fetching entire objects
- Reduce payload size
- Benefit: Faster responses, less bandwidth

### Error Prevention

**Pre-flight Checks**:
- Verify token hasn't expired
- Confirm ad account is active
- Check budget availability
- Validate targeting parameters
- Benefit: Catch issues before creation

**Defensive Programming**:
- Assume external services can fail
- Handle null/undefined gracefully
- Validate all external data
- Use strict type checking
- Benefit: More robust system

**Graceful Degradation**:
- Continue with partial data if possible
- Provide fallback values
- Skip optional features on failure
- Never fail completely on non-critical errors
- Benefit: Better user experience

### Maintenance Procedures

**Regular Audits**:
- Review error logs weekly
- Analyze performance trends monthly
- Check for API deprecations
- Update documentation
- Verify compliance requirements

**Capacity Planning**:
- Monitor queue depths
- Track API usage trends
- Forecast growth needs
- Plan scaling events
- Provision ahead of demand

**Disaster Recovery**:
- Maintain operation playbooks
- Test failover procedures quarterly
- Keep backup credentials
- Document recovery steps
- Practice incident response

### Security Considerations

**Token Management**:
- Never log access tokens
- Rotate tokens regularly
- Use minimum required scopes
- Store encrypted at rest
- Implement token refresh

**Data Privacy**:
- Hash PII in logs
- Comply with GDPR/CCPA
- Implement data retention policies
- Support right-to-deletion
- Audit data access

**Access Control**:
- Implement role-based access
- Require authentication for all operations
- Audit all sensitive operations
- Use principle of least privilege
- Monitor for suspicious activity

---

## Appendix

### Glossary

**Ambient Agent**: External orchestrating system that initiates META marketing operations

**Orchestrator Agent**: Central coordinator managing workflow and specialized agents

**Asset Agent**: Specialized agent handling image/video uploads

**Campaign Agent**: Specialized agent managing campaigns and ad sets

**Ad Creation Agent**: Specialized agent handling creatives and ads

**Insights Agent**: Specialized agent fetching analytics and reports

**CBO**: Campaign Budget Optimization - META feature for automatic budget allocation

**ODAX**: Outcome-Driven Ad Experiences - META's simplified objective framework

**Learning Phase**: Initial period where META's algorithm learns optimal delivery

**ROAS**: Return on Ad Spend - Revenue generated per dollar spent

**CPA**: Cost Per Action - Average cost for each conversion

**CTR**: Click-Through Rate - Percentage of impressions that result in clicks

**CPM**: Cost Per Mille - Cost per 1,000 impressions

**Attribution Window**: Time period for attributing conversions to ads

**Lookalike Audience**: Audience similar to existing customers

**Custom Audience**: Audience from your own data (website, customer list)

**Flexible Spec**: Targeting specification allowing interest/behavior combinations

### Common Workflow Patterns

**Pattern 1: Asset → Creative → Ad**
- Upload asset first
- Use hash in creative
- Link creative to ad
- Most common pattern

**Pattern 2: Campaign → AdSet → Ad**
- Create hierarchy top-down
- Inject parent IDs at each level
- Enables batch creation

**Pattern 3: Create → Test → Optimize**
- Create initial entities
- Monitor performance
- Pause/adjust based on data
- Continuous improvement cycle

**Pattern 4: Duplicate → Modify → Compare**
- Copy successful entity
- Change one variable
- Run A/B test
- Determine winner

### Troubleshooting Guide

**Issue: Asset Upload Fails**
- Check file size and format
- Verify dimensions and aspect ratio
- Ensure network connectivity
- Check ad account permissions
- Try different asset source

**Issue: Campaign Creation Fails**
- Verify access token validity
- Check ad account status
- Validate objective parameter
- Ensure budget meets minimums
- Review special ad categories

**Issue: Targeting Errors**
- Validate location keys exist
- Check interest/behavior IDs
- Verify age range is valid
- Ensure audience exists
- Review placement compatibility

**Issue: Insights Not Returning**
- Check date range validity
- Verify entity has data
- Ensure metrics are valid for entity type
- Check breakdown compatibility
- Reduce query complexity

**Issue: Rate Limit Hit**
- Reduce request frequency
- Implement exponential backoff
- Use batch endpoints
- Cache frequently accessed data
- Spread load across time

---

## Document Version

**Version**: 1.0
**Last Updated**: January 2026
**Authors**: System Architecture Team
**Status**: Approved
**Next Review**: March 2026