"""Run every discontent regression against a paired, disposable implementation mutation."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
HOOK = 'self-improve/hooks/discontent.py'
INSTALL = 'scripts/install-discontent-hook.py'

# Test name, mutated source, exact replacement, explanation.
PAIRS = [
    ('DiscontentTests.test_fucking_fires', HOOK, 'fuck(?:', 'never(?:', 'remove fuck vocabulary'),
    ('DiscontentTests.test_shit_fires', HOOK, '|shit(?:', '|never(?:', 'remove shit vocabulary'),
    ('DiscontentTests.test_wtf_fires', HOOK, '|wtf|', '|never|', 'remove wtf vocabulary'),
    ('DiscontentTests.test_case_insensitive', HOOK, ', re.IGNORECASE)', ')', 'make word matching case-sensitive'),
    ('DiscontentTests.test_shitake_is_quiet', HOOK, 'r")(?![\\w-])"', 'r")"', 'remove trailing word boundary'),
    ('DiscontentTests.test_kutter_is_quiet', HOOK, 'r")(?![\\w-])"', 'r")"', 'remove trailing word boundary'),
    ('DiscontentTests.test_damnation_is_quiet', HOOK, 'r")(?![\\w-])"', 'r")"', 'remove trailing word boundary'),
    ('DiscontentTests.test_fitness_sake_is_quiet', HOOK, 'r"piss(?:ed)? off|bloody hell|"',
     'r"for f\\w*\'?s sake|piss(?:ed)? off|bloody hell|"', 'treat a non-swear phrase as discontent'),
    ('DiscontentTests.test_pasted_content_is_quiet', HOOK, 'PASTE.sub(" ", prompt)', 'prompt', 'scan pasted words'),
    ('DiscontentTests.test_system_reminder_is_quiet', HOOK,
     'SYSTEM.sub(" ", PASTE.sub(" ", prompt))', 'PASTE.sub(" ", prompt)', 'scan system reminders'),
    ('DiscontentTests.test_own_words_outside_exclusions_fire', HOOK,
     'own = SYSTEM.sub(" ", PASTE.sub(" ", prompt))', 'own = ""', 'discard words outside excluded blocks'),
    ('DiscontentTests.test_malformed_json_is_quiet', HOOK,
     'except (ValueError, TypeError, OSError, TimeoutError):',
     'except (TypeError, OSError, TimeoutError):', 'let malformed JSON escape'),
    ('DiscontentTests.test_invalid_payloads_are_quiet', HOOK,
     'if not isinstance(payload, dict):', 'if False:', 'accept non-object payloads'),
    ('DiscontentTests.test_timeout_is_quiet', HOOK, 'signal.alarm(1)', 'signal.alarm(0)', 'disable internal deadline'),
    ('DiscontentTests.test_fucking_fires', HOOK,
     'FORCED independent review to CONVERGED', 'optional review', 'drop forced review context'),
    ('DiscontentInstallTests.test_install_and_idempotence', INSTALL,
     'if not any(is_our_command(hook, link) for entry in entries for hook in entry["hooks"]):',
     'if True:', 'register a duplicate on every install'),
    ('DiscontentInstallTests.test_install_and_idempotence', INSTALL,
     'shlex.join(["python3", str(link)])', '" ".join(["python3", str(link)])', 'remove shell path quoting'),
    ('DiscontentInstallTests.test_install_and_idempotence', INSTALL,
     'link.symlink_to(source)', 'link.write_bytes(source.read_bytes())', 'copy instead of linking'),
    ('DiscontentInstallTests.test_preserves_other_settings_and_legacy_registration', INSTALL,
     'return (len(args) == 2', 'return (False and len(args) == 2', 'ignore legacy registration'),
    ('DiscontentInstallTests.test_preserves_other_settings_and_legacy_registration', INSTALL,
     'hooks = data.get("hooks", {})', 'hooks = {}; data["hooks"] = hooks', 'erase unrelated hooks'),
    ('DiscontentInstallTests.test_existing_file_requires_explicit_migration', INSTALL,
     'if not replace_hook or link.is_symlink() or not link.is_file():',
     'if link.is_symlink() or not link.is_file():', 'replace existing file without opt-in'),
    ('DiscontentInstallTests.test_foreign_symlink_and_existing_backup_are_preserved', INSTALL,
     'if os.path.lexists(backup):', 'if False:', 'overwrite the previous backup'),
    ('DiscontentInstallTests.test_foreign_symlink_and_existing_backup_are_preserved', INSTALL,
     'if not replace_hook or link.is_symlink() or not link.is_file():',
     'if not replace_hook or not link.is_file():', 'replace a foreign symlink'),
    ('DiscontentInstallTests.test_bad_settings_fail_before_changing_hook', INSTALL,
     'data = json.loads(settings.read_text()) if settings.exists() else {}',
     'data = {}', 'silently discard invalid settings'),
    ('DiscontentInstallTests.test_custom_home_and_settings_symlink', INSTALL,
     'settings = (claude / "settings.json").resolve()',
     'settings = claude / "settings.json"', 'replace settings symlink'),
    ('DiscontentInstallTests.test_custom_home_and_settings_symlink', INSTALL,
     'mode = stat.S_IMODE(settings.stat().st_mode) if settings.exists() else 0o600',
     'mode = 0o600', 'discard existing settings permissions'),
    ('DiscontentInstallTests.test_refuses_worktree', INSTALL,
     'if (REPO / ".git").is_file():', 'if False:', 'allow links into a disposable worktree'),
    ('DiscontentInstallTests.test_uninstall_removes_only_owned_hook', INSTALL,
     'if not is_our_command(hook, link)', 'if True', 'retain the owned registration on uninstall'),
    ('DiscontentInstallTests.test_uninstall_removes_only_owned_hook', INSTALL,
     'link.unlink()', 'pass', 'retain the owned symlink on uninstall'),
    ('DiscontentInstallTests.test_uninstall_preserves_foreign_files_and_backup', INSTALL,
     'if owned:', 'if os.path.lexists(link):', 'unlink foreign hooks on uninstall'),
    ('DiscontentInstallTests.test_uninstall_without_settings_is_noop', INSTALL,
     'if not settings.exists():', 'if False:', 'create missing settings during uninstall'),
]


def test_ids(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from test_ids(item)
        else:
            yield item.id()[len('test_discontent.'):]


def main():
    suite = unittest.defaultTestLoader.discover(str(REPO / 'tests'), pattern='test_discontent.py')
    actual = set(test_ids(suite))
    paired = {pair[0] for pair in PAIRS}
    if actual != paired:
        raise SystemExit(f'pairing mismatch: unpaired={actual - paired}, unknown={paired - actual}')
    # Check the unmodified control first: an already-red fixture is not mutation evidence.
    baseline = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
                               '-p', 'test_discontent.py'], cwd=REPO, capture_output=True, text=True, timeout=30)
    if baseline.returncode:
        raise SystemExit(baseline.stdout + baseline.stderr)
    print(f'GREEN: {len(actual)} unmodified regressions', flush=True)
    with tempfile.TemporaryDirectory(prefix='discontent mutants ') as scratch:
        root = Path(scratch)
        for relative in (HOOK, INSTALL):
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / relative, target)
        for test, relative, before, after, explanation in PAIRS:
            original = (REPO / relative).read_text()
            if original.count(before) != 1:
                raise SystemExit(f'mutation anchor is not unique: {explanation}')
            mutant = original.replace(before, after)
            compile(mutant, str(root / relative), 'exec')
            (root / relative).write_text(mutant)
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'unittest', f'test_discontent.{test}'],
                    cwd=REPO / 'tests', env={**os.environ, 'MUSTER_DISCONTENT_ROOT': str(root)},
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode == 0 or 'Ran 1 test' not in result.stderr:
                    raise SystemExit(f'NOT RED: {test}: {explanation}\n{result.stdout}{result.stderr}')
                print(f'RED: {test} ← {explanation}', flush=True)
            finally:
                (root / relative).write_text(original)
    print(f'PASS: {len(PAIRS)} mutations killed; {len(actual)} tests paired', flush=True)


if __name__ == '__main__':
    main()
