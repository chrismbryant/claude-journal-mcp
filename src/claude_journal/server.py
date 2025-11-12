"""MCP server for Claude Journal."""

import asyncio
from typing import Optional, List
from mcp.server import Server
from mcp.types import Tool, TextContent
import json

from .database import JournalDatabase
from .time_parser import parse_time_expression


# Initialize database
db = JournalDatabase()

# Create MCP server
app = Server("claude-journal")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available journal tools."""
    return [
        Tool(
            name="journal_add",
            description="Add a new journal entry manually. Use when the user explicitly asks to save/remember something.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Brief title for the entry"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description (1-2 sentences)"
                    },
                    "project": {
                        "type": "string",
                        "description": "Optional project/repo name"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of tags"
                    }
                },
                "required": ["title", "description"]
            }
        ),
        Tool(
            name="journal_auto_capture",
            description="Automatically capture significant work. Use when substantial progress or decisions were made (context-based). Called by hooks every 30 minutes if activity occurred. Summarize the goal (what we were trying to do) and what was accomplished.",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Brief title summarizing what was accomplished"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description: the goal (what we were trying to do) and what was done (1-2 sentences)"
                    },
                    "project": {
                        "type": "string",
                        "description": "Optional project/repo name"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of tags"
                    }
                },
                "required": ["title", "description"]
            }
        ),
        Tool(
            name="journal_search",
            description="Search journal entries with advanced query syntax. Supports: ID search (\"42\" or \"id:42\"), tag filtering (\"tag:bugfix\" or \"#bugfix\"), exact phrases (\"\\\"user auth\\\"\"), date ranges (\"last week authentication\"), and keywords. All filters can be combined.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query with optional syntax: ID (42 or id:42), tags (tag:name or #name), exact phrases (\"phrase\"), time (last week, yesterday), keywords"
                    },
                    "project": {
                        "type": "string",
                        "description": "Optional project filter"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default: 20)",
                        "default": 20
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="journal_time_query",
            description="Find entries by time period. Supports natural language like 'last month', 'yesterday', 'january 2024', 'last 3 days'. Use when user asks 'what did I work on X time ago' or 'when did I do X'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_expression": {
                        "type": "string",
                        "description": "Time period (e.g., 'last week', 'yesterday', 'january')"
                    },
                    "query": {
                        "type": "string",
                        "description": "Optional text filter within time range"
                    },
                    "project": {
                        "type": "string",
                        "description": "Optional project filter"
                    }
                },
                "required": ["time_expression"]
            }
        ),
        Tool(
            name="journal_list_recent",
            description="Get most recent journal entries. Useful for remembering recent work after context cleared.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of entries (default: 10)",
                        "default": 10
                    },
                    "project": {
                        "type": "string",
                        "description": "Optional project filter"
                    }
                }
            }
        ),
        Tool(
            name="journal_list_projects",
            description="List all projects with entry counts. Useful for seeing what projects we've worked on.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="journal_stats",
            description="Get journal statistics including total entries, date ranges, and per-project counts.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="journal_delete",
            description="Delete a specific journal entry by ID. Use when user asks to forget something specific.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {
                        "type": "integer",
                        "description": "ID of the entry to delete"
                    }
                },
                "required": ["entry_id"]
            }
        ),
        Tool(
            name="journal_delete_by_project",
            description="Delete all entries for a specific project. Use with caution.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name"
                    }
                },
                "required": ["project"]
            }
        ),
        Tool(
            name="journal_import",
            description="Import entries from another journal database file. Merges with existing entries (avoids duplicates).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to source database file"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="journal_export",
            description="Export journal to a SQLite database file for sharing or backup.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Optional destination path (default: journal_export_TIMESTAMP.db)"
                    }
                }
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls."""

    try:
        if name == "journal_add":
            entry_id = db.add_entry(
                title=arguments["title"],
                description=arguments["description"],
                project=arguments.get("project"),
                tags=arguments.get("tags")
            )
            return [TextContent(
                type="text",
                text=f"✅ Journal entry created (ID: {entry_id})"
            )]

        elif name == "journal_auto_capture":
            entry_id = db.add_entry(
                title=arguments["title"],
                description=arguments["description"],
                project=arguments.get("project"),
                tags=["auto-capture"] + (arguments.get("tags") or [])
            )
            return [TextContent(
                type="text",
                text=f"📝 Auto-captured to journal (ID: {entry_id})"
            )]

        elif name == "journal_search":
            results = db.search(
                query=arguments["query"],
                project=arguments.get("project"),
                limit=arguments.get("limit", 20)
            )

            if not results:
                return [TextContent(
                    type="text",
                    text=f"No entries found matching '{arguments['query']}'"
                )]

            formatted = format_entries(results)
            return [TextContent(type="text", text=formatted)]

        elif name == "journal_time_query":
            start_date, end_date = parse_time_expression(arguments["time_expression"])

            results = db.get_by_time_range(
                start_date=start_date,
                end_date=end_date,
                query=arguments.get("query"),
                project=arguments.get("project")
            )

            if not results:
                return [TextContent(
                    type="text",
                    text=f"No entries found for '{arguments['time_expression']}'"
                )]

            formatted = format_entries(results, show_time=arguments["time_expression"])
            return [TextContent(type="text", text=formatted)]

        elif name == "journal_list_recent":
            results = db.list_recent(
                limit=arguments.get("limit", 10),
                project=arguments.get("project")
            )

            if not results:
                return [TextContent(
                    type="text",
                    text="No journal entries found"
                )]

            formatted = format_entries(results)
            return [TextContent(type="text", text=formatted)]

        elif name == "journal_list_projects":
            projects = db.list_projects()

            if not projects:
                return [TextContent(
                    type="text",
                    text="No projects found in journal"
                )]

            formatted = "**Projects:**\n\n"
            for p in projects:
                formatted += f"- {p['project']}: {p['count']} entries\n"

            return [TextContent(type="text", text=formatted)]

        elif name == "journal_stats":
            stats = db.get_stats()

            formatted = f"""**Journal Statistics:**

Total Entries: {stats['total_entries']}
First Entry: {stats['first_entry'] or 'N/A'}
Last Entry: {stats['last_entry'] or 'N/A'}
Total Projects: {stats['total_projects']}

**Entries per Project:**
"""
            if stats['entries_per_project']:
                for p in stats['entries_per_project']:
                    formatted += f"- {p['project']}: {p['count']}\n"
            else:
                formatted += "No projects tracked\n"

            return [TextContent(type="text", text=formatted)]

        elif name == "journal_delete":
            deleted = db.delete_entry(arguments["entry_id"])

            if deleted:
                return [TextContent(
                    type="text",
                    text=f"✅ Deleted journal entry {arguments['entry_id']}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ Entry {arguments['entry_id']} not found"
                )]

        elif name == "journal_delete_by_project":
            count = db.delete_by_project(arguments["project"])

            return [TextContent(
                type="text",
                text=f"✅ Deleted {count} entries for project '{arguments['project']}'"
            )]

        elif name == "journal_import":
            imported = db.import_from_db(arguments["file_path"])

            return [TextContent(
                type="text",
                text=f"✅ Imported {imported} new entries from {arguments['file_path']}"
            )]

        elif name == "journal_export":
            file_path = db.export_to_db(arguments.get("file_path"))

            return [TextContent(
                type="text",
                text=f"✅ Exported journal to {file_path}"
            )]

        else:
            return [TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Error: {str(e)}"
        )]


def format_entries(entries: List[dict], show_time: Optional[str] = None) -> str:
    """Format journal entries for display."""
    header = f"**Journal Entries"
    if show_time:
        header += f" ({show_time})"
    header += f":** ({len(entries)} found)\n\n"

    formatted = header

    for entry in entries:
        formatted += f"**[{entry['id']}]** {entry['title']}\n"
        formatted += f"📅 {entry['created_at']}"

        if entry['project']:
            formatted += f" | 📁 {entry['project']}"

        if entry['tags']:
            formatted += f" | 🏷️ {entry['tags']}"

        formatted += f"\n{entry['description']}\n\n"

    return formatted


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
