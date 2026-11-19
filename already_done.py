"""Exit successfully when a slot is already public and commented."""

import json
from pathlib import Path
import sys


state = Path(__file__).resolve().parent / "state.json"
if not state.is_file():
    raise SystemExit(1)
entry = json.loads(state.read_text(encoding="utf-8")).get(f"{sys.argv[1]}-{sys.argv[2]}", {})
raise SystemExit(0 if entry.get("public") and entry.get("commented") else 1)
