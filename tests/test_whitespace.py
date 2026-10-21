"""Exercise the workflow's actual Git command in checkout's depth-one topology."""

from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest


class CheckoutWhitespaceTests(unittest.TestCase):
    def test_clean_and_mutated_depth_one_merge(self):
        workflow = (Path(__file__).resolve().parents[1] / '.github/workflows/skill-source.yml').read_text()
        command = shlex.split(next(line.strip() for line in workflow.splitlines()
                                  if line.strip().startswith('git show')))
        with tempfile.TemporaryDirectory(prefix='skill-whitespace-') as scratch:
            root = Path(scratch)
            repo = root / 'repo'
            repo.mkdir()

            def git(*args, cwd=repo):
                return subprocess.run(
                    ['git', '-c', 'user.name=Source fixture', '-c', 'user.email=fixture@invalid',
                     '-c', 'commit.gpgsign=false', *args], cwd=cwd, check=True,
                    text=True, capture_output=True, timeout=20
                )

            git('init', '-q', '-b', 'main')
            readme = repo / 'README.md'
            readme.write_text('fixture\n')
            git('add', '.')
            git('commit', '-qm', 'baseline')
            clean = root / 'clean'
            git('clone', '-q', '--depth', '1', repo.as_uri(), str(clean))
            result = subprocess.run(command, cwd=clean, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            git('switch', '-qc', 'pr')
            readme.write_text('fixture\ntrailing whitespace   \n')
            git('add', '.')
            git('commit', '-qm', 'Whitespace mutant')
            git('switch', '-q', 'main')
            git('merge', '--no-ff', 'pr', '-m', 'Synthetic PR merge')
            shallow = root / 'shallow'
            git('clone', '-q', '--depth', '1', repo.as_uri(), str(shallow))
            self.assertEqual(git('rev-parse', '--is-shallow-repository', cwd=shallow).stdout.strip(), 'true')
            result = subprocess.run(command, cwd=shallow, capture_output=True, text=True, timeout=20)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn('trailing whitespace', result.stdout)


if __name__ == '__main__':
    unittest.main()
