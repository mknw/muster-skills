"""Prompt-hook and opt-in setup regressions, each paired in mutate_discontent.py."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(os.environ.get('MUSTER_DISCONTENT_ROOT', Path(__file__).resolve().parents[1]))
HOOK = REPO / 'self-improve/hooks/discontent.py'
INSTALLER = 'scripts/install-discontent-hook.py'


class DiscontentTests(unittest.TestCase):
    def invoke(self, prompt=None, raw=None):
        result = subprocess.run(
            [sys.executable, str(HOOK)], input=raw if raw is not None else json.dumps({'prompt': prompt}),
            text=True, capture_output=True, timeout=4,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        return result.stdout

    def fires(self, prompt):
        output = json.loads(self.invoke(prompt))
        self.assertEqual(output['hookSpecificOutput']['hookEventName'], 'UserPromptSubmit')
        context = output['hookSpecificOutput']['additionalContext']
        for term in ('DISCONTENT', 'self-improve', 'SUBAGENT', 'extract', 'Expected',
                     'Observed', 'Decisions made and why', 'Attempts and outcomes',
                     'FORCED independent review to CONVERGED'):
            self.assertIn(term, context)

    def test_fucking_fires(self):
        self.fires('The fucking do it.')

    def test_shit_fires(self):
        self.fires('This is shit.')

    def test_wtf_fires(self):
        self.fires('wtf, do it now')

    def test_case_insensitive(self):
        self.fires('WTF!')

    def test_shitake_is_quiet(self):
        self.assertEqual(self.invoke('Shitake'), '')

    def test_kutter_is_quiet(self):
        self.assertEqual(self.invoke('kutter'), '')

    def test_damnation_is_quiet(self):
        self.assertEqual(self.invoke('Damnation'), '')

    def test_pasted_content_is_quiet(self):
        self.assertEqual(self.invoke('Please read <PASTED_CONTENT source="log">\nfucking shit\n'
                                     '</PASTED_CONTENT> and explain.'), '')

    def test_system_reminder_is_quiet(self):
        self.assertEqual(self.invoke('Please read <system-reminder>\nwtf\n'
                                     '</system-reminder> and explain.'), '')

    def test_own_words_outside_exclusions_fire(self):
        self.fires('<pasted_content>clean</pasted_content> fucking do it '
                   '<system-reminder>clean</system-reminder>')

    def test_malformed_json_is_quiet(self):
        self.assertEqual(self.invoke(raw='{'), '')

    def test_invalid_payloads_are_quiet(self):
        for raw in ('[]', 'null', '"wtf"', '{}', '{"prompt":null}', '{"prompt":7}',
                    '{"prompt":["wtf"]}'):
            with self.subTest(raw=raw):
                self.assertEqual(self.invoke(raw=raw), '')

    def test_timeout_is_quiet(self):
        # Keep stdin open without EOF: json.load must be interrupted by the real deadline.
        process = subprocess.Popen([sys.executable, str(HOOK)], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(process.wait(timeout=3), 0)
            self.assertEqual(process.stdout.read(), '')
            self.assertEqual(process.stderr.read(), '')
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=3)
            for stream in (process.stdin, process.stdout, process.stderr):
                stream.close()


class DiscontentInstallTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix='discontent setup ')
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name).resolve()
        self.repo = self.root / 'main checkout'
        for relative in (INSTALLER, 'self-improve/hooks/discontent.py'):
            target = self.repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / relative, target)
        self.home = self.root / 'home dir `touch INJECTED`'
        self.home.mkdir()
        self.claude = self.home / '.claude'
        self.settings = self.claude / 'settings.json'
        self.link = self.claude / 'hooks/discontent.py'
        self.env = {**os.environ, 'HOME': str(self.home)}
        self.env.pop('CLAUDE_CONFIG_DIR', None)

    def run_installer(self, *args):
        return subprocess.run([sys.executable, str(self.repo / INSTALLER), *args],
                              env=self.env, capture_output=True, text=True, timeout=5)

    def write_settings(self, data):
        self.claude.mkdir(parents=True, exist_ok=True)
        self.settings.write_text(json.dumps(data))

    def test_install_and_idempotence(self):
        first = self.run_installer()
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertTrue(self.link.is_symlink())
        self.assertEqual(self.link.resolve(), self.repo / 'self-improve/hooks/discontent.py')
        content = self.settings.read_bytes()
        self.assertEqual(self.run_installer().returncode, 0)
        self.assertEqual(self.settings.read_bytes(), content)
        entries = json.loads(content)['hooks']['UserPromptSubmit']
        self.assertEqual(len(entries), 1)
        hook = entries[0]['hooks'][0]
        self.assertEqual(hook['timeout'], 5)
        result = subprocess.run(hook['command'], shell=True, input='{"prompt":"wtf"}',
                                env=self.env, cwd=self.root, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('CONVERGED', json.loads(result.stdout)['hookSpecificOutput']['additionalContext'])
        self.assertFalse((self.root / 'INJECTED').exists())

    def test_preserves_other_settings_and_legacy_registration(self):
        original = {'theme': 'dark', 'hooks': {
            'Stop': [{'hooks': [{'type': 'command', 'command': 'echo stop'}]}],
            'UserPromptSubmit': [{'matcher': '*', 'hooks': [
                {'type': 'command', 'command': 'echo unrelated'},
                {'type': 'command', 'command': 'python3 ~/.claude/hooks/discontent.py', 'timeout': 5},
            ]}],
        }}
        self.write_settings(original)
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.settings.read_text()), original)

    def test_existing_file_requires_explicit_migration(self):
        self.link.parent.mkdir(parents=True)
        self.link.write_text('previous standalone hook\n')
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.link.read_text(), 'previous standalone hook\n')
        self.assertFalse(self.settings.exists())
        result = self.run_installer('--replace-hook')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.link.is_symlink())
        self.assertEqual(self.link.with_name('discontent.py.pre-muster').read_text(),
                         'previous standalone hook\n')
        self.assertEqual(self.run_installer('--replace-hook').returncode, 0)

    def test_foreign_symlink_and_existing_backup_are_preserved(self):
        self.link.parent.mkdir(parents=True)
        foreign = self.root / 'foreign.py'
        foreign.write_text('foreign hook')
        self.link.symlink_to(foreign)
        result = self.run_installer('--replace-hook')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.link.resolve(), foreign)
        self.link.unlink()
        self.link.write_text('current hook')
        backup = self.link.with_name('discontent.py.pre-muster')
        backup.write_text('older hook')
        self.assertNotEqual(self.run_installer('--replace-hook').returncode, 0)
        self.assertEqual(self.link.read_text(), 'current hook')
        self.assertEqual(backup.read_text(), 'older hook')

    def test_bad_settings_fail_before_changing_hook(self):
        for text in ('{', '[]', '{"hooks":[]}', '{"hooks":{"UserPromptSubmit":{}}}',
                     '{"hooks":{"UserPromptSubmit":[{"hooks":[7]}]}}'):
            with self.subTest(text=text):
                self.claude.mkdir(parents=True, exist_ok=True)
                self.settings.write_text(text)
                self.assertNotEqual(self.run_installer().returncode, 0)
                self.assertEqual(self.settings.read_text(), text)
                self.assertFalse(self.link.is_symlink())

    def test_custom_home_and_settings_symlink(self):
        self.claude = self.root / 'custom config'
        self.claude.mkdir()
        self.env['CLAUDE_CONFIG_DIR'] = str(self.claude)
        actual = self.root / 'shared-settings.json'
        actual.write_text('{"theme":"dark"}')
        actual.chmod(0o640)
        alias = self.claude / 'settings.json'
        alias.symlink_to(actual)
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(alias.is_symlink())
        self.assertEqual(actual.stat().st_mode & 0o777, 0o640)
        self.assertEqual(json.loads(actual.read_text())['theme'], 'dark')
        self.assertIn('UserPromptSubmit', json.loads(actual.read_text())['hooks'])
        self.assertTrue((self.claude / 'hooks/discontent.py').is_symlink())
        self.assertFalse((self.home / '.claude').exists())

    def test_refuses_worktree(self):
        (self.repo / '.git').write_text('gitdir: /elsewhere\n')
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('main checkout', result.stderr)
        self.assertFalse(self.settings.exists())


if __name__ == '__main__':
    unittest.main()
