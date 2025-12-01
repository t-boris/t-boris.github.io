import os
import json
import requests
import logging
import time
import hashlib
from datetime import datetime, timezone
from openai import OpenAI
from collections import defaultdict
from functools import wraps
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

def retry_with_exponential_backoff(max_retries=3, initial_delay=1, backoff_factor=2):
    """
    Decorator that retries a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        backoff_factor: Multiplier for delay after each retry
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts: {e}")

            raise last_exception
        return wrapper
    return decorator

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

@retry_with_exponential_backoff(max_retries=3, initial_delay=2, backoff_factor=2)
def fetch_google_search_results(api_key, cx_id, query):
    """Performs a Google search and returns the results."""
    logger.info(f"Searching for: {query}...")
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx_id}&q={query}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("items", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error during search: {e}")
        return []

@retry_with_exponential_backoff(max_retries=3, initial_delay=2, backoff_factor=2)
def analyze_with_openai(client, search_results, address):
    """Analyzes search results with OpenAI and generates structured JSON."""
    logger.info("Analyzing results with OpenAI...")

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
            model="gpt-5-mini",  # Using GPT-5 mini for cost-effective event extraction
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
        logger.error(f"Error with OpenAI API: {e}")
        return []

def generate_event_key(title, event_date):
    """Generate unique key for idempotency check."""
    return f"{title.lower().strip()}|{event_date}"

def load_active_events():
    """Load active events from storage."""
    events_path = "public/events-data/active-events.json"
    try:
        if os.path.exists(events_path):
            with open(events_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    logger.warning(f"Invalid active events format, resetting to empty dict")
                    return {}
                return data
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading active events: {e}. Starting with empty dict.")
    return {}

def save_active_events(events):
    """Save active events to storage."""
    events_path = "public/events-data/active-events.json"
    try:
        os.makedirs("public/events-data", exist_ok=True)
        with open(events_path, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved {len(events)} active events to {events_path}")
    except (IOError, OSError) as e:
        logger.error(f"Error saving active events: {e}")

def load_geocode_cache():
    """Load geocoding cache."""
    cache_path = "public/events-data/geocode-cache.json"
    try:
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    logger.warning(f"Invalid geocode cache format, resetting to empty dict")
                    return {}
                return data
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading geocode cache: {e}. Starting with empty dict.")
    return {}

def save_geocode_cache(cache):
    """Save geocoding cache."""
    cache_path = "public/events-data/geocode-cache.json"
    try:
        os.makedirs("public/events-data", exist_ok=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except (IOError, OSError) as e:
        logger.error(f"Error saving geocode cache: {e}")

def load_trusted_sources():
    """Load trusted sources tracking."""
    sources_path = "public/events-data/trusted-sources.json"
    try:
        if os.path.exists(sources_path):
            with open(sources_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    logger.warning(f"Invalid trusted sources format, resetting to empty dict")
                    return {}
                return data
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading trusted sources: {e}. Starting with empty dict.")
    return {}

def save_trusted_sources(sources):
    """Save trusted sources tracking."""
    sources_path = "public/events-data/trusted-sources.json"
    try:
        os.makedirs("public/events-data", exist_ok=True)
        with open(sources_path, 'w', encoding='utf-8') as f:
            json.dump(sources, f, ensure_ascii=False, indent=2)
    except (IOError, OSError) as e:
        logger.error(f"Error saving trusted sources: {e}")

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
    logger.info(f"Geocoding new location via API: {location}")
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

            logger.info(f"Geocoded {location} -> ({lat}, {lng})")
            return lat, lng
        else:
            logger.warning(f"Geocoding failed for {location}: {data['status']}")
            return None, None
    except Exception as e:
        logger.error(f"Error geocoding {location}: {e}")
        return None, None

@retry_with_exponential_backoff(max_retries=2, initial_delay=1, backoff_factor=2)
def extract_image_from_url(url):
    """
    Extract Open Graph image or first suitable image from a URL.
    Returns the image URL if found, None otherwise.
    """
    if not url:
        return None

    try:
        logger.info(f"Extracting image from URL: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try Open Graph image first (og:image)
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image_url = og_image['content']
            # Make absolute URL if relative
            if not image_url.startswith('http'):
                image_url = urljoin(url, image_url)
            logger.info(f"Found Open Graph image: {image_url}")
            return image_url

        # Try Twitter card image
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            image_url = twitter_image['content']
            if not image_url.startswith('http'):
                image_url = urljoin(url, image_url)
            logger.info(f"Found Twitter card image: {image_url}")
            return image_url

        # Try finding first large image in content
        images = soup.find_all('img')
        for img in images:
            src = img.get('src') or img.get('data-src')
            if src:
                # Skip small images (icons, logos, etc.)
                width = img.get('width')
                height = img.get('height')
                if width and height:
                    try:
                        if int(width) >= 400 and int(height) >= 300:
                            if not src.startswith('http'):
                                src = urljoin(url, src)
                            logger.info(f"Found content image: {src}")
                            return src
                    except ValueError:
                        pass
                else:
                    # If no size specified, check if it's not an icon/logo
                    if 'icon' not in src.lower() and 'logo' not in src.lower():
                        if not src.startswith('http'):
                            src = urljoin(url, src)
                        logger.info(f"Found content image: {src}")
                        return src

        logger.warning(f"No suitable image found at {url}")
        return None

    except Exception as e:
        logger.error(f"Error extracting image from {url}: {e}")
        return None

@retry_with_exponential_backoff(max_retries=2, initial_delay=1, backoff_factor=2)
def download_and_save_image(image_url, event_title):
    """
    Download an image and save it locally.
    Returns the filename if successful, None otherwise.
    """
    if not image_url:
        return None

    # Create a hash of the event title for unique filename
    event_hash = hashlib.md5(event_title.encode()).hexdigest()[:12]

    # Detect image extension from URL
    parsed = urlparse(image_url)
    path = parsed.path.lower()
    if path.endswith('.jpg') or path.endswith('.jpeg'):
        ext = 'jpg'
    elif path.endswith('.png'):
        ext = 'png'
    elif path.endswith('.webp'):
        ext = 'webp'
    else:
        ext = 'jpg'  # Default to jpg

    image_filename = f"{event_hash}.{ext}"
    image_path = f"public/events-images/{image_filename}"

    # Check if image already exists
    if os.path.exists(image_path):
        logger.info(f"Image already exists: {image_filename}")
        return image_filename

    # Create image directory if it doesn't exist
    os.makedirs("public/events-images", exist_ok=True)

    try:
        logger.info(f"Downloading image: {image_url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Save the image
        with open(image_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"Successfully saved image: {image_filename}")
        return image_filename

    except Exception as e:
        logger.error(f"Error downloading image from {image_url}: {e}")
        return None

def update_events_data(new_events, google_api_key=None):
    """Updates the events with idempotency and freshness validation."""
    logger.info("Updating events data with idempotency...")
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
            logger.info(f"Updating existing event: {event['title']}")
            active_events[event_key]["found_date"] = today_str  # Update last seen date
            active_events[event_key]["description"] = event.get("description", "")
            active_events[event_key]["link"] = event.get("link", "")
            if event.get("location"):
                active_events[event_key]["location"] = event["location"]

            # Extract image if not already present
            if not active_events[event_key].get("image") and event.get("link"):
                image_url = extract_image_from_url(event["link"])
                if image_url:
                    image_filename = download_and_save_image(image_url, event["title"])
                    if image_filename:
                        active_events[event_key]["image"] = image_filename
        else:
            # Add new event
            logger.info(f"Adding new event: {event['title']}")

            # Geocode location if provided
            lat, lng = None, None
            if event.get("location") and google_api_key:
                lat, lng = geocode_location(event["location"], google_api_key, geocode_cache)

            # Extract and download image from event URL
            image_filename = None
            if event.get("link"):
                image_url = extract_image_from_url(event["link"])
                if image_url:
                    image_filename = download_and_save_image(image_url, event["title"])

            active_events[event_key] = {
                "title": event["title"],
                "event_date": event["event_date"],
                "found_date": today_str,
                "description": event.get("description", ""),
                "link": event.get("link", ""),
                "location": event.get("location"),
                "category": event.get("category", "News"),
                "lat": lat,
                "lng": lng,
                "image": image_filename
            }

    # Apply 3-day freshness rule: remove events not seen in 3 days
    events_to_remove = []
    for event_key, event_data in active_events.items():
        found_date = datetime.strptime(event_data["found_date"], "%Y-%m-%d").date()
        days_since_found = (today_date - found_date).days

        # Remove if not seen in 3 days (validation rule)
        if days_since_found >= 3:
            logger.info(f"Removing stale event (not seen in {days_since_found} days): {event_data['title']}")
            events_to_remove.append(event_key)
            continue

        # Remove if event date is in the past (keep today's events, remove yesterday and earlier)
        event_date = datetime.strptime(event_data["event_date"], "%Y-%m-%d").date()
        if event_date < today_date:
            logger.info(f"Removing past event: {event_data['title']} ({event_data['event_date']})")
            events_to_remove.append(event_key)

    # Remove stale/past events
    for event_key in events_to_remove:
        del active_events[event_key]

    # Save updated active events and trusted sources
    save_active_events(active_events)
    save_trusted_sources(trusted_sources)

    # Also create daily snapshot for historical reference (same format as active-events.json)
    day_path = f"public/events-data/{today_str}.json"
    try:
        with open(day_path, 'w', encoding='utf-8') as f:
            json.dump(active_events, f, ensure_ascii=False, indent=2)
        logger.info(f"Created daily snapshot: {day_path}")
    except (IOError, OSError) as e:
        logger.error(f"Error saving daily snapshot: {e}")

    logger.info(f"Events data updated successfully. Active events: {len(active_events)}, Trusted sources: {len(trusted_sources)}")

if __name__ == "__main__":
    try:
        logger.info("Starting daily events update process...")
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
            try:
                results = fetch_google_search_results(
                    config["google_api_key"], config["search_engine_id"], query
                )
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Failed to fetch results for query '{query}': {e}")
                # Continue with other queries even if one fails

        if all_results:
            openai_client = OpenAI(api_key=config["openai_api_key"])
            try:
                newly_generated_events = analyze_with_openai(openai_client, all_results, config["target_address"])

                if newly_generated_events:
                    update_events_data(newly_generated_events, google_api_key=config["google_api_key"])
                    logger.info("Process completed successfully.")
                else:
                    logger.warning("Failed to generate content from OpenAI.")
            except Exception as e:
                logger.error(f"Failed to analyze events with OpenAI: {e}")
        else:
            logger.warning("No search results found. Exiting.")
    except Exception as e:
        logger.critical(f"Critical error in main process: {e}", exc_info=True)
        raise
