#!/usr/bin/env python3
"""Validate an orca.yaml the way Orca actually parses it.

Orca has no `validate` command, and `orca repo show` reports only per-machine
hook settings — so a rejected orca.yaml is indistinguishable from a missing one.
This reimplements `parseOrcaYaml` (Orca 1.4.182) to make that failure loud.

Usage:
    python3 validate_orca_yaml.py [path/to/orca.yaml]

Needs PyYAML. Without it:
    uv run --with pyyaml python3 validate_orca_yaml.py orca.yaml

Caveat: PyYAML implements YAML 1.1 while Orca uses the JS `yaml` package
(YAML 1.2). They differ on unquoted scalars like `yes`/`no`/`on`/`off` and
sexagesimals. Quote anything ambiguous and the two agree.

Exit codes: 0 = Orca will use the file, 1 = Orca will ignore it (or a field is
silently dropped), 2 = could not run.
"""

from __future__ import annotations

import re
import sys

MAX_FILE = 262144
MAX_FIELD = 65536
MAX_TABS = 256
MAX_RECIPES = 256
MAX_SHARED = 100

RECIPE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
TAB_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$")
KNOWN_KEYS = {
    "scripts",
    "issueCommand",
    "defaultTabs",
    "environmentRecipes",
    "worktree",
}

errors: list[str] = []   # file is rejected, or a field is silently dropped
notes: list[str] = []    # accepted, but worth knowing


def fail(msg: str) -> None:
    errors.append(msg)


def note(msg: str) -> None:
    notes.append(msg)


def trimmed(value, label: str):
    """Mirror asTrimmedString: non-strings and oversized values become undefined."""
    if value is None:
        return None
    if not isinstance(value, str):
        fail(f"{label}: must be a string, got {type(value).__name__} — Orca drops it")
        return None
    if len(value) > MAX_FIELD or len(value.encode("utf-8")) > MAX_FIELD:
        fail(f"{label}: exceeds the {MAX_FIELD}-byte field limit — Orca drops it")
        return None
    return value.strip() or None


def load(path: str):
    try:
        import yaml
    except ImportError:
        print(
            "PyYAML is required.\n"
            "  uv run --with pyyaml python3 validate_orca_yaml.py " + path,
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        print(f"cannot read {path}: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"{path}: {len(text)} chars / {len(text.encode('utf-8'))} bytes "
          f"(limit {MAX_FILE})")
    if len(text) > MAX_FILE or len(text.encode("utf-8")) > MAX_FILE:
        fail(f"file exceeds the {MAX_FILE}-byte limit — Orca rejects the whole file")

    # Orca parses with uniqueKeys:true, so ONE duplicate key anywhere kills the
    # entire document. PyYAML allows duplicates by default; make it strict.
    class StrictLoader(yaml.SafeLoader):
        pass

    def no_duplicates(loader, node, deep=False):
        seen = {}
        for key_node, _ in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in seen:
                fail(
                    f"duplicate key {key!r} (line {key_node.start_mark.line + 1}, "
                    f"first seen line {seen[key] + 1}) — Orca rejects the WHOLE file"
                )
            seen[key] = key_node.start_mark.line
        return yaml.SafeLoader.construct_mapping(loader, node, deep)

    StrictLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, no_duplicates
    )

    try:
        return yaml.load(text, Loader=StrictLoader)
    except yaml.YAMLError as e:
        fail(f"YAML syntax error — Orca treats the file as missing:\n    {e}")
        return None


def check_scripts(root) -> list[str]:
    found = []
    scripts = root.get("scripts")
    if scripts is None:
        return found
    if not isinstance(scripts, dict):
        fail("scripts: must be a mapping — Orca ignores it")
        return found
    for key in ("setup", "archive"):
        if trimmed(scripts.get(key), f"scripts.{key}"):
            found.append(f"scripts.{key}")
    for unknown in set(scripts) - {"setup", "archive"}:
        note(f"scripts.{unknown}: not a recognised hook, ignored")
    return found


def check_default_tabs(root) -> list[str]:
    tabs = root.get("defaultTabs")
    if tabs is None:
        return []
    if not isinstance(tabs, list):
        fail("defaultTabs: must be a list — Orca ignores all of them")
        return []
    if len(tabs) > MAX_TABS:
        fail(f"defaultTabs: {len(tabs)} entries exceeds {MAX_TABS} — all ignored")
        return []
    kept = 0
    for i, entry in enumerate(tabs):
        if not isinstance(entry, dict):
            fail(f"defaultTabs[{i}]: must be a mapping — dropped")
            continue
        title = trimmed(entry.get("title"), f"defaultTabs[{i}].title")
        command = trimmed(entry.get("command"), f"defaultTabs[{i}].command")
        raw_color = trimmed(entry.get("color"), f"defaultTabs[{i}].color")
        color = raw_color if raw_color and TAB_COLOR_RE.match(raw_color) else None
        if raw_color and not color:
            fail(
                f"defaultTabs[{i}].color: {raw_color!r} is not #rgb/#rrggbb — "
                f"silently dropped (quote hex colours; bare # starts a comment)"
            )
        if not (title or command or color):
            fail(f"defaultTabs[{i}]: no title, command or valid color — dropped")
            continue
        kept += 1
    return [f"defaultTabs ({kept} entries)"] if kept else []


def check_recipes(root) -> list[str]:
    recipes = root.get("environmentRecipes")
    if recipes is None:
        return []
    if not isinstance(recipes, list):
        fail("environmentRecipes: must be a list — ignored")
        return []
    if len(recipes) > MAX_RECIPES:
        fail(f"environmentRecipes: exceeds {MAX_RECIPES} — all ignored")
        return []
    seen: set[str] = set()
    kept = 0
    for i, entry in enumerate(recipes):
        if not isinstance(entry, dict):
            fail(f"environmentRecipes[{i}]: must be a mapping")
            continue
        rid = trimmed(entry.get("id"), f"environmentRecipes[{i}].id")
        name = trimmed(entry.get("name"), f"environmentRecipes[{i}].name")
        create = trimmed(entry.get("create"), f"environmentRecipes[{i}].create") or \
            trimmed(entry.get("command"), f"environmentRecipes[{i}].command")
        if not rid:
            fail(f"environmentRecipes[{i}]: id is required")
            continue
        if not RECIPE_ID_RE.match(rid):
            fail(f"environmentRecipes[{i}].id {rid!r}: use 1-64 lowercase letters, "
                 f"numbers, dots, underscores or hyphens, starting alphanumeric")
            continue
        if rid in seen:
            fail(f"environmentRecipes[{i}].id {rid!r}: duplicate")
            continue
        if not name:
            fail(f"environmentRecipes[{i}] ({rid}): name is required")
            continue
        if not create:
            fail(f"environmentRecipes[{i}] ({rid}): create is required")
            continue
        seen.add(rid)
        kept += 1
    if kept:
        note("environmentRecipes appear in the workspace composer only once this "
             "file is committed to the project's PRIMARY branch")
        return [f"environmentRecipes ({kept} recipes)"]
    return []


def check_shared(root, yaml_path: str) -> list[str]:
    worktree = root.get("worktree")
    if worktree is None:
        return []
    if not isinstance(worktree, dict):
        fail("worktree: must be a mapping — ignored")
        return []
    shared = worktree.get("sharedDirectories")
    if shared is None:
        return []
    if not isinstance(shared, list):
        fail("worktree.sharedDirectories: must be a list — ignored")
        return []
    kept: list[str] = []
    for entry in shared[:MAX_SHARED]:
        raw = trimmed(entry, "worktree.sharedDirectories[]")
        if not raw:
            continue
        norm = raw.replace("\\", "/")
        norm = re.sub(r"^\./", "", norm)
        norm = re.sub(r"/+$", "", norm)
        segments = norm.split("/")
        bad = (
            not norm
            or norm.startswith("/")
            or re.match(r"^[a-zA-Z]:", norm)
            or any(s in ("..", ".", "", ".git") for s in segments)
        )
        if bad:
            fail(f"worktree.sharedDirectories: {raw!r} is skipped "
                 f"(absolute, drive-letter, or contains '.', '..', '' or '.git')")
            continue
        if norm not in kept:
            kept.append(norm)
    if len(shared) > MAX_SHARED:
        fail(f"worktree.sharedDirectories: only the first {MAX_SHARED} are read")

    # Best effort: entries must exist as gitignored DIRECTORIES in the primary
    # checkout, or they are skipped at materialisation time without complaint.
    import os
    import subprocess

    repo = os.path.dirname(os.path.abspath(yaml_path))
    for entry in kept:
        target = os.path.join(repo, entry)
        if not os.path.isdir(target):
            note(f"sharedDirectories {entry!r}: not a directory here — skipped at "
                 f"worktree creation unless it exists in the primary checkout")
            continue
        try:
            ignored = subprocess.run(
                ["git", "-C", repo, "check-ignore", "-q", entry],
                capture_output=True,
            ).returncode == 0
        except OSError:
            continue
        if not ignored:
            note(f"sharedDirectories {entry!r}: not gitignored — Orca skips "
                 f"tracked paths")
    return [f"worktree.sharedDirectories ({len(kept)} dirs)"] if kept else []


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else "orca.yaml"
    root = load(path)

    if root is None and not errors:
        fail("file is empty — treated as missing")
    if root is not None and not isinstance(root, dict):
        fail(f"root must be a mapping, got {type(root).__name__} — treated as missing")
        root = None

    found: list[str] = []
    if isinstance(root, dict):
        for unknown in sorted(set(root) - KNOWN_KEYS):
            note(f"{unknown}: not a recognised top-level key, ignored")
        found += check_scripts(root)
        if trimmed(root.get("issueCommand"), "issueCommand"):
            found.append("issueCommand")
        found += check_default_tabs(root)
        found += check_recipes(root)
        found += check_shared(root, path)

    print()
    fatal = any(
        "whole file" in e.lower() or "treated as missing" in e.lower()
        for e in errors
    )
    if found:
        # When the document is rejected these fields are academic — saying
        # "Orca will use" would be exactly the wrong impression.
        print("Fields that parse (but the file is rejected, see below):"
              if fatal else "Orca will use:")
        for f in found:
            print(f"  + {f}")
    for n in notes:
        print(f"  note: {n}")
    for e in errors:
        print(f"  ERROR: {e}")

    print()
    if fatal or not found:
        print("VERDICT: Orca treats this file as MISSING.")
        return 1
    if errors:
        print("VERDICT: parsed, but fields above are silently dropped.")
        return 1
    print("VERDICT: valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
