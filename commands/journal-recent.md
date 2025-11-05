# Show Recent Journal Entries

You are helping the user view their recent journal entries.

This command is especially useful after `/clear` to restore context about recent work.

## Process

1. **Determine scope:**
   - Ask how many recent entries to show (default: 10)
   - Ask if they want to filter by project

2. **Use the MCP tool:**
   Call `journal_list_recent`:
   ```
   journal_list_recent(
     limit=10 (or user's preference),
     project="project-name" (optional)
   )
   ```

3. **Present results:**
   - Show entries chronologically (newest first)
   - Highlight key information:
     - Date/time
     - Project name
     - Title
     - Brief description
   - Include entry IDs for reference
   - Summarize what they were working on

## Use Cases

**After /clear:**
```
User: "What was I working on?"
→ journal_list_recent(limit=10)
→ Summarize: "You were recently working on X, Y, and Z"
```

**Start of day:**
```
User: "What did I do yesterday?"
→ journal_list_recent(limit=20)
→ Filter to yesterday's entries and summarize
```

**Project context:**
```
User: "Show recent work on my-api"
→ journal_list_recent(project="my-api", limit=15)
```

## Presentation Format

Present entries like:
```
**Recent Journal Entries** (10 shown)

[42] Implemented OAuth login (2024-01-15 14:30)
📁 my-app | 🏷️ auth, oauth
Built OAuth2 flow with JWT tokens for user authentication

[41] Fixed cache memory leak (2024-01-15 10:15)
🏷️ bugfix, performance
Cache wasn't clearing old entries, causing gradual memory growth

...
```

## Context Recovery Tips

After showing entries, help user:
- "You were focusing on authentication in my-app"
- "Last thing was fixing a performance issue"
- "Ready to continue where you left off?"
