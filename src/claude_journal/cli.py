"""CLI interface for Claude Journal MCP.

Currently, all journal operations are performed through the MCP server.
This CLI module is reserved for future command-line utilities if needed.
"""

import sys
import argparse


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Journal CLI",
        prog="claude-journal"
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    args = parser.parse_args()

    if args.command:
        print(f"Unknown command: {args.command}")
        sys.exit(1)
    else:
        print("Claude Journal")
        print("")
        print("All journal operations are performed through the MCP server.")
        print("Use the MCP tools from Claude Code instead of this CLI.")
        print("")
        print("Available MCP tools:")
        print("  - journal_add: Add a new entry")
        print("  - journal_auto_capture: Auto-capture session activity")
        print("  - journal_search: Search entries")
        print("  - journal_time_query: Query by time period")
        print("  - journal_list_recent: List recent entries")
        print("  - journal_stats: View statistics")
        print("  - journal_export/import: Export/import journal")
        sys.exit(0)


if __name__ == '__main__':
    main()
