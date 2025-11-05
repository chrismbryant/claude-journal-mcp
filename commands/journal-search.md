# Search Journal

You are helping the user search their journal entries.

## Process

1. **Get search parameters:**
   - **Query** (required): What are they looking for?
     - Keywords, technologies, concepts
     - Can be partial matches
   - **Project** (optional): Filter to specific project?
   - **Limit** (optional): How many results? (default: 20)

2. **Use the MCP tool:**
   Call `journal_search` with parameters:
   ```
   journal_search(
     query="search terms",
     project="project-name" (optional),
     limit=20 (optional)
   )
   ```

3. **Present results:**
   - Show results clearly with IDs
   - Highlight relevant matches
   - If many results, suggest refining search
   - If no results, suggest trying different terms or checking spelling

## Search Tips to Share

- **Broad terms** find more: "auth" finds authentication, authorization, OAuth
- **Specific terms** find less: "JWT token expiration" is very specific
- **Technical terms work well**: Language names, framework names, tool names
- **Try project filter** if working across multiple repos

## Examples

**Example 1: Technology search**
```
User: "Find entries about React"
→ journal_search(query="React", limit=20)
```

**Example 2: Project-specific**
```
User: "Search for database work in my-api"
→ journal_search(query="database", project="my-api")
```

**Example 3: Concept search**
```
User: "Find anything about performance optimization"
→ journal_search(query="performance optimization")
```

## No Results?

If search returns nothing, suggest:
- Trying broader terms
- Checking if they meant a different word
- Using time-based query instead: `/journal-time`
- Checking if journal has entries: `/journal-stats`
