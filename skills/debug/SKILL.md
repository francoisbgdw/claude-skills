---
name: debug
description: Systematic root-cause debugging — investigates before fixing, with a 3-strike circuit breaker. Use when asked to "debug", "find the bug", "why is this broken", "fix this error", or "troubleshoot".
allowed-tools: Bash(*), Read, Edit, Write, Grep, Glob
---

# Systematic Debugging

Systematic root-cause analysis inspired by gstack's debug methodology. The iron law: **no fixes without investigation**.

## Current context

- Current branch: !`git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "not a git repo"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "no git history"`

## The iron law

**Never apply a fix until you understand the root cause.** A fix without understanding is a guess, and guesses compound into harder bugs.

## Debugging process

$ARGUMENTS should describe the bug, error message, or unexpected behavior.

### Phase 1: Reproduce

1. **Understand the symptom**: What is the user seeing? What should happen instead?
2. **Reproduce the bug**: Run the failing command, test, or scenario
3. **Capture the error**: Save the exact error message, stack trace, or unexpected output
4. **Isolate the trigger**: Find the minimal steps to reproduce

If you cannot reproduce:
- Check if the issue is environment-specific (OS, Node version, Python version, etc.)
- Check if it's a race condition (timing-dependent)
- Ask the user for reproduction steps before guessing

### Phase 2: Investigate

1. **Read the stack trace** — start from the bottom (root cause) not the top (symptom)
2. **Trace the data flow** — follow the input from entry point to failure point
3. **Check recent changes** — `git log --oneline -20` and `git diff HEAD~5` to see what changed
4. **Search for related code** — use Grep to find all callers/callees of the failing function
5. **Read the tests** — existing tests reveal intended behavior and known edge cases
6. **Check dependencies** — version mismatches, breaking changes in updates

Document your findings as you go:

```
## Investigation notes
- Symptom: <what's happening>
- Expected: <what should happen>
- Stack trace points to: <file:line>
- Root cause hypothesis: <your theory>
- Evidence: <what supports this theory>
```

### Phase 3: Hypothesize

Before fixing, state your hypothesis clearly:

```
## Root cause
<One-sentence explanation of why the bug occurs>

## Evidence
- <Fact 1 that supports this>
- <Fact 2 that supports this>

## Proposed fix
<What you will change and why it addresses the root cause>
```

### Phase 4: Fix

1. Apply the minimal fix that addresses the root cause
2. Do not refactor surrounding code — fix the bug only
3. Run the failing test/scenario to verify the fix
4. Run the full test suite to check for regressions

### Phase 5: Verify

1. Confirm the original bug is fixed (re-run the reproduction steps)
2. Confirm no regressions (run related tests)
3. If the bug had no test, write one that catches the specific failure

## Three-strike rule

Track failed fix attempts:

| Attempt | Outcome | Action |
|---------|---------|--------|
| Strike 1 | Fix didn't work | Re-investigate. Your hypothesis was wrong. |
| Strike 2 | Second fix didn't work | Step back. Re-read the code from scratch with fresh eyes. Consider that the bug may be elsewhere. |
| Strike 3 | Third fix didn't work | **Stop.** Report your findings to the user. Present all three hypotheses and what you've learned. Ask for their input. |

**After 3 failed fixes, do NOT continue guessing.** The cost of wrong fixes compounds — each bad fix can introduce new bugs and obscure the real problem.

## Circuit breaker

Apply the circuit breaker from [shared safety patterns](../_shared/safety.md):
- If a fix breaks something that was previously working: +25% risk
- If you're touching files unrelated to the original bug report: +20% risk
- At risk > 20%: pause and check with the user

## Common debugging patterns

### "It works on my machine"
```bash
# Check runtime versions
node --version; python --version; git --version
# Check environment variables
env | grep -i <relevant-keyword>
# Check OS-specific behavior
uname -a
```

### "It worked yesterday"
```bash
# Find what changed
git log --oneline --since="yesterday"
git diff HEAD~10 -- <suspect-file>
# Binary search for the breaking commit
git bisect start
git bisect bad HEAD
git bisect good <known-good-commit>
```

### "It works sometimes" (race condition)
- Look for shared mutable state
- Check for missing `await` or uncaught promises
- Look for event ordering assumptions
- Add logging with timestamps to trace execution order

### "The error message is misleading"
- Read the source code that throws the error, not just the message
- Check if the error is caught and re-thrown with lost context
- Look for error swallowing (`catch {}` with no body)

## Best practices

- **Log your investigation** — write down what you checked and what you found, even if it's "this is fine"
- **Don't fix what you don't understand** — if you can't explain why the fix works, it's not a fix
- **Minimal fixes only** — resist the urge to clean up code while debugging
- **One change at a time** — don't combine multiple fixes, you won't know which one worked
- **Verify with the original reproduction** — not just with tests
