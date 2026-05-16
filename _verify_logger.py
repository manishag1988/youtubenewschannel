import sys
sys.stdout.reconfigure(encoding='utf-8')
print("starting...", flush=True)

import run_with_logging
import activity_logger as al

print("imported OK", flush=True)

# test interception
import logging
log = logging.getLogger('verify')
log.info('Verify test message')

print("summary:", al.summary(), flush=True)
