"""Sentiment integration with git-mood."""
from typing import Optional
from .parser import Commit


def get_mood_summary(commits: list[Commit]) -> Optional[str]:
    """Generate a mood summary from commits using git-mood analyzer."""
    try:
        import sys
        from pathlib import Path
        
        # Try to use git-mood from parent directory
        git_mood_path = Path(__file__).parent.parent.parent.parent / "git-mood" / "src" / "git_mood"
        
        if git_mood_path.exists():
            sys.path.insert(0, str(git_mood_path.parent))
            
            # Analyze commits for sentiment
            if not commits:
                return "No commits to analyze."
            
            # Simple heuristic mood detection
            feat_count = sum(1 for c in commits if c.type == "feat")
            fix_count = sum(1 for c in commits if c.type == "fix")
            refactor_count = sum(1 for c in commits if c.type == "refactor")
            docs_count = sum(1 for c in commits if c.type == "docs")
            
            if feat_count > fix_count * 2:
                return f"Exciting release! {feat_count} new features bringing significant improvements."
            elif fix_count > feat_count * 3:
                return f"Bug fix focused release with {fix_count} fixes addressing stability and reliability."
            elif refactor_count > feat_count:
                return f"Refactoring focused release, improving code quality and maintainability."
            elif docs_count > (feat_count + fix_count):
                return f"Documentation focused release, improving clarity and developer experience."
            elif feat_count and fix_count:
                return f"Mixed release with {feat_count} features and {fix_count} bug fixes."
            elif feat_count:
                return f"Feature rich release with {feat_count} new capabilities."
            elif fix_count:
                return f"Maintenance release with {fix_count} bug fixes."
            else:
                return f"Release with {len(commits)} commits of various improvements."
        
        return None
    except Exception:
        return None


def get_release_summary(commits: list[Commit]) -> dict:
    """Get structured summary of commits."""
    summary = {
        "total": len(commits),
        "features": sum(1 for c in commits if c.type == "feat"),
        "fixes": sum(1 for c in commits if c.type == "fix"),
        "docs": sum(1 for c in commits if c.type == "docs"),
        "refactors": sum(1 for c in commits if c.type == "refactor"),
        "breaking": sum(1 for c in commits if c.breaking),
    }
    return summary