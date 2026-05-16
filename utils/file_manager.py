"""
File management utilities for handling outputs
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from config import config, OUTPUT_DIR
from utils.logger import get_logger

logger = get_logger()


class FileManager:
    """Manages file operations for the automation tool"""

    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or OUTPUT_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_session_dir(self, session_name: str = None) -> Path:
        """Create a timestamped session directory"""
        if session_name is None:
            session_name = datetime.now().strftime("%Y%m%d_%H%M%S")

        session_dir = self.base_dir / session_name
        session_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Created session directory: {session_dir}")
        return session_dir

    def get_output_path(self, filename: str, session_dir: Path = None) -> Path:
        """Get full output path for a file"""
        if session_dir is None:
            session_dir = self.base_dir

        return session_dir / filename

    def save_text(self, content: str, filename: str, session_dir: Path = None) -> Path:
        """Save text content to file"""
        path = self.get_output_path(filename, session_dir)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.debug(f"Saved text to: {path}")
        return path

    def save_binary(self, data: bytes, filename: str, session_dir: Path = None) -> Path:
        """Save binary content to file"""
        path = self.get_output_path(filename, session_dir)

        with open(path, 'wb') as f:
            f.write(data)

        logger.debug(f"Saved binary to: {path}")
        return path

    def read_text(self, filename: str, session_dir: Path = None) -> str:
        """Read text from file"""
        path = self.get_output_path(filename, session_dir)

        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def list_files(self, session_dir: Path = None, extension: str = None) -> List[Path]:
        """List files in directory, optionally filtered by extension"""
        target_dir = session_dir or self.base_dir

        if extension:
            if not extension.startswith('.'):
                extension = f'.{extension}'
            return sorted(target_dir.glob(f'*{extension}'))

        return sorted(target_dir.glob('*'))

    def cleanup_old_sessions(self, keep_days: int = 7):
        """Remove session directories older than specified days"""
        cutoff = datetime.now().timestamp() - (keep_days * 86400)

        for item in self.base_dir.iterdir():
            if item.is_dir():
                mtime = item.stat().st_mtime
                if mtime < cutoff:
                    shutil.rmtree(item)
                    logger.info(f"Cleaned up old session: {item.name}")

    def get_file_size(self, filename: str, session_dir: Path = None) -> int:
        """Get file size in bytes"""
        path = self.get_output_path(filename, session_dir)
        return path.stat().st_size if path.exists() else 0

    def move_file(self, src: Path, dest: Path):
        """Move file to destination"""
        shutil.move(str(src), str(dest))
        logger.debug(f"Moved {src} to {dest}")

    def copy_file(self, src: Path, dest: Path):
        """Copy file to destination"""
        shutil.copy2(str(src), str(dest))
        logger.debug(f"Copied {src} to {dest}")