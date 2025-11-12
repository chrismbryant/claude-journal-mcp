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
        """Search journal entries with advanced query syntax.

        Supports:
        - ID search: "42" or "id:42" returns entry with that ID
        - Tag filter: "tag:bugfix" or "#bugfix" filters by tag
        - Exact phrases: "\"user authentication\"" matches exact phrase
        - Date ranges: "last week", "yesterday", etc. combined with text
        - Keywords: regular text searches title, description, tags

        Args:
            query: Search query with optional special syntax
            project: Optional project filter
            limit: Maximum results to return

        Returns:
            List of matching entries
        """
        import re

        # Check for ID-only search (numeric or id:N)
        id_match = re.match(r'^(?:id:)?(\d+)$', query.strip(), re.IGNORECASE)
        if id_match:
            entry_id = int(id_match.group(1))
            cursor = self.conn.execute(
                "SELECT * FROM journal_entries WHERE id = ?",
                (entry_id,)
            )
            result = cursor.fetchone()
            return [dict(result)] if result else []

        # Parse query components
        tags_to_filter = []
        exact_phrases = []
        keywords = []
        time_expression = None

        # Extract tags (tag:name or #name)
        query = re.sub(
            r'(?:tag:(\w+)|#(\w+))',
            lambda m: (tags_to_filter.append(m.group(1) or m.group(2)), '')[1],
            query
        )

        # Extract exact phrases ("quoted text")
        query = re.sub(
            r'"([^"]+)"',
            lambda m: (exact_phrases.append(m.group(1)), '')[1],
            query
        )

        # Check for time expressions (last week, yesterday, etc.)
        time_keywords = [
            'yesterday', 'today', 'last week', 'last month', 'last year',
            'this week', 'this month', 'this year', 'last \\d+ days?',
            'last \\d+ weeks?', 'last \\d+ months?', 'january', 'february',
            'march', 'april', 'may', 'june', 'july', 'august', 'september',
            'october', 'november', 'december'
        ]
        time_pattern = '|'.join(time_keywords)
        time_match = re.search(rf'\b({time_pattern})\b(?:\s+(\d{{4}}))?', query, re.IGNORECASE)
        if time_match:
            time_expression = time_match.group(0).strip()
            query = query.replace(time_match.group(0), '')

        # Remaining text is keywords
        keywords = [k.strip() for k in query.split() if k.strip()]

        # Build SQL query
        sql = "SELECT * FROM journal_entries WHERE 1=1"
        params = []

        # Apply time range filter if time expression found
        if time_expression:
            try:
                from .time_parser import parse_time_expression
                start_date, end_date = parse_time_expression(time_expression)
                sql += " AND created_at BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            except:
                # If parsing fails, treat as keyword
                keywords.append(time_expression)

        # Apply tag filters
        for tag in tags_to_filter:
            sql += " AND (LOWER(tags) LIKE ? OR LOWER(tags) LIKE ? OR LOWER(tags) LIKE ? OR LOWER(tags) = ?)"
            tag_lower = tag.lower()
            params.extend([
                f"%,{tag_lower},%",  # middle of list
                f"{tag_lower},%",     # start of list
                f"%,{tag_lower}",     # end of list
                tag_lower             # only item
            ])

        # Apply exact phrase matches
        for phrase in exact_phrases:
            phrase_lower = f"%{phrase.lower()}%"
            sql += """ AND (
                LOWER(title) LIKE ? OR
                LOWER(description) LIKE ?
            )"""
            params.extend([phrase_lower, phrase_lower])

        # Apply keyword searches
        if keywords:
            keyword_conditions = []
            for keyword in keywords:
                keyword_lower = f"%{keyword.lower()}%"
                keyword_conditions.append("""(
                    LOWER(title) LIKE ? OR
                    LOWER(description) LIKE ? OR
                    LOWER(tags) LIKE ?
                )""")
                params.extend([keyword_lower, keyword_lower, keyword_lower])

            sql += " AND (" + " AND ".join(keyword_conditions) + ")"

        # Apply project filter
        if project:
            sql += " AND project = ?"
            params.append(project)

        # Order and limit
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
