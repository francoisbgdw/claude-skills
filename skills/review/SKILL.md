---
name: review
description: Two-pass code review with auto-fix — reviews PRs or staged changes, auto-fixes obvious issues, batches judgment calls for the user. Use when asked to "review code", "review this PR", "code review", or "check my changes".
allowed-tools: Bash(git *), Bash(gh *), Read, Edit, Write, Grep, Glob
---

# Code Review

Two-pass code review inspired by gstack's fix-first review pattern. Every finding gets action — either an immediate fix or a batched question.

## Current context

- Current branch: !`git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "not a git repo"`
- Base branch: !`git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}' || echo "main"`
- Open PR: !`gh pr view --json number,title,state -q '"\(.number): \(.title) [\(.state)]"' 2>/dev/null || echo "no PR on this branch"`

## How to review

$ARGUMENTS may specify a PR number, branch, or file list. If not provided, review the diff of the current branch against the base branch.

### Step 1: Gather context

1. Identify what to review:
   - If a PR number is given: `gh pr diff <number>`
   - If files are specified: read those files
   - Otherwise: `git diff $(git merge-base HEAD origin/main)..HEAD`
2. List all changed files: `git diff --name-only $(git merge-base HEAD origin/main)..HEAD`
3. Read each changed file in full to understand surrounding context
4. Check for related tests: search for test files matching changed source files

### Step 2: First pass — AUTO-FIX

Scan for issues that have objectively correct fixes. Apply them immediately with the Edit tool. Each fix gets a one-line summary.

Auto-fix categories:
- **Typos** in strings, comments, variable names
- **Unused imports** or variables
- **Missing error handling** for obvious failure cases (unchecked nulls, missing try/catch on I/O)
- **Security issues** — SQL injection, XSS, command injection, hardcoded secrets
- **Style consistency** — match the surrounding code's conventions (naming, formatting)
- **Dead code** — unreachable branches, commented-out code blocks
- **Missing `await`** on async calls
- **Obvious logic bugs** — off-by-one errors, wrong comparison operators, swapped arguments

After all auto-fixes, report a summary:

```
## Auto-fixes applied
- [file:line] Fixed: <one-line description>
- [file:line] Fixed: <one-line description>
```

### Step 3: Second pass — ASK

Scan for issues that require human judgment. Do NOT fix these — batch them into a single question.

ASK categories:
- **Architecture concerns** — coupling, responsibility boundaries, abstraction levels
- **Performance** — N+1 queries, unnecessary re-renders, missing indexes, unbound loops
- **Race conditions** — concurrent access, shared mutable state, missing locks
- **Missing tests** — untested edge cases, missing integration tests
- **API design** — breaking changes, naming inconsistencies, missing validation
- **Business logic** — assumptions that may not hold, edge cases in domain rules
- **SQL safety** — migrations that lock tables, missing transactions, data loss risk

Present all ASK items together with clear options:

```
## Review items needing your input

1. **[file:line] Performance**: The `getUsers()` call inside the loop creates N+1 queries.
   - A) Refactor to batch query outside loop
   - B) Accept — volume is low enough
   - C) Skip for now, create a follow-up issue

2. **[file:line] Missing test**: The error branch on line 45 has no test coverage.
   - A) I'll add a test now
   - B) Skip — not critical path
   - C) Create a follow-up issue

(Reply with choices like "1A, 2C" or discuss any item)
```

### Step 4: Apply ASK decisions

After the user responds, apply their chosen fixes and report the final state.

## Review checklist

For each changed file, verify:

- [ ] No hardcoded secrets, tokens, or credentials
- [ ] No SQL injection or command injection vectors
- [ ] Error cases are handled (not swallowed silently)
- [ ] New public APIs have input validation
- [ ] Database migrations are reversible
- [ ] Breaking changes are documented
- [ ] Test coverage exists for new logic
- [ ] No accidental debug/console.log statements left in

## Circuit breaker

Apply the circuit breaker from [shared safety patterns](../_shared/safety.md):
- If auto-fixes exceed 15 items, pause and confirm with the user before continuing
- If a fix breaks existing tests, stop and report immediately
- Track risk score across the review session

## Best practices

- Review the full file context, not just the diff lines — bugs often lurk in unchanged code that interacts with changes
- Check that tests actually test the right thing (not just that they pass)
- Look for what's missing, not just what's wrong
- Be specific: cite exact file paths and line numbers
- Keep auto-fixes minimal and safe — when in doubt, make it an ASK item
