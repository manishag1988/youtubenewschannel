"""
Logging utility for the automation tool
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from config import config


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console output"""

    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
    }
    RESET = '\033[0m'

    def format(self, record):
        original_levelname = record.levelname
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        result = super().format(record)
        record.levelname = original_levelname
        return result


class ActivityLogger:
    """Structured activity logger that writes JSON entries for easy review"""

    def __init__(self, log_path: Path = None):
        if log_path is None:
            log_path = config.BASE_DIR / "activities.jsonl"
        self.log_path = log_path
        self._ensure_file()

    def _ensure_file(self):
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.write_text("", encoding='utf-8')

    def log(self, level: str, module: str, message: str, **context):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.upper(),
            "module": module,
            "message": message,
        }
        if context:
            entry["context"] = {k: str(v) if not isinstance(v, (str, int, float, bool, type(None))) else v
                                for k, v in context.items()}
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception:
            pass

    def info(self, module: str, message: str, **context):
        self.log("INFO", module, message, **context)

    def warning(self, module: str, message: str, **context):
        self.log("WARNING", module, message, **context)

    def error(self, module: str, message: str, **context):
        self.log("ERROR", module, message, **context)

    def debug(self, module: str, message: str, **context):
        self.log("DEBUG", module, message, **context)


_activity_logger: Optional[ActivityLogger] = None


def get_activity_logger() -> ActivityLogger:
    global _activity_logger
    if _activity_logger is None:
        _activity_logger = ActivityLogger()
    return _activity_logger


class ActivityLogHandler(logging.Handler):
    """Logging handler that forwards to the structured activity log"""

    def __init__(self, activity_logger: ActivityLogger = None):
        super().__init__()
        self.activity = activity_logger or get_activity_logger()

    def emit(self, record):
        try:
            context = {}
            if hasattr(record, 'activity_context') and record.activity_context:
                context = record.activity_context
            self.activity.log(
                record.levelname,
                record.name or "root",
                self.format(record),
                **context
            )
        except Exception:
            pass


def setup_logger(name: str = None) -> logging.Logger:
    """
    Set up logger with file and console handlers

    Args:
        name: Logger name, defaults to project name

    Returns:
        Configured logger instance
    """
    project_name = getattr(config.logging, 'PROJECT_NAME', 'YouTubeNewsAutomator')
    logger = logging.getLogger(name or project_name)

    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, config.logging.LOG_LEVEL))

    log_format = '%(asctime)s | %(levelname)-8s | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)

    if config.logging.CONSOLE_OUTPUT:
        logger.addHandler(console_handler)

    try:
        file_handler = logging.FileHandler(
            config.logging.LOG_FILE,
            mode='a',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create log file: {e}")

    try:
        activity_handler = ActivityLogHandler()
        activity_handler.setLevel(logging.INFO)
        activity_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(activity_handler)
    except Exception as e:
        logger.warning(f"Could not create activity log: {e}")

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get or create logger"""
    project_name = getattr(config.logging, 'PROJECT_NAME', 'YouTubeNewsAutomator')
    return logging.getLogger(name or project_name)
