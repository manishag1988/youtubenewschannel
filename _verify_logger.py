import sys, traceback
sys.stdout.reconfigure(encoding='utf-8')
print("starting...", flush=True)

import activity_logger as al
import logging
from pathlib import Path

al.configure(str(Path(__file__).parent / "activity_log.jsonl"))

import logging

original_log = logging.Logger._log

def patched_log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
    print(f"  _log called: level={level}, msg={msg!r}, args={args!r}, stacklevel={stacklevel}", flush=True)
    entry = original_log(self, level, msg, args, exc_info, extra, stack_info, stacklevel)
    try:
        source = self.name or 'root'
        message = str(msg)
        if args:
            message = message % args
        if source != 'activity_logger':
            al.log('INFO', source, message)
    except Exception as e:
        print(f"PATCH ERR: {e}", flush=True)
        traceback.print_exc()
    return entry

logging.Logger._log = patched_log
print("patched OK", flush=True)

# Also patch info/warning to pass stacklevel correctly
log = logging.getLogger('verify')
print(f"logger isEnabledFor(20): {log.isEnabledFor(20)}", flush=True)
log.info('Verify test message')
print("logged OK", flush=True)

print("summary:", al.summary(), flush=True)
