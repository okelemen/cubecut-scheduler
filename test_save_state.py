"""Exercise state persistence against a concurrent remote update."""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path


SOURCE = Path(__file__).with_name("save_state.py")


def run(cwd, *args):
    return subprocess.run(args, cwd=cwd, check=True, text=True,
                          capture_output=True).stdout


with tempfile.TemporaryDirectory() as scratch:
    root = Path(scratch)
    remote = root / "remote.git"
    one, two = root / "one", root / "two"
    run(root, "git", "init", "--bare", "--initial-branch=main", str(remote))
    run(root, "git", "clone", str(remote), str(one))
    run(one, "git", "config", "user.name", "Test")
    run(one, "git", "config", "user.email", "test@example.invalid")
    (one / "state.json").write_text("{}\n", encoding="utf-8")
    run(one, "git", "add", "state.json")
    run(one, "git", "commit", "-m", "init")
    run(one, "git", "push", "origin", "main")
    run(root, "git", "clone", str(remote), str(two))
    run(two, "git", "config", "user.name", "Test")
    run(two, "git", "config", "user.email", "test@example.invalid")
    shutil.copyfile(SOURCE, one / "save_state.py")
    key = "2026-11-20-14:00"
    entry = {"video_id": "abc", "uploaded": True, "localized": True,
             "public": False, "commented": False}
    (one / "state.json").write_text(json.dumps({key: entry}), encoding="utf-8")
    run(one, "python", "save_state.py", key)
    run(two, "git", "pull", "--rebase", "origin", "main")
    (two / "state.json").write_text(json.dumps({**json.loads((two / "state.json").read_text()),
                                                  "another-slot": {"video_id": "other"}}), encoding="utf-8")
    run(two, "git", "add", "state.json")
    run(two, "git", "commit", "-m", "other slot")
    run(two, "git", "push", "origin", "main")
    entry["public"] = True
    entry["commented"] = True
    (one / "state.json").write_text(json.dumps({key: entry}), encoding="utf-8")
    run(one, "python", "save_state.py", key)
    run(one, "git", "fetch", "origin", "main")
    final = json.loads(run(one, "git", "show", "origin/main:state.json"))
    assert final[key]["public"] and final[key]["commented"]
    assert final["another-slot"]["video_id"] == "other"
    print("save_state: concurrent state preserved")
