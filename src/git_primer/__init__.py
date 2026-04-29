"""git-primer - AI-powered changelog generator."""
__version__ = "0.1.0"
__author__ = "PHclaw"
__description__ = "Generate changelogs and release notes from git history"

from .parser import Commit, parse_commits, group_by_type
from .generator import generate_changelog, ChangelogGenerator
from .git import GitHistory

__all__ = [
    "Commit", "parse_commits", "group_by_type",
    "generate_changelog", "ChangelogGenerator",
    "GitHistory"
]