import requests
import csv
import statistics
import re
import time
from datetime import datetime

API_URL = "https://api.hypixel.net/skyblock/auctions"
OUTPUT_FILE = "data/ah_daily.csv"
MIN_PRICE = 10_000_000  # 10m Filter


# ---------------- PET HELPERS ----------------

def extract_pet_level(name):
    if name.startswith("[Lvl"):
        try:
            return int(name.split("[Lvl ")[1].split("]")[0])
        except Exception:
            return None
    return None


def pet_level_category(level):
    return "80_100" if level >= 80 else "0_79"


# ---------------- ITEM NORMALIZATION ----------------

REFORGES = [
    "Spiritual", "Rapid", "Precise", "Hasty", "Unreal",
    "Deadly", "Fine", "Grand", "Epic", "Fair",
    "Fast", "Awkward", "Rich", "Wise", "Clean"
]


def normalize_item_name(name):
    if name.startswith("[Lvl"):
        name = name.split("] ", 1)[1]

    for ref in REFORGES:
        if name.startswith(ref + " "):
            name = name[len(ref) + 1:]
            break

    name = re.sub(r"[✪➊➋➌➍➎➏➐➑➒]", "", name)
    return " ".join(name.split())


def is_clean_item(auction):
    extra = auction.get("item", {}).get("tag", {}).get("ExtraAttributes", {})

    if "rarity_upgrades" in extra:
        return False
    if extra.get("dungeon_item_level", 0) > 0:
        return False
    if extra.get("hot_potato_count", 0) > 0:
        return False
    if "art_of_war_count" in extra:
        return False

    return True


# ---------------- API (ROBUST) ----------------

def fetch_all_auctions():
    page = 0
    auctions = []

    while True:
        tries = 0
        while True:
            try:
                res = requests.get(API_URL, params={"page": page}, timeout=20)
                res.raise_for_status()
                data = res.json()
                break
            except Exception as e:
                tries += 1
                if tries >= 5:
                    print(f"❌ Seite {page} nach 5 Versuchen fehlgeschlagen – breche AH ab.")
                    return auctions
                print(f"⚠️ API Fehler auf Seite {page}, Retry {tries}/5: {e}")
                time.sleep(2)

        auctions.extend(data.get("auctions", []))

        if page >= data.get("totalPages", 1) - 1:
            break

        page += 1
        time.sleep(0.25)

    return auctions


# ---------------- MAIN COLLECTOR ----------------

def collect_ah():
    auctions = fetch_all_auctions()
    if not auctions:
        print("❌ Keine AH-Daten erhalten.")
        return

    timestamp = datetime.utcnow().isoformat()
    buckets = {}

    for a in auctions:
        if not a.get("bin"):
            continue

        price = a.get("starting_bid", 0)
        raw_name = a.get("item_name", "")
        tier = a.get("tier")  # LEGENDARY / MYTHIC / etc.

        # ---------- PETS ----------
        if raw_name.startswith("[Lvl"):
            level = extract_pet_level(raw_name)
            if level is None:
                continue

            if tier not in ("LEGENDARY", "MYTHIC"):
                continue

            base_name = normalize_item_name(raw_name)
            lvl_cat = pet_level_category(level)
            category = f"pet_{lvl_cat}_{tier.lower()}"
            key = (base_name, category)

        # ---------- ITEMS ----------
        else:
            if raw_name.endswith(" Skin"):
                continue

            if price < MIN_PRICE:
                continue

            if not is_clean_item(a):
                continue

            base_name = normalize_item_name(raw_name)
            category = "item"
            key = (base_name, category)

        buckets.setdefault(key, []).append(price)

    # ---------- CSV WRITE ----------
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for (item, category), prices in buckets.items():
            writer.writerow([
                timestamp,
                item,
                category,
                min(prices),
                int(statistics.median(prices)),
                len(prices)
            ])


if __name__ == "__main__":
    collect_ah()
