# Events System Documentation

## Overview

The Events System is a fully automated pipeline that collects, analyzes, geocodes, and displays local events for the Gurnee, IL area and surrounding Lake County suburbs. The system runs daily, automatically updating the events page with new information.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Daily Workflow (3:00 UTC)                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Google Custom Search API                                 │
│     ↓ (4 search queries × 14 suburbs)                       │
│                                                               │
│  2. OpenAI GPT-5.1-chat-latest                              │
│     ↓ (Analyze, classify, extract dates/locations)          │
│                                                               │
│  3. Geocoding (3-tier fallback)                             │
│     • KNOWN_LOCATIONS (14 suburbs)                          │
│     • Cache (geocode-cache.json)                            │
│     • Google Geocoding API                                  │
│     ↓                                                        │
│                                                               │
│  4. Idempotency & Freshness                                 │
│     • Deduplicate by title + event_date                     │
│     • Remove events not seen in 3 days                      │
│     • Remove past events                                    │
│     ↓                                                        │
│                                                               │
│  5. Storage                                                  │
│     • active-events.json (current events)                   │
│     • YYYY-MM-DD.json (daily snapshot)                      │
│     • geocode-cache.json (location cache)                   │
│     • trusted-sources.json (source tracking)                │
│     ↓                                                        │
│                                                               │
│  6. Auto-Deploy                                              │
│     • Commit changes to main                                │
│     • Trigger deploy workflow                               │
│     • Build Astro site                                      │
│     • Deploy to GitHub Pages                                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. **Automated Event Collection**
- Runs daily at 3:00 UTC via GitHub Actions
- Searches Google for events in 14 Lake County suburbs
- Uses 4 different search queries to maximize coverage
- Collects up to 15 results per query (60 total)

### 2. **AI-Powered Event Analysis**
- Uses OpenAI GPT-5.1-chat-latest for intelligent event extraction
- Classifies events into 7 categories:
  - Business
  - Manufacturing
  - Community
  - Culture
  - Sports
  - News
  - Incidents
- Extracts structured data:
  - Title
  - Description
  - Event date (YYYY-MM-DD)
  - Location
  - Link to source

### 3. **Smart Geocoding**
- 3-tier fallback system for maximum efficiency:
  1. **KNOWN_LOCATIONS**: 14 suburbs hardcoded with coordinates
  2. **Cache**: Previously geocoded locations stored in JSON
  3. **API**: Google Geocoding API for new locations
- Prevents redundant API calls
- Handles geocoding failures gracefully

### 4. **Data Quality & Freshness**
- **Idempotency**: Events deduplicated by `title + event_date` key
- **3-Day Freshness Rule**: Events must be re-confirmed within 3 days or removed
- **Past Event Removal**: Events with dates in the past are automatically deleted
- **Source Tracking**: Tracks trusted sources (never deleted, accumulates forever)

### 5. **Enhanced Calendar UI**
- Interactive month-view calendar
- Month navigation (prev/next buttons)
- Event count badges on days with events
- Today highlighting
- Click-to-filter functionality
- Responsive design

### 6. **Error Handling & Reliability**
- Retry logic with exponential backoff (3 retries, 2s → 4s → 8s)
- Comprehensive error handling for:
  - API failures (Google Search, OpenAI, Geocoding)
  - File I/O errors
  - JSON parsing errors
  - Network failures
- Structured logging with timestamps
- Graceful degradation

## File Structure

```
project/
├── .github/workflows/
│   ├── daily_events_update.yml      # Daily event collection (3:00 UTC)
│   ├── monthly_cleanup.yml           # Monthly snapshot cleanup (1st of month)
│   └── deploy.yml                    # Astro build & deploy
│
├── scripts/
│   ├── update_events.py              # Main event collection script
│   └── requirements.txt              # Python dependencies
│
├── public/events-data/
│   ├── active-events.json            # Current active events
│   ├── geocode-cache.json            # Geocoding cache
│   ├── trusted-sources.json          # Source tracking
│   └── YYYY-MM-DD.json               # Daily snapshots (90-day retention)
│
└── src/pages/
    └── events.astro                  # Events page with calendar
```

## Data Models

### active-events.json
```json
{
  "event title|2025-12-01": {
    "title": "Event Title",
    "event_date": "2025-12-01",
    "found_date": "2025-11-30",
    "description": "Event description...",
    "link": "https://source.com/event",
    "location": "Gurnee",
    "category": "Community",
    "lat": 42.3703,
    "lng": -87.9023
  }
}
```

### geocode-cache.json
```json
{
  "gurnee": {
    "lat": 42.3703,
    "lng": -87.9023
  }
}
```

### trusted-sources.json
```json
{
  "example.com": {
    "count": 15,
    "first_seen": "2025-11-01",
    "last_seen": "2025-11-30"
  }
}
```

## Configuration

### GitHub Secrets (Required)

| Secret | Description | Used By |
|--------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-5.1 | Event analysis |
| `GOOGLE_API_KEY` | Google API key for Search + Geocoding | Search & geocoding |
| `GOOGLE_SEARCH_ENGINE_ID` | Custom Search Engine ID | Search queries |
| `GOOGLE_MAPS_API_KEY` | Google Maps JavaScript API key | Frontend map display |

### Environment Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `TARGET_ADDRESS` | "Gurnee, IL" | Center point for event search |
| `SEARCH_QUERIES` | "placeholder" | Legacy (queries built dynamically) |

### Target Suburbs

The system searches for events in these 14 Lake County, IL suburbs:
- Gurnee
- Waukegan
- Beach Park
- Lindenhurst
- Round Lake Beach
- Grayslake
- Mundelein
- Vernon Hills
- Libertyville
- Lake Villa
- Wauconda
- Antioch
- Zion
- North Chicago

## Workflows

### Daily Events Update (`.github/workflows/daily_events_update.yml`)

**Schedule**: Daily at 3:00 UTC (9:00 PM CST)

**Steps**:
1. Checkout repository
2. Set up Python 3.10
3. Install dependencies (`pip install -r scripts/requirements.txt`)
4. Run event collection script
5. Commit changes to `public/events-data/`
6. **If changes exist**: Trigger deploy workflow
7. Deploy workflow builds Astro site and deploys to GitHub Pages

**Trigger**: Scheduled cron OR manual via GitHub UI

### Monthly Cleanup (`.github/workflows/monthly_cleanup.yml`)

**Schedule**: 1st of each month at 00:00 UTC

**Steps**:
1. Find all daily snapshot files (`20*.json`)
2. Delete files older than 90 days
3. Commit changes

**Trigger**: Scheduled cron OR manual via GitHub UI

## API Quotas & Limits

### Google Custom Search API
- **Free Tier**: 100 requests/day
- **Usage**: 4 search queries per day
- **Remaining**: 96 requests/day buffer

### OpenAI GPT-5.1-chat-latest
- **Model**: gpt-5.1-chat-latest
- **Usage**: 1 request per day (~15 results analyzed)
- **Cost**: Variable based on token usage

### Google Geocoding API
- **Free Tier**: $200/month credit (≈40,000 requests)
- **Usage**: Minimal (uses cache & known locations)
- **Cost**: Nearly zero (cache hits)

## Setup Instructions

### 1. Enable Required APIs

Go to [Google Cloud Console](https://console.cloud.google.com/):

1. **Enable APIs**:
   - Custom Search API
   - Geocoding API ⚠️ **(Required - Currently Not Enabled)**
   - Maps JavaScript API

2. **Create API Key** (if not done):
   - Go to "Credentials" → "Create Credentials" → "API Key"
   - Restrict key to your domain (optional but recommended)
   - Add to GitHub Secrets

### 2. Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions:

```bash
# Required secrets:
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...              # For Search + Geocoding
GOOGLE_SEARCH_ENGINE_ID=...
GOOGLE_MAPS_API_KEY=AIza...         # For frontend Maps
```

### 3. Install Python Dependencies

Locally:
```bash
pip install -r scripts/requirements.txt
```

Dependencies:
- `requests` - HTTP requests
- `openai` - OpenAI API client

### 4. Manual Testing

Test the event collection locally:

```bash
# Set environment variables
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AIza..."
export GOOGLE_SEARCH_ENGINE_ID="..."
export TARGET_ADDRESS="Gurnee, IL"
export SEARCH_QUERIES="placeholder"

# Run script
python scripts/update_events.py
```

## Monitoring & Maintenance

### Check Workflow Status

```bash
# View recent runs
gh run list --workflow="Daily Events Update"

# Watch live run
gh run watch <run-id>

# View logs
gh run view <run-id> --log
```

### Monitor Data Quality

Check these metrics:
- **Active Events Count**: Should have 5-20 events typically
- **Trusted Sources**: Should grow over time (never decreases)
- **Geocoding Success Rate**: Check how many events have `lat`/`lng`
- **Event Categories**: Should be diverse (not all "News")

### Common Issues

#### 1. **Geocoding Fails (REQUEST_DENIED)**

**Cause**: Geocoding API not enabled

**Solution**:
1. Go to Google Cloud Console
2. Enable "Geocoding API"
3. Wait 5-10 minutes for propagation
4. Re-run workflow

#### 2. **No Events Found**

**Cause**: Google Search quota exhausted OR bad search queries

**Solution**:
1. Check Google Cloud Console quota usage
2. Review search query construction in `update_events.py`
3. Adjust search terms if needed

#### 3. **Deploy Not Triggered**

**Cause**: `github-script` action failed OR no changes to commit

**Solution**:
1. Check workflow logs for errors
2. Verify `GITHUB_TOKEN` has proper permissions
3. Check if events data actually changed

## Troubleshooting

### View Logs

```bash
# Daily events workflow
gh run list --workflow="Daily Events Update" --limit 5
gh run view <run-id> --log

# Deploy workflow
gh run list --workflow="Deploy to GitHub Pages" --limit 5
```

### Test Locally

```bash
# Run event collection
cd /path/to/project
python scripts/update_events.py

# Check output
cat public/events-data/active-events.json | jq '.'
```

### Debug Geocoding

Check if location is in cache:
```bash
cat public/events-data/geocode-cache.json | jq '.gurnee'
```

Check KNOWN_LOCATIONS in script:
```python
KNOWN_LOCATIONS = {
    "Gurnee": {"lat": 42.3703, "lng": -87.9023},
    # ... 13 more suburbs
}
```

## Performance Optimization

### Current Optimizations
- ✅ Geocoding cache (prevents redundant API calls)
- ✅ KNOWN_LOCATIONS for 14 suburbs (no API calls needed)
- ✅ Retry logic with exponential backoff
- ✅ 90-day snapshot retention (prevents infinite growth)

### Future Optimizations
- ⏳ Rate limiting for API calls
- ⏳ Batch geocoding for efficiency
- ⏳ CDN caching for static event data
- ⏳ Incremental builds (only rebuild on changes)

## Statistics

### Current Status (as of 2025-11-30)

| Metric | Value |
|--------|-------|
| Active Events | 11 |
| Trusted Sources | 3 |
| Geocode Cache Size | ~14 locations |
| Daily Snapshots | 2 days |
| Workflow Success Rate | 100% |

### Event Distribution

| Category | Count |
|----------|-------|
| Community | 6 |
| News | 3 |
| Business | 1 |
| Culture | 1 |

## Changelog

### 2025-11-30 - v1.0 Complete Implementation
- ✅ Backend data collection system
- ✅ Enhanced calendar widget with month navigation
- ✅ Error handling and retry logic
- ✅ Comprehensive logging
- ✅ Auto-deployment after events update
- ✅ Monthly cleanup workflow
- ⚠️ Geocoding API needs to be enabled

### Next Steps
1. Enable Geocoding API in Google Cloud Console
2. Monitor first week of automated runs
3. Adjust search queries based on event quality
4. Add monitoring/alerting for failures

## Support

For issues or questions:
1. Check workflow logs: `gh run view <run-id> --log`
2. Review this documentation
3. Check [plan.md](plan.md) for original design
4. File an issue in the repository

---

**Last Updated**: 2025-11-30
**System Status**: ✅ Operational (Geocoding API needs enablement)
**Next Scheduled Run**: Daily at 3:00 UTC
