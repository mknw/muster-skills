#!/usr/bin/env python3
"""Opt-in Claude Code prompt-hook setup; preserves unrelated settings and hooks."""

import argparse
import json
import os
from pathlib import Path
import shlex
import stat
import tempfile


REPO = Path(__file__).resolve().parents[1]


def is_our_command(hook, link):
    if hook.get("type") != "command":
        return False
    try:
        args = shlex.split(hook.get("command", ""))
    except ValueError:
        return False
    return (len(args) == 2 and Path(args[0]).name.startswith("python")
            and Path(os.path.expandvars(args[1])).expanduser().absolute() == link)


def install(replace_hook=False, uninstall=False):
    if (REPO / ".git").is_file():
        raise ValueError("run hook setup from the main checkout, not a linked worktree")
    source = REPO / "self-improve/hooks/discontent.py"
    if not source.is_file():
        raise ValueError(f"hook source missing: {source}")
    claude = Path(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude")).expanduser().absolute()
    link = claude / "hooks/discontent.py"
    # Follow a settings symlink so atomic replacement preserves that symlink.
    settings = (claude / "settings.json").resolve()
    data = json.loads(settings.read_text()) if settings.exists() else {}
    if not isinstance(data, dict) or not isinstance(data.get("hooks", {}), dict):
        raise ValueError("settings and hooks must be JSON objects")
    hooks = data.get("hooks", {})
    entries = hooks.get("UserPromptSubmit", [])
    if not isinstance(entries, list) or any(
        not isinstance(entry, dict) or not isinstance(entry.get("hooks"), list)
        or any(not isinstance(hook, dict) or not isinstance(hook.get("command", ""), str)
               for hook in entry["hooks"]) for entry in entries
    ):
        raise ValueError("UserPromptSubmit must contain hook groups")
    owned = link.is_symlink() and link.resolve() == source
    if uninstall:
        remaining = []
        for entry in entries:
            kept = [hook for hook in entry["hooks"] if not is_our_command(hook, link)]
            if kept == entry["hooks"]:
                remaining.append(entry)
            elif kept:
                remaining.append({**entry, "hooks": kept})
        if remaining != entries:
            hooks["UserPromptSubmit"] = remaining
        if owned:
            link.unlink()
        if not settings.exists():
            print("discontent hook uninstalled; no settings file")
            return
    else:
        data.setdefault("hooks", hooks)
        hooks.setdefault("UserPromptSubmit", entries)
        if not any(is_our_command(hook, link) for entry in entries for hook in entry["hooks"]):
            entries.append({"hooks": [{
                "type": "command", "command": shlex.join(["python3", str(link)]), "timeout": 5,
            }]})
        if os.path.lexists(link) and not owned:
            if not replace_hook or link.is_symlink() or not link.is_file():
                raise ValueError(f"left existing hook alone: {link}; use --replace-hook for a regular file")
            backup = link.with_name("discontent.py.pre-self-improve.bak")
            if os.path.lexists(backup):
                raise ValueError(f"left existing hook alone: backup already exists at {backup}")
            link.rename(backup)
            print(f"saved existing hook to {backup}")
        link.parent.mkdir(parents=True, exist_ok=True)
        if not owned:
            link.symlink_to(source)

    content = json.dumps(data, indent=2) + "\n"
    if not settings.exists() or json.loads(settings.read_text()) != data:
        settings.parent.mkdir(parents=True, exist_ok=True)
        mode = stat.S_IMODE(settings.stat().st_mode) if settings.exists() else 0o600
        fd, temporary = tempfile.mkstemp(prefix=".self-improve-settings-", dir=settings.parent)
        try:
            with os.fdopen(fd, "w") as output:
                os.fchmod(output.fileno(), mode)
                output.write(content)
            os.replace(temporary, settings)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    print(f"discontent hook {'uninstalled' if uninstall else 'installed'}: {link}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--replace-hook", action="store_true",
                      help="back up an existing regular hook file before linking")
    mode.add_argument("--uninstall", action="store_true",
                      help="remove this hook's registrations and owned symlink")
    args = parser.parse_args()
    try:
        install(args.replace_hook, args.uninstall)
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
