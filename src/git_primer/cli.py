"""CLI for git-primer."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .git import GitHistory
from .parser import parse_commits, COMMIT_TYPES
from .generator import generate_changelog, ChangelogGenerator


console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """git-primer - AI-powered changelog generator from git history."""
    pass


@main.command()
@click.option("--from", "from_ref", default=None, help="Start from this tag/ref")
@click.option("--to", "to_ref", default="HEAD", help="End at this ref (default: HEAD)")
@click.option("--count", default=500, help="Max commits to analyze")
@click.option("--format", "fmt", type=click.Choice(["keepachangelog", "simple", "conventional", "release"]), 
              default="keepachangelog", help="Output format")
@click.option("-o", "--output", "output_file", type=click.Path(), default=None, help="Output file (default: stdout)")
@click.option("--version", "version", default="Unreleased", help="Version for changelog")
@click.option("--preview", is_flag=True, help="Preview only (don't write)")
@click.option("--repo", default=None, help="Repository path")
def changelog(from_ref, to_ref, count, fmt, output_file, version, preview, repo):
    """Generate changelog from git history."""
    try:
        git = GitHistory(repo)
        
        # Get commits
        if from_ref:
            commits_data = git.get_commits_since(from_ref, count)
        else:
            commits_data = git.get_commits_since(None, count)
        
        if not commits_data:
            console.print("[yellow]No commits found.[/yellow]")
            return
        
        commits = parse_commits(commits_data)
        
        # Generate
        gen = ChangelogGenerator(commits)
        
        if fmt == "keepachangelog":
            content = gen.generate_keepachangelog(version)
        elif fmt == "simple":
            content = gen.generate_simple_markdown(version=version)
        elif fmt == "conventional":
            content = gen.generate_conventional(version)
        elif fmt == "release":
            content = gen.generate_release_notes(version)
        else:
            content = gen.generate_keepachangelog(version)
        
        if preview or output_file is None:
            console.print(content)
        else:
            Path(output_file).write_text(content, encoding="utf-8")
            console.print(f"[green]Written to {output_file}[/green]")
        
        # Summary table
        table = Table(title="Commit Summary")
        table.add_column("Type", style="cyan")
        table.add_column("Count", justify="right", style="green")
        
        grouped = gen.generate_grouped()
        type_order = ["feat", "fix", "docs", "refactor", "perf", "test", "ci", "build", "chore", "style", "revert"]
        
        for ct in type_order:
            if ct in grouped:
                table.add_row(COMMIT_TYPES.get(ct, ct), str(len(grouped[ct])))
        
        console.print("\n")
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise


@main.command()
@click.argument("version")
@click.option("--repo", default=None, help="Repository path")
@click.option("--from-tag", "from_tag", default=None, help="Start from this tag")
@click.option("--ai/--no-ai", default=False, help="Enable AI enhancement (requires OPENAI_API_KEY)")
@click.option("-o", "--output", "output_file", type=click.Path(), default=None, help="Output file")
@click.option("--format", "fmt", type=click.Choice(["markdown", "keepachangelog"]), default="markdown")
def release(version, repo, from_tag, ai, output_file, fmt):
    """Generate release notes for a specific version."""
    try:
        git = GitHistory(repo)
        
        # Determine start point
        if from_tag is None:
            from_tag = git.get_last_tag()
        
        # Get commits
        commits_data = git.get_commits_since(from_tag, 500)
        
        if not commits_data:
            console.print("[yellow]No commits found.[/yellow]")
            return
        
        commits = parse_commits(commits_data)
        gen = ChangelogGenerator(commits)
        
        # Add sentiment if available
        sentiment = None
        if ai:
            try:
                from .sentiment import get_mood_summary
                sentiment = get_mood_summary(commits)
            except Exception:
                console.print("[yellow]AI summarization unavailable, skipping.[/yellow]")
        
        content = gen.generate_release_notes(version, sentiment)
        
        if output_file:
            Path(output_file).write_text(content, encoding="utf-8")
            console.print(f"[green]Written to {output_file}[/green]")
        else:
            console.print(content)
        
        console.print(f"\n[green]Release notes for {version} generated successfully.[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise


@main.command()
@click.option("--repo", default=None, help="Repository path")
def info(repo):
    """Show repository info."""
    try:
        git = GitHistory(repo)
        info_data = git.get_repo_info()
        tags = git.get_tags()
        
        console.print(f"\n[bold]Repository:[/bold] {info_data['name']}")
        console.print(f"[bold]Path:[/bold] {info_data['path']}")
        console.print(f"[bold]Remote:[/bold] {info_data['remote']}")
        console.print(f"[bold]Branch:[/bold] {info_data['branch']}")
        console.print(f"[bold]Total commits:[/bold] {info_data['total_commits']}")
        console.print(f"[bold]Tags:[/bold] {', '.join(tags[:10]) if tags else 'None'}")
        
        last_tag = git.get_last_tag()
        if last_tag:
            console.print(f"\n[green]Last tag: {last_tag}[/green]")
            
            commits = git.get_commits_since(last_tag, 100)
            console.print(f"[green]Commits since last tag: {len(commits)}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()