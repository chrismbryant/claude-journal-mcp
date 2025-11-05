# Time-Based Journal Query

You are helping the user query journal entries by time period.

This command uses natural language time expressions to find entries.

## Process

1. **Understand the time query:**
   User might ask in various ways:
   - "What did I work on last week?"
   - "Show me entries from January"
   - "When did I implement feature X?"
   - "What happened yesterday?"

2. **Extract time expression:**
   Supported formats:
   - **Relative**: "yesterday", "today", "last week", "last month", "last year"
   - **Recent periods**: "last 3 days", "last 2 weeks"
   - **Current periods**: "this week", "this month", "this year"
   - **Month names**: "january", "january 2024"
   - **ISO dates**: "2024-01-15"

3. **Use the MCP tool:**
   Call `journal_time_query`:
   ```
   journal_time_query(
     time_expression="last week",
     query="optional search terms" (if looking for something specific),
     project="project-name" (optional)
   )
   ```

4. **Present results:**
   - Show entries within the time range
   - Highlight what they accomplished
   - Group by day or week if many results
   - Summarize patterns or themes

## Examples

**Example 1: Recent past**
```
User: "What did I do last week?"
→ journal_time_query(time_expression="last week")
→ Present all entries from last week
```

**Example 2: Specific search in time range**
```
User: "When did I work on authentication?"
→ journal_time_query(time_expression="last month", query="authentication")
→ Find auth-related entries from last month
```

**Example 3: Historical lookup**
```
User: "Show me what I did in January"
→ journal_time_query(time_expression="january")
→ All January entries
```

**Example 4: Project timeline**
```
User: "What have I done on my-api this year?"
→ journal_time_query(time_expression="this year", project="my-api")
```

## Presentation Format

Present with time context:
```
**Journal Entries: Last Week** (15 found)

Week of Jan 8-14, 2024

Monday, Jan 8:
- [45] Implemented OAuth login (my-app)
- [44] Set up testing framework

Tuesday, Jan 9:
- [43] Fixed cache memory leak
...
```

## Tips for Users

Share these time expression examples:
- **yesterday, today** - Single days
- **last week, last month** - Previous period
- **last 7 days** - Exact day count
- **january, february** - Specific months
- **this year** - Year to date
