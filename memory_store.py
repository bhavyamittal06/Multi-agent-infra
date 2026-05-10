"""Append-only JSON file store for triage runs."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path(__file__).resolve().parent / "triage_memory.json"


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"runs": []}
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if "runs" not in data:
        data["runs"] = []
    return data


def append_run(record: dict[str, Any], path: Path | None = None) -> None:
    p = path or DEFAULT_PATH
    data = _load(p)
    entry = {
        **record,
        "stored_at": datetime.now(timezone.utc).isoformat(),
    }
    data["runs"].append(entry)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
