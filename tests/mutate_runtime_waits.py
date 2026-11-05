"""Kill runtime regressions in disposable copies, leaving the lane worktree intact."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


REPO = Path(__file__).resolve().parents[1]
WATCH = 'dispatching-work/scripts/watch-inbox.sh'
DEADLINES = 'dispatching-work/scripts/deadlines.py'
PAIRS = [
    ('test_orca_not_installed', WATCH,
     'command -v orca >/dev/null 2>&1 || { echo "watch-inbox.sh: runtime orca not installed" >&2; exit 2; }', ':'),
    ('test_herdr_agent', WATCH, 'if [ "$ms" -gt "$remaining" ]; then ms=$remaining; fi', ':'),
    ('test_watcher_deadline_runtime', WATCH, '--runtime "$runtime" --ledger "$ledger" --new', '--runtime orca --ledger "$ledger" --new'),
    ('test_deadline_invalid_probe', DEADLINES, "parts[0] not in ('herdr:agent', 'herdr:pane')", 'False'),
    ('test_default_orca', WATCH, 'runtime="${MUSTER_RUNTIME:-orca}"', 'runtime="${MUSTER_RUNTIME:-herdr}"'),
    ('test_herdr_agent', WATCH, 'herdr agent wait "$target"', 'herdr agent get "$target"'),
    ('test_env_and_pane_literal', WATCH, '--match "$match" --source', '--regex "$match" --source'),
    ('test_flag_overrides_env', WATCH, 'runtime=$2; shift 2', 'runtime=herdr; shift 2'),
    ('test_requires_context_and_target', WATCH, '[ "${HERDR_ENV:-}" != 1 ]', '[ 1 != 1 ]'),
    ('test_invalid_runtime', WATCH, 'unknown runtime: $runtime" >&2; exit 2', 'unknown runtime: $runtime" >&2; exit 0'),
    ('test_timeout_rearms', WATCH, '== "timeout" else 1', '== "never" else 1'),
    ('test_error_is_visible', WATCH, 'wait failed (rc=%s): %s\\n\' "$rc" "$raw" >&2\n    exit 1',
     'wait failed (rc=%s): %s\\n\' "$rc" "$raw" >&2\n    exit 0'),
    ('test_deadline_herdr_argv', DEADLINES, "'read', parts[1]", "'get', parts[1]"),
    ('test_deadline_pane_env', DEADLINES, "surface = parts[0].split(':')[1]", "surface = 'agent'"),
    ('test_deadline_requires_herdr_mode', DEADLINES, "if runtime != 'herdr':", 'if False:'),
    ('test_deadline_requires_context', DEADLINES, "if os.environ.get('HERDR_ENV') != '1':", 'if False:'),
    ('test_deadline_shell_and_seen', DEADLINES, "return check_cmd, True", "return 'printf WRONG', True"),
]


def run(test=None, root=REPO):
    command = [sys.executable, '-m', 'unittest']
    command += [f'test_runtime_waits.RuntimeTests.{test}'] if test else ['test_runtime_waits']
    return subprocess.run(command, cwd=REPO / 'tests', text=True, capture_output=True,
                          env={**os.environ, 'MUSTER_RUNTIME_ROOT': str(root)}, timeout=30)


def main():
    baseline = run()
    if baseline.returncode:
        raise SystemExit(baseline.stdout + baseline.stderr)
    print('GREEN: unmodified runtime pins', flush=True)
    with tempfile.TemporaryDirectory(prefix='runtime mutants ') as tmp:
        root = Path(tmp)
        for path in (WATCH, DEADLINES):
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / path, root / path)
        for test, relative, before, after in PAIRS:
            original = (REPO / relative).read_text()
            if original.count(before) != 1:
                raise SystemExit(f'non-unique mutation: {test}: {before}')
            try:
                (root / relative).write_text(original.replace(before, after))
                result = run(test, root)
                if result.returncode == 0 or 'FAIL:' not in result.stderr:
                    raise SystemExit(f'NOT RED: {test}\n{result.stdout}{result.stderr}')
                print(f'RED: {test}', flush=True)
            finally:
                (root / relative).write_text(original)
    print(f'PASS: {len(PAIRS)} mutations killed', flush=True)


if __name__ == '__main__':
    main()
