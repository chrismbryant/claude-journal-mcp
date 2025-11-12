# Claude Journal - Claude Code Plugin

A lightweight journal/memory system for Claude Code with no ML dependencies. Uses simple SQLite for fast, local storage.

This is a full-featured Claude Code plugin with slash commands, skills, an agent, and auto-capture hooks.

## Features

- ✅ **Lightweight**: No embeddings, no ML models, just SQLite
- ✅ **Fast**: Sub-millisecond queries on local database
- ✅ **Smart Search**: Advanced search with ID lookup, tag filtering, exact phrases, date ranges, and keywords
- ✅ **Time Queries**: Natural language like "last month", "yesterday"
- ✅ **Project Tracking**: Organize entries by repository/project
- ✅ **Auto-Capture**: Automatic periodic journaling via hooks
- ✅ **Import/Export**: Share journal between instances
- ✅ **Flexible Tags**: Organize with custom tags
- ✅ **Slash Commands**: 6 user-friendly commands for common operations
- ✅ **Skills**: 3 proactive AI skills for context recovery and smart capture
- ✅ **Agent**: Optional journal assistant for enhanced workflows

## Requirements

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

### Quick Start (Recommended)

1. **Install uv** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Clone and install the plugin:**
```bash
git clone https://github.com/chrismbryant/claude-journal-mcp.git
cd claude-journal-mcp
uv sync
```

3. **Install as a Claude Code plugin:**
```bash
# Option A: Direct install from current directory
claude /plugin install .

# Option B: Add marketplace first, then install
claude /marketplace add ./marketplace.json
claude /plugin install claude-journal
```

This automatically:
- Configures the MCP server (provides all 11 journal tools)
- Registers 6 slash commands (/journal-add, /journal-search, etc.)
- Enables 3 proactive skills (journal-capture, context-recovery, find-related-work)
- Sets up auto-capture hooks (triggers every 30 min or 3 messages)
- Prompts you to enable the journal-assistant agent (opt-in)

### Alternative: Manual MCP Server Installation

If you prefer to install just the MCP server without the plugin features:

1. **Install dependencies:**
```bash
# With uv (recommended - faster)
uv sync

# Or with pip
pip install -e .
```

2. **Add to `~/.claude/config.json` or your project's `.mcp.json`:**
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

**Note:** Manual installation only provides MCP tools. You won't get slash commands, skills, or the agent without installing as a plugin.

## Database Location

Default: `~/.claude/journal.db`

Override with environment variable:
```bash
export JOURNAL_DB_PATH="/path/to/your/journal.db"
```

## Slash Commands

The plugin provides 6 slash commands for easy interaction:

### `/journal-add`
Interactively create a new journal entry. Claude guides you through:
- Title
- Description
- Project (auto-detected from git)
- Tags (suggested based on content)

```
You: /journal-add
Claude: Let's create a journal entry. What's the title?
You: Implemented rate limiting
Claude: Great! Tell me more about it...
```

### `/journal-search`
Search entries with advanced query syntax. Supports ID lookup, tag filtering, exact phrases, date ranges, and keywords.

```
You: /journal-search
Claude: What would you like to search for?
You: authentication
Claude: [Shows all auth-related entries]
```

**Advanced search syntax:**
- **ID search**: `42` or `id:42` - Find specific entry by ID
- **Tag filter**: `tag:bugfix` or `#bugfix` - Filter by tag
- **Exact phrase**: `"user authentication"` - Match exact phrase
- **Date range**: `last week authentication` - Combine time with search
- **Combined**: `tag:bugfix "login error" last month` - Mix multiple filters

### `/journal-recent`
Show recent entries to restore context (especially useful after `/clear`).

```
You: /clear
You: /journal-recent
Claude: Here's what you were working on:
[Lists recent entries with summaries]
```

### `/journal-time`
Query entries using natural language time expressions.

```
You: /journal-time
You: last week
Claude: [Shows all entries from last week]
```

Supports: "yesterday", "last month", "january 2024", "last 3 days", etc.

### `/journal-stats`
View statistics about your journal usage.

```
You: /journal-stats
Claude:
📊 247 entries across 5 projects
📅 Jan 15 - Jul 20, 2024 (6 months)
Most active: my-app (89 entries)
```

### `/journal-export`
Export your journal for backup or sharing between machines.

```
You: /journal-export
Claude: Where should I save the export?
You: ~/backups/journal_2024.db
Claude: ✅ Exported to ~/backups/journal_2024.db
```

## Skills

The plugin includes 3 proactive skills that Claude uses automatically:

### `journal-capture`
Automatically captures significant work when you:
- Complete features or tasks
- Fix complex bugs
- Make technical decisions
- Solve challenging problems

Claude recognizes important moments and captures them without being asked.

### `context-recovery`
Restores your working context from the journal:
- **Automatically** after `/clear` command
- When you ask "what was I working on?"
- At session start to resume past work

Brings back project context, recent changes, and next steps.

### `find-related-work`
Searches for past work related to current tasks:
- Before implementing similar features
- When making architecture decisions
- During troubleshooting
- When you explicitly ask about past work

Helps avoid reinventing solutions and maintains consistency.

## Agent

The plugin includes an **optional** Journal Assistant agent.

When you first use journal features, Claude will prompt:
```
Would you like to enable the Journal Assistant agent?

The agent helps by:
- Automatically capturing significant work
- Recovering context after /clear
- Finding related past work
- Suggesting when to journal

Enable now?
```

The agent is **opt-in** but recommended for the best experience.

## Available MCP Tools

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

**`journal_search`** - Advanced text search
```
Search examples:
- "authentication" - Keyword search
- "42" or "id:42" - Find entry by ID
- "tag:bugfix" or "#bugfix" - Filter by tag
- "\"user authentication\"" - Exact phrase match
- "last week authentication" - Date range + keyword
- "tag:bugfix \"login error\" performance" - Combined filters
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

## Auto-Capture Hook

The plugin includes an auto-capture hook that runs automatically when installed.

**How it works:**
- Monitors conversation activity
- Triggers every 30 minutes **or** when 3+ messages are sent (whichever comes first)
- Automatically creates journal entries via CLI
- Maintains state in `~/.claude/journal-capture-state.json`
- Auto-enabled on plugin installation

**Configuration:**

The hook is defined in `hooks/hooks.json` and automatically enabled:
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "node ${CLAUDE_PLUGIN_ROOT}/hooks/journal-auto-capture.js"
          }
        ]
      }
    ]
  }
}
```

**Behavior:**
- Runs on every user prompt submission
- Low overhead (checks timestamp and counter)
- When threshold reached (30 min or 3+ messages), prompts Claude to analyze the session
- Claude reviews the conversation and creates a meaningful journal entry with:
  - Goal (what we were trying to do)
  - Accomplishments (what was done)
  - Relevant tags and project information
- Claude can also proactively use journal tools to capture significant work at any time based on conversation context

## CLI Interface

The plugin includes a minimal CLI that provides information about available MCP tools:

```bash
python -m claude_journal.cli
# Or: claude-journal
```

All journal operations are performed through the MCP server, not via CLI commands. The auto-capture hook triggers Claude to create entries using the `journal_auto_capture` MCP tool.

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

### Contributing Changes

**Important:** The `main` branch is protected and requires pull requests.

```bash
# Create a feature branch
git checkout -b your-feature-name

# Make your changes and commit
git add .
git commit -m "Description of changes"

# Push your branch
git push -u origin your-feature-name

# Create a pull request
gh pr create --title "Your PR title" --body "Description"

# After CI passes, merge the PR
gh pr merge <PR-number> --squash --delete-branch
```

**Do not push directly to main** - all changes must go through pull requests.

### Project Structure

```
claude-journal-mcp/
├── .claude-plugin/
│   └── plugin.json         # Plugin manifest
├── agents/
│   └── journal-assistant.md # Journal assistant agent
├── commands/
│   ├── journal-add.md      # /journal-add command
│   ├── journal-export.md   # /journal-export command
│   ├── journal-recent.md   # /journal-recent command
│   ├── journal-search.md   # /journal-search command
│   ├── journal-stats.md    # /journal-stats command
│   └── journal-time.md     # /journal-time command
├── hooks/
│   ├── hooks.json          # Hook configuration
│   └── journal-auto-capture.js # Auto-capture hook
├── skills/
│   ├── journal-capture/
│   │   └── SKILL.md        # Proactive capture skill
│   ├── context-recovery/
│   │   └── SKILL.md        # Context recovery skill
│   └── find-related-work/
│       └── SKILL.md        # Related work finder skill
├── src/
│   └── claude_journal/
│       ├── __init__.py
│       ├── server.py       # MCP server
│       ├── database.py     # SQLite operations
│       └── time_parser.py  # Natural language time parsing
├── tests/
├── .mcp.json               # MCP server config
├── pyproject.toml
├── LICENSE
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
