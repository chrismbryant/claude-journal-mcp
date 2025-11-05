# Add Journal Entry

You are helping the user add a journal entry.

## Process

1. **Gather information:**
   - **Title** (required): Ask for a brief title
   - **Description** (required): Ask for 1-2 sentence description
   - **Project** (optional): Ask if this is related to a specific project/repo
     - If user is in a git repo, suggest using the repo name
     - If not specified, can be left empty
   - **Tags** (optional): Suggest relevant tags based on the content
     - Technical terms mentioned
     - Type of work (feature, bugfix, refactor, etc.)
     - Technologies used

2. **Use the MCP tool:**
   Call `journal_add` with the gathered information:
   ```
   journal_add(
     title="User's title",
     description="User's description",
     project="project-name" (if provided),
     tags=["tag1", "tag2"] (if provided)
   )
   ```

3. **Confirm success:**
   Tell the user their entry was saved and show the ID for reference.

## Examples

**Example 1: Simple entry**
- Title: "Implemented OAuth login"
- Description: "Built OAuth2 flow with JWT tokens for user authentication"
- Project: "my-app"
- Tags: ["auth", "oauth", "backend"]

**Example 2: Bug fix**
- Title: "Fixed memory leak in cache"
- Description: "Cache wasn't clearing old entries, causing gradual memory growth"
- Tags: ["bugfix", "performance", "cache"]

## Tips

- Suggest concise titles (3-7 words)
- Descriptions should be complete sentences
- Tags help with searching later
- Project name helps organize multi-repo work
