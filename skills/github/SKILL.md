---
name: github
description: GitHub workflow automation — PRs, issues, Actions, repo management. Use when working with GitHub pull requests, issues, CI/CD pipelines, or repository operations.
allowed-tools: Bash(gh *), Read, Grep, Glob
---

# GitHub Workflow Automation

You have full access to the `gh` CLI. Use it for all GitHub operations. The user is authenticated via `gh auth login`.

## Current context

- Current branch: !`git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "not a git repo"`
- Current repo: !`gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "no repo detected"`
- Open PR on this branch: !`gh pr view --json number,title,state -q '"\(.number): \(.title) [\(.state)]"' 2>/dev/null || echo "no PR on this branch"`

## Pull Request workflows

### View & review PRs
```bash
# List open PRs
gh pr list

# View PR details with diff
gh pr view <number>
gh pr diff <number>

# View PR checks and review status
gh pr checks <number>
gh pr view <number> --json reviews,statusCheckRollup

# View PR comments and review comments
gh api repos/{owner}/{repo}/pulls/<number>/comments
gh pr view <number> --comments
```

### Create & manage PRs
```bash
# Create PR from current branch
gh pr create --title "title" --body "description"

# Create draft PR
gh pr create --draft --title "title" --body "description"

# Merge PR (prefer squash for clean history)
gh pr merge <number> --squash --delete-branch

# Request review
gh pr edit <number> --add-reviewer <username>
```

### PR review process
When reviewing a PR:
1. Read the PR description: `gh pr view <number>`
2. Check the diff: `gh pr diff <number>`
3. View changed files list: `gh pr diff <number> --name-only`
4. Read specific changed files using the Read tool
5. Check CI status: `gh pr checks <number>`
6. Leave a review: `gh pr review <number> --approve` or `--request-changes --body "feedback"`

## Issue management

```bash
# List issues (with filters)
gh issue list
gh issue list --label "bug" --assignee "@me"

# Create issue
gh issue create --title "title" --body "description" --label "bug"

# Close issue with comment
gh issue close <number> --comment "Fixed in PR #123"

# Link issue to PR (in PR body, use "Closes #123" or "Fixes #123")
```

## GitHub Actions

```bash
# List recent workflow runs
gh run list

# View a specific run
gh run view <run-id>

# View failed run logs
gh run view <run-id> --log-failed

# Re-run failed jobs
gh run rerun <run-id> --failed

# Watch a running workflow
gh run watch <run-id>

# List workflows
gh workflow list

# Trigger a workflow manually
gh workflow run <workflow-name>
```

## Repository operations

```bash
# Search code in the repo
gh api search/code -X GET -f q="<query> repo:{owner}/{repo}"

# View releases
gh release list
gh release view <tag>

# Compare branches
gh api repos/{owner}/{repo}/compare/<base>...<head>

# View repo stats
gh repo view --json description,stargazerCount,forkCount,primaryLanguage
```

## Best practices

- Always check CI status before merging PRs
- Use squash merge for feature branches to keep history clean
- Link PRs to issues using "Closes #N" in PR descriptions
- When creating PRs, include a clear description with context and test plan
- For large changes, create draft PRs first for early feedback
