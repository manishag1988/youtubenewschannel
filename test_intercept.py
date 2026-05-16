import sys
import logging
sys.stdout.reconfigure(encoding='utf-8')

import activity_logger as al
from pathlib import Path

al.configure(str(Path.cwd() / 'activity_log.jsonl'))

# Patch logging
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
        print(f"PATCH ERROR: {e}", flush=True)
    return entry

logging.Logger._log = patched_log

# Test
log = logging.getLogger('test_module')
log.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, force=True)

print("--- logging test ---", flush=True)
log.info('Hello from %s', 'module')
log.warning('Warning: %s', 'something')

print("--- summary ---", flush=True)
print(al.summary(), flush=True)
