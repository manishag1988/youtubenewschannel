import sys
sys.stdout.reconfigure(encoding='utf-8')

print("step 1: importing activity_logger", flush=True)

import activity_logger as al
from pathlib import Path

print("step 2: configuring", flush=True)
al.configure(str(Path.cwd() / 'activity_log.jsonl'))

print("step 3: logging", flush=True)
al.info('test', 'alive check')

print("step 4: summary", flush=True)
s = al.summary()
print("summary:", s, flush=True)
