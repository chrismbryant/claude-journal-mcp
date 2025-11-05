# Claude Journal MCP Server

A lightweight journal/memory system for Claude Code with no ML dependencies. Uses simple SQLite for fast, local storage.

## Features

- ✅ **Lightweight**: No embeddings, no ML models, just SQLite
- ✅ **Fast**: Sub-millisecond queries on local database
- ✅ **Smart Search**: Full-text search across titles, descriptions, tags
- ✅ **Time Queries**: Natural language like "last month", "yesterday"
- ✅ **Project Tracking**: Organize entries by repository/project
- ✅ **Auto-Capture**: Automatic and context-based journaling
- ✅ **Import/Export**: Share journal between instances
- ✅ **Flexible Tags**: Organize with custom tags

## Installation

```bash
cd ~/claude-journal-mcp
pip install -e .
```

## Configuration

Add to `~/.claude/config.json` or your project's `.mcp.json`:

```json
{
  "mcpServers": {
    "journal": {
      "command": "python",
      "args": ["-m", "claude_journal.server"]
    }
  }
}
```

## Database Location

Default: `~/.claude/journal.db`

Override with environment variable:
```bash
export JOURNAL_DB_PATH="/path/to/your/journal.db"
```

## Available Tools

### Write Operations

**`journal_add`** - Manually add entry
```
Add a journal entry:
- title: "Implemented auth system"
- description: "Built OAuth2 flow with JWT tokens"
- project: "my-app"
- tags: ["auth", "backend"]
```

**`journal_auto_capture`** - Auto-save progress
```
Automatically called by hooks or when Claude detects significant work
```

### Read Operations

**`journal_search`** - Text search
```
Search for "authentication" in project "my-app"
```

**`journal_time_query`** - Time-based search
```
What did I work on last week?
What did I do in January?
When did I implement feature X?
```

Supported time expressions:
- `today`, `yesterday`
- `last week`, `last month`, `last year`
- `last 3 days`, `last 2 weeks`
- `this week`, `this month`, `this year`
- `january`, `january 2024`
- `2024-01-15` (ISO date)

**`journal_list_recent`** - Recent entries
```
Show me the last 10 entries
Show recent work on project X
```

**`journal_list_projects`** - All projects
```
List all projects with entry counts
```

**`journal_stats`** - Statistics
```
Show journal statistics
```

### Management Operations

**`journal_delete`** - Delete by ID
```
Delete entry 42
```

**`journal_delete_by_project`** - Delete all for project
```
Delete all entries for project "old-app"
```

**`journal_import`** - Import from file
```
Import from ~/other-machine/journal.db
```

**`journal_export`** - Export to file
```
Export to ~/backup/journal_2024.db
```

## Usage Examples

### Manual Journaling

```
You: Remember that we implemented rate limiting today

Claude: [Calls journal_add]
✅ Journal entry created (ID: 42)
```

### Time-Based Queries

```
You: What did I work on last month?

Claude: [Calls journal_time_query with "last month"]
Shows all entries from last month
```

```
You: When did I add the auth system?

Claude: [Calls journal_time_query with search for "auth"]
Shows entries matching "auth" with dates
```

### Context Recovery

```
You: /clear
You: What was I working on?

Claude: [Calls journal_list_recent]
Shows recent work to restore context
```

### Project Organization

```
You: Show me everything I've done on my-app

Claude: [Calls journal_search with project filter]
Lists all my-app entries
```

### Sharing Between Machines

Machine 1:
```
You: Export my journal

Claude: [Calls journal_export]
✅ Exported journal to journal_export_20241105.db
```

Machine 2:
```
You: Import journal from ~/Downloads/journal_export_20241105.db

Claude: [Calls journal_import]
✅ Imported 150 new entries
```

## Auto-Capture

### Context-Based
Claude automatically creates entries when:
- Significant implementation work is completed
- Important decisions are made
- Complex problems are solved
- Major milestones are reached

### Time-Based Hook
Configure a hook to auto-capture every 30 minutes if activity occurred.

Create `~/.claude/hooks/config.json`:
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matchers": ["*"],
        "hooks": [
          {
            "type": "command",
            "command": "node ~/.claude/hooks/journal-auto-capture.js",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

Create `~/.claude/hooks/journal-auto-capture.js`:
```javascript
#!/usr/bin/env node

// Auto-capture journal entry every 30 minutes if activity occurred
const CAPTURE_INTERVAL = 30 * 60 * 1000; // 30 minutes
const STATE_FILE = require('path').join(
  process.env.HOME, '.claude', 'journal-capture-state.json'
);

// Load state
let state = { lastCapture: 0, messageCount: 0 };
try {
  state = require(STATE_FILE);
} catch {}

// Update message count
state.messageCount++;

// Check if we should capture
const now = Date.now();
const elapsed = now - state.lastCapture;

if (elapsed > CAPTURE_INTERVAL && state.messageCount > 3) {
  // Trigger auto-capture by calling MCP tool
  // (Claude Code will handle this via MCP)
  console.log("🕐 30 minutes elapsed with activity - consider auto-capturing");

  // Reset state
  state.lastCapture = now;
  state.messageCount = 0;

  // Save state
  require('fs').writeFileSync(STATE_FILE, JSON.stringify(state));
}
```

## Database Schema

```sql
CREATE TABLE journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    project TEXT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    tags TEXT
);

CREATE INDEX idx_created_at ON journal_entries(created_at);
CREATE INDEX idx_project ON journal_entries(project);
```

## Development

### Running Tests

```bash
pytest tests/
```

### Project Structure

```
claude-journal-mcp/
├── src/
│   └── claude_journal/
│       ├── __init__.py
│       ├── server.py      # MCP server
│       ├── database.py    # SQLite operations
│       └── time_parser.py # Natural language time parsing
├── tests/
├── pyproject.toml
└── README.md
```

## Why Not Embeddings?

**Embeddings/Semantic Search:**
- Pros: Find by meaning, not exact words
- Cons: 4GB+ dependencies, requires PyTorch/CUDA

**This Approach (SQLite Full-Text):**
- Pros: Lightweight (~10MB), instant queries, no ML deps
- Cons: Must use similar keywords to find entries

**Trade-off**: For a journal, exact keyword matching is usually sufficient. You remember rough terms like "auth", "bug", "deploy" better than abstract concepts.

## License

MIT

## Contributing

Pull requests welcome! Please ensure:
- Tests pass
- Code follows existing style
- Update README for new features
