# Safety & Circuit Breaker Patterns

These patterns apply to all skills that perform modifications or destructive operations.

## Circuit breaker — self-regulation for autonomous work

When performing a sequence of fixes, modifications, or automated operations, track your progress and stop if things go sideways.

### Risk accumulation

Maintain a mental "risk score" starting at 0%. Accumulate risk as follows:

| Event | Risk increase |
|-------|--------------|
| Each reverted or undone change | +15% |
| Each fix touching more than 3 files | +5% |
| After 15 consecutive fixes | +1% per additional fix |
| Touching files unrelated to the original task | +20% |
| A fix that breaks something that was working | +25% |
| All remaining issues are low severity | +10% |

### Thresholds

- **Risk > 20%**: Stop and ask the user before continuing. Explain what's happened and propose next steps.
- **Risk > 50%**: Hard stop. Do not continue without explicit user approval and a revised plan.
- **Hard cap**: Never exceed 50 consecutive modifications in a single session without user checkpoint.

### When to apply

- Automated code review fixes (`/review`)
- QA bug fix chains (`/debug`, `/qa`)
- Bulk resource operations (Azure, Fabric)
- Any iterative fix-and-retry loop

## Production resource detection

Before any modification, check if the target appears to be a production resource:

- Resource name contains: `prod`, `prd`, `production`, `live`, `main` (when referring to environments)
- Branch name is `main`, `master`, or `release/*`
- Environment variable or config indicates production

If detected: **warn the user explicitly** and require confirmation before proceeding.

## Destructive operation protocol

For any delete, stop, drop, reset, or force operation:

1. Show the exact resource name/ID and environment
2. State what will happen and what cannot be undone
3. Wait for explicit user confirmation
4. Prefer soft-delete or disable over hard-delete when available

## Blast radius awareness

Before bulk operations:

1. Count how many resources will be affected
2. If more than 5 resources: show the full list and ask for confirmation
3. If more than 20 resources: require the user to explicitly acknowledge the count
4. Prefer dry-run modes when available (`--dry-run`, `--what-if`, `--confirm`)
