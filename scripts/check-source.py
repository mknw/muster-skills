"""Validate tracked skill metadata and local Markdown dependency closure."""

from pathlib import Path
import subprocess
import sys
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt
import yaml


def markdown_body(text, path):
    if path.name != 'SKILL.md':
        return text
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip('\r\n') != '---':
        raise ValueError('missing skill frontmatter')
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip('\r\n') == '---'), None)
    if end is None:
        raise ValueError('unclosed skill frontmatter')
    metadata = yaml.safe_load(''.join(lines[1:end]))
    if not isinstance(metadata, dict) or not all(
        isinstance(metadata.get(key), str) and metadata[key].strip()
        for key in ('name', 'description')
    ):
        raise ValueError('name and description must be nonempty YAML strings')
    return ''.join(lines[end + 1:])


def destinations(text):
    env = {}
    tokens = MarkdownIt('commonmark').parse(text, env)
    # Include definitions even if currently unused, plus resolved full,
    # collapsed and shortcut reference links in the parsed inline tokens.
    targets = {ref['href'] for ref in env.get('references', {}).values()}
    while tokens:
        token = tokens.pop()
        if token.type in ('link_open', 'image'):
            targets.add(token.attrGet('href' if token.type == 'link_open' else 'src'))
        tokens.extend(token.children or [])
    return targets


def check(root):
    paths = subprocess.check_output(
        ['git', 'ls-files', '-z'], cwd=root, text=True
    ).split('\0')
    markdown = [Path(p) for p in paths if p.endswith('.md')]
    errors = []
    for relative in markdown:
        path = root / relative
        try:
            if not path.resolve().is_relative_to(root):
                raise ValueError('Markdown source escapes repository')
            body = markdown_body(path.read_text(encoding='utf-8'), path)
            for target in destinations(body):
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path:
                    continue
                resolved = (path.parent / unquote(url.path)).resolve()
                if not resolved.is_relative_to(root) or not resolved.is_file():
                    errors.append(f'{relative}: missing or external local reference {target}')
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(f'{relative}: {exc}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'Checked {len(markdown)} Markdown files; source references only, no behavioral acceptance.')


if __name__ == '__main__':
    check(Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve())
