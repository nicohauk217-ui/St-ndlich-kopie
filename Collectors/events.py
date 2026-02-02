import requests
import csv
from datetime import datetime, timezone

ELECTION_API = "https://api.hypixel.net/resources/skyblock/election"
CALENDAR_API = "https://api.hypixel.net/resources/skyblock/calendar"
OUTPUT_FILE = "data/events_daily.csv"


def get_active_calendar_events():
    now = datetime.now(timezone.utc).timestamp() * 1000
    res = requests.get(CALENDAR_API).json()

    active = []

    for event in res.get("events", []):
        start = event.get("start")
        end = event.get("end")

        if start and end and start <= now <= end:
            active.append(event.get("name"))

    return active


def collect_events():
    timestamp = datetime.utcnow().isoformat()

    # -------- MAYOR --------
    mayor_res = requests.get(ELECTION_API).json()
    mayor = mayor_res.get("mayor", {})

    mayor_name = mayor.get("name", "UNKNOWN")
    minister = mayor.get("minister", {}).get("name", "NONE")
    perks = [p.get("name") for p in mayor.get("perks", [])]

    # -------- EVENTS --------
    active_events = get_active_calendar_events()

    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp,
            mayor_name,
            minister,
            "|".join(perks),
            "|".join(active_events)
        ])
