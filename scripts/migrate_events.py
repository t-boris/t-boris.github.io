#!/usr/bin/env python3
"""
Migrate existing events.json to new active-events.json structure
"""
import json
import os
from datetime import datetime, timezone

def generate_event_key(title, event_date):
    """Generate unique key for idempotency check."""
    return f"{title.lower().strip()}|{event_date}"

def migrate_events():
    """Migrate old events.json to new active-events.json structure."""
    print("Starting events migration...")

    # Paths
    old_events_path = "public/events-data/events.json"
    active_events_path = "public/events-data/active-events.json"

    # Load old events
    if not os.path.exists(old_events_path):
        print(f"Error: {old_events_path} not found")
        return

    with open(old_events_path, 'r', encoding='utf-8') as f:
        old_events_data = json.load(f)

    print(f"Loaded old events data with {len(old_events_data)} date keys")

    # Initialize new structure
    active_events = {}

    # Get today's date
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_date = datetime.now(timezone.utc).date()

    # Track statistics
    total_events = 0
    migrated_events = 0
    skipped_past = 0
    skipped_invalid = 0

    # Process each date in old structure
    for found_date, events_list in old_events_data.items():
        if not isinstance(events_list, list):
            print(f"Warning: events for {found_date} is not a list, wrapping...")
            events_list = [events_list]

        for event in events_list:
            total_events += 1

            # Validate required fields
            if not event.get("title"):
                print(f"Skipping event without title")
                skipped_invalid += 1
                continue

            # Set event_date if missing (use found_date)
            if not event.get("event_date"):
                event["event_date"] = found_date

            event_date = event["event_date"]

            # Skip past events
            try:
                event_date_obj = datetime.strptime(event_date, "%Y-%m-%d").date()
                if event_date_obj < today_date:
                    skipped_past += 1
                    continue
            except:
                print(f"Warning: Invalid date format for event: {event.get('title')}")
                skipped_invalid += 1
                continue

            # Generate unique key
            event_key = generate_event_key(event["title"], event_date)

            # Check if already exists (keep first occurrence)
            if event_key in active_events:
                # Update found_date to most recent
                existing_found = active_events[event_key]["found_date"]
                if found_date > existing_found:
                    active_events[event_key]["found_date"] = found_date
                continue

            # Normalize category names
            category = event.get("category", "News")
            category_mapping = {
                "Politics": "News",  # Politics -> News
                "Entertainment": "Culture",  # Entertainment -> Culture
                "Upcoming Events": "Community"  # Upcoming Events -> Community
            }
            if category in category_mapping:
                category = category_mapping[category]

            # Add to active events
            active_events[event_key] = {
                "title": event["title"],
                "event_date": event_date,
                "found_date": found_date,
                "description": event.get("description", ""),
                "link": event.get("link", ""),
                "location": event.get("location"),
                "category": category,
                "lat": None,  # Will be geocoded later
                "lng": None
            }
            migrated_events += 1

    # Save new structure
    print(f"\nMigration Summary:")
    print(f"Total events processed: {total_events}")
    print(f"Successfully migrated: {migrated_events}")
    print(f"Skipped (past events): {skipped_past}")
    print(f"Skipped (invalid): {skipped_invalid}")
    print(f"Active events in new structure: {len(active_events)}")

    with open(active_events_path, 'w', encoding='utf-8') as f:
        json.dump(active_events, f, ensure_ascii=False, indent=2)

    print(f"\nMigration complete! Saved to {active_events_path}")

    # Show sample events
    if active_events:
        print("\nSample migrated events:")
        sample_keys = list(active_events.keys())[:3]
        for key in sample_keys:
            event = active_events[key]
            print(f"  - {event['title']} ({event['category']}) on {event['event_date']}")

if __name__ == "__main__":
    migrate_events()
