import os
import subprocess
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DEBOUNCE_SECONDS = 10
IGNORE_DIRS = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '.gitattributes'}
IGNORE_EXTS = {'.pyc', '.log'}

last_change = 0
timer_active = False


def run_git_commands():
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=REPO_DIR
        )
        if not result.stdout.strip():
            print(f"[{now()}] No changes to commit.")
            return

        subprocess.run(["git", "add", "-A"], cwd=REPO_DIR, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"auto: update {datetime.now().strftime('%Y-%m-%d %H:%M')}"],
            cwd=REPO_DIR, check=True, capture_output=True
        )
        print(f"[{now()}] Committed changes.")

        push = subprocess.run(
            ["git", "push"], cwd=REPO_DIR, capture_output=True, text=True
        )
        if push.returncode == 0:
            print(f"[{now()}] Pushed to GitHub.")
        else:
            print(f"[{now()}] Push failed: {push.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"[{now()}] Git error: {e}")


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
