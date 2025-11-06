"""CLI interface for Claude Journal MCP.

Provides command-line access to journal operations, primarily for hooks.
"""

import sys
import argparse
from claude_journal.database import JournalDatabase


def auto_capture():
    """Auto-capture from conversation context.

    This is called by hooks and creates a simple timestamped entry.
    For detailed entries, use the MCP tool journal_auto_capture instead.
    """
    db = JournalDatabase()

    # Get current project from git if available
    project = None
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        if result.returncode == 0:
            import os
            project = os.path.basename(result.stdout.strip())
    except Exception:
        pass

    # Create a simple auto-capture entry
    db.add_entry(
        title="Auto-captured session activity",
        description="Automatically captured conversation activity. Review and update with more details if needed.",
        project=project,
        tags=["auto-capture"]
    )

    db.close()
    print("✓ Auto-captured session activity to journal")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Journal CLI",
        prog="claude-journal"
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # auto-capture command
    subparsers.add_parser(
        'auto-capture',
        help='Auto-capture current session (called by hooks)'
    )

    args = parser.parse_args()

    if args.command == 'auto-capture':
        auto_capture()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
