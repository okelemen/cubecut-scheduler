"""Download and verify the encrypted approved video for a publication slot."""

import os
import subprocess
import sys

from publisher import ROOT, approved_video_path, slot_for


date, publication_time = sys.argv[1:3]
slot = slot_for(date, publication_time)
if slot is None or slot.get("qa_passed") is not True:
    raise RuntimeError("No approved video for this publication slot")
slug = slot["object"].lower().replace(" ", "-")
encrypted = ROOT / "media" / f"{slug}.enc"
subprocess.run([
    "gh", "release", "download", f"media-{date}",
    "--repo", os.environ["GITHUB_REPOSITORY"],
    "--pattern", f"{encrypted.name}.part*",
    "--dir", str(encrypted.parent), "--clobber",
], check=True)
parts = sorted(encrypted.parent.glob(f"{encrypted.name}.part*"))
expected = [encrypted.parent / f"{encrypted.name}.part{i:02d}"
            for i in range(slot["encrypted_parts"])]
if parts != expected:
    raise RuntimeError("An encrypted media part is missing or unexpected")
encrypted.write_bytes(b"".join(part.read_bytes() for part in parts))
subprocess.run([
    sys.executable, str(ROOT / "media_crypto.py"), "decrypt",
    str(encrypted), str(ROOT / slot["video"]), "--sha256", slot["sha256"],
], check=True)
print(f"Approved video ready: {approved_video_path(slot).name}")
