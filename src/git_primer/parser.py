"""Git history parsing."""
import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Commit:
    hash_short: str
    hash_full: str
    message: str
    author: str
    email: str
    date: str
    type: str = ""
    scope: str = ""
    breaking: bool = False
    body: str = ""
    
    @property
    def conventional(self) -> str:
        """Format as conventional commit."""
        scope_part = f"({self.scope})" if self.scope else ""
        break_part = "!" if self.breaking else ""
        return f"{self.type}{scope_part}{break_part}: {self.message.split(chr(10))[0]}"


# Conventional commit types
COMMIT_TYPES = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "docs": "Documentation",
    "refactor": "Refactoring",
    "perf": "Performance",
    "test": "Tests",
    "chore": "Chores",
    "style": "Styles",
    "ci": "CI/CD",
    "build": "Builds",
    "revert": "Reverts",
    "wip": "Work in Progress",
}

# Breaking change patterns
BREAKING_PATTERNS = [
    re.compile(r"^([^:]+)\s*:\s*[^:]+!?\s*:\s*.*"),
    re.compile(r"^breaking\s*change", re.IGNORECASE),
    re.compile(r"^breaking!", re.IGNORECASE),
]


def parse_commit_message(msg: str) -> tuple[str, str, bool, str]:
    """Parse conventional commit format."""
    # Pattern: type(scope)!: message
    pattern = r'^([a-z]+)(?:\(([^)]+)\))?(!)?:\s*(.+)$'
    match = re.match(pattern, msg.strip(), re.IGNORECASE)
    
    if match:
        commit_type = match.group(1).lower()
        scope = match.group(2) or ""
        breaking = bool(match.group(3)) or "breaking" in msg.lower()
        message = match.group(4)
        return commit_type, scope, breaking, message
    
    # Fallback: try to find type at start
    for commit_type in COMMIT_TYPES:
        pattern2 = rf'^({commit_type})(?:\(([^)]+)\))?(?::|\s)'
        match2 = re.match(pattern2, msg.strip(), re.IGNORECASE)
        if match2:
            scope = match2.group(2) or ""
            breaking = "breaking" in msg.lower()
            # Get message after the type part
            rest = msg.strip()[match2.end():].lstrip(": ").lstrip(" ")
            return commit_type, scope, breaking, rest
    
    return "chore", "", "breaking" in msg.lower(), msg.strip()


def parse_commits(commits_data: list) -> list[Commit]:
    """Parse raw commit data into Commit objects."""
    result = []
    for c in commits_data:
        msg = c.get("message", "") or ""
        commit_type, scope, breaking, short_msg = parse_commit_message(msg)
        
        # Extract body (everything after first line)
        parts = msg.split("\n", 1)
        body = parts[1].strip() if len(parts) > 1 else ""
        
        commit = Commit(
            hash_short=c.get("hash_short", ""),
            hash_full=c.get("hash_full", ""),
            message=short_msg,
            author=c.get("author", ""),
            email=c.get("email", ""),
            date=c.get("date", ""),
            type=commit_type,
            scope=scope,
            breaking=breaking,
            body=body
        )
        result.append(commit)
    return result


def group_by_type(commits: list[Commit]) -> dict[str, list[Commit]]:
    """Group commits by their type."""
    grouped = {}
    for c in commits:
        if c.type not in grouped:
            grouped[c.type] = []
        grouped[c.type].append(c)
    return grouped


def extract_breaking_commits(commits: list[Commit]) -> list[Commit]:
    """Extract commits marked as breaking changes."""
    return [c for c in commits if c.breaking]