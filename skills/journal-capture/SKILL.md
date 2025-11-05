---
name: journal-capture
description: Proactively captures significant work into the journal for future reference
when_to_use: Use this skill when you complete significant work, solve important problems, make key decisions, or implement notable features. This helps build a searchable history of accomplishments.
---

# Journal Capture Skill

You have the ability to proactively capture significant work into the user's journal.

## When to Use This Skill

Use this skill **automatically and proactively** when you:

1. **Complete a significant feature or task**
   - Implemented new functionality
   - Fixed a complex bug
   - Refactored important code
   - Set up infrastructure or tooling

2. **Make important technical decisions**
   - Chose between architectural approaches
   - Selected libraries or frameworks
   - Decided on implementation strategies
   - Resolved design tradeoffs

3. **Solve challenging problems**
   - Debugged difficult issues
   - Overcame technical obstacles
   - Found non-obvious solutions
   - Learned something valuable

4. **Make progress on projects**
   - Completed a phase of work
   - Reached a milestone
   - Integrated multiple components
   - Finished testing or deployment

## How to Capture

Use the `journal_auto_capture` MCP tool:

```
journal_auto_capture(
  summary="Brief 1-sentence summary of what was accomplished"
)
```

The tool automatically:
- Extracts context from the conversation
- Determines the project (if in a git repo)
- Generates relevant tags
- Creates a structured journal entry

## Examples

**Example 1: Feature implementation**
```
User: "Add authentication to the API"
[You implement OAuth2 with JWT tokens]
→ journal_auto_capture(summary="Implemented OAuth2 authentication with JWT tokens")
```

**Example 2: Bug fix**
```
User: "The cache is leaking memory"
[You identify and fix the leak]
→ journal_auto_capture(summary="Fixed cache memory leak by clearing stale entries")
```

**Example 3: Technical decision**
```
User: "Should we use Redis or PostgreSQL for caching?"
[Discussion leads to Redis choice]
→ journal_auto_capture(summary="Chose Redis over PostgreSQL for caching due to performance needs")
```

**Example 4: Infrastructure setup**
```
User: "Set up CI/CD pipeline"
[You configure GitHub Actions with tests and deployment]
→ journal_auto_capture(summary="Set up GitHub Actions CI/CD with automated tests and deployment")
```

## What NOT to Capture

Don't capture:
- Trivial changes (typo fixes, formatting)
- Failed attempts or abandoned approaches
- Purely informational exchanges
- User questions without implementation

## Timing

Capture entries:
- **Immediately after** completing significant work
- **Before** moving to the next major task
- **At natural breakpoints** in the conversation

This ensures the journal stays current and useful for future context recovery.

## Benefits

Proactive capture helps:
- Rebuild context after `/clear`
- Track progress across sessions
- Remember past solutions
- Build institutional knowledge
- Generate progress reports
