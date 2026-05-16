import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.logger import ActivityLogger

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
CHANGELOG_PATH = os.path.join(REPO_DIR, 'CHANGELOG.md')
DEBOUNCE_SECONDS = 10
IGNORE_DIRS = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '.gitattributes'}
IGNORE_EXTS = {'.pyc', '.log'}

_activity = ActivityLogger(Path(REPO_DIR) / "activities.jsonl")

last_change = 0
timer_active = False


def update_changelog():
    """Prepend pending file changes as a new changelog entry."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=REPO_DIR
        )
        lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
        if not lines:
            return

        date_str = datetime.now().strftime('%Y-%m-%d')
        time_str = datetime.now().strftime('%H:%M')
        entry = f"\n### auto: update {time_str}\n"

        for line in lines:
            status = line[:2].strip()
            filepath = line[3:].strip()
            if status in ('??', 'A '):
                action = 'Added'
            elif 'D' in status:
                action = 'Deleted'
            elif 'R' in status:
                action = 'Renamed'
            else:
                action = 'Modified'
            entry += f"- **{filepath}**: {action}\n"

        if not os.path.exists(CHANGELOG_PATH):
            print(f"[{now()}] CHANGELOG.md not found, skipping update.")
            return

        with open(CHANGELOG_PATH, 'r', encoding='utf-8') as f:
            content = f.read()

        today_header = f"## {date_str}"
        marker = '---\n'

        # Check if today's section already exists
        if today_header in content:
            # Append entry inside existing today's section
            # Find the end of today's section (next ## or end of file)
            today_idx = content.index(today_header)
            next_section = content.find('\n## ', today_idx + len(today_header))
            if next_section != -1:
                content = content[:next_section] + entry + content[next_section:]
            else:
                content += entry
        else:
            # Insert after the --- marker (before version history)
            section = f"\n{today_header}\n{entry}\n"
            idx = content.find(marker)
            if idx != -1:
                idx += len(marker)
                content = content[:idx] + section + content[idx:]
            else:
                content += '\n' + section

        with open(CHANGELOG_PATH, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[{now()}] CHANGELOG.md updated.")
    except Exception as e:
        print(f"[{now()}] Changelog update error: {e}")


def run_git_commands():
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=REPO_DIR
        )
        if not result.stdout.strip():
            print(f"[{now()}] No changes to commit.")
            return

        update_changelog()

        # Skip commit if only CHANGELOG.md changed
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=REPO_DIR
        )
        remaining = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
        real_changes = [l for l in remaining if 'CHANGELOG.md' not in l]
        if not real_changes:
            print(f"[{now()}] Only CHANGELOG.md changed; skipping commit cycle.")
            return

        subprocess.run(["git", "add", "-A"], cwd=REPO_DIR, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"auto: update {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
            cwd=REPO_DIR, check=True, capture_output=True
        )
        print(f"[{now()}] Committed changes.")
        _activity.info("auto_watcher", "Committed changes")

        push = subprocess.run(
            ["git", "push"], cwd=REPO_DIR, capture_output=True, text=True
        )
        if push.returncode == 0:
            print(f"[{now()}] Pushed to GitHub.")
            _activity.info("auto_watcher", "Pushed to GitHub")
        else:
            print(f"[{now()}] Push failed: {push.stderr.strip()}")
            _activity.warning("auto_watcher", f"Push failed: {push.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"[{now()}] Git error: {e}")
        _activity.error("auto_watcher", f"Git error: {e}")


def now():
    return datetime.now().strftime("%H:%M:%S")


class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        self.schedule_commit(event)

    def on_created(self, event):
        self.schedule_commit(event)

    def on_deleted(self, event):
        self.schedule_commit(event)

    def on_moved(self, event):
        self.schedule_commit(event)

    def schedule_commit(self, event):
        global last_change, timer_active
        src = event.src_path.replace("\\", "/")
        if any(ign in src for ign in IGNORE_DIRS):
            return
        if any(src.endswith(ext) for ext in IGNORE_EXTS):
            return
        if timer_active:
            return
        last_change = time.time()
        timer_active = True
        print(f"[{now()}] Change detected: {os.path.basename(src)}")
        while time.time() - last_change < DEBOUNCE_SECONDS:
            time.sleep(1)
        timer_active = False
        run_git_commands()


if __name__ == "__main__":
    print(f"[{now()}] Auto-watcher started for: {REPO_DIR}")
    print(f"[{now()}] Watching for changes (debounce: {DEBOUNCE_SECONDS}s)...")
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, REPO_DIR, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
