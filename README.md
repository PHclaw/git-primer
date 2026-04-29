# git-primer

AI-powered changelog and release notes generator from git history.

## Features

- 🤖 **AI Enhancement** - Uses sentiment analysis to generate "story-like" release notes
- 📝 **Multiple Formats** - Keep a Changelog, Conventional Commits, Markdown
- 🔍 **Smart Grouping** - Automatically groups commits by type (feat, fix, docs, etc.)
- ⚡ **CLI First** - Simple command-line interface
- 🏷️ **Git Integration** - Works with tags, branches, and commit ranges

## Installation

```bash
pip install git-primer
```

## Usage

### Generate Changelog

```bash
# From last tag to now
git-primer changelog

# From specific tag
git-primer changelog --from v1.0.0

# Keep a Changelog format (default)
git-primer changelog --format keepachangelog

# Simple grouped markdown
git-primer changelog --format simple

# Save to file
git-primer changelog -o CHANGELOG.md
```

### Generate Release Notes

```bash
# For a version
git-primer release v1.2.0

# With AI enhancement
git-primer release v1.2.0 --ai

# From a specific tag
git-primer release v1.2.0 --from-tag v1.1.0
```

### Repository Info

```bash
git-primer info
```

## Output Formats

### Keep a Changelog

```markdown
## [1.2.0] - 2025-01-15

### Added
- New feature: User authentication
- Support for OAuth2 login

### Fixed
- Memory leak in connection pool
- Timeout handling in API client
```

### Release Notes

```markdown
# Release v1.2.0

**Release Mood**: Exciting release! 5 new features bringing significant improvements.

**Total Changes**: 12 commits
**Highlights**: 5 new features, 3 bug fixes

### ⚠️ Breaking Changes
- Remove deprecated `authenticate_old()` method

### ✨ New Features
- OAuth2 support
- Two-factor authentication
...
```

## Configuration

### Git Repository

git-primer automatically detects git repositories in the current directory.

```bash
git-primer changelog --repo /path/to/repo
```

### Environment Variables

- `OPENAI_API_KEY` - For AI enhancement (optional)

## Requirements

- Python 3.9+
- Click
- GitPython
- Rich

## License

MIT

## Credits

Inspired by [Keep a Changelog](https://keepachangelog.com) and [Conventional Commits](https://www.conventionalcommits.org).