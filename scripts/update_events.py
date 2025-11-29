import os
import json
import requests
from datetime import datetime, timezone
from openai import OpenAI
from collections import defaultdict

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

    prompt = f"""
    Analyze the following search results related to events around the address "{address}".

    Search Results:
    {json.dumps(simplified_results, indent=2, ensure_ascii=False)}

    Your task is to return a JSON object containing a list of key events.
    Each event must have the fields: "category", "title", "description", and "link".
    Use the following categories: "Culture", "Sports", "Community News", "Upcoming Events", "Incidents", "Society".

    Return ONLY the JSON array, without any extra text.
    Example:
    [
      {{ "category": "Upcoming Events", "title": "Fair in the Park", "description": "An autumn fair will be held this weekend.", "link": "http://example.com" }}
    ]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful assistant that returns structured JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        data = json.loads(response.choices[0].message.content)
        if isinstance(data, dict):
            for key in data:
                if isinstance(data[key], list):
                    return data[key]
        return data
    except Exception as e:
        print(f"Error with OpenAI API: {e}")
        return None

def update_events_data(new_events):
    """Updates the events JSON file for Astro to consume."""
    print("Updating events data file...")
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Update the master JSON data file
    events_path = "public/events-data/events.json"
    os.makedirs("public/events-data", exist_ok=True)

    all_events = {}
    if os.path.exists(events_path):
        with open(events_path, 'r', encoding='utf-8') as f:
            all_events = json.load(f)

    all_events[today_str] = new_events

    with open(events_path, 'w', encoding='utf-8') as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    # Create individual day data file
    day_path = f"public/events-data/{today_str}.json"
    with open(day_path, 'w', encoding='utf-8') as f:
        json.dump(new_events, f, ensure_ascii=False, indent=2)

    print("Events data updated successfully.")

if __name__ == "__main__":
    print("Starting daily events update process...")
    config = load_config()
    all_results = []
    for query_template in config["search_queries"]:
        query = query_template.replace("{address}", config["target_address"])
        all_results.extend(fetch_google_search_results(
            config["google_api_key"], config["search_engine_id"], query
        ))

    if all_results:
        openai_client = OpenAI(api_key=config["openai_api_key"])
        newly_generated_events = analyze_with_openai(openai_client, all_results, config["target_address"])

        if newly_generated_events:
            update_events_data(newly_generated_events)
            print("Process completed successfully.")
        else:
            print("Failed to generate content from OpenAI.")
    else:
        print("No search results found. Exiting.")
