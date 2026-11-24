"""Time-bounded backup dispatch when a required YouTube state is absent."""

import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
import subprocess

from publisher import ZONE, slot_for


parser = argparse.ArgumentParser()
parser.add_argument("slot", choices=("morning", "evening"))
parser.add_argument("phase", choices=("stage", "publish"))
args = parser.parse_args()

now = datetime.now(ZONE)
date = now.date().isoformat()
publish_time = "14:00" if args.slot == "morning" else "21:00"
slot = slot_for(date, publish_time)
if slot is None or slot.get("qa_passed") is not True:
    raise RuntimeError(f"Approved slot missing: {date} {publish_time}")

state = json.loads((Path(__file__).parent / "state.json").read_text(encoding="utf-8"))
entry = state.get(f"{date}-{publish_time}", {})
done = (entry.get("uploaded") and entry.get("localized") if args.phase == "stage"
        else entry.get("public") and entry.get("commented"))
if done:
    print(f"Already verified in state.json: {date} {publish_time} {args.phase}")
    raise SystemExit(0)

target_time = "12:00" if args.slot == "morning" else "19:00"
if args.phase == "publish":
    target_time = publish_time
target = datetime.fromisoformat(f"{date}T{target_time}").replace(tzinfo=ZONE)
age = now - target
limit = timedelta(hours=1, minutes=45) if args.phase == "stage" else timedelta(minutes=25)
if age < timedelta(0):
    print(f"Skipping stale scheduled watchdog before today's {target_time} TR check")
    raise SystemExit(0)
if not timedelta(0) <= age <= limit:
    raise RuntimeError(f"Missing {args.phase} state outside bounded backup window: {date} {publish_time}")

command = ["gh", "workflow", "run", "publish.yml", "--repo", "okelemen/cubecut-scheduler",
           "--ref", "main", "-f", f"slot={args.slot}", "-f", f"date={date}",
           "-f", "dry_run=false", "-f", f"recovery={'true' if args.phase == 'publish' else 'false'}"]
subprocess.run(command, check=True)
print(f"Backup dispatched: {date} {publish_time} {args.phase}")
