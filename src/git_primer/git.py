"""Git history fetching."""
import os
from datetime import datetime
from git import Repo, GitCommandError
from pathlib import Path
from typing import Optional


class GitHistory:
    def __init__(self, repo_path: Optional[str] = None):
        if repo_path is None:
            repo_path = os.getcwd()
        self.repo_path = Path(repo_path)
        try:
            self.repo = Repo(repo_path)
        except Exception as e:
            raise ValueError(f"Not a git repository: {repo_path}") from e
    
    def get_commits_since(self, tag_or_ref: Optional[str] = None, count: int = 500) -> list[dict]:
        """Get commits since last tag or ref."""
        commits = []
        
        try:
            if tag_or_ref:
                # Get commits from tag to HEAD
                ref = self.repo.tag_prereleases(tag_or_ref)
                commits_iter = list(self.repo.iter_commits(f"{tag_or_ref}..HEAD", max_count=count))
            else:
                # Get recent commits
                commits_iter = list(self.repo.iter_commits(max_count=count))
        except (GitCommandError, Exception):
            # Fallback to all commits
            commits_iter = list(self.repo.iter_commits(max_count=count))
        
        for commit in commits_iter:
            if commit.message.startswith("Merge"):
                continue  # Skip merge commits
            
            commits.append({
                "hash_short": commit.hexsha[:8],
                "hash_full": commit.hexsha,
                "message": commit.message.strip(),
                "author": str(commit.author),
                "email": str(commit.author.email),
                "date": datetime.fromtimestamp(commit.committed_date).strftime("%Y-%m-%d"),
            })
        
        return commits
    
    def get_tags(self) -> list[str]:
        """Get all tags sorted by date."""
        tags = []
        for tag in self.repo.tags:
            try:
                date = tag.commit.committed_date
                tags.append((tag.name, date))
            except:
                pass
        tags.sort(key=lambda x: x[1], reverse=True)
        return [t[0] for t in tags]
    
    def get_last_tag(self) -> Optional[str]:
        """Get the most recent tag."""
        tags = self.get_tags()
        return tags[0] if tags else None
    
    def get_repo_info(self) -> dict:
        """Get basic repo info."""
        try:
            origin = self.repo.remote("origin").url
        except:
            origin = "unknown"
        
        return {
            "name": self.repo_path.name,
            "path": str(self.repo_path),
            "remote": origin,
            "branch": self.repo.active_branch.name if self.repo.head.is_detached is False else "detached",
            "total_commits": len(list(self.repo.iter_commits())),
        }