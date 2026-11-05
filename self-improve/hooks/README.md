# Discontent prompt hook

Opt in from the main checkout with Python 3.8+ on macOS or Linux:

```sh
python3 scripts/install-discontent-hook.py
```

This links `discontent.py` into `~/.claude/hooks` and registers a command in
`~/.claude/settings.json` under `UserPromptSubmit`. `CLAUDE_CONFIG_DIR` overrides
the Claude directory. Existing settings, other hooks and hook groups are
preserved; repeating setup adds no duplicate registration. A legacy command
`python3 ~/.claude/hooks/discontent.py` is recognized as already registered.
The installer refuses a linked worktree so the link survives workspace removal.
Skill installation through `scripts/install.sh` does not opt in to this hook.

If that hook path already holds a regular file, setup leaves it alone. To
migrate the earlier standalone hook, explicitly run:

```sh
python3 scripts/install-discontent-hook.py --replace-hook
```

This first saves the file as `discontent.py.pre-muster`; an existing backup or
foreign symlink is left alone with an error. Inspect the backup before removing
it. Restart Claude Code or review the registration in `/hooks` after setup.

The hook reads JSON from stdin and emits `hookSpecificOutput.additionalContext`
only when swearing appears in the owner's own prompt. The vocabulary comes from
the original live hook; matching uses word boundaries and ignores case.
`<pasted_content ...>...</pasted_content>` and
`<system-reminder>...</system-reminder>` blocks are excluded. These are lexical
exclusions, not a general sentiment or quotation classifier: unmarked quotes
remain part of the prompt. A match is a discontent signal for investigation.

Malformed input and a one-second internal deadline return silently with status
0; the registered command also has a five-second host timeout. This implements
the [Claude Code command-hook contract](https://code.claude.com/docs/en/hooks#userpromptsubmit).
The hook injects instructions; the agent performs the dispatch and the forced
review required by [self-improve](../SKILL.md). A successful pipe test proves
detection and output, not that an agent has dispatched or a reviewer converged.

Codex and pi have no hook supplied here. Invoke `/self-improve` manually with
the discontent quote and incident extract, then use the same subagent and
review contract.

Run regressions and their paired mutations from the checkout:

```sh
python3 -m unittest discover -s tests -p 'test_discontent.py' -v
python3 tests/mutate_discontent.py
```

Mutation checks copy the implementation into a temporary repository. Each
mutation must make its paired regression fail; the working implementation and
the user's Claude settings are never changed by these checks.
