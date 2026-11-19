"""Wait on a cloud runner until an explicit Turkey-time publication step."""

import argparse
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

parser = argparse.ArgumentParser()
parser.add_argument("date")
parser.add_argument("time")
parser.add_argument("--allow-past", action="store_true")
args = parser.parse_args()
zone = ZoneInfo("Europe/Istanbul")
target = datetime.fromisoformat(f"{args.date}T{args.time}").replace(tzinfo=zone)
while True:
    now = datetime.now(zone)
    remaining = (target - now).total_seconds()
    if remaining <= 0:
        if not args.allow_past and now - target > timedelta(minutes=2):
            raise SystemExit(f"Missed exact trigger: {target.isoformat()}")
        break
    time.sleep(min(remaining, 30))
print(f"Turkey-time trigger reached: {target.isoformat()}", flush=True)
