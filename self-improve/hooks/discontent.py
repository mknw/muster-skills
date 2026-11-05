#!/usr/bin/env python3
"""Claude Code UserPromptSubmit hook: route owner swearing to self-improve.

Derived from the live prompt hook. Emit context only for the owner's own words;
malformed input and the one-second POSIX deadline exit silently with status 0.
"""

import json
import re
import signal
import sys


WORDS = (
    r"fuck(?:s|ed|ing|in)?|f\*+k(?:ing)?|shit(?:s|ty|head)?|bullshit|crap(?:py)?|damn(?:it)?|goddamn(?:it)?|wtf|ffs|"
    r"piss(?:ed)? off|bloody hell|"
    r"cazzo|merda|porca \w+|vaffanculo|"  # Italian
    r"kut|godverdomme|verdomme|klote\w*|"  # Dutch
    r"putain|merde|bordel"  # French
)
PAT = re.compile(r"(?<![\w-])(" + WORDS + r")(?![\w-])", re.IGNORECASE)
PASTE = re.compile(r"<pasted_content\b.*?</pasted_content[^>]*>", re.IGNORECASE | re.DOTALL)
SYSTEM = re.compile(r"<system-reminder>.*?</system-reminder>", re.IGNORECASE | re.DOTALL)


def main():
    payload = json.load(sys.stdin)
    if not isinstance(payload, dict):
        return
    prompt = payload.get("prompt")
    if not isinstance(prompt, str):
        return
    own = SYSTEM.sub(" ", PASTE.sub(" ", prompt))
    match = PAT.search(own)
    if not match:
        return
    context = (
        "OWNER DISCONTENT SIGNAL (matched: " + repr(match.group(1)) + "). "
        "Read self-improve's owner discontent trigger. Carry out the authorized "
        "request in this turn, or acknowledge the mistake in one line, then "
        "dispatch self-improve as a SUBAGENT under 'Dispatched runs — the extract "
        "contract': Expected / Observed / Decisions made and why / Attempts and "
        "outcomes, quoting the owner's words verbatim. The extract is the whole "
        "incident record. Land tracked changes in the repository that owns them "
        "as branch → PR, with FORCED independent review to CONVERGED under the "
        "skill's autonomous review gate. Mention the dispatch in one line."
    )
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit", "additionalContext": context,
    }}))


def timed_out(signum, frame):
    raise TimeoutError("prompt hook deadline")


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGALRM, timed_out)
        signal.alarm(1)
        main()
    except (ValueError, TypeError, OSError, TimeoutError):
        pass
    finally:
        signal.alarm(0)
