#!/usr/bin/env python3
"""Deadline ledger check for a waiting Orca coordinator or PM.

Silence from a dispatched lane is not evidence of progress. This script reads a
tab-separated ledger of expected completion times and reports the lines that
have passed theirs, running each line's outcome check so the waiter judges the
OUTCOME (a report file, a PR, a commit) rather than polling the mailbox. It is
the deadline half of watch-inbox.sh, Orca's orchestration mailbox watcher: run
watch-inbox.sh as a background task, and when it exits, drain and ack the
mailbox, then start it again.

Ledger format, one line per dispatched lane:

    <expected_by ISO-8601 or epoch>\t<label>\t<outcome check shell command>

Use expected_by = dispatch time plus twice the expected duration. Delete the
line once the lane's worker_done is handled.

The ledger path comes from --ledger or the DEADLINE_LEDGER environment
variable; with neither the script refuses to guess a default.

--next prints the seconds until the nearest future deadline (empty when there
is none), for sizing watch-inbox.sh's mailbox wait. --new reports only
deadlines not reported by an earlier run, keeping a seen-file beside the
ledger, so a waiter wakes once per overdue lane instead of on every poll; the
coordinator still acts on every overdue lane on the next full run.
"""

import argparse
import datetime
import os
import pathlib
import subprocess
import sys
import time


def parse_timestamp(ts):
    ts = ts.strip()
    if ts.isdigit():
        return int(ts)
    return int(datetime.datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp())


def load_rows(ledger):
    rows = []
    if ledger.exists():
        for line in ledger.read_text().splitlines():
            if not line.strip() or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) >= 3:
                rows.append((parse_timestamp(parts[0]), parts[1], parts[2]))
    return rows


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--ledger', default=os.environ.get('DEADLINE_LEDGER'),
                        help='path to the deadline ledger (default: $DEADLINE_LEDGER)')
    parser.add_argument('--next', action='store_true',
                        help='print seconds until the nearest future deadline and exit')
    parser.add_argument('--new', action='store_true',
                        help='report only deadlines not reported by an earlier run')
    args = parser.parse_args()

    if not args.ledger:
        parser.error('no ledger given: pass --ledger or set DEADLINE_LEDGER')
    ledger = pathlib.Path(args.ledger).expanduser()
    rows = load_rows(ledger)
    now = int(time.time())

    if args.next:
        future = [t - now for t, _, _ in rows if t > now]
        print(min(future) if future else '')
        return

    overdue = [r for r in rows if r[0] <= now]
    if args.new:
        seen_file = ledger.with_name('.' + ledger.name + '.seen')
        seen = set(seen_file.read_text().splitlines()) if seen_file.exists() else set()
        overdue = [r for r in overdue if f'{r[1]}|{r[0]}' not in seen]
        with seen_file.open('a') as f:
            for r in overdue:
                f.write(f'{r[1]}|{r[0]}\n')

    for expected, label, check_cmd in overdue:
        due = datetime.datetime.fromtimestamp(expected).isoformat(timespec='minutes')
        print(f'OVERDUE {label} (expected by {due})')
        try:
            out = subprocess.run(check_cmd, shell=True, capture_output=True,
                                 text=True, timeout=60)
            text = (out.stdout + out.stderr).strip()[:400]
        except subprocess.TimeoutExpired:
            text = '(check command timed out)'
        print('  check:', text or '(no output)')
    sys.exit(1 if overdue else 0)


if __name__ == '__main__':
    main()