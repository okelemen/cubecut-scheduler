"""CubeCut publisher: private upload, 25 localizations, separate public update, first comment."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib import error, parse, request
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


ROOT = Path(__file__).resolve().parent
try:
    ZONE = ZoneInfo("Europe/Istanbul")
except ZoneInfoNotFoundError:
    # Windows Python may lack the IANA tzdata package; Turkey is UTC+03:00 for this launch week.
    ZONE = timezone(timedelta(hours=3))
CHANNEL_ID = "UCB4kH7DBy-616hPpLFMjRIg"
COMMENT = "What should we cube next? 🔪 Drop your pick below 👇"
SCHEDULE = {
    "53 11 * * *": ("upload", "14:00", "12:00"),
    "53 13 * * *": ("publish", "14:00", "14:00"),
    "53 18 * * *": ("upload", "21:00", "19:00"),
    "53 20 * * *": ("publish", "21:00", "21:00"),
    "7 12 * * *": ("upload", "14:00", "12:00"),
    "7 14 * * *": ("publish", "14:00", "14:00"),
    "7 19 * * *": ("upload", "21:00", "19:00"),
    "7 21 * * *": ("publish", "21:00", "21:00"),
}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def oauth_token():
    client = json.loads(os.environ["CUBECUT_OAUTH_CLIENT_JSON"])["installed"]
    saved = json.loads(os.environ["CUBECUT_YOUTUBE_TOKEN_JSON"])
    if client.get("project_id") != saved.get("project_id") or saved.get("channel_id") != CHANNEL_ID:
        raise RuntimeError("OAuth credentials do not match the authorized CubeCut channel")
    body = parse.urlencode({
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "refresh_token": saved["refresh_token"],
        "grant_type": "refresh_token",
    }).encode("ascii")
    req = request.Request("https://oauth2.googleapis.com/token", data=body,
                          headers={"Content-Type": "application/x-www-form-urlencoded"})
    with request.urlopen(req, timeout=30) as response:
        return json.load(response)["access_token"]


def youtube(token, method, resource, params=None, body=None):
    url = "https://www.googleapis.com/youtube/v3/" + resource
    if params:
        url += "?" + parse.urlencode(params)
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    headers = {"Authorization": "Bearer " + token}
    if data is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=60) as response:
            return json.load(response)
    except error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"YouTube {method} {resource}: HTTP {exc.code}: {message[:700]}") from None


def channel_check(token):
    items = youtube(token, "GET", "channels", {"part": "snippet,contentDetails,brandingSettings", "mine": "true"})["items"]
    if len(items) != 1 or items[0]["id"] != CHANNEL_ID or items[0]["snippet"]["title"] != "CubeCut":
        raise RuntimeError("Authorized YouTube channel does not match CubeCut")
    if items[0].get("brandingSettings", {}).get("channel", {}).get("defaultLanguage") != "en":
        raise RuntimeError("CubeCut channel default language is not English")
    return items[0]


def slot_for(date, publish_time):
    for slot in read_json(ROOT / "schedule.json")["slots"]:
        if slot["date"] == date and slot["time"] == publish_time:
            return slot
    return None


def metadata(slot):
    name = slot["object"].lower()
    file = ROOT / "metadata" / (name.replace(" ", "-") + ".json")
    if not file.is_file():
        raise RuntimeError(f"Metadata not ready for {slot['object']}")
    data = read_json(file)
    title, description, tags = data["title"], data["description"], data["tags"]
    expected_title = f"{slot['object']} vs 1000 Cuts #satisfying #oddlysatisfying #asmr"
    expected_tags = [name, name + " cutting", name + " vs 1000 cuts", "CubeCut", "cutting ASMR",
                     "knife ASMR", "satisfying cuts", "oddly satisfying", "cube cutting", "cubes",
                     "3D animation", "shorts"]
    if title != expected_title or tags != expected_tags:
        raise RuntimeError(f"Fixed upload title or Studio tags changed for {slot['object']}")
    if len(title) > 100 or len(",".join(tags)) > 500 or not description.startswith(f"One {name}, six rounds:"):
        raise RuntimeError("Video metadata does not match the approved template")
    if f"#satisfying #cutting #{name.replace(' ', '')} #asmr #3danimation #shorts" not in description:
        raise RuntimeError("Object-specific description hashtag is missing")
    return {"snippet": {"title": title, "description": description, "tags": tags,
                        "categoryId": "24", "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False,
                       "containsSyntheticMedia": False}}


def approved_video_path(slot):
    if slot.get("qa_passed") is not True or "video" not in slot or "sha256" not in slot:
        raise RuntimeError(f"Video not prepared for {slot['object']}")
    path = (ROOT / slot["video"]).resolve()
    if not path.is_relative_to(ROOT):
        raise RuntimeError("Approved video path escapes the repository")
    if not path.is_file() and slot.get("parts"):
        with path.open("wb") as output:
            for part in slot["parts"]:
                part_path = (ROOT / part).resolve()
                if not part_path.is_relative_to(ROOT) or not part_path.is_file():
                    raise RuntimeError("Approved video part is missing")
                with part_path.open("rb") as source:
                    while chunk := source.read(1024 * 1024):
                        output.write(chunk)
    if not path.is_file():
        raise RuntimeError("Approved video is missing from the private repository")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != slot["sha256"]:
        raise RuntimeError("Video hash differs from approved file")
    return path


def validate_localizations(token, localizations):
    expected = {"es", "pt", "fr", "de", "it", "tr", "ru", "ja", "ko", "pl", "nl", "uk",
                "lt", "ro", "sv", "el", "cs", "hu", "da", "no", "fi", "sk", "hr", "bg", "sr"}
    if set(localizations) != expected:
        raise RuntimeError("Video localizations do not match the approved 25 languages")
    for code, item in localizations.items():
        if not item.get("title") or len(item["title"]) > 100 or not item.get("description"):
            raise RuntimeError(f"Missing or invalid video translation for {code}")
    supported = {item["id"] for item in youtube(token, "GET", "i18nLanguages", {"part": "snippet"})["items"]}
    if not expected <= supported:
        raise RuntimeError("Some approved video languages are not supported by YouTube")


def existing_video(token, channel, title):
    playlist = channel["contentDetails"]["relatedPlaylists"]["uploads"]
    result = youtube(token, "GET", "playlistItems", {"part": "snippet", "playlistId": playlist,
                                                      "maxResults": 50})
    matches = [item["snippet"]["resourceId"]["videoId"] for item in result.get("items", [])
               if item["snippet"]["title"] == title]
    if len(matches) > 1:
        raise RuntimeError("Multiple uploads have the same title; refusing to choose one")
    return matches[0] if matches else None


def upload_video(token, path, body):
    video = path.read_bytes()
    params = parse.urlencode({"uploadType": "resumable", "part": "snippet,status"})
    req = request.Request(
        "https://www.googleapis.com/upload/youtube/v3/videos?" + params,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json; charset=utf-8",
                 "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(len(video))},
        method="POST",
    )
    with request.urlopen(req, timeout=60) as response:
        location = response.headers["Location"]
    req = request.Request(location, data=video, headers={"Authorization": "Bearer " + token,
                                                        "Content-Type": "video/mp4",
                                                        "Content-Length": str(len(video))}, method="PUT")
    with request.urlopen(req, timeout=300) as response:
        return json.load(response)["id"]


def video_read(token, video_id, parts="snippet,status,localizations"):
    items = youtube(token, "GET", "videos", {"part": parts, "id": video_id}).get("items", [])
    if len(items) != 1:
        raise RuntimeError("Uploaded video is not readable by the channel")
    return items[0]


def verify_localizations(token, video_id, expected):
    for _ in range(6):
        got = video_read(token, video_id).get("localizations", {})
        if localizations_match(got, expected):
            return
        time.sleep(5)
    raise RuntimeError("Video title/description translations incomplete or mismatched")


def localizations_match(got, expected):
    for code, text in expected.items():
        item = got.get(code)
        if item is None and code == "no":
            item = got.get("nb")
        if item is None or any(item.get(field) != text[field] for field in ("title", "description")):
            return False
    return True


def video_languages_match(snippet):
    return snippet.get("defaultLanguage") == "en" and snippet.get("defaultAudioLanguage") == "en"


def stage(token, slot, state):
    key = slot["date"] + "-" + slot["time"]
    path = approved_video_path(slot)
    body = metadata(slot)
    slug = slot["object"].lower().replace(" ", "-")
    localizations = read_json(ROOT / "metadata" / (slug + "-localizations.json"))
    validate_localizations(token, localizations)
    channel = channel_check(token)
    video_id = state.get(key, {}).get("video_id") or existing_video(token, channel, body["snippet"]["title"])
    if video_id:
        current = video_read(token, video_id)
        if current["status"]["privacyStatus"] != "private":
            raise RuntimeError("Video is not private during translation check")
        if current["snippet"]["title"] != body["snippet"]["title"]:
            raise RuntimeError("Uploaded video title differs from approved metadata")
        if video_languages_match(current["snippet"]) and localizations_match(current.get("localizations", {}), localizations):
            state[key] = {"video_id": video_id, "uploaded": True, "localized": True,
                          "public": False, "commented": False}
            print(f"Private upload and 25 translations already verified: {key} {video_id}")
            return True
    if not video_id:
        video_id = upload_video(token, path, body)
    current = video_read(token, video_id)
    if current["status"]["privacyStatus"] != "private":
        raise RuntimeError("Video is not private after upload")
    if current["snippet"]["title"] != body["snippet"]["title"]:
        raise RuntimeError("Uploaded video title differs from approved metadata")
    if not video_languages_match(current["snippet"]):
        youtube(token, "PUT", "videos", {"part": "snippet"},
                {"id": video_id, "snippet": body["snippet"]})
        for _ in range(8):
            current = video_read(token, video_id)
            if video_languages_match(current["snippet"]):
                break
            time.sleep(2)
        else:
            raise RuntimeError("Video language and title/description language are not English")
    youtube(token, "PUT", "videos", {"part": "localizations"},
            {"id": video_id, "localizations": localizations})
    verify_localizations(token, video_id, localizations)
    if video_read(token, video_id, "status")["status"]["privacyStatus"] != "private":
        raise RuntimeError("Video lost private status during localization")
    state[key] = {"video_id": video_id, "uploaded": True, "localized": True,
                  "public": False, "commented": False}
    print(f"Private upload and 25 localizations verified: {key} {video_id}")
    return True


def comment_exists(token, video_id):
    result = youtube(token, "GET", "commentThreads", {"part": "snippet", "videoId": video_id,
                                                        "maxResults": 100, "order": "time"})
    for item in result.get("items", []):
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        if snippet.get("authorChannelId", {}).get("value") == CHANNEL_ID and snippet.get("textOriginal") == COMMENT:
            return True
    return False


def publish(token, slot, state):
    key = slot["date"] + "-" + slot["time"]
    entry = state.get(key)
    if not entry or not entry.get("localized"):
        raise RuntimeError("Private upload and 25 localizations not complete; refusing publication")
    video_id = entry["video_id"]
    current = video_read(token, video_id)
    if not video_languages_match(current["snippet"]):
        raise RuntimeError("English video or title/description language missing before publication")
    slug = slot["object"].lower().replace(" ", "-")
    expected = read_json(ROOT / "metadata" / (slug + "-localizations.json"))
    if not localizations_match(current.get("localizations", {}), expected):
        raise RuntimeError("25 title/description translations missing or mismatched before publication")
    privacy = current["status"]["privacyStatus"]
    if privacy == "private":
        status = {"privacyStatus": "public"}
        for field in ("embeddable", "license", "publicStatsViewable", "selfDeclaredMadeForKids", "containsSyntheticMedia"):
            if field in current["status"]:
                status[field] = current["status"][field]
        youtube(token, "PUT", "videos", {"part": "status"}, {"id": video_id, "status": status})
    elif privacy != "public":
        raise RuntimeError(f"Unexpected video privacy state: {privacy}")
    for _ in range(6):
        if video_read(token, video_id, "status")["status"]["privacyStatus"] == "public":
            break
        time.sleep(5)
    else:
        raise RuntimeError("Public status did not verify")
    entry["public"] = True
    if not entry.get("commented") and not comment_exists(token, video_id):
        youtube(token, "POST", "commentThreads", {"part": "snippet"},
                {"snippet": {"videoId": video_id,
                             "topLevelComment": {"snippet": {"textOriginal": COMMENT}}}})
    entry["commented"] = True
    print(f"Public and first comment verified: {key} {video_id}; owner pins comment")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--schedule", choices=tuple(SCHEDULE), required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--date", help="Date override for dry run or explicit recovery (YYYY-MM-DD)")
    parser.add_argument("--recovery", action="store_true", help="Recover a missed past slot explicitly")
    args = parser.parse_args()
    stage_name, publish_time, action_time = SCHEDULE[args.schedule]
    now = datetime.now(ZONE)
    if args.date and not (args.dry_run or args.recovery):
        raise RuntimeError("Live date override requires explicit recovery mode")
    if args.recovery and (args.dry_run or not args.date):
        raise RuntimeError("Recovery requires a live past date")
    date = args.date or now.date().isoformat()
    target = datetime.fromisoformat(date + "T" + action_time).replace(tzinfo=ZONE)
    slot = slot_for(date, publish_time)
    if slot is None:
        print(f"SKIP: no approved video slot for {date} {publish_time}")
        return
    if args.dry_run:
        if stage_name == "upload":
            approved_video_path(slot)
            metadata(slot)
        token = oauth_token()
        channel_check(token)
        if stage_name == "upload":
            slug = slot["object"].lower().replace(" ", "-")
            validate_localizations(token, read_json(ROOT / "metadata" / (slug + "-localizations.json")))
        print(f"DRY RUN: {stage_name} {date} {publish_time}, object={slot['object']}, no YouTube write")
        return
    if args.recovery:
        if not (timedelta(0) <= now - target <= timedelta(hours=48)):
            raise RuntimeError("Recovery is limited to missed slots within 48 hours")
    elif target - now > timedelta(minutes=15) or now - target > (
            timedelta(hours=2) if stage_name == "upload" else timedelta(minutes=30)):
        raise RuntimeError("Job is outside its allowed publication window")
    if now < target:
        time.sleep((target - now).total_seconds())
    state_path = ROOT / "state.json"
    state = read_json(state_path) if state_path.exists() else {}
    token = oauth_token()
    if stage_name == "upload":
        changed = stage(token, slot, state)
    else:
        changed = publish(token, slot, state)
    if changed:
        write_json(state_path, state)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"CubeCut publication failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
