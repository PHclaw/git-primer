"""Changelog and release notes generator."""
from datetime import datetime
from typing import Optional

from .parser import Commit, group_by_type, COMMIT_TYPES, extract_breaking_commits


class ChangelogGenerator:
    def __init__(self, commits: list[Commit]):
        self.commits = commits
    
    def generate_grouped(self) -> dict[str, list[Commit]]:
        """Generate grouped by type."""
        return group_by_type(self.commits)
    
    def generate_simple_markdown(self, title: str = "Changelog", version: Optional[str] = None, date: Optional[str] = None) -> str:
        """Generate simple grouped markdown."""
        grouped = self.generate_grouped()
        lines = [f"# {title}"]
        
        if version:
            lines.append(f"\n## {version}")
        if date:
            lines.append(f"*_{date}_")
        
        lines.append("")
        
        # Breaking changes first
        breaking = extract_breaking_commits(self.commits)
        if breaking:
            lines.append("### Breaking Changes\n")
            for c in breaking:
                lines.append(f"- {c.message} ({c.hash_short})")
            lines.append("")
        
        # Other types in order
        type_order = ["feat", "fix", "perf", "refactor", "docs", "test", "ci", "build", "chore", "style", "revert", "wip"]
        
        for commit_type in type_order:
            if commit_type in grouped:
                type_commits = grouped[commit_type]
                type_name = COMMIT_TYPES.get(commit_type, commit_type.title())
                lines.append(f"### {type_name}\n")
                
                for c in type_commits:
                    lines.append(f"- {c.message} ({c.hash_short})")
                lines.append("")
        
        return "\n".join(lines)
    
    def generate_keepachangelog(self, version: str = "Unreleased", date: Optional[str] = None) -> str:
        """Generate in Keep a Changelog format."""
        grouped = self.generate_grouped()
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        lines = [
            "# Changelog",
            "",
            "All notable changes to this project will be documented in this file.",
            "",
            "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),",
            "and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).",
            "",
            f"## [{version}] - {date}",
            "",
        ]
        
        # Breaking changes
        breaking = extract_breaking_commits(self.commits)
        if breaking:
            lines.append("### ⚠️ BREAKING CHANGES\n")
            for c in breaking:
                lines.append(f"- {c.message}")
            lines.append("")
        
        # Types in standard order
        type_order = [
            ("feat", "Added"),
            ("fix", "Fixed"), 
            ("perf", "Performance"),
            ("refactor", "Refactored"),
            ("docs", "Documentation"),
            ("test", "Tests"),
            ("ci", "CI/CD"),
            ("build", "Builds"),
            ("chore", "Chores"),
        ]
        
        for commit_type, header in type_order:
            if commit_type in grouped and grouped[commit_type]:
                lines.append(f"### {header}\n")
                for c in grouped[commit_type]:
                    lines.append(f"- {c.message}")
                lines.append("")
        
        return "\n".join(lines)
    
    def generate_conventional(self, version: str = "Unreleased") -> str:
        """Generate in conventional commits format."""
        grouped = self.generate_grouped()
        
        lines = [f"# {version}\n"]
        
        for commit_type, type_name in COMMIT_TYPES.items():
            if commit_type in grouped:
                commits = grouped[commit_type]
                lines.append(f"\n## {type_name}\n")
                for c in commits:
                    lines.append(f"- {c.conventional}")
        
        return "\n".join(lines)
    
    def generate_release_notes(self, version: str, sentiment_summary: Optional[str] = None) -> str:
        """Generate narrative release notes."""
        grouped = self.generate_grouped()
        
        # Count by type
        counts = {k: len(v) for k, v in grouped.items()}
        
        lines = [
            f"# Release {version}",
            "",
        ]
        
        # Add sentiment summary if provided
        if sentiment_summary:
            lines.append(f"**Release Mood**: {sentiment_summary}\n")
        
        # Summary
        total = sum(counts.values())
        lines.append(f"**Total Changes**: {total} commits\n")
        
        feat_count = counts.get("feat", 0)
        fix_count = counts.get("fix", 0)
        
        if feat_count or fix_count:
            parts = []
            if feat_count:
                parts.append(f"{feat_count} new features")
            if fix_count:
                parts.append(f"{fix_count} bug fixes")
            lines.append(f"**Highlights**: {', '.join(parts)}\n")
        
        lines.append("")
        
        # Breaking changes
        breaking = extract_breaking_commits(self.commits)
        if breaking:
            lines.append("### ⚠️ Breaking Changes\n")
            for c in breaking:
                lines.append(f"- {c.message}")
            lines.append("")
        
        # Group by category for readability
        if feat_count:
            lines.append("### ✨ New Features\n")
            for c in grouped.get("feat", []):
                lines.append(f"- {c.message}")
            lines.append("")
        
        if fix_count:
            lines.append("### 🐛 Bug Fixes\n")
            for c in grouped.get("fix", []):
                lines.append(f"- {c.message}")
            lines.append("")
        
        # Other changes
        other_types = [(t, COMMIT_TYPES.get(t, t)) for t in grouped if t not in ["feat", "fix"]]
        if other_types:
            lines.append("### Other Changes\n")
            for t, name in other_types:
                for c in grouped[t]:
                    lines.append(f"- **{name}**: {c.message}")
            lines.append("")
        
        return "\n".join(lines)


def generate_changelog(commits: list[Commit], format: str = "keepachangelog", version: str = "Unreleased", 
                     sentiment: Optional[str] = None) -> str:
    """Generate changelog in specified format."""
    gen = ChangelogGenerator(commits)
    
    if format == "simple":
        return gen.generate_simple_markdown(version=version)
    elif format == "conventional":
        return gen.generate_conventional(version)
    elif format == "keepachangelog":
        return gen.generate_keepachangelog(version)
    elif format == "release":
        return gen.generate_release_notes(version, sentiment)
    else:
        return gen.generate_keepachangelog(version)