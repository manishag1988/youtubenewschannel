"""
Automated Activity Logging Wrapper

Automatically captures ALL logging activity from the main workflow
into activity_log.jsonl.  Standalone — does NOT modify any existing project files.
"""

import sys
import logging
from pathlib import Path

import activity_logger as al

BASE = Path(__file__).parent
al.configure(str(BASE / "activity_log.jsonl"))
al.info("run_with_logging", "Activity logging wrapper started", detail={"cwd": str(BASE)})


# ---- ensure loggers are enabled so _log is actually called ----
logging.getLogger().setLevel(logging.INFO)


# ---- intercept every Logger._log call and mirror to activity_logger ----
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
    _original_log(self, level, msg, args, exc_info, extra, stack_info, stacklevel)
    try:
        source = self.name or "root"
        message = str(msg)
        if args:
            message = message % args
        if source != "activity_logger":
            al.log(_activity_level(level), source, message)
    except Exception:
        pass


logging.Logger._log = _patched_log

al.info("run_with_logging", "Log interceptor installed")


# ---- patch run_full_workflow for structured result detail ----
def _apply_patches():
    import main as m
    cls = getattr(m, "YouTubeNewsAutomator", None)
    if cls and hasattr(cls, "run_full_workflow"):
        original = cls.run_full_workflow

        def wrapper(*args, **kwargs):
            result = original(*args, **kwargs)
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

        cls.run_full_workflow = wrapper
        al.info("run_with_logging", "Patched run_full_workflow")


# ---- main ----
if __name__ == "__main__":
    _apply_patches()

    al.info("run_with_logging", "Launching main workflow", detail={"log_file": str(al.get_log_path()), "python": sys.version.split()[0]})

    try:
        from main import main as _run_main
        exit_code = _run_main()
        al.info("run_with_logging", "Process exited", detail={"exit_code": exit_code})
        sys.exit(exit_code)
    except KeyboardInterrupt:
        al.warning("run_with_logging", "Process interrupted")
        sys.exit(130)
    except Exception as exc:
        al.error("run_with_logging", "Fatal error", detail={"error": str(exc)})
        raise
