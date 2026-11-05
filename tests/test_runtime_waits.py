"""Behavioral pins for runtime waits and deadline probes; no live server needed."""

import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(os.environ.get('MUSTER_RUNTIME_ROOT', Path(__file__).resolve().parents[1]))
SCRIPTS = REPO / 'dispatching-work/scripts'


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.log = self.root / 'calls'
        fake = '''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
log = Path(os.environ['CALL_LOG'])
calls = log.read_text().splitlines() if log.exists() else []
with log.open('a') as stream:
    stream.write(json.dumps([Path(sys.argv[0]).name, *sys.argv[1:]]) + '\\n')
mode = os.environ.get('FAKE_MODE', '')
if mode == 'timeout' and not calls:
    print(json.dumps({'error': {'code': 'timeout'}}), file=sys.stderr)
    sys.exit(1)
if mode == 'error':
    print(json.dumps({'error': {'code': 'agent_not_found'}}), file=sys.stderr)
    sys.exit(1)
print(json.dumps({'ok': True, 'count': 1, 'result': {'agent_status': 'done'}, 'output': 'REPORT_OK'}))
'''
        for name in ('orca', 'herdr'):
            path = self.root / name
            path.write_text(fake)
            path.chmod(0o755)
        self.env = {**os.environ, 'PATH': str(self.root) + os.pathsep + os.environ['PATH'],
                    'CALL_LOG': str(self.log), 'HERDR_ENV': '1'}
        self.env.pop('MUSTER_RUNTIME', None)
        self.env.pop('DEADLINE_LEDGER', None)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def watch(self, *args):
        return subprocess.run(['bash', str(SCRIPTS / 'watch-inbox.sh'),
                               '--window', '2', '--poll-secs', '1', *args],
                              env=self.env, capture_output=True, text=True, timeout=5)

    def test_default_orca(self):
        result = self.watch('--run', 'run-one')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('REPORT_OK', result.stdout)
        self.assertEqual(self.calls()[0][:6], ['orca', 'orchestration', 'check', '--run', 'run-one', '--peek'])

    def test_herdr_agent(self):
        result = self.watch('--runtime', 'herdr', '--target', 'lane', '--poll-secs', '10')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('REPORT_OK', result.stdout)
        self.assertEqual(self.calls()[0][:4], ['herdr', 'agent', 'wait', 'lane'])
        self.assertLessEqual(int(self.calls()[0][-1]), 2000)

    def test_env_and_pane_literal(self):
        self.env['MUSTER_RUNTIME'] = 'herdr'
        result = self.watch('--target', 'w99:p1', '--match', 'a;$(touch nope)')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('REPORT_OK', result.stdout)
        self.assertEqual(self.calls()[0][:8], ['herdr', 'pane', 'wait-output', 'w99:p1',
                                               '--match', 'a;$(touch nope)', '--source', 'recent-unwrapped'])

    def test_flag_overrides_env(self):
        self.env['MUSTER_RUNTIME'] = 'herdr'
        result = self.watch('--runtime', 'orca', '--run', 'one')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls()[0][0], 'orca')

    def test_requires_context_and_target(self):
        self.env.pop('HERDR_ENV')
        result = self.watch('--runtime', 'herdr', '--target', 'lane')
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.log.exists())
        self.env['HERDR_ENV'] = '1'
        self.assertEqual(self.watch('--runtime', 'herdr').returncode, 2)

    def test_orca_not_installed(self):
        (self.root / 'orca').unlink()
        for tool in ('bash', 'date', 'dirname'):
            (self.root / tool).symlink_to(shutil.which(tool))
        self.env['PATH'] = str(self.root)
        result = self.watch('--runtime', 'orca', '--run', 'one', '--window', '0')
        self.assertEqual(result.returncode, 2)
        self.assertIn('watch-inbox.sh: runtime orca not installed', result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertFalse(self.log.exists())

    def test_invalid_runtime(self):
        self.assertEqual(self.watch('--runtime', 'unknown', '--run', 'one').returncode, 2)
        self.assertFalse(self.log.exists())

    def test_timeout_rearms(self):
        self.env['FAKE_MODE'] = 'timeout'
        result = self.watch('--runtime', 'herdr', '--target', 'lane')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('REPORT_OK', result.stdout)
        self.assertEqual(len(self.calls()), 2)

    def test_error_is_visible(self):
        self.env['FAKE_MODE'] = 'error'
        result = self.watch('--runtime', 'herdr', '--target', 'lane')
        self.assertEqual(result.returncode, 1)
        self.assertIn('agent_not_found', result.stderr)
        self.assertEqual(len(self.calls()), 1)

    def deadline(self, check, *args):
        ledger = self.root / 'ledger'
        ledger.write_text('1\tlane\t' + check + '\n')
        return subprocess.run([sys.executable, str(SCRIPTS / 'deadlines.py'),
                               '--ledger', str(ledger), *args], env=self.env,
                              capture_output=True, text=True, timeout=5)

    def test_watcher_deadline_runtime(self):
        ledger = self.root / 'ledger'
        ledger.write_text('1\tlane\therdr:agent lane\n')
        result = self.watch('--runtime', 'herdr', '--target', 'lane', '--ledger', str(ledger))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('OVERDUE lane', result.stdout)
        self.assertIn('REPORT_OK', result.stdout)
        self.assertEqual(self.calls()[0][:4], ['herdr', 'agent', 'read', 'lane'])

    def test_deadline_invalid_probe(self):
        result = self.deadline('herdr:invalid lane', '--runtime', 'herdr')
        self.assertIn('use herdr:agent TARGET', result.stdout)
        self.assertFalse(self.log.exists())

    def test_deadline_herdr_argv(self):
        result = self.deadline('herdr:agent lane', '--runtime', 'herdr')
        self.assertEqual(result.returncode, 1)
        self.assertIn('OVERDUE lane', result.stdout)
        self.assertIn('REPORT_OK', result.stdout)
        self.assertEqual(self.calls()[0], ['herdr', 'agent', 'read', 'lane', '--source',
                                           'recent-unwrapped', '--lines', '120'])

    def test_deadline_pane_env(self):
        self.env['MUSTER_RUNTIME'] = 'herdr'
        result = self.deadline('herdr:pane w99:p1')
        self.assertIn('REPORT_OK', result.stdout)
        self.assertEqual(self.calls()[0][:4], ['herdr', 'pane', 'read', 'w99:p1'])

    def test_deadline_requires_herdr_mode(self):
        result = self.deadline('herdr:agent lane')
        self.assertIn('requires --runtime herdr', result.stdout)
        self.assertFalse(self.log.exists())

    def test_deadline_requires_context(self):
        self.env.pop('HERDR_ENV')
        result = self.deadline('herdr:agent lane', '--runtime', 'herdr')
        self.assertIn('requires HERDR_ENV=1', result.stdout)
        self.assertFalse(self.log.exists())

    def test_deadline_shell_and_seen(self):
        result = self.deadline('printf OUTCOME', '--new')
        self.assertIn('check: OUTCOME', result.stdout)
        result = self.deadline('printf OUTCOME', '--new')
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('OVERDUE', result.stdout)


if __name__ == '__main__':
    unittest.main()
