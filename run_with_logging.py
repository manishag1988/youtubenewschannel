"""
Automated Activity Logging Wrapper
Runs the main workflow and automatically captures all activity into activity_log.jsonl.
Does NOT modify any existing project files — this is a standalone launcher.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
import threading

import activity_logger as al

BASE = Path(__file__).parent
al.configure(str(BASE / "activity_log.jsonl"))

al.info("run_with_logging", "Activity logging wrapper started", detail={"cwd": str(BASE)})


# ---- capture every logging.Logger call and mirror it to activity_logger ----
_log_lock = threading.Lock()
_log_counter = 0


def _activity_level(log_level: int) -> str:
    if log_level >= logging.ERROR:
        return "ERROR"
    if log_level >= logging.WARNING:
        return "WARNING"
    if log_level >= logging.INFO:
        return "INFO"
    return "DEBUG"


_original_log = logging.Logger._log


def _patched_log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
    entry = _original_log(self, level, msg, args, exc_info, extra, stack_info, stacklevel)
    try:
        source = self.name or "root"
        message = str(msg)
        if args:
            message = message % args
        # Skip activity_logger's own calls to avoid infinite recursion
        if source != "activity_logger":
            al.log(_activity_level(level), source, message)
    except Exception:
        pass
    return entry


logging.Logger._log = _patched_log

al.info("run_with_logging", "Log interceptor installed — all module logs will be captured")


# ---- wrap common workflow entry points for structured detail ----
_original_main_fn = None


def _wrap_run_full_workflow(original_method):
    def wrapper(*args, **kwargs):
        result = original_method(*args, **kwargs)
        al.info(
            "workflow",
            "Workflow completed",
            detail={
                "success": getattr(result, "success", None),
                "duration_s": round(getattr(result, "duration", 0), 1),
                "stories": len(getattr(result, "news", [])),
                "errors": len(getattr(result, "errors", [])),
            },
        )
        return result
    return wrapper


# Dynamically patch YouTubeNewsAutomator at import time (after it's defined)
_original_run = None


def _apply_patches():
    """
    Monkey-patch main.YouTubeNewsAutomator.run_full_workflow
    so structured result details flow into the activity log.
    """
    import main as m

    cls = getattr(m, "YouTubeNewsAutomator", None)
    if cls and hasattr(cls, "run_full_workflow"):
        original = cls.run_full_workflow
        cls.run_full_workflow = _wrap_run_full_workflow(original)
        al.info("run_with_logging", "Patched YouTubeNewsAutomator.run_full_workflow")


# ---- startup banner ----
al.info(
    "run_with_logging",
    "Ready — launching main workflow",
    detail={
        "log_file": str(al.get_log_path()),
        "python": sys.version.split()[0],
    },
)

# ---- go ----
if __name__ == "__main__":
    _apply_patches()

    try:
        from main import main as _run_main
        exit_code = _run_main()
        al.info("run_with_logging", "Process exited", detail={"exit_code": exit_code})
        sys.exit(exit_code)
    except KeyboardInterrupt:
        al.warning("run_with_logging", "Interrupted by user")
        sys.exit(130)
    except Exception as exc:
        al.error("run_with_logging", "Fatal error", detail={"error": str(exc)})
        raise
