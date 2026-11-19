"""Persist a publication result while preserving concurrent scheduler commits."""

import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STATE = ROOT / "state.json"


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, check=check,
                          text=True, capture_output=True)


def main():
    if not STATE.is_file():
        raise RuntimeError("No verified publication state to save")
    changed = json.loads(STATE.read_text(encoding="utf-8"))
    key = sys.argv[1]
    if key not in changed:
        raise RuntimeError(f"Publication slot missing from local state: {key}")
    entry = changed[key]
    if not entry.get("video_id") or not entry.get("uploaded"):
        raise RuntimeError("Refusing to save an unverified upload")
    STATE.unlink()
    git("restore", "--", "state.json", check=False)
    git("config", "user.name", "cubecut-scheduler[bot]")
    git("config", "user.email", "cubecut-scheduler[bot]@users.noreply.github.com")
    for attempt in range(5):
        git("fetch", "origin", "main")
        git("switch", "-C", "publication-state", "origin/main")
        remote = json.loads(STATE.read_text(encoding="utf-8")) if STATE.is_file() else {}
        old = remote.get(key, {})
        if old.get("video_id") and old["video_id"] != entry["video_id"]:
            raise RuntimeError("Remote state points to another video; stopping")
        remote[key] = {**old, **entry}
        STATE.write_text(json.dumps(remote, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        git("add", "state.json")
        if git("diff", "--cached", "--quiet", check=False).returncode == 0:
            print(f"State already saved: {key}")
            return
        git("commit", "-m", f"Record {key} publication state")
        pushed = git("push", "origin", "HEAD:main", check=False)
        if pushed.returncode == 0:
            print(f"State saved: {key}")
            return
        STATE.unlink()
        git("restore", "--", "state.json", check=False)
        time.sleep(2 + attempt * 2)
    raise RuntimeError("Could not save verified publication state after five attempts")


if __name__ == "__main__":
    main()
