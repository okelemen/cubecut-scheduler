"""Check both approved slots before publication day, without writing to YouTube."""

import argparse
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import subprocess

from publisher import ZONE, channel_check, metadata, oauth_token, slot_for, validate_localizations


def check(date):
    token = oauth_token()
    channel_check(token)
    release = f"media-{date}"
    result = subprocess.run(
        ["gh", "release", "view", release, "--repo", os.environ["GITHUB_REPOSITORY"],
         "--json", "assets"], capture_output=True, text=True, check=True,
    )
    names = {item["name"] for item in json.loads(result.stdout)["assets"]}
    for time in ("14:00", "21:00"):
        slot = slot_for(date, time)
        if slot is None or slot.get("qa_passed") is not True:
            raise RuntimeError(f"Approved slot missing: {date} {time}")
        metadata(slot)
        slug = slot["object"].lower().replace(" ", "-")
        localizations = json.loads((Path(__file__).parent / "metadata" /
                                    f"{slug}-localizations.json").read_text(encoding="utf-8"))
        validate_localizations(token, localizations)
        expected = {f"{slug}.enc.part{i:02d}" for i in range(slot["encrypted_parts"])}
        if not expected <= names:
            raise RuntimeError(f"Encrypted media incomplete: {date} {time} {slot['object']}")
        print(f"READY: {date} {time} {slot['object']}; 25 languages; encrypted media", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date")
    parser.add_argument("--tomorrow", action="store_true")
    args = parser.parse_args()
    if args.date and args.tomorrow:
        parser.error("Choose --date or --tomorrow")
    date = args.date or (datetime.now(ZONE).date() + timedelta(days=int(args.tomorrow))).isoformat()
    check(date)
