#!/usr/bin/env python3
"""
code2md.py - Convert annotated code files to Markdown documentation

Scans directory tree for .py and .cpp files that start with a special marker.
Converts them to .md files with code blocks and prose interleaved.

Markers:
  Python: \"\"\"<md-comment> ... \"\"\"
  C++:    /*<md-comment> ... */

Usage:
  ./code2md.py [directory]   # defaults to current directory

Example input (example.py):
    \"\"\"<md-comment>
    # My Tutorial
    This demonstrates something cool.
    \"\"\"
    print("hello")
    \"\"\"<md-comment>
    Now we do something interesting:
    \"\"\"
    x = calculate(42)

Example output (example.md):
    # My Tutorial
    This demonstrates something cool.
    ```python
    print("hello")
    ```
    Now we do something interesting:
    ```python
    x = calculate(42)
    ```
"""

import os
import re
import sys
from pathlib import Path

# Markers
PY_MARKER_START = '"""<md-comment>'
PY_MARKER_END = '"""'
CPP_MARKER_START = '/*<md-comment>'
CPP_MARKER_END = '*/'


def parse_python(content: str) -> list[tuple[str, str]]:
    """Parse Python file into [(type, content), ...] where type is 'code' or 'md'."""
    parts = []

    # Check if file starts with our marker
    if not content.strip().startswith(PY_MARKER_START):
        return []  # Not a doc file

    # Split by marker pattern
    # Pattern: """<md-comment>\n...\n"""
    pattern = r'"""<md-comment>\s*\n(.*?)"""'

    pos = 0
    for match in re.finditer(pattern, content, re.DOTALL):
        # Code before this comment
        code_before = content[pos:match.start()].strip()
        if code_before:
            parts.append(('code', code_before))

        # The markdown content
        md_content = match.group(1).rstrip()
        if md_content:
            parts.append(('md', md_content))

        pos = match.end()

    # Remaining code after last comment
    code_after = content[pos:].strip()
    if code_after:
        parts.append(('code', code_after))

    return parts


def parse_cpp(content: str) -> list[tuple[str, str]]:
    """Parse C++ file into [(type, content), ...] where type is 'code' or 'md'."""
    parts = []

    # Check if file starts with our marker
    if not content.strip().startswith(CPP_MARKER_START):
        return []  # Not a doc file

    # Pattern: /*<md-comment>\n...\n*/
    pattern = r'/\*<md-comment>\s*\n(.*?)\*/'

    pos = 0
    for match in re.finditer(pattern, content, re.DOTALL):
        # Code before this comment
        code_before = content[pos:match.start()].strip()
        if code_before:
            parts.append(('code', code_before))

        # The markdown content
        md_content = match.group(1).rstrip()
        if md_content:
            parts.append(('md', md_content))

        pos = match.end()

    # Remaining code after last comment
    code_after = content[pos:].strip()
    if code_after:
        parts.append(('code', code_after))

    return parts


def generate_markdown(parts: list[tuple[str, str]], lang: str) -> str:
    """Generate markdown from parsed parts."""
    lines = []

    for part_type, content in parts:
        if part_type == 'md':
            lines.append(content)
            lines.append('')  # blank line after prose
        elif part_type == 'code':
            lines.append(f'```{lang}')
            lines.append(content)
            lines.append('```')
            lines.append('')  # blank line after code

    return '\n'.join(lines)


def process_file(filepath: Path) -> bool:
    """Process a single file. Returns True if converted."""
    content = filepath.read_text()

    if filepath.suffix == '.py':
        parts = parse_python(content)
        lang = 'python'
    elif filepath.suffix in ('.cpp', '.hpp', '.h', '.cc'):
        parts = parse_cpp(content)
        lang = 'cpp'
    else:
        return False

    if not parts:
        return False  # Not a doc file (no marker)

    md_content = generate_markdown(parts, lang)
    md_path = filepath.with_suffix('.md')

    # Check if .md is newer than source (skip if so)
    if md_path.exists():
        if md_path.stat().st_mtime >= filepath.stat().st_mtime:
            print(f"  skip (up to date): {md_path.name}")
            return False

    md_path.write_text(md_content)
    print(f"  generated: {md_path.name}")
    return True


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')

    if not root.is_dir():
        print(f"Error: {root} is not a directory")
        sys.exit(1)

    print(f"Scanning {root.absolute()} for doc files...")

    converted = 0
    for filepath in root.rglob('*'):
        if filepath.suffix in ('.py', '.cpp', '.hpp', '.h', '.cc'):
            if process_file(filepath):
                converted += 1

    print(f"Converted {converted} file(s)")


if __name__ == '__main__':
    main()
