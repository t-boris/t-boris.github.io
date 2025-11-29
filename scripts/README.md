# Events Aggregator

This directory contains the scripts and workflows for the daily events aggregator functionality.

## How it works

1. **Daily Schedule**: GitHub Actions runs every day at 3:00 UTC
2. **Data Collection**: Python script searches Google for local events using configured queries
3. **AI Analysis**: OpenAI GPT-4 analyzes search results and categorizes events
4. **Data Storage**: Results are saved to `public/events-data/events.json`
5. **Auto Rebuild**: Astro automatically rebuilds the site with new data

## Required GitHub Secrets

You need to set up the following secrets in your GitHub repository settings:

1. **OPENAI_API_KEY** - Your OpenAI API key for GPT-4 access
2. **GOOGLE_API_KEY** - Google Custom Search API key
3. **SEARCH_ENGINE_ID** - Google Custom Search Engine ID
4. **TARGET_ADDRESS** - The location to search for (e.g., "San Francisco, CA")
5. **SEARCH_QUERIES** - Comma-separated search query templates (use `{address}` placeholder)

Example SEARCH_QUERIES:
```
events near {address},news {address},community {address},upcoming events {address}
```

## Setting up secrets

Use GitHub CLI to set secrets:

```bash
gh secret set OPENAI_API_KEY
gh secret set GOOGLE_API_KEY
gh secret set SEARCH_ENGINE_ID
gh secret set TARGET_ADDRESS
gh secret set SEARCH_QUERIES
```

Or set them manually in GitHub repository settings:
Settings → Secrets and variables → Actions → New repository secret

## Manual Trigger

You can manually trigger the events update from GitHub Actions:
Actions → Daily Events Update → Run workflow

## Local Testing

To test locally:

1. Install Python dependencies:
   ```bash
   pip install -r scripts/requirements.txt
   ```

2. Set environment variables:
   ```bash
   export OPENAI_API_KEY="your-key"
   export GOOGLE_API_KEY="your-key"
   export SEARCH_ENGINE_ID="your-id"
   export TARGET_ADDRESS="Your City, State"
   export SEARCH_QUERIES="events near {address},news {address}"
   ```

3. Run the script:
   ```bash
   python scripts/update_events.py
   ```

## Event Categories

Events are automatically categorized into:
- Culture
- Sports
- Community News
- Upcoming Events
- Incidents
- Society
