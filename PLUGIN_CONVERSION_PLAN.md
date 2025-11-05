# Claude Journal MCP → Full Plugin Conversion Plan

## Current State

**What we have:**
```
claude-journal-mcp/
├── src/claude_journal/
│   ├── __init__.py
│   ├── server.py          # MCP server with 11 tools
│   ├── database.py        # SQLite operations
│   └── time_parser.py     # Natural language time parsing
├── hooks/
│   ├── journal-auto-capture.js
│   └── README.md
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

**What we need to add:**
- `.claude-plugin/plugin.json` - Plugin manifest
- `commands/` - Slash commands (5-6 commands)
- `agents/` - Specialized journal agent (optional)
- `hooks/hooks.json` - Formal hooks configuration
- `.mcp.json` - MCP server configuration
- Update README for plugin installation

---

## Target Directory Structure

```
claude-journal-mcp/
├── .claude-plugin/
│   └── plugin.json                    # Plugin manifest (NEW)
├── src/claude_journal/
│   ├── __init__.py
│   ├── server.py
│   ├── database.py
│   └── time_parser.py
├── commands/                          # NEW DIRECTORY
│   ├── journal-add.md
│   ├── journal-search.md
│   ├── journal-recent.md
│   ├── journal-time.md
│   ├── journal-stats.md
│   └── journal-export.md
├── agents/                            # NEW DIRECTORY (optional)
│   └── journal-assistant.md
├── hooks/
│   ├── hooks.json                     # NEW - formalized config
│   ├── journal-auto-capture.js
│   └── README.md
├── .mcp.json                          # NEW - MCP config
├── pyproject.toml
├── README.md                          # UPDATE for plugin
├── LICENSE
└── .gitignore
```

---

## Component Details

### 1. Plugin Manifest (`.claude-plugin/plugin.json`)

**Purpose:** Makes plugin discoverable and installable via `/plugin`

**Content:**
```json
{
  "name": "claude-journal",
  "displayName": "Claude Journal",
  "description": "Lightweight journal/memory system with zero ML dependencies. SQLite-based with natural language time queries and auto-capture.",
  "version": "0.1.0",
  "author": "Chris Bryant",
  "homepage": "https://github.com/chrismbryant/claude-journal-mcp",
  "repository": {
    "type": "git",
    "url": "https://github.com/chrismbryant/claude-journal-mcp"
  },
  "keywords": [
    "journal",
    "memory",
    "sqlite",
    "mcp",
    "lightweight",
    "no-ml"
  ],
  "license": "MIT"
}
```

---

### 2. Slash Commands (`commands/`)

#### **`journal-add.md`**
Quick entry creation without calling tool directly.

```markdown
You are helping the user add a journal entry.

Ask them for:
- Title (brief)
- Description (1-2 sentences)
- Project (optional, default to current directory if in a repo)
- Tags (optional)

Then use the `journal_add` MCP tool to save the entry.
```

#### **`journal-search.md`**
Search journal entries.

```markdown
You are helping the user search their journal.

Ask for search query and optional project filter, then use the `journal_search` MCP tool.

Show results in a readable format with IDs for reference.
```

#### **`journal-recent.md`**
Show recent entries (context recovery).

```markdown
Show the user their recent journal entries to restore context after `/clear`.

Use the `journal_list_recent` MCP tool with limit=10 (or ask how many they want).

Present entries chronologically with key details highlighted.
```

#### **`journal-time.md`**
Time-based queries.

```markdown
You are helping the user query journal entries by time.

Examples:
- "What did I work on last week?"
- "Show me entries from January"
- "When did I implement feature X?"

Use the `journal_time_query` MCP tool with natural language time expressions.
```

#### **`journal-stats.md`**
Show journal statistics.

```markdown
Display journal statistics and insights using the `journal_stats` MCP tool.

Show:
- Total entries
- Date range (first to last entry)
- Projects with entry counts
- Suggest using journal_list_projects for detailed project view
```

#### **`journal-export.md`**
Export journal for backup/sharing.

```markdown
You are helping the user export their journal.

Use the `journal_export` MCP tool.

If no path specified, it will auto-generate: journal_export_YYYYMMDD_HHMMSS.db

Remind them they can import this on another machine with journal_import.
```

---

### 3. Journal Assistant Agent (`agents/journal-assistant.md`)

**Purpose:** Specialized agent for automatic journaling and context management

```markdown
# Journal Assistant Agent

You are the Journal Assistant, specialized in managing the user's development journal.

## Capabilities

1. **Auto-Capture**: Detect when significant work has been done and suggest saving it
2. **Context Recovery**: When user returns after `/clear`, proactively offer recent entries
3. **Smart Tagging**: Suggest relevant tags based on conversation content
4. **Pattern Recognition**: Identify recurring tasks/projects and suggest organization

## When to Activate

- User mentions "remember this"
- After completing implementation work
- When user asks "what was I working on?"
- After 30+ minutes of active development

## Tools Available

Use these MCP tools:
- journal_add - Save entries
- journal_auto_capture - Auto-save summaries
- journal_search - Find past work
- journal_time_query - Time-based search
- journal_list_recent - Recent entries
- journal_stats - Get overview

## Behavior Guidelines

- Be proactive but not intrusive
- Suggest tags based on technical terms used
- Always confirm before auto-capturing (unless triggered by hook)
- When user asks about past work, search comprehensively
- Format results clearly with IDs for easy reference
```

---

### 4. Formal Hooks Config (`hooks/hooks.json`)

**Purpose:** Standardized hooks configuration for the plugin

```json
{
  "UserPromptSubmit": [
    {
      "matchers": ["*"],
      "hooks": [
        {
          "type": "command",
          "command": "node hooks/journal-auto-capture.js",
          "timeout": 5,
          "description": "Auto-capture journal entries every 30 minutes when active"
        }
      ]
    }
  ]
}
```

**Note:** Users can optionally enable this by copying to `~/.claude/hooks/hooks.json`

---

### 5. MCP Server Config (`.mcp.json`)

**Purpose:** Define how the MCP server connects to the plugin

```json
{
  "mcpServers": {
    "journal": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "claude_journal.server"],
      "description": "Claude Journal MCP server - lightweight SQLite-based memory system"
    }
  }
}
```

**Note:** This gets merged into user's `.claude.json` when plugin is installed

---

### 6. Updated README.md

**Changes needed:**

1. **Add "Plugin Installation" section at top:**
```markdown
## Installation

### As a Plugin (Recommended)

Install via Claude Code's plugin system:

\`\`\`bash
/plugin install claude-journal
\`\`\`

This automatically:
- Installs the Python package
- Configures the MCP server
- Makes slash commands available
- Sets up hooks (optional)

### Manual Installation

\`\`\`bash
git clone https://github.com/chrismbryant/claude-journal-mcp.git
cd claude-journal-mcp
pip install -e .
claude mcp add journal python -- -m claude_journal.server
\`\`\`
```

2. **Add "Slash Commands" section:**
```markdown
## Slash Commands

Quick access to journal features:

- `/journal-add` - Create new entry interactively
- `/journal-search` - Search your journal
- `/journal-recent` - View recent entries (great after /clear)
- `/journal-time` - Query by time ("last week", etc.)
- `/journal-stats` - Show journal statistics
- `/journal-export` - Export journal for backup/sharing
```

3. **Add "Journal Assistant Agent" section:**
```markdown
## Journal Assistant Agent

The plugin includes a specialized agent that:
- Proactively suggests capturing important work
- Helps recover context after clearing conversation
- Recommends relevant tags
- Recognizes patterns in your workflow

The agent activates automatically when needed but stays unobtrusive.
```

---

## Implementation Order

### Phase 1: Core Plugin Structure
1. ✅ Create `.claude-plugin/` directory
2. ✅ Write `plugin.json` manifest
3. ✅ Create `.mcp.json` configuration
4. ✅ Update `.gitignore` if needed

### Phase 2: Slash Commands
5. ✅ Create `commands/` directory
6. ✅ Write all 6 command markdown files
7. ✅ Test each command individually

### Phase 3: Formal Hooks
8. ✅ Create `hooks/hooks.json`
9. ✅ Update `hooks/README.md` to reference hooks.json
10. ✅ Keep existing JS implementation

### Phase 4: Agent (Optional)
11. ✅ Create `agents/` directory
12. ✅ Write `journal-assistant.md`
13. ✅ Test agent activation

### Phase 5: Documentation
14. ✅ Update main README.md
15. ✅ Add CHANGELOG.md entry
16. ✅ Update installation instructions

### Phase 6: Testing & Release
17. ✅ Test plugin installation locally
18. ✅ Test all slash commands
19. ✅ Test MCP tools still work
20. ✅ Test hooks functionality
21. ✅ Commit and push to GitHub
22. ✅ Tag release as v0.1.0

---

## Testing Strategy

### Local Plugin Testing

1. **Install plugin locally:**
```bash
cd ~/claude-journal-mcp
/plugin install --local .
```

2. **Test slash commands:**
```bash
/journal-add
/journal-search
/journal-recent
/journal-time
/journal-stats
/journal-export
```

3. **Test MCP tools directly:**
```bash
# In Claude Code conversation
Use journal_add tool to create entry
Use journal_search to find it
```

4. **Test hooks:**
```bash
# Send 3+ messages over 30 minutes
# Verify auto-capture triggers
```

5. **Test agent:**
```bash
# Clear context: /clear
# Agent should offer recent entries
```

---

## Breaking Changes

**None** - This is purely additive:
- Existing MCP server functionality unchanged
- All 11 tools work exactly the same
- Database schema unchanged
- Hook behavior unchanged
- Only adds plugin structure around existing code

---

## User Migration Path

**Existing users** (installed manually):
1. Can continue using as-is (no changes needed)
2. Or reinstall as plugin: `/plugin install claude-journal`
3. Database at `~/.claude/journal.db` remains unchanged
4. All existing entries preserved

**New users**:
- Just use `/plugin install claude-journal`
- Everything configured automatically

---

## Open Questions

1. **Agent Behavior**: Should the agent be proactive by default, or require user opt-in?
   - **Recommendation**: Start conservative (opt-in via command)

2. **Auto-Capture Hook**: Install automatically with plugin, or require manual setup?
   - **Recommendation**: Document but don't auto-enable (let user choose)

3. **Command Naming**: Use `journal-*` prefix or just `journal` with subcommands?
   - **Recommendation**: Keep `journal-*` for clarity and discoverability

4. **Version Management**: Start at 0.1.0 or 1.0.0?
   - **Recommendation**: 0.1.0 (signals "working but early")

---

## Success Criteria

✅ Plugin discoverable via `/plugin` menu
✅ One-command installation works
✅ All slash commands functional
✅ MCP tools accessible from commands and directly
✅ Hooks work as documented
✅ Agent provides helpful context recovery
✅ Documentation clear for both plugin and manual install
✅ Zero breaking changes to existing functionality
✅ Database and entries fully backward compatible

---

## Estimated Effort

- **Phase 1-2**: 30 minutes (structure + commands)
- **Phase 3**: 10 minutes (hooks formalization)
- **Phase 4**: 20 minutes (agent)
- **Phase 5**: 20 minutes (docs)
- **Phase 6**: 30 minutes (testing)

**Total**: ~2 hours

---

## Next Steps

1. Review this plan
2. Approve or request changes
3. Begin implementation in phases
4. Test after each phase
5. Release as v0.1.0

