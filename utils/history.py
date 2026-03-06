import json
from datetime import datetime, date
from pathlib import Path

HISTORY_FILE = Path(__file__).resolve().parent.parent / "cache" / "history.json"


def _load() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save(data: dict):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.write_text(json.dumps(data, indent=2))


def record_snapshot(source: str, metrics: dict):
    """Record a daily snapshot for a source. Only stores one entry per day."""
    today = date.today().isoformat()
    data = _load()
    if source not in data:
        data[source] = {}
    data[source][today] = metrics
    _save(data)


def get_history(source: str) -> list[dict]:
    """Return list of {date, ...metrics} sorted by date."""
    data = _load()
    entries = data.get(source, {})
    rows = []
    for d, metrics in sorted(entries.items()):
        rows.append({"date": d, **metrics})
    return rows
