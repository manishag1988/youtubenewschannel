"""
Standalone Activity Logger — independent, zero-dependency logging of all work done.
Writes structured JSONL entries to a configurable log file.
Does NOT import or modify any existing project files.
"""

import json
import os
import threading
from datetime import datetime
from pathlib import Path

_ACTIVITY_LOG_PATH = None
_lock = threading.Lock()


def configure(log_path: str = None):
    """Set the activity log file path. Default: <project_root>/activity_log.jsonl"""
    global _ACTIVITY_LOG_PATH
    if log_path:
        _ACTIVITY_LOG_PATH = Path(log_path)
    else:
        _ACTIVITY_LOG_PATH = Path(__file__).parent / "activity_log.jsonl"
    _ACTIVITY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _ensure_configured():
    if _ACTIVITY_LOG_PATH is None:
        configure()


def log(level: str, source: str, message: str, detail: dict = None):
    """Write a single activity entry to the log file."""
    _ensure_configured()
    entry = {
        "timestamp": datetime.now().isoformat(sep=" ", timespec="milliseconds"),
        "level": level.upper(),
        "source": source,
        "message": message,
    }
    if detail:
        entry["detail"] = detail

    with _lock:
        try:
            with open(_ACTIVITY_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass


def info(source: str, message: str, detail: dict = None):
    """Log an INFO-level activity."""
    log("INFO", source, message, detail)


def warning(source: str, message: str, detail: dict = None):
    """Log a WARNING-level activity."""
    log("WARNING", source, message, detail)


def error(source: str, message: str, detail: dict = None):
    """Log an ERROR-level activity."""
    log("ERROR", source, message, detail)


def debug(source: str, message: str, detail: dict = None):
    """Log a DEBUG-level activity."""
    log("DEBUG", source, message, detail)


def get_log_path() -> Path:
    """Return the current activity log file path."""
    _ensure_configured()
    return _ACTIVITY_LOG_PATH


def read_all() -> list[dict]:
    """Read all entries from the activity log file."""
    _ensure_configured()
    if not _ACTIVITY_LOG_PATH.exists():
        return []
    entries = []
    with _lock:
        try:
            with open(_ACTIVITY_LOG_PATH, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except Exception:
            pass
    return entries


def read_filter(level: str = None, source: str = None, limit: int = None) -> list[dict]:
    """Read entries with optional filtering."""
    entries = read_all()
    if level:
        entries = [e for e in entries if e["level"] == level.upper()]
    if source:
        entries = [e for e in entries if e["source"] == source]
    if limit:
        entries = entries[-limit:]
    return entries


def summary() -> dict:
    """Return a summary of all logged activity."""
    entries = read_all()
    levels = {}
    sources = {}
    for e in entries:
        lv = e["level"]
        levels[lv] = levels.get(lv, 0) + 1
        src = e["source"]
        sources[src] = sources.get(src, 0) + 1
    return {
        "total_entries": len(entries),
        "time_range": {
            "first": entries[0]["timestamp"] if entries else None,
            "last": entries[-1]["timestamp"] if entries else None,
        },
        "by_level": levels,
        "by_source": sources,
    }
