"""Encrypt a QA-approved MP4 and upload only ciphertext to a public release."""

import argparse
import base64
import hashlib
import os
from pathlib import Path
import re
import subprocess

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


ROOT = Path(__file__).resolve().parent
MAGIC = b"CCUT1"
PART_BYTES = 1024 * 1024


def run(*args, check=True):
    return subprocess.run(args, cwd=ROOT, check=check, text=True, capture_output=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("date")
    parser.add_argument("slug")
    parser.add_argument("video", type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z][a-z0-9-]*", args.slug):
        raise RuntimeError("Invalid object slug")
    if args.video.name != f"{args.slug}-vs-1000-cuts.mp4":
        raise RuntimeError("Approved video filename does not match object slug")
    for suffix in (".json", "-localizations.json"):
        if not (ROOT / "metadata" / f"{args.slug}{suffix}").is_file():
            raise RuntimeError("Object metadata or translations are missing")
    if not args.video.is_file():
        raise RuntimeError("QA-approved MP4 is missing")
    key_file = Path.home() / ".cubecut-auth" / "media-key.txt"
    key = base64.b64decode(key_file.read_text(encoding="ascii").strip(), validate=True)
    if len(key) != 32:
        raise RuntimeError("Invalid local media encryption key")
    video = args.video.read_bytes()
    digest = hashlib.sha256(video).hexdigest()
    nonce = os.urandom(12)
    encrypted = MAGIC + nonce + AESGCM(key).encrypt(nonce, video, None)
    if AESGCM(key).decrypt(nonce, encrypted[len(MAGIC)+12:], None) != video:
        raise RuntimeError("Encryption round trip failed")
    folder = ROOT / "media"
    folder.mkdir(exist_ok=True)
    parts = []
    for i, start in enumerate(range(0, len(encrypted), PART_BYTES)):
        part = folder / f"{args.slug}.enc.part{i:02d}"
        part.write_bytes(encrypted[start:start+PART_BYTES])
        parts.append(part)
    release = f"media-{args.date}"
    if run("gh", "release", "view", release, "--repo", "okelemen/cubecut-scheduler", check=False).returncode:
        run("gh", "release", "create", release, "--repo", "okelemen/cubecut-scheduler",
            "--title", f"Encrypted approved media {args.date}",
            "--notes", "AES-GCM ciphertext only; no plaintext video or credentials.")
    run("gh", "release", "upload", release, *map(str, parts),
        "--repo", "okelemen/cubecut-scheduler", "--clobber")
    import json
    assets = json.loads(run("gh", "release", "view", release, "--repo",
                            "okelemen/cubecut-scheduler", "--json", "assets").stdout)["assets"]
    names = {asset["name"] for asset in assets}
    if not {part.name for part in parts} <= names:
        raise RuntimeError("Not all encrypted parts appeared in the cloud release")
    print(f"{args.slug}: sha256={digest}, encrypted_parts={len(parts)}, release={release}")


if __name__ == "__main__":
    main()
