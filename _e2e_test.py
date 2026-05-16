"""End-to-end test: verify run_with_logging captures all log calls."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import run_with_logging
import activity_logger as al
import logging

# Verify the patch is installed
log = logging.getLogger('e2e_test')
logging.basicConfig(level=logging.INFO, force=True)
log.info('E2E verification message')
log.warning('E2E warning')
log.error('E2E error')

s = al.summary()
print("Total entries:", s['total_entries'], file=sys.stderr)
assert s['total_entries'] >= 3, f"Expected >=3, got {s['total_entries']}"

sources = s['by_source']
print("Sources:", sources, file=sys.stderr)
assert 'e2e_test' in sources, f"e2e_test not found in {sources}"

# Read filtered
from_src = al.read_filter(source='e2e_test')
print(f"e2e_test entries: {len(from_src)}", file=sys.stderr)
assert len(from_src) == 3

# Verify all three levels present
levels = {e['level'] for e in from_src}
assert 'INFO' in levels and 'WARNING' in levels and 'ERROR' in levels

print("ALL ASSERTIONS PASSED", file=sys.stderr)
