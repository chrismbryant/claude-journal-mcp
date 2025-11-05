# Journal Statistics

You are helping the user view statistics about their journal.

## Process

1. **Use the MCP tool:**
   Call `journal_stats` (no parameters needed):
   ```
   journal_stats()
   ```

2. **Present insights:**
   The tool returns:
   - Total number of entries
   - Date range (first to last entry)
   - Number of projects tracked
   - Entries per project breakdown

3. **Add interpretation:**
   - Highlight most active projects
   - Show how long they've been journaling
   - Suggest actions based on stats

## Presentation Format

```
**📊 Journal Statistics**

**Overview:**
- **Total Entries:** 247 entries
- **Journaling Since:** January 15, 2024 (6 months)
- **Last Entry:** July 20, 2024
- **Projects Tracked:** 5 projects

**Entries by Project:**
1. my-app: 89 entries (36%)
2. api-service: 62 entries (25%)
3. website: 51 entries (21%)
4. mobile-app: 31 entries (13%)
5. internal-tools: 14 entries (6%)

**Insights:**
- Most active on my-app - main focus recently
- Consistent journaling over 6 months
- Good project organization across 5 repos
```

## Additional Actions to Suggest

Based on stats, suggest:

**If many entries:**
- "Want to search for something specific? Try `/journal-search`"
- "Interested in recent work? Try `/journal-recent`"

**If few entries:**
- "Keep journaling! It gets more valuable over time"
- "Consider using auto-capture to save more context"

**If uneven distribution:**
- "my-app has lots of entries - want to see them? `/journal-search project:my-app`"

**If stale (last entry old):**
- "Haven't journaled recently - anything to capture? `/journal-add`"

## Use Cases

**Project planning:**
```
User: "How much have I worked on each project?"
→ journal_stats()
→ Show breakdown by project
```

**Progress tracking:**
```
User: "How long have I been using the journal?"
→ journal_stats()
→ Highlight date range and growth
```

**General overview:**
```
User: "Give me an overview of my journal"
→ journal_stats()
→ Full statistics with insights
```
