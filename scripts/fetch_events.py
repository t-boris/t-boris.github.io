#!/usr/bin/env python3
"""
Local Events Fetcher for Jekyll Blog
=====================================

This script fetches local events from Google Custom Search API,
analyzes them with OpenAI, and stores results in events.json.

Author: Claude Code
Date: 2025-11-01
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests

# ============================================================================
# Configuration Loading
# ============================================================================

def load_config() -> Dict[str, Any]:
    """
    Load configuration from config/events.json

    Returns:
        dict: Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    config_path = Path(__file__).parent.parent / 'config' / 'events.json'

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    print(f"✓ Configuration loaded from {config_path}")
    return config


def load_secrets() -> Dict[str, str]:
    """
    Load API keys from environment variables (GitHub Secrets)

    Returns:
        dict: Dictionary with API keys

    Raises:
        ValueError: If required secrets are missing
    """
    secrets = {
        'google_api_key': os.getenv('GOOGLE_API_KEY'),
        'google_search_engine_id': os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
        'openai_api_key': os.getenv('OPENAI_API_KEY')
    }

    # Validate all secrets are present
    missing = [k for k, v in secrets.items() if not v]
    if missing:
        raise ValueError(f"Missing required secrets: {', '.join(missing)}")

    print("✓ API secrets loaded from environment")
    return secrets


# ============================================================================
# Query Generation
# ============================================================================

def get_cities_for_today(config: Dict[str, Any]) -> List[str]:
    """
    Determine which group of cities to query based on day of week

    Monday, Wednesday, Friday -> Group 1
    Tuesday, Thursday, Saturday, Sunday -> Group 2

    Args:
        config: Configuration dictionary

    Returns:
        list: List of city names for today
    """
    today = datetime.now().strftime('%A')  # Monday, Tuesday, etc.

    group_1_days = config['schedule']['group_1_days']
    group_2_days = config['schedule']['group_2_days']

    if today in group_1_days:
        cities = config['cities']['group_1']
        group = "Group 1"
    elif today in group_2_days:
        cities = config['cities']['group_2']
        group = "Group 2"
    else:
        # Fallback to group 1 if day not found
        cities = config['cities']['group_1']
        group = "Group 1 (fallback)"

    print(f"✓ Today is {today} -> Using {group}: {len(cities)} cities")
    return cities


def build_queries(cities: List[str], config: Dict[str, Any]) -> List[str]:
    """
    Generate search queries from templates and city list

    Args:
        cities: List of city names
        config: Configuration dictionary

    Returns:
        list: List of search query strings
    """
    templates = config['query_templates']
    queries = []

    for city in cities:
        for template in templates:
            query = template.replace('{city}', city)
            queries.append(query)

    print(f"✓ Generated {len(queries)} queries ({len(cities)} cities × {len(templates)} templates)")
    return queries


# ============================================================================
# Google Custom Search API Integration
# ============================================================================

def fetch_google_results(
    query: str,
    api_key: str,
    search_engine_id: str,
    num_results: int = 10,
    max_retries: int = 3
) -> List[Dict[str, Any]]:
    """
    Fetch search results from Google Custom Search API

    Args:
        query: Search query string
        api_key: Google API key
        search_engine_id: Custom Search Engine ID
        num_results: Number of results to fetch (max 10 per request)
        max_retries: Number of retry attempts on failure

    Returns:
        list: List of search result dictionaries with 'title', 'link', 'snippet'
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': query,
        'num': min(num_results, 10)  # API max is 10
    }

    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            items = data.get('items', [])

            # Extract relevant fields
            results = []
            for item in items:
                results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })

            return results

        except requests.exceptions.RequestException as e:
            print(f"  ⚠ Attempt {attempt + 1}/{max_retries} failed for query '{query[:50]}...': {e}")

            if attempt < max_retries - 1:
                # Wait before retry (exponential backoff)
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                print(f"  ✗ Failed to fetch results for query '{query[:50]}...' after {max_retries} attempts")
                return []

    return []


def fetch_all_search_results(
    queries: List[str],
    api_key: str,
    search_engine_id: str,
    config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Fetch results for all queries with rate limiting

    Args:
        queries: List of search queries
        api_key: Google API key
        search_engine_id: Custom Search Engine ID
        config: Configuration dictionary

    Returns:
        list: Combined list of all search results
    """
    all_results = []
    results_per_query = config['google_config']['results_per_query']
    total_limit = config['google_config'].get('total_results_limit', 50)

    print(f"\n🔍 Fetching search results from Google...")

    for i, query in enumerate(queries, 1):
        print(f"  [{i}/{len(queries)}] Querying: {query[:60]}...")

        results = fetch_google_results(
            query=query,
            api_key=api_key,
            search_engine_id=search_engine_id,
            num_results=results_per_query,
            max_retries=config['openai_config']['max_retries']
        )

        all_results.extend(results)

        # Respect API rate limits (slight delay between requests)
        if i < len(queries):
            time.sleep(0.5)

        # Stop if we've hit the total limit
        if len(all_results) >= total_limit:
            print(f"  ℹ Reached total results limit ({total_limit}), stopping")
            break

    print(f"✓ Fetched {len(all_results)} total search results\n")
    return all_results


# ============================================================================
# OpenAI API Integration
# ============================================================================

def analyze_with_openai(
    results: List[Dict[str, Any]],
    current_date: str,
    api_key: str,
    config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Send search results to OpenAI for event extraction and analysis

    Args:
        results: List of Google search results
        current_date: Current date in YYYY-MM-DD format
        api_key: OpenAI API key
        config: Configuration dictionary

    Returns:
        list: List of extracted events
    """
    if not results:
        print("⚠ No search results to analyze")
        return []

    # Prepare the prompt
    categories_list = ', '.join(config['categories'])

    # Format search results for prompt
    results_text = "\n\n".join([
        f"Title: {r['title']}\nURL: {r['link']}\nSnippet: {r['snippet']}"
        for r in results[:50]  # Limit to 50 results to stay within token limits
    ])

    prompt = f"""Current date: {current_date}

Analyze these search results and extract local events, news, and updates.

IMPORTANT RULES:
- SKIP events that already happened (dates before {current_date})
- ONLY include current events, upcoming events, or events without specific dates
- Focus on recent news and future happenings

For each relevant event or news item you find, provide:
- category: Choose from [{categories_list}] or create a new appropriate category
- title: Clear, concise event name or headline
- description: Brief description (2-3 sentences maximum)
- link: Source URL
- tags: Array of 2-5 relevant keywords
- event_date: YYYY-MM-DD format if specific date is mentioned AND it's today or in the future, otherwise "unknown"

IMPORTANT: Return ONLY a valid JSON array. No markdown formatting, no code blocks, no explanations.

Search Results:
{results_text}

Return JSON array of events:"""

    model = config['openai_config']['model']
    max_retries = config['openai_config']['max_retries']
    retry_delay = config['openai_config']['retry_delay_seconds']

    print(f"🤖 Analyzing results with OpenAI ({model})...")

    for attempt in range(max_retries):
        try:
            # Using the official OpenAI library
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts structured event data from search results. Always return valid JSON arrays."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000
            )

            # Parse the response
            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()

            # Parse JSON
            events = json.loads(content)

            # Validate structure
            if not isinstance(events, list):
                raise ValueError("OpenAI did not return a list")

            # Validate each event has required fields
            required_fields = ['category', 'title', 'description', 'link', 'tags', 'event_date']
            validated_events = []

            for event in events:
                if all(field in event for field in required_fields):
                    # Filter out past events (except "unknown" dates)
                    event_date = event.get('event_date', 'unknown')
                    if event_date != 'unknown' and event_date < current_date:
                        print(f"  ⚠ Skipping past event ({event_date}): {event.get('title', 'N/A')}")
                        continue

                    # Add found_date
                    event['found_date'] = current_date
                    validated_events.append(event)
                else:
                    print(f"  ⚠ Skipping invalid event (missing fields): {event.get('title', 'N/A')}")

            print(f"✓ Extracted {len(validated_events)} valid events from {len(results)} search results\n")
            return validated_events

        except json.JSONDecodeError as e:
            print(f"  ⚠ Attempt {attempt + 1}/{max_retries} - JSON parse error: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

        except Exception as e:
            print(f"  ⚠ Attempt {attempt + 1}/{max_retries} - OpenAI API error: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)

    print(f"✗ Failed to analyze results after {max_retries} attempts\n")
    return []


# ============================================================================
# Events JSON Management
# ============================================================================

def load_events_json() -> Dict[str, List[Dict[str, Any]]]:
    """
    Load existing events.json file

    Returns:
        dict: Events dictionary (date -> list of events)
    """
    events_path = Path(__file__).parent.parent / '_data' / 'events.json'

    if events_path.exists():
        with open(events_path, 'r', encoding='utf-8') as f:
            events = json.load(f)
        print(f"✓ Loaded existing events.json ({len(events)} dates)")
        return events
    else:
        print("ℹ events.json doesn't exist yet, will create new file")
        return {}


def find_duplicate_by_link(events_dict: Dict[str, List[Dict[str, Any]]], link: str) -> Optional[tuple]:
    """
    Find an event by link across all dates

    Args:
        events_dict: Events dictionary
        link: URL to search for

    Returns:
        tuple: (date, event_index) if found, None otherwise
    """
    for date, events_list in events_dict.items():
        for idx, event in enumerate(events_list):
            if event.get('link') == link:
                return (date, idx)
    return None


def merge_events(
    events_dict: Dict[str, List[Dict[str, Any]]],
    new_events: List[Dict[str, Any]],
    current_date: str
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Merge new events into existing events dictionary
    Updates duplicates (by link) or adds new events

    Args:
        events_dict: Existing events dictionary
        new_events: List of new events to merge
        current_date: Current date string

    Returns:
        dict: Updated events dictionary
    """
    updates_count = 0
    additions_count = 0

    for new_event in new_events:
        link = new_event['link']
        duplicate = find_duplicate_by_link(events_dict, link)

        if duplicate:
            # Update existing event
            date, idx = duplicate
            events_dict[date][idx] = new_event
            updates_count += 1
        else:
            # Add new event under found_date
            found_date = new_event['found_date']
            if found_date not in events_dict:
                events_dict[found_date] = []
            events_dict[found_date].append(new_event)
            additions_count += 1

    print(f"✓ Merged events: {additions_count} new, {updates_count} updated")
    return events_dict


def cleanup_old_events(events_dict: Dict[str, List[Dict[str, Any]]], config: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Remove events older than retention period

    Args:
        events_dict: Events dictionary
        config: Configuration dictionary

    Returns:
        dict: Cleaned events dictionary
    """
    if not config['data_retention']['cleanup_enabled']:
        return events_dict

    keep_days = config['data_retention']['keep_days']
    cutoff_date = (datetime.now() - timedelta(days=keep_days)).strftime('%Y-%m-%d')

    dates_to_remove = [date for date in events_dict.keys() if date < cutoff_date]

    for date in dates_to_remove:
        del events_dict[date]

    if dates_to_remove:
        print(f"✓ Cleaned up {len(dates_to_remove)} dates older than {keep_days} days")

    return events_dict


def save_events_json(events_dict: Dict[str, List[Dict[str, Any]]]):
    """
    Save events dictionary to _data/events.json with sorted dates

    Args:
        events_dict: Events dictionary to save
    """
    events_path = Path(__file__).parent.parent / '_data' / 'events.json'

    # Sort by date (descending)
    sorted_events = dict(sorted(events_dict.items(), reverse=True))

    with open(events_path, 'w', encoding='utf-8') as f:
        json.dump(sorted_events, f, indent=2, ensure_ascii=False)

    total_events = sum(len(events) for events in sorted_events.values())
    print(f"✓ Saved events.json: {len(sorted_events)} dates, {total_events} total events")


# ============================================================================
# Markdown Archive Generation
# ============================================================================

def create_markdown_for_date(date: str, events: List[Dict[str, Any]]):
    """
    Create markdown archive file for a specific date

    Args:
        date: Date string (YYYY-MM-DD)
        events: List of events for this date
    """
    md_path = Path(__file__).parent.parent / '_event_archives' / f'{date}.md'

    # Don't overwrite if already exists
    if md_path.exists():
        return

    # Group events by category
    by_category = {}
    for event in events:
        category = event['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(event)

    # Generate markdown content
    lines = [
        "---",
        "layout: event-day",
        f"date: {date}",
        "---",
        "",
        f"# Events Archive - {date}",
        ""
    ]

    # Add events by category
    for category in sorted(by_category.keys()):
        lines.append(f"## {category}")
        lines.append("")

        for event in by_category[category]:
            lines.append(f"### {event['title']}")
            lines.append("")
            lines.append(event['description'])
            lines.append("")
            lines.append(f"**Link**: [{event['link']}]({event['link']})")
            lines.append("")
            if event.get('event_date') and event['event_date'] != 'unknown':
                lines.append(f"**Event Date**: {event['event_date']}")
                lines.append("")
            if event.get('tags'):
                tags_str = ', '.join([f"`{tag}`" for tag in event['tags']])
                lines.append(f"**Tags**: {tags_str}")
                lines.append("")
            lines.append("---")
            lines.append("")

    # Write file
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"✓ Created markdown archive: {md_path.name}")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Main execution function"""
    print("=" * 70)
    print("🎉 LOCAL EVENTS FETCHER")
    print("=" * 70)
    print()

    try:
        # 1. Load configuration and secrets
        config = load_config()
        secrets = load_secrets()

        # 2. Determine cities for today
        cities = get_cities_for_today(config)

        # 3. Build search queries
        queries = build_queries(cities, config)

        # 4. Fetch search results from Google
        search_results = fetch_all_search_results(
            queries=queries,
            api_key=secrets['google_api_key'],
            search_engine_id=secrets['google_search_engine_id'],
            config=config
        )

        # 5. Analyze results with OpenAI
        current_date = datetime.now().strftime('%Y-%m-%d')
        new_events = analyze_with_openai(
            results=search_results,
            current_date=current_date,
            api_key=secrets['openai_api_key'],
            config=config
        )

        if not new_events:
            print("ℹ No events found today")
            # Still save to preserve data
            events_dict = load_events_json()
            save_events_json(events_dict)
            return 0

        # 6. Load existing events and merge
        events_dict = load_events_json()
        events_dict = merge_events(events_dict, new_events, current_date)

        # 7. Cleanup old events (if enabled)
        events_dict = cleanup_old_events(events_dict, config)

        # 8. Save updated events.json
        save_events_json(events_dict)

        # 9. Create markdown archive for yesterday (if not exists)
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        if yesterday in events_dict:
            create_markdown_for_date(yesterday, events_dict[yesterday])

        print()
        print("=" * 70)
        print("✅ SUCCESS: Events fetched and saved!")
        print("=" * 70)
        return 0

    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ ERROR: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
