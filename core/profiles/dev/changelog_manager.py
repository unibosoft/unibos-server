"""
UNIBOS Changelog Manager
Automatic changelog generation from Conventional Commits

Conventional Commits Format:
    <type>(<scope>): <description>

    [optional body]

    [optional footer]

Types:
    feat:     New feature (MINOR version bump)
    fix:      Bug fix (PATCH version bump)
    docs:     Documentation only
    style:    Code style (formatting, semicolons, etc)
    refactor: Code refactoring (no feature/fix)
    perf:     Performance improvement
    test:     Adding/updating tests
    build:    Build system or dependencies
    ci:       CI/CD configuration
    chore:    Maintenance tasks

Breaking Changes:
    feat!:    Breaking change (MAJOR version bump)
    fix!:     Breaking change fix
    Or add "BREAKING CHANGE:" in footer

Examples:
    feat(tui): add dark mode support
    fix(pipeline): resolve archive duplication issue
    docs: update README with new examples
    feat!: redesign CLI argument structure

Usage:
    from core.profiles.dev.changelog_manager import ChangelogManager

    manager = ChangelogManager()
    entries = manager.get_unreleased_changes()
    manager.generate_release_entry("1.1.0", "20251202120000")
"""

import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class CommitEntry:
    """Represents a parsed commit"""
    hash: str
    type: str
    scope: Optional[str]
    description: str
    body: Optional[str]
    breaking: bool
    breaking_description: Optional[str]
    date: str
    author: str

    @property
    def emoji(self) -> str:
        """Get emoji for commit type"""
        emojis = {
            'feat': '✨',
            'fix': '🐛',
            'docs': '📝',
            'style': '💄',
            'refactor': '♻️',
            'perf': '⚡',
            'test': '✅',
            'build': '📦',
            'ci': '👷',
            'chore': '🔧',
        }
        if self.breaking:
            return '💥'
        return emojis.get(self.type, '📌')

    @property
    def category(self) -> str:
        """Get changelog category"""
        if self.breaking:
            return 'Breaking Changes'
        categories = {
            'feat': 'Added',
            'fix': 'Fixed',
            'docs': 'Documentation',
            'style': 'Changed',
            'refactor': 'Changed',
            'perf': 'Performance',
            'test': 'Testing',
            'build': 'Build',
            'ci': 'CI/CD',
            'chore': 'Maintenance',
        }
        return categories.get(self.type, 'Other')


class ChangelogManager:
    """
    Manages CHANGELOG.md generation from git commits

    Features:
    - Parse Conventional Commits format
    - Generate release entries
    - Update [Unreleased] section
    - Maintain Keep a Changelog format
    """

    # Conventional Commit regex
    COMMIT_PATTERN = re.compile(
        r'^(?P<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore)'
        r'(?P<breaking>!)?'
        r'(?:\((?P<scope>[^)]+)\))?'
        r':\s*(?P<description>.+)$',
        re.IGNORECASE
    )

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or self._find_project_root()
        self.changelog_path = self.project_root / "CHANGELOG.md"

    def _find_project_root(self) -> Path:
        """Find project root using git"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True, text=True, check=True
            )
            return Path(result.stdout.strip())
        except:
            return Path(__file__).parent.parent.parent.parent

    def _run_git(self, args: List[str]) -> str:
        """Run git command and return output"""
        result = subprocess.run(
            ['git'] + args,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.strip()

    def get_last_tag(self) -> Optional[str]:
        """Get the most recent version tag"""
        output = self._run_git(['tag', '-l', 'v*', '--sort=-v:refname'])
        if output:
            return output.split('\n')[0]
        return None

    def get_commits_since_tag(self, tag: Optional[str] = None) -> List[Dict]:
        """Get all commits since the given tag (or all if no tag)"""
        if tag:
            range_arg = f"{tag}..HEAD"
        else:
            range_arg = "HEAD"

        # Format: hash|subject|body|date|author
        format_str = "%H|%s|%b|%Y-%m-%d|%an"
        separator = "---COMMIT_SEPARATOR---"

        output = self._run_git([
            'log', range_arg,
            f'--format={format_str}{separator}',
            '--no-merges'
        ])

        commits = []
        if output:
            for commit_str in output.split(separator):
                commit_str = commit_str.strip()
                if not commit_str:
                    continue

                parts = commit_str.split('|', 4)
                if len(parts) >= 4:
                    commits.append({
                        'hash': parts[0][:8],
                        'subject': parts[1],
                        'body': parts[2] if len(parts) > 2 else '',
                        'date': parts[3] if len(parts) > 3 else '',
                        'author': parts[4] if len(parts) > 4 else '',
                    })

        return commits

    def parse_commit(self, commit: Dict) -> Optional[CommitEntry]:
        """Parse a commit into a CommitEntry"""
        subject = commit.get('subject', '')
        match = self.COMMIT_PATTERN.match(subject)

        if not match:
            return None

        # Check for breaking change in body
        body = commit.get('body', '')
        breaking = bool(match.group('breaking'))
        breaking_desc = None

        if 'BREAKING CHANGE:' in body:
            breaking = True
            # Extract breaking change description
            for line in body.split('\n'):
                if line.startswith('BREAKING CHANGE:'):
                    breaking_desc = line.replace('BREAKING CHANGE:', '').strip()
                    break

        return CommitEntry(
            hash=commit.get('hash', ''),
            type=match.group('type').lower(),
            scope=match.group('scope'),
            description=match.group('description'),
            body=body if body else None,
            breaking=breaking,
            breaking_description=breaking_desc,
            date=commit.get('date', ''),
            author=commit.get('author', ''),
        )

    def get_unreleased_changes(self) -> Dict[str, List[CommitEntry]]:
        """Get all unreleased changes grouped by category"""
        last_tag = self.get_last_tag()
        commits = self.get_commits_since_tag(last_tag)

        changes: Dict[str, List[CommitEntry]] = {}

        for commit in commits:
            entry = self.parse_commit(commit)
            if entry:
                category = entry.category
                if category not in changes:
                    changes[category] = []
                changes[category].append(entry)

        return changes

    def format_changelog_entry(self, version: str, build: str,
                               changes: Dict[str, List[CommitEntry]],
                               release_name: Optional[str] = None) -> str:
        """Format changes into a changelog entry"""
        from core.version import parse_build_timestamp

        # Parse build timestamp for date
        build_info = parse_build_timestamp(build)
        if build_info:
            date_str = build_info['date']
        else:
            date_str = datetime.now().strftime('%Y-%m-%d')

        lines = []
        lines.append(f"## [{version}] - {date_str}")
        lines.append("")

        if release_name:
            lines.append(f"### {release_name}")
            lines.append("")

        # Order categories
        category_order = [
            'Breaking Changes',
            'Added',
            'Changed',
            'Fixed',
            'Performance',
            'Documentation',
            'Build',
            'CI/CD',
            'Testing',
            'Maintenance',
            'Other',
        ]

        for category in category_order:
            if category in changes and changes[category]:
                lines.append(f"### {category}")
                lines.append("")

                for entry in changes[category]:
                    scope_str = f"**{entry.scope}**: " if entry.scope else ""
                    lines.append(f"- {entry.emoji} {scope_str}{entry.description}")

                    if entry.breaking_description:
                        lines.append(f"  - ⚠️ {entry.breaking_description}")

                lines.append("")

        return '\n'.join(lines)

    def update_changelog(self, version: str, build: str,
                         release_name: Optional[str] = None) -> bool:
        """
        Update CHANGELOG.md with new release entry

        Returns:
            bool: True if changelog was updated, False if no changes
        """
        changes = self.get_unreleased_changes()

        if not changes:
            return False

        # Generate new entry
        new_entry = self.format_changelog_entry(version, build, changes, release_name)

        # Read existing changelog
        if self.changelog_path.exists():
            content = self.changelog_path.read_text()
        else:
            content = self._create_initial_changelog()

        # Find [Unreleased] section and insert new entry after it
        unreleased_pattern = r'## \[Unreleased\]\s*\n+'
        match = re.search(unreleased_pattern, content)

        if match:
            # Insert new entry after [Unreleased] section marker
            insert_pos = match.end()

            # Check if there's existing unreleased content (before next ## header)
            next_header = re.search(r'\n## \[', content[insert_pos:])
            if next_header:
                # Replace unreleased content with new entry
                end_pos = insert_pos + next_header.start()
                new_content = (
                    content[:match.end()] +
                    '\n---\n\n' +
                    new_entry +
                    content[end_pos:]
                )
            else:
                # Just add new entry
                new_content = (
                    content[:match.end()] +
                    '\n---\n\n' +
                    new_entry +
                    content[match.end():]
                )
        else:
            # No [Unreleased] section, add at the beginning after header
            header_end = content.find('\n## ')
            if header_end == -1:
                new_content = content + '\n\n' + new_entry
            else:
                new_content = (
                    content[:header_end] +
                    '\n\n## [Unreleased]\n\n---\n\n' +
                    new_entry +
                    content[header_end:]
                )

        # Write updated changelog
        self.changelog_path.write_text(new_content)
        return True

    def _create_initial_changelog(self) -> str:
        """Create initial CHANGELOG.md content"""
        return """# UNIBOS Changelog

All notable changes to UNIBOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This changelog is automatically generated from [Conventional Commits](https://www.conventionalcommits.org/).

## [Unreleased]

"""

    def get_suggested_version_bump(self) -> str:
        """
        Suggest version bump type based on unreleased changes

        Returns:
            'major', 'minor', or 'patch'
        """
        changes = self.get_unreleased_changes()

        if 'Breaking Changes' in changes and changes['Breaking Changes']:
            return 'major'

        if 'Added' in changes and changes['Added']:
            return 'minor'

        return 'patch'

    def validate_commit_message(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a commit message follows Conventional Commits

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Get first line (subject)
        subject = message.split('\n')[0].strip()

        if not subject:
            return False, "Commit message cannot be empty"

        match = self.COMMIT_PATTERN.match(subject)

        if not match:
            return False, (
                "Commit message must follow Conventional Commits format:\n"
                "  <type>(<scope>): <description>\n"
                "\n"
                "Valid types: feat, fix, docs, style, refactor, perf, test, build, ci, chore\n"
                "\n"
                "Examples:\n"
                "  feat(tui): add dark mode support\n"
                "  fix: resolve memory leak\n"
                "  docs(readme): update installation guide"
            )

        description = match.group('description')
        if len(description) < 10:
            return False, "Description should be at least 10 characters"

        if len(subject) > 72:
            return False, "Subject line should be 72 characters or less"

        return True, None


def generate_commit_message(
    type: str,
    description: str,
    scope: Optional[str] = None,
    body: Optional[str] = None,
    breaking: bool = False,
    breaking_description: Optional[str] = None
) -> str:
    """
    Generate a properly formatted Conventional Commit message

    Args:
        type: Commit type (feat, fix, docs, etc.)
        description: Short description
        scope: Optional scope
        body: Optional longer description
        breaking: Is this a breaking change?
        breaking_description: Description of breaking change

    Returns:
        Formatted commit message
    """
    # Build subject line
    breaking_marker = '!' if breaking else ''
    scope_str = f"({scope})" if scope else ""
    subject = f"{type}{breaking_marker}{scope_str}: {description}"

    lines = [subject]

    if body:
        lines.append("")
        lines.append(body)

    if breaking and breaking_description:
        lines.append("")
        lines.append(f"BREAKING CHANGE: {breaking_description}")

    # Add standard footer
    lines.append("")
    lines.append("🤖 Generated with [Claude Code](https://claude.com/claude-code)")

    return '\n'.join(lines)
