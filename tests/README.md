# Source validation

Use Python 3.10 or newer and Git. In a virtual environment, install the pinned
dependencies with `python3 -m pip install -r tests/requirements.txt`, then run:

```sh
python3 scripts/check-source.py
python3 -m unittest discover -s tests -v
```

The checker uses safe YAML loading for required nonempty string metadata and a
CommonMark parser for inline, image and reference-link destinations. It validates
tracked Markdown files and resolves local paths inside the repository, including
symlinks. External URLs and fragment-only links are not fetched; HTML links and
fragment existence are outside this source check. Code examples are not links.
The workflow installs the same dependencies and runs these commands on Linux.

These black-box tests were adapted by the author from independently harvested PR7
Correctness probes `review_source.py` and `review_whitespace.py`. They invoke the
actual checker against current tracked Markdown and disposable mutations, covering
null/comment-only/malformed/non-string metadata, missing inline/reference links,
omitted files, traversal and symlink escape. The Git test retains the reviewer's
depth-one checkout contract: clean source passes and a whitespace mutant fails.
No whitespace algorithm change was needed. Original reviewer scripts, red results
and patch remain separately preserved in the delivery evidence; these tests do
not import mission paths or old source pins.

`probe_native.py` adapts the third harvested probe. It is opt-in because it needs
an actual Herdr 0.9.5 binary for the current Unix platform, independently verified
against its official release asset digest. Supply that binary and its exact
SHA256 explicitly:

```sh
python3 tests/probe_native.py --binary "$HERDR_BINARY" --sha256 "$HERDR_SHA256" --evidence "$PROBE_OUTPUT"
```

It checks protocol 22/schema 1, seven CLI requests and five rejecting controls
with a private rejecting Unix socket and private config/state directories. It
starts no server, provider, agent, SSH connection or integration. It requires
only the Python standard library, runs on macOS/Linux with the matching binary,
and is separate from default CI; no binary is downloaded or trusted implicitly.

All these checks are L1 source/Git/CLI contract evidence. They do not establish
model invocation, server deployment, provider authentication or live acceptance.
