---
name: ship
description: Full release pipeline — tests, review, version bump, changelog, PR creation. Use when asked to "ship it", "release", "create a release", "prepare for release", or "cut a release".
allowed-tools: Bash(*), Read, Edit, Write, Grep, Glob
---

# Ship

Full release pipeline inspired by gstack's ship workflow. Takes code from current state to a merge-ready PR with tests, review, version bump, and changelog.

## Current context

- Current branch: !`git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "not a git repo"`
- Base branch: !`git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}' || echo "main"`
- Uncommitted changes: !`git status --porcelain 2>/dev/null | head -5 || echo "clean"`
- Latest tag: !`git describe --tags --abbrev=0 2>/dev/null || echo "no tags"`

## Ship process

$ARGUMENTS may specify a version bump type (patch, minor, major), a PR title, or specific instructions.

### Step 1: Pre-flight checks

1. **Check for uncommitted changes**: If dirty working tree, ask the user whether to commit or stash
2. **Ensure on a feature branch**: If on main/master, warn and ask the user to create a branch first
3. **Merge base branch**: Pull latest base branch and merge into current branch
   ```bash
   git fetch origin
   git merge origin/main --no-edit
   ```
4. If merge conflicts: **stop and report**. Do not auto-resolve merge conflicts.

### Step 2: Run tests

1. **Detect test framework**:
   - Check for `package.json` scripts: `test`, `test:unit`, `test:integration`
   - Check for `pytest.ini`, `setup.cfg`, `pyproject.toml`
   - Check for `Makefile` test targets
   - Check for `.github/workflows` test steps
2. **Run tests**:
   ```bash
   # Node.js
   npm test

   # Python
   pytest

   # Or whatever the project uses
   ```
3. If tests fail: **stop and report**. Do not skip failing tests.

### Step 3: Quick review

Perform a lightweight review of all changes since the base branch:

1. `git diff origin/main...HEAD --name-only` — list all changed files
2. Scan for common issues:
   - Hardcoded secrets or credentials
   - Debug/console.log statements
   - TODO/FIXME/HACK comments in new code
   - Missing error handling
   - Obvious security issues
3. Auto-fix trivial issues (unused imports, trailing whitespace)
4. If substantive issues found: report them and ask the user before continuing

### Step 4: Version bump (if applicable)

Only if the project has a version file (`package.json`, `pyproject.toml`, `version.txt`, etc.):

1. Determine bump type from $ARGUMENTS or infer from changes:
   - **patch**: Bug fixes, documentation, minor improvements
   - **minor**: New features, non-breaking enhancements
   - **major**: Breaking changes, API modifications
2. Update the version file
3. If the user didn't specify a bump type, ask before applying

### Step 5: Changelog

If a `CHANGELOG.md` exists (do not create one if it doesn't):

1. Gather commits since last tag: `git log $(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD~20")..HEAD --oneline`
2. Group changes by type:
   - **Added**: New features
   - **Changed**: Modifications to existing features
   - **Fixed**: Bug fixes
   - **Removed**: Removed features or deprecated code
3. Add a new entry at the top of the changelog with the new version and date
4. Use the existing changelog format — match the style already in the file

### Step 6: Commit and push

1. Stage all changes (version bump, changelog, auto-fixes):
   ```bash
   git add -A
   git commit -m "chore: prepare release vX.Y.Z"
   ```
2. Push to remote:
   ```bash
   git push origin HEAD
   ```

### Step 7: Create PR

Create a pull request with a clear summary:

```bash
gh pr create --title "Release vX.Y.Z" --body "$(cat <<'EOF'
## Summary
- <key changes from changelog>

## Checklist
- [x] Tests pass
- [x] Code reviewed (auto-review)
- [x] Version bumped
- [x] Changelog updated
- [ ] Manual QA (if applicable)

## Changes since last release
<abbreviated commit list>
EOF
)"
```

## Abort conditions

Stop the ship process immediately if:

- Tests fail and cannot be fixed trivially
- Merge conflicts require manual resolution
- The review finds security issues
- The user is on main/master branch
- There are no changes to ship

## Circuit breaker

Apply the circuit breaker from [shared safety patterns](../_shared/safety.md):
- If auto-fixes during review exceed 10 items, pause and confirm
- Never force-push or amend published commits
- Never push directly to main/master

## Best practices

- Ship small, ship often — smaller PRs are easier to review and less risky
- Every commit in the PR should be bisectable (each commit should build and pass tests)
- The PR description should explain "why", not just "what"
- Tag reviewers if the project has a CODEOWNERS file
- If the project uses conventional commits, match that format
