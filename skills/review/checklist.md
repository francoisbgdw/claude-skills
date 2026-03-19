# Review Checklist Reference

Detailed checklist for thorough code reviews, organized by category.

## Security

- [ ] No hardcoded secrets, API keys, tokens, or passwords
- [ ] No SQL injection vectors (parameterize all queries)
- [ ] No command injection (sanitize shell inputs, avoid string interpolation)
- [ ] No XSS vectors (escape user content in HTML/templates)
- [ ] No path traversal (validate file paths, reject `..`)
- [ ] Authentication/authorization checks on new endpoints
- [ ] Sensitive data not logged or exposed in error messages
- [ ] CORS configuration is restrictive, not wildcard

## Data integrity

- [ ] Database migrations are reversible (have a down migration)
- [ ] Migrations don't lock large tables for extended periods
- [ ] Transactions used for multi-step data modifications
- [ ] No data loss risk in schema changes (column drops, type changes)
- [ ] Cascading deletes are intentional and documented

## Error handling

- [ ] Errors are not silently swallowed (`catch {}` with no body)
- [ ] Error messages are useful for debugging (include context)
- [ ] Async errors are properly caught (no unhandled promise rejections)
- [ ] Retry logic has backoff and max attempts (no infinite retry loops)
- [ ] Graceful degradation for external service failures

## Performance

- [ ] No N+1 query patterns (batch/join instead of loop queries)
- [ ] No unbounded data fetching (pagination, limits)
- [ ] No unnecessary re-renders (React: missing memo, deps arrays)
- [ ] Heavy operations are async/background where appropriate
- [ ] Database queries have appropriate indexes

## Race conditions

- [ ] Concurrent access to shared mutable state is protected
- [ ] Check-then-act patterns use atomic operations
- [ ] File operations handle concurrent access
- [ ] Event ordering assumptions are documented or enforced

## API design

- [ ] Breaking changes are versioned or flagged
- [ ] Input validation at system boundaries
- [ ] Consistent naming with existing API
- [ ] Response format matches existing patterns
- [ ] Error responses use standard format

## Testing

- [ ] New logic has test coverage
- [ ] Edge cases are tested (empty, null, boundary values)
- [ ] Tests are testing behavior, not implementation details
- [ ] Test names describe the expected behavior
- [ ] No flaky test patterns (timing-dependent, order-dependent)
