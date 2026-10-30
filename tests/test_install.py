"""Run scripts/install.sh against a disposable HOME and check every link it makes or prunes."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / 'scripts/install.sh'
SKILLS = sorted(p.parent.name for p in REPO.glob('*/SKILL.md'))


def run(home, **env):
    return subprocess.run(['bash', str(SCRIPT)], env={**os.environ, 'HOME': str(home), **env},
                          check=True, text=True, capture_output=True, timeout=30).stdout


class InstallTests(unittest.TestCase):
    def test_links_prunes_and_is_idempotent(self):
        with tempfile.TemporaryDirectory(prefix='skill-install-') as scratch:
            home = Path(scratch)
            (home / '.claude').mkdir()
            (home / '.codex').mkdir()
            claude, agents = home / '.claude/skills', home / '.agents/skills'
            claude.mkdir()
            (claude / 'old-name').symlink_to(REPO / 'old-name')       # a renamed skill
            (claude / 'scripts').symlink_to(f'{REPO}/scripts/')       # not a skill
            (claude / 'mine').symlink_to(home)                        # outside the repo
            (claude / SKILLS[0]).mkdir()                              # a real directory

            out = run(home)
            for d in (claude, agents):
                for name in SKILLS[1:]:
                    self.assertEqual(os.readlink(d / name), str(REPO / name))
            self.assertEqual(os.readlink(agents / SKILLS[0]), str(REPO / SKILLS[0]))
            self.assertTrue((claude / SKILLS[0]).is_dir() and not (claude / SKILLS[0]).is_symlink())
            self.assertFalse((claude / 'old-name').is_symlink())
            self.assertFalse((claude / 'scripts').is_symlink())
            self.assertTrue((claude / 'mine').is_symlink())
            self.assertFalse((agents / 'scripts').exists())
            self.assertIn('2 pruned, 1 left alone', out)

            again = run(home)
            self.assertIn(f'{claude}: 0 linked, {len(SKILLS) - 1} already linked, 0 pruned, 1 left alone', again)
            self.assertIn(f'{agents}: 0 linked, {len(SKILLS)} already linked, 0 pruned, 0 left alone', again)

    def test_skips_absent_agents_and_links_extra_dirs(self):
        with tempfile.TemporaryDirectory(prefix='skill-install-') as scratch:
            home = Path(scratch)
            extra = home / 'other-agent/skills'
            out = run(home, MUSTER_SKILL_DIRS=str(extra))
            self.assertIn(f'skip {home}/.claude/skills', out)
            self.assertIn(f'skip {home}/.agents/skills', out)
            self.assertFalse((home / '.claude').exists())
            self.assertEqual(sorted(p.name for p in extra.iterdir()), SKILLS)


if __name__ == '__main__':
    unittest.main()
