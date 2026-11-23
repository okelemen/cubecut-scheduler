"""Check a finished CubeCut MP4 and build frames for a human visual review."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw


TIMES = (0.8, 4.8, 12.0, 30.0, 58.0, 59.7)


def run(*command):
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout


def audio_hash(path):
    output = run("ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0",
                 "-c", "copy", "-f", "hash", "-hash", "sha256", "-")
    return output.strip().split("=", 1)[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=Path)
    parser.add_argument("sheet", type=Path)
    parser.add_argument("--reference-audio", type=Path, required=True)
    args = parser.parse_args()

    probe = json.loads(run("ffprobe", "-v", "error", "-show_entries",
                           "format=duration:stream=codec_type,codec_name,width,height",
                           "-of", "json", str(args.video)))
    duration = float(probe["format"]["duration"])
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    audio = next(s for s in probe["streams"] if s["codec_type"] == "audio")
    if not 59.8 <= duration <= 60.2:
        raise RuntimeError(f"Wrong duration: {duration}")
    if (video["width"], video["height"]) != (1080, 1920):
        raise RuntimeError("Not a 1080x1920 Shorts video")
    if audio["codec_name"] != "aac":
        raise RuntimeError("Unexpected audio codec")
    actual_audio, expected_audio = audio_hash(args.video), audio_hash(args.reference_audio)
    if actual_audio != expected_audio:
        raise RuntimeError("Audio differs from the approved reference")

    args.sheet.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGB", (270 * len(TIMES), 510), "white")
    with TemporaryDirectory() as tmp:
        for i, seconds in enumerate(TIMES):
            frame = Path(tmp) / f"frame-{i}.jpg"
            run("ffmpeg", "-v", "error", "-ss", str(seconds), "-i", str(args.video),
                "-frames:v", "1", "-vf", "scale=270:480", "-y", str(frame))
            with Image.open(frame) as im:
                canvas.paste(im, (270 * i, 0))
            ImageDraw.Draw(canvas).text((270 * i + 8, 486), f"{seconds:.1f}s", fill="black")
    canvas.save(args.sheet, quality=90)
    print(json.dumps({"video": str(args.video), "sha256": hashlib.sha256(args.video.read_bytes()).hexdigest(),
                      "duration": duration, "size": "1080x1920", "audio_sha256": actual_audio,
                      "sheet": str(args.sheet)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
