import sys
sys.stdout.reconfigure(encoding='utf-8')
print("starting...", flush=True)

import activity_logger as al
import logging
from pathlib import Path

al.configure(str(Path(__file__).parent / "activity_log.jsonl"))
print("configured OK, path:", al.get_log_path(), flush=True)

# Direct test of the log function
al.info('direct_test', 'Testing direct log')
print("direct log done", flush=True)

import json
with open(al.get_log_path(), 'r') as f:
    content = f.read()
print("file content:", repr(content), flush=True)

# Now test patching
original_log = logging.Logger._log
def patched_log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
    entry = original_log(self, level, msg, args, exc_info, extra, stack_info, stacklevel)
    try:
        source = self.name or 'root'
        message = str(msg)
        if args:
            message = message % args
        if source != 'activity_logger':
            al.log('INFO', source, message)
    except Exception as e:
        import traceback
        print(f"PATCH ERR: {e}", flush=True)
        traceback.print_exc()
    return entry

logging.Logger._log = patched_log
print("patched OK", flush=True)

log = logging.getLogger('verify')
log.info('Verify test message')
print("logged OK", flush=True)

with open(al.get_log_path(), 'r') as f:
    content = f.read()
print("file content2:", repr(content), flush=True)

print("summary:", al.summary(), flush=True)
