"""SQLite database operations for journal entries."""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import os


class JournalDatabase:
    """Manages journal entries in SQLite database."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file.
                    Defaults to ~/.claude/journal.db
        """
        if db_path is None:
            db_path = os.path.expanduser("~/.claude/journal.db")

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_database()

    def _init_database(self):
        """Create tables and indexes if they don't exist."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                project TEXT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                tags TEXT
            )
        """)

        # Create indexes for better query performance
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at
            ON journal_entries(created_at)
        """)

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_project
            ON journal_entries(project)
        """)

        self.conn.commit()

    def add_entry(
        self,
        title: str,
        description: str,
        project: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        """Add a new journal entry.

        Args:
            title: Brief title for the entry
            description: Detailed description (1-2 sentences)
            project: Optional project/repo name
            tags: Optional list of tags

        Returns:
            ID of the created entry
        """
        tags_str = ",".join(tags) if tags else None

        cursor = self.conn.execute("""
            INSERT INTO journal_entries (project, title, description, tags)
            VALUES (?, ?, ?, ?)
        """, (project, title, description, tags_str))

        self.conn.commit()
        return cursor.lastrowid

    def search(
        self,
        query: str,
        project: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search journal entries by text.

        Args:
            query: Search query (searches title, description, tags)
            project: Optional project filter
            limit: Maximum results to return

        Returns:
            List of matching entries
        """
        query_lower = f"%{query.lower()}%"

        sql = """
            SELECT * FROM journal_entries
            WHERE (
                LOWER(title) LIKE ? OR
                LOWER(description) LIKE ? OR
                LOWER(tags) LIKE ?
            )
        """
        params = [query_lower, query_lower, query_lower]

        if project:
            sql += " AND project = ?"
            params.append(project)

        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_by_time_range(
        self,
        start_date: str,
        end_date: str,
        query: Optional[str] = None,
        project: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get entries within a time range.

        Args:
            start_date: ISO format start date
            end_date: ISO format end date
            query: Optional text search within time range
            project: Optional project filter

        Returns:
            List of entries in time range
        """
        sql = """
            SELECT * FROM journal_entries
            WHERE created_at BETWEEN ? AND ?
        """
        params = [start_date, end_date]

        if query:
            query_lower = f"%{query.lower()}%"
            sql += """ AND (
                LOWER(title) LIKE ? OR
                LOWER(description) LIKE ? OR
                LOWER(tags) LIKE ?
            )"""
            params.extend([query_lower, query_lower, query_lower])

        if project:
            sql += " AND project = ?"
            params.append(project)

        sql += " ORDER BY created_at DESC"

        cursor = self.conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def list_recent(
        self,
        limit: int = 10,
        project: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get most recent journal entries.

        Args:
            limit: Number of entries to return
            project: Optional project filter

        Returns:
            List of recent entries
        """
        sql = "SELECT * FROM journal_entries"
        params = []

        if project:
            sql += " WHERE project = ?"
            params.append(project)

        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def list_projects(self) -> List[Dict[str, Any]]:
        """Get all projects with entry counts.

        Returns:
            List of {project, count} dicts
        """
        cursor = self.conn.execute("""
            SELECT
                project,
                COUNT(*) as count
            FROM journal_entries
            WHERE project IS NOT NULL
            GROUP BY project
            ORDER BY count DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics.

        Returns:
            Dict with total entries, date range, projects
        """
        cursor = self.conn.execute("""
            SELECT
                COUNT(*) as total_entries,
                MIN(created_at) as first_entry,
                MAX(created_at) as last_entry,
                COUNT(DISTINCT project) as total_projects
            FROM journal_entries
        """)

        stats = dict(cursor.fetchone())

        # Get entries per project
        cursor = self.conn.execute("""
            SELECT project, COUNT(*) as count
            FROM journal_entries
            WHERE project IS NOT NULL
            GROUP BY project
        """)
        stats['entries_per_project'] = [dict(row) for row in cursor.fetchall()]

        return stats

    def delete_entry(self, entry_id: int) -> bool:
        """Delete a specific journal entry.

        Args:
            entry_id: ID of entry to delete

        Returns:
            True if entry was deleted, False if not found
        """
        cursor = self.conn.execute("""
            DELETE FROM journal_entries WHERE id = ?
        """, (entry_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_by_project(self, project: str) -> int:
        """Delete all entries for a project.

        Args:
            project: Project name

        Returns:
            Number of entries deleted
        """
        cursor = self.conn.execute("""
            DELETE FROM journal_entries WHERE project = ?
        """, (project,))
        self.conn.commit()
        return cursor.rowcount

    def import_from_db(self, source_db_path: str) -> int:
        """Import entries from another journal database.

        Args:
            source_db_path: Path to source database file

        Returns:
            Number of entries imported
        """
        source_path = Path(source_db_path).expanduser()
        if not source_path.exists():
            raise FileNotFoundError(f"Source database not found: {source_path}")

        # Attach source database
        self.conn.execute(f"ATTACH DATABASE ? AS source", (str(source_path),))

        # Import entries (avoiding duplicates by checking if exact match exists)
        cursor = self.conn.execute("""
            INSERT INTO journal_entries (created_at, project, title, description, tags)
            SELECT created_at, project, title, description, tags
            FROM source.journal_entries
            WHERE NOT EXISTS (
                SELECT 1 FROM journal_entries
                WHERE journal_entries.created_at = source.journal_entries.created_at
                AND journal_entries.title = source.journal_entries.title
                AND journal_entries.description = source.journal_entries.description
            )
        """)

        imported = cursor.rowcount
        self.conn.commit()

        # Detach source database
        self.conn.execute("DETACH DATABASE source")

        return imported

    def export_to_db(self, dest_db_path: Optional[str] = None) -> str:
        """Export journal to a new database file.

        Args:
            dest_db_path: Destination path.
                         Defaults to journal_export_{timestamp}.db

        Returns:
            Path to exported database
        """
        if dest_db_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_db_path = f"journal_export_{timestamp}.db"

        dest_path = Path(dest_db_path).expanduser()

        # Create backup using SQLite backup API
        backup_conn = sqlite3.connect(str(dest_path))
        self.conn.backup(backup_conn)
        backup_conn.close()

        return str(dest_path)

    def close(self):
        """Close database connection."""
        self.conn.close()
