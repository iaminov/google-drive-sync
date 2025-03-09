#!/usr/bin/env python3
import sys
import re

# Transform commit messages into Conventional Commits style while
# preserving the original body and dates.
# - If already conventional, leave as-is.
# - Otherwise categorize based on subject heuristics and add an optional scope.

def decap(s: str) -> str:
    return s[:1].lower() + s[1:] if s else s

CONVENTIONAL_RE = re.compile(r'^(build|ci|chore|docs|feat|fix|perf|refactor|revert|style|test)(\([^)]+\))?(!)?:\s', re.IGNORECASE)

STARTS = {
    'feat': ['feat', 'add', 'introduce', 'implement', 'create', 'enable', 'support'],
    'fix': ['fix', 'repair', 'correct', 'address', 'resolve', 'patch', 'bugfix'],
    'refactor': ['refactor', 'restructure', 'cleanup', 'tidy', 'simplify', 'modernize'],
    'docs': ['docs', 'document', 'readme', 'finalize documentation', 'guide'],
    'test': ['test', 'tests', 'coverage', 'pytest', 'unit', 'integration'],
    'build': ['build', 'package', 'packaging', 'release', 'version', 'setup', 'pyproject', 'setuptools'],
    'ci': ['ci', 'workflow', 'github actions', 'pipeline'],
    'style': ['style', 'format', 'formatting', 'lint', 'pep8', 'ruff', 'black', 'isort'],
    'perf': ['perf', 'optimize', 'optimization', 'performance'],
    'chore': ['chore', 'deps', 'dependency', 'dependencies', 'editor', 'config', 'configuration'],
}

SCOPES = [
    ('typing', ['typing', 'type hint', 'mypy']),
    ('docs', ['readme', 'docs', 'documentation', 'guide']),
    ('tests', ['test', 'pytest', 'coverage']),
    ('build', ['build', 'pyproject', 'setuptools', 'packaging']),
    ('auth', ['auth', 'oauth', 'credentials']),
    ('drive', ['drive']),
    ('photos', ['photos', 'photo']),
    ('ci', ['ci', 'workflow', 'github actions']),
    ('lint', ['lint', 'ruff', 'black', 'isort', 'format']),
]


def categorize(subject: str) -> str:
    s_lower = subject.lower()
    # direct starts
    for t, keywords in STARTS.items():
        for kw in keywords:
            if s_lower.startswith(kw):
                return t
    # keyword fallbacks
    for kw in ['readme', 'docs', 'documentation', 'guide']:
        if kw in s_lower:
            return 'docs'
    for kw in ['fix', 'bug', 'error', 'issue', 'resolve']:
        if kw in s_lower:
            return 'fix'
    for kw in ['test', 'pytest', 'coverage', 'unit', 'integration']:
        if kw in s_lower:
            return 'test'
    for kw in ['refactor', 'cleanup', 'restructure', 'modernize', 'simplify']:
        if kw in s_lower:
            return 'refactor'
    for kw in ['ci', 'workflow', 'github actions', 'pipeline']:
        if kw in s_lower:
            return 'ci'
    for kw in ['build', 'packaging', 'pyproject', 'setuptools', 'release']:
        if kw in s_lower:
            return 'build'
    for kw in ['perf', 'optimize', 'optimization', 'performance']:
        if kw in s_lower:
            return 'perf'
    for kw in ['style', 'format', 'lint', 'pep8', 'ruff', 'black', 'isort']:
        if kw in s_lower:
            return 'style'
    return 'chore'


def choose_scope(subject: str) -> str | None:
    s_lower = subject.lower()
    for scope, kws in SCOPES:
        for kw in kws:
            if kw in s_lower:
                return scope
    return None


def transform(raw: str) -> str:
    lines = raw.splitlines()
    if not lines:
        return raw
    subject = lines[0].strip()
    body = "\n".join(lines[1:]).rstrip()

    # Keep merge commits readable as chore
    if subject.lower().startswith('merge '):
        subject = f"chore: {decap(subject)}"
        return subject + ("\n\n" + body if body else "")

    if CONVENTIONAL_RE.match(subject):
        return raw

    type_ = categorize(subject)
    scope = choose_scope(subject)
    new_subject = f"{type_}{f'({scope})' if scope else ''}: {decap(subject)}"
    return new_subject + ("\n\n" + body if body else "")


def main() -> int:
    raw = sys.stdin.read()
    if raw is None:
        return 0
    out = transform(raw)
    sys.stdout.write(out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

