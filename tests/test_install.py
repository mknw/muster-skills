"""Run scripts/install.sh against a disposable HOME and check every link it makes, keeps or prunes."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / 'scripts/install.sh'
SKILLS = sorted(p.parent.name for p in REPO.glob('*/SKILL.md'))
BASH = os.environ.get('MUSTER_TEST_BASH', 'bash')   # set to /bin/bash to exercise macOS's bash 3.2
BASE_ENV = {k: v for k, v in os.environ.items()
            if k not in ('CLAUDE_CONFIG_DIR', 'CODEX_HOME', 'PI_CODING_AGENT_DIR', 'MUSTER_SKILL_DIRS')}


def run(home, script=SCRIPT, check=True, **env):
    return subprocess.run([BASH, str(script)], env={**BASE_ENV, 'HOME': str(home), 'MUSTER_ALLOW_WORKTREE': '1', **env},
                          check=check, text=True, capture_output=True, timeout=30)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.scratch = Path(tempfile.mkdtemp(prefix='skill install '))   # a space in HOME
        self.home = self.scratch / 'home dir'
        (self.home / '.claude/skills').mkdir(parents=True)
        (self.home / '.codex').mkdir()
        self.claude, self.agents = self.home / '.claude/skills', self.home / '.agents/skills'

    def tearDown(self):
        shutil.rmtree(self.scratch)

    def test_links_every_skill_into_every_present_agent(self):
        out = run(self.home).stdout
        for d in (self.claude, self.agents):
            self.assertEqual(sorted(p.name for p in d.iterdir()), SKILLS)
            for name in SKILLS:
                self.assertEqual(os.readlink(d / name), str(REPO / name))
        self.assertIn(f'{self.agents}: {len(SKILLS)} linked, 0 repointed, 0 already linked', out)
        again = run(self.home).stdout
        self.assertIn(f'{self.claude}: 0 linked, 0 repointed, {len(SKILLS)} already linked, 0 pruned, 0 left alone', again)

    def test_keeps_what_it_does_not_own(self):
        elsewhere = self.scratch / 'my skills' / SKILLS[0]
        elsewhere.mkdir(parents=True)
        (self.claude / SKILLS[0]).symlink_to(elsewhere)                    # a working link elsewhere
        (self.claude / SKILLS[1]).mkdir()                                  # a real directory
        (self.claude / SKILLS[2]).symlink_to(f'{REPO}/{SKILLS[2]}/')       # ours, trailing slash
        (self.claude / 'sibling').symlink_to(f'{REPO}-old/gone')           # dead, sibling repo prefix
        (self.claude / 'outside').symlink_to(self.scratch / 'gone')        # dead, outside the repo
        (self.claude / 'deeper').symlink_to(f'{REPO}/scripts/gone')        # below a repo subdirectory
        (self.claude / 'escape').symlink_to(f'{REPO}/x/../../gone')        # leaves the repo
        out = run(self.home).stdout
        self.assertEqual(os.readlink(self.claude / SKILLS[0]), str(elsewhere))
        self.assertFalse((self.claude / SKILLS[1]).is_symlink())
        for name in ('sibling', 'outside', 'deeper', 'escape'):
            self.assertTrue((self.claude / name).is_symlink(), name)
        self.assertIn(f'{len(SKILLS) - 3} linked, 0 repointed, 1 already linked, 0 pruned, 2 left alone', out)

    def test_repoints_dead_links_and_prunes_removed_skills(self):
        (self.claude / SKILLS[0]).symlink_to(self.scratch / 'deleted-worktree' / SKILLS[0])
        (self.claude / 'old-name').symlink_to(REPO / 'old-name')            # a renamed skill
        (self.claude / 'scripts').symlink_to(f'{REPO}/scripts/')            # not a skill
        out = run(self.home).stdout
        self.assertEqual(os.readlink(self.claude / SKILLS[0]), str(REPO / SKILLS[0]))
        self.assertFalse((self.claude / 'old-name').is_symlink())
        self.assertFalse((self.claude / 'scripts').is_symlink())
        self.assertIn('1 repointed', out)
        self.assertIn('2 pruned', out)

    def test_skips_absent_agents_and_checks_extra_dirs(self):
        bare = self.scratch / 'bare home'
        bare.mkdir()
        extra = self.scratch / 'other agent/skills'
        res = run(bare, MUSTER_SKILL_DIRS=f':{extra}::relative/dir')
        self.assertIn(f'skip {bare}/.claude/skills', res.stdout)
        self.assertIn(f'skip {bare}/.agents/skills', res.stdout)
        self.assertIn('skip relative/dir', res.stderr)
        self.assertFalse((bare / '.claude').exists())
        self.assertEqual(sorted(p.name for p in extra.iterdir()), SKILLS)

    def test_refuses_a_worktree_and_an_empty_checkout(self):
        fake = self.scratch / 'checkout'
        (fake / 'scripts').mkdir(parents=True)
        shutil.copy(SCRIPT, fake / 'scripts/install.sh')
        empty = run(self.home, script=fake / 'scripts/install.sh', check=False)
        self.assertEqual(empty.returncode, 1)
        self.assertIn('no skills found', empty.stderr)
        (fake / 'demo').mkdir()
        (fake / 'demo/SKILL.md').write_text('---\nname: demo\ndescription: d\n---\n')
        (fake / '.git').write_text('gitdir: /elsewhere\n')
        env = {**BASE_ENV, 'HOME': str(self.home)}
        wt = subprocess.run([BASH, str(fake / 'scripts/install.sh')], env=env, text=True, capture_output=True, timeout=30)
        self.assertEqual(wt.returncode, 1)
        self.assertIn('linked worktree', wt.stderr)
        self.assertEqual(list(self.claude.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
