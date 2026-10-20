"""Black-box regressions adapted from independently harvested PR7 probes."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
CHECKER = REPO / 'scripts/check-source.py'


class SourceGuardTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix='skill-source-')
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name) / 'repo'
        self.root.mkdir()
        paths = subprocess.check_output(
            ['git', 'ls-files', '-z'], cwd=REPO, text=True
        ).split('\0')
        for name in paths:
            if name:
                target = self.root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((REPO / name).read_bytes())
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', 'add', '.'], cwd=self.root, check=True)
        self.skill = self.root / 'dispatching-work/SKILL.md'
        self.original = self.skill.read_text()
        self.body = self.original.split('---', 2)[2]
        # A broken fixture must never make the rejecting controls pass.
        self.check_result(True)

    def check_result(self, accepted):
        result = subprocess.run(
            [sys.executable, str(CHECKER), str(self.root)],
            cwd=self.root, text=True, capture_output=True, timeout=20
        )
        self.assertEqual(result.returncode == 0, accepted,
                         result.stdout + result.stderr)

    def test_current_metadata_and_links(self):
        self.check_result(True)

    def test_required_yaml_strings(self):
        # Values are independent examples of YAML's actual types/syntax.
        bad_values = ['', '# no value', 'null', '~', '""', '"   "',
                      'false', '42', '[]', '{}', '[unterminated',
                      '!!python/object/apply:os.getcwd []']
        for key in ('name', 'description'):
            for value in bad_values + [None]:
                with self.subTest(key=key, value=value):
                    fields = {'name': 'dispatching-work', 'description': 'Valid description'}
                    if value is None:
                        del fields[key]
                    else:
                        fields[key] = value
                    header = '\n'.join(f'{k}: {v}' for k, v in fields.items())
                    self.skill.write_text('---\n' + header + '\n---' + self.body)
                    self.check_result(False)
        for header in ('- name\n- description', '# empty mapping', 'name: only\n---\n---'):
            with self.subTest(header=header):
                self.skill.write_text('---\n' + header + '\n---' + self.body)
                self.check_result(False)

    def test_valid_yaml_strings(self):
        for value in ('"quoted: value"', '>\n  folded description',
                      '|\n  literal description', '|\n  ---\n  literal delimiter'):
            with self.subTest(value=value):
                self.skill.write_text('---\nname: dispatching-work\ndescription: ' + value + '\n---' + self.body)
                self.check_result(True)

    def test_local_link_syntax(self):
        cases = [
            ('inline', '[native](TARGET)'),
            ('inline-title', '[native](<TARGET> "Native procedure")'),
            ('full-reference', '[native][route]\n\n[route]: TARGET'),
            ('collapsed-reference', '[route][]\n\n[route]: TARGET'),
            ('shortcut-reference', '[route]\n\n[route]: TARGET'),
            ('image', '![native](TARGET)'),
            ('unused-definition', '[route]: TARGET'),
        ]
        for label, markup in cases:
            for target, accepted in (('herdr-native.md', True), ('missing-native.md', False)):
                with self.subTest(syntax=label, target=target):
                    self.skill.write_text(self.original + '\n' + markup.replace('TARGET', target) + '\n')
                    self.check_result(accepted)

    def test_escapes_and_omitted_reference(self):
        outside = self.root.parent / 'outside.md'
        outside.write_text('test-owned outside file\n')
        for target in ('../../outside.md', '..%2F..%2Foutside.md', str(outside)):
            for markup in ('[native](TARGET)', '[native][route]\n\n[route]: TARGET'):
                with self.subTest(target=target, markup=markup):
                    self.skill.write_text(self.original + '\n' + markup.replace('TARGET', target) + '\n')
                    self.check_result(False)
        self.skill.write_text(self.original)
        reference = self.root / 'dispatching-work/herdr-native.md'
        reference.unlink()
        self.check_result(False)
        reference.symlink_to(outside)
        self.check_result(False)

    def test_code_examples_are_not_disclosures(self):
        self.skill.write_text(self.original + '\n```md\n[example](missing.md)\n[x]: missing.md\n```\n')
        self.check_result(True)

    def test_markdown_source_containment(self):
        # This tracked source is unreferenced: link-target checks cannot catch it.
        source = self.root / 'extra-source.md'
        source.write_text('Test-owned tracked Markdown\n')
        subprocess.run(['git', 'add', source.name], cwd=self.root, check=True)
        self.check_result(True)

        outside = self.root.parent / 'outside-source.md'
        outside.write_text('Test-owned external Markdown\n')
        for label, target, accepted in (
            ('internal-source-symlink', 'README.md', True),
            ('external-source-symlink', outside, False),
        ):
            with self.subTest(source=label):
                source.unlink()
                source.symlink_to(target)
                subprocess.run(['git', 'add', source.name], cwd=self.root, check=True)
                self.check_result(accepted)


if __name__ == '__main__':
    unittest.main()
