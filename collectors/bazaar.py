import requests
import csv
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

URL = "https://api.hypixel.net/skyblock/bazaar"

def collect_bazaar():
    r = requests.get(URL, timeout=30)
    data = r.json()["products"]

    now = datetime.utcnow().isoformat()

    file = DATA_DIR / "bazaar_daily.csv"
    write_header = not file.exists()

    with open(file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow([
                "timestamp",
                "item_id",
                "buy_price",
                "sell_price",
                "buy_volume",
                "sell_volume"
            ])

        for item_id, item in data.items():
            writer.writerow([
                now,
                item_id,
                item["quick_status"]["buyPrice"],
                item["quick_status"]["sellPrice"],
                item["quick_status"]["buyVolume"],
                item["quick_status"]["sellVolume"]
            ])

if __name__ == "__main__":
    collect_bazaar()

