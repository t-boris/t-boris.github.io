import os
import json
import requests
from datetime import datetime, timezone
from openai import OpenAI
from collections import defaultdict

# Target suburbs within 20-mile radius of Gurnee, IL
SUBURBS = [
    "Gurnee", "Waukegan", "Beach Park", "Lindenhurst", "Round Lake Beach",
    "Grayslake", "Mundelein", "Vernon Hills", "Libertyville", "Lake Villa",
    "Wauconda", "Antioch", "Zion", "North Chicago"
]

# Known locations for geocoding cache
KNOWN_LOCATIONS = {
    "Gurnee": {"lat": 42.3703, "lng": -87.9023},
    "Waukegan": {"lat": 42.3636, "lng": -87.8448},
    "Beach Park": {"lat": 42.4239, "lng": -87.8576},
    "Lindenhurst": {"lat": 42.4108, "lng": -88.0287},
    "Round Lake Beach": {"lat": 42.3714, "lng": -88.0901},
    "Grayslake": {"lat": 42.3414, "lng": -88.0418},
    "Mundelein": {"lat": 42.2631, "lng": -88.0040},
    "Vernon Hills": {"lat": 42.2194, "lng": -87.9795},
    "Libertyville": {"lat": 42.2831, "lng": -87.9534},
    "Lake Villa": {"lat": 42.4167, "lng": -88.0723},
    "Wauconda": {"lat": 42.2589, "lng": -88.1390},
    "Antioch": {"lat": 42.4772, "lng": -88.0956},
    "Zion": {"lat": 42.4461, "lng": -87.8328},
    "North Chicago": {"lat": 42.3256, "lng": -87.8410},
    "7612 Cascade Way, Gurnee": {"lat": 42.3703, "lng": -87.9023}  # User's home
}

# Valid event categories
CATEGORIES = ["Business", "Manufacturing", "Community", "Culture", "Sports", "News", "Incidents"]

def load_config():
    """Loads configuration from environment variables."""
    config = {
        "openai_api_key": os.environ.get("OPENAI_API_KEY"),
        "google_api_key": os.environ.get("GOOGLE_API_KEY"),
        "search_engine_id": os.environ.get("SEARCH_ENGINE_ID") or os.environ.get("GOOGLE_SEARCH_ENGINE_ID"),
        "target_address": os.environ.get("TARGET_ADDRESS"),
        "search_queries_raw": os.environ.get("SEARCH_QUERIES"),
    }
    if not all(config.values()):
        raise ValueError("One or more environment variables are not set!")

    config["search_queries"] = [q.strip() for q in config["search_queries_raw"].split(',')]
    return config

def fetch_google_search_results(api_key, cx_id, query):
    """Performs a Google search and returns the results."""
    print(f"Searching for: {query}...")
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx_id}&q={query}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("items", [])
    except requests.exceptions.RequestException as e:
        print(f"Error during search: {e}")
        return []

def analyze_with_openai(client, search_results, address):
    """Analyzes search results with OpenAI and generates structured JSON."""
    print("Analyzing results with OpenAI...")

    simplified_results = [{"title": item.get("title"), "link": item.get("link"), "snippet": item.get("snippet")} for item in search_results[:15]]

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    prompt = f"""
    Analyze the following search results related to events around the address "{address}".
    Today's date is {today_str}.

    Search Results:
    {json.dumps(simplified_results, indent=2, ensure_ascii=False)}

    Your task is to return a JSON object containing a list of key events.
    Each event must have the fields: "category", "title", "description", "link", "event_date", and "location".

    For event_date:
    - If the event mentions a specific date, use that date in YYYY-MM-DD format
    - If the event is described as "today" or "happening now", use {today_str}
    - If the event is "upcoming" or "this weekend" or similar, estimate a date within the next 7 days
    - If no date can be determined, use {today_str}

    For location:
    - Extract the specific location/venue name if mentioned (e.g., "Gurnee Mills", "Waukegan Harbor")
    - If only a city is mentioned, use the city name (e.g., "Gurnee", "Waukegan")
    - If no location is specified, set to null

    Use ONLY these categories: "Business", "Manufacturing", "Community", "Culture", "Sports", "News", "Incidents".

    Return ONLY a JSON object with an "events" key containing the array, without any extra text.
    Example:
    {{
      "events": [
        {{ "category": "Community", "title": "Fair in the Park", "description": "An autumn fair will be held this weekend.", "link": "http://example.com", "event_date": "2025-12-01", "location": "Gurnee" }}
      ]
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency with Chat Completions API
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful assistant that returns structured JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        data = json.loads(response.choices[0].message.content)

        # Handle dict wrapper from OpenAI
        if isinstance(data, dict):
            for key in data:
                if isinstance(data[key], list):
                    return data[key]
            # If dict has no list values, wrap the dict in an array
            return [data]

        # If data is already a list, return it
        if isinstance(data, list):
            return data

        # Fallback: wrap in array
        return [data] if data else []
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return []

def generate_event_key(title, event_date):
    """Generate unique key for idempotency check."""
    return f"{title.lower().strip()}|{event_date}"

def load_active_events():
    """Load active events from storage."""
    events_path = "public/events-data/active-events.json"
    if os.path.exists(events_path):
        with open(events_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_active_events(events):
    """Save active events to storage."""
    events_path = "public/events-data/active-events.json"
    os.makedirs("public/events-data", exist_ok=True)
    with open(events_path, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def load_geocode_cache():
    """Load geocoding cache."""
    cache_path = "public/events-data/geocode-cache.json"
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_geocode_cache(cache):
    """Save geocoding cache."""
    cache_path = "public/events-data/geocode-cache.json"
    os.makedirs("public/events-data", exist_ok=True)
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def load_trusted_sources():
    """Load trusted sources tracking."""
    sources_path = "public/events-data/trusted-sources.json"
    if os.path.exists(sources_path):
        with open(sources_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_trusted_sources(sources):
    """Save trusted sources tracking."""
    sources_path = "public/events-data/trusted-sources.json"
    os.makedirs("public/events-data", exist_ok=True)
    with open(sources_path, 'w', encoding='utf-8') as f:
        json.dump(sources, f, ensure_ascii=False, indent=2)

def extract_domain(url):
    """Extract domain from URL for source tracking."""
    if not url:
        return "Unknown"
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        # Remove www. prefix if present
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except:
        return "Unknown"

def geocode_location(location, google_api_key, cache):
    """
    Geocode a location using hybrid approach:
    1. Check KNOWN_LOCATIONS
    2. Check cache
    3. Call Google Geocoding API
    """
    if not location:
        return None, None

    location_key = location.lower().strip()

    # Step 1: Check known locations
    if location in KNOWN_LOCATIONS:
        coords = KNOWN_LOCATIONS[location]
        return coords["lat"], coords["lng"]

    # Step 2: Check cache
    if location_key in cache:
        coords = cache[location_key]
        return coords["lat"], coords["lng"]

    # Step 3: Call Google Geocoding API
    print(f"Geocoding new location via API: {location}")
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": f"{location}, Lake County, Illinois",
        "key": google_api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data["status"] == "OK" and len(data["results"]) > 0:
            loc_data = data["results"][0]["geometry"]["location"]
            lat, lng = loc_data["lat"], loc_data["lng"]

            # Save to cache
            cache[location_key] = {"lat": lat, "lng": lng}
            save_geocode_cache(cache)

            print(f"Geocoded {location} -> ({lat}, {lng})")
            return lat, lng
        else:
            print(f"Geocoding failed for {location}: {data['status']}")
            return None, None
    except Exception as e:
        print(f"Error geocoding {location}: {e}")
        return None, None

def update_events_data(new_events, google_api_key=None):
    """Updates the events with idempotency and freshness validation."""
    print("Updating events data with idempotency...")
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_date = datetime.now(timezone.utc).date()

    # Load existing active events, geocoding cache, and trusted sources
    active_events = load_active_events()
    geocode_cache = load_geocode_cache()
    trusted_sources = load_trusted_sources()

    # Process each new event
    for event in new_events:
        if not event.get("title") or not event.get("event_date"):
            continue

        # Track source (never delete)
        if event.get("link"):
            domain = extract_domain(event["link"])
            if domain not in trusted_sources:
                trusted_sources[domain] = {"count": 0, "first_seen": today_str}
            trusted_sources[domain]["count"] += 1
            trusted_sources[domain]["last_seen"] = today_str

        # Generate unique key
        event_key = generate_event_key(event["title"], event["event_date"])

        # Check if event already exists
        if event_key in active_events:
            # Update existing event
            print(f"Updating existing event: {event['title']}")
            active_events[event_key]["found_date"] = today_str  # Update last seen date
            active_events[event_key]["description"] = event.get("description", "")
            active_events[event_key]["link"] = event.get("link", "")
            if event.get("location"):
                active_events[event_key]["location"] = event["location"]
        else:
            # Add new event
            print(f"Adding new event: {event['title']}")

            # Geocode location if provided
            lat, lng = None, None
            if event.get("location") and google_api_key:
                lat, lng = geocode_location(event["location"], google_api_key, geocode_cache)

            active_events[event_key] = {
                "title": event["title"],
                "event_date": event["event_date"],
                "found_date": today_str,
                "description": event.get("description", ""),
                "link": event.get("link", ""),
                "location": event.get("location"),
                "category": event.get("category", "News"),
                "lat": lat,
                "lng": lng
            }

    # Apply 3-day freshness rule: remove events not seen in 3 days
    events_to_remove = []
    for event_key, event_data in active_events.items():
        found_date = datetime.strptime(event_data["found_date"], "%Y-%m-%d").date()
        days_since_found = (today_date - found_date).days

        # Remove if not seen in 3 days (validation rule)
        if days_since_found >= 3:
            print(f"Removing stale event (not seen in {days_since_found} days): {event_data['title']}")
            events_to_remove.append(event_key)
            continue

        # Remove if event date is in the past
        event_date = datetime.strptime(event_data["event_date"], "%Y-%m-%d").date()
        if event_date < today_date:
            print(f"Removing past event: {event_data['title']} ({event_data['event_date']})")
            events_to_remove.append(event_key)

    # Remove stale/past events
    for event_key in events_to_remove:
        del active_events[event_key]

    # Save updated active events and trusted sources
    save_active_events(active_events)
    save_trusted_sources(trusted_sources)

    # Also create daily snapshot for historical reference
    daily_events = [event for event in active_events.values()]
    day_path = f"public/events-data/{today_str}.json"
    with open(day_path, 'w', encoding='utf-8') as f:
        json.dump(daily_events, f, ensure_ascii=False, indent=2)

    print(f"Events data updated successfully. Active events: {len(active_events)}, Trusted sources: {len(trusted_sources)}")

if __name__ == "__main__":
    print("Starting daily events update process...")
    config = load_config()
    all_results = []

    # Build search queries for each suburb
    search_queries = []
    for suburb in SUBURBS:
        # Create queries with explicit OR operators for all suburbs
        suburbs_string = " OR ".join(SUBURBS)
        search_queries.extend([
            f"events today ({suburbs_string}) Lake County Illinois",
            f"news today ({suburbs_string}) Lake County Illinois",
            f"community events ({suburbs_string}) Lake County",
            f"business news ({suburbs_string}) Lake County Illinois"
        ])
        break  # Only need to run once since suburbs_string contains all suburbs

    # Execute searches
    for query in search_queries:
        all_results.extend(fetch_google_search_results(
            config["google_api_key"], config["search_engine_id"], query
        ))

    if all_results:
        openai_client = OpenAI(api_key=config["openai_api_key"])
        newly_generated_events = analyze_with_openai(openai_client, all_results, config["target_address"])

        if newly_generated_events:
            update_events_data(newly_generated_events, google_api_key=config["google_api_key"])
            print("Process completed successfully.")
        else:
            print("Failed to generate content from OpenAI.")
    else:
        print("No search results found. Exiting.")
