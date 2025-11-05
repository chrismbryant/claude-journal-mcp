"""Tests for database operations."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from claude_journal.database import JournalDatabase


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    db = JournalDatabase(db_path)
    yield db

    db.close()
    Path(db_path).unlink()


@pytest.fixture
def populated_db(temp_db):
    """Create a database with sample data."""
    # Add entries for multiple projects
    temp_db.add_entry(
        title="Implemented OAuth2",
        description="Built OAuth2 flow with JWT tokens",
        project="my-app",
        tags=["auth", "security"]
    )

    temp_db.add_entry(
        title="Fixed cache memory leak",
        description="Cache wasn't clearing old entries",
        project="api-service",
        tags=["bugfix", "performance"]
    )

    temp_db.add_entry(
        title="Added rate limiting",
        description="Rate limiting with Redis backend",
        project="my-app",
        tags=["api", "redis"]
    )

    temp_db.add_entry(
        title="Database migration",
        description="Migrated from MySQL to PostgreSQL",
        project="api-service",
        tags=["database", "migration"]
    )

    temp_db.add_entry(
        title="Setup CI/CD pipeline",
        description="GitHub Actions for tests and deployment",
        project="my-app",
        tags=["ci", "deployment"]
    )

    return temp_db


class TestDatabaseInit:
    """Test database initialization."""

    def test_init_creates_database(self):
        """Test that database file is created."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        Path(db_path).unlink()  # Delete it first

        db = JournalDatabase(db_path)
        assert Path(db_path).exists()
        db.close()
        Path(db_path).unlink()

    def test_init_creates_tables(self, temp_db):
        """Test that tables are created."""
        cursor = temp_db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        assert "journal_entries" in tables

    def test_init_creates_indexes(self, temp_db):
        """Test that indexes are created."""
        cursor = temp_db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
        )
        indexes = [row[0] for row in cursor.fetchall()]
        assert "idx_created_at" in indexes
        assert "idx_project" in indexes


class TestAddEntry:
    """Test adding journal entries."""

    def test_add_entry_basic(self, temp_db):
        """Test adding a basic entry."""
        entry_id = temp_db.add_entry(
            title="Test entry",
            description="Test description"
        )
        assert entry_id > 0

    def test_add_entry_with_project(self, temp_db):
        """Test adding entry with project."""
        entry_id = temp_db.add_entry(
            title="Test entry",
            description="Test description",
            project="test-project"
        )

        entries = temp_db.list_recent(limit=1)
        assert entries[0]["project"] == "test-project"

    def test_add_entry_with_tags(self, temp_db):
        """Test adding entry with tags."""
        entry_id = temp_db.add_entry(
            title="Test entry",
            description="Test description",
            tags=["tag1", "tag2", "tag3"]
        )

        entries = temp_db.list_recent(limit=1)
        assert entries[0]["tags"] == "tag1,tag2,tag3"

    def test_add_entry_auto_timestamp(self, temp_db):
        """Test that timestamp is automatically set."""
        entry_id = temp_db.add_entry(
            title="Test entry",
            description="Test description"
        )

        entries = temp_db.list_recent(limit=1)
        assert entries[0]["created_at"] is not None

        # Parse and verify timestamp is recent
        created_at = datetime.fromisoformat(entries[0]["created_at"])
        now = datetime.now()
        assert abs((now - created_at).total_seconds()) < 5  # Within 5 seconds


class TestSearch:
    """Test search functionality."""

    def test_search_by_title(self, populated_db):
        """Test searching by title."""
        results = populated_db.search("OAuth2")
        assert len(results) == 1
        assert results[0]["title"] == "Implemented OAuth2"

    def test_search_by_description(self, populated_db):
        """Test searching by description."""
        results = populated_db.search("cache")
        assert len(results) == 1
        assert "cache" in results[0]["description"].lower()

    def test_search_by_tags(self, populated_db):
        """Test searching by tags."""
        results = populated_db.search("performance")
        assert len(results) == 1
        assert "performance" in results[0]["tags"]

    def test_search_case_insensitive(self, populated_db):
        """Test that search is case insensitive."""
        results1 = populated_db.search("OAUTH2")
        results2 = populated_db.search("oauth2")
        results3 = populated_db.search("OAuth2")

        assert len(results1) == len(results2) == len(results3) == 1

    def test_search_with_project_filter(self, populated_db):
        """Test searching with project filter."""
        results = populated_db.search("", project="my-app")
        assert len(results) == 3
        assert all(r["project"] == "my-app" for r in results)

    def test_search_with_limit(self, populated_db):
        """Test search limit."""
        results = populated_db.search("", limit=2)
        assert len(results) == 2

    def test_search_no_results(self, populated_db):
        """Test search with no matches."""
        results = populated_db.search("nonexistent query xyz")
        assert len(results) == 0


class TestTimeRange:
    """Test time range queries."""

    def test_get_by_time_range(self, populated_db):
        """Test getting entries by time range."""
        # Get all entries to find the actual time range
        all_entries = populated_db.list_recent(limit=10)

        # Get earliest and latest timestamps
        timestamps = [e["created_at"] for e in all_entries]
        start = min(timestamps)
        end = max(timestamps)

        results = populated_db.get_by_time_range(start, end)
        assert len(results) == 5  # All entries should be in range

    def test_get_by_time_range_with_query(self, populated_db):
        """Test time range with text query."""
        # Get all entries to find the actual time range
        all_entries = populated_db.list_recent(limit=10)
        timestamps = [e["created_at"] for e in all_entries]
        start = min(timestamps)
        end = max(timestamps)

        results = populated_db.get_by_time_range(start, end, query="OAuth2")
        assert len(results) == 1
        assert results[0]["title"] == "Implemented OAuth2"

    def test_get_by_time_range_with_project(self, populated_db):
        """Test time range with project filter."""
        # Get all entries to find the actual time range
        all_entries = populated_db.list_recent(limit=10)
        timestamps = [e["created_at"] for e in all_entries]
        start = min(timestamps)
        end = max(timestamps)

        results = populated_db.get_by_time_range(start, end, project="my-app")
        assert len(results) == 3
        assert all(r["project"] == "my-app" for r in results)


class TestListRecent:
    """Test listing recent entries."""

    def test_list_recent_default(self, populated_db):
        """Test listing recent entries with default limit."""
        results = populated_db.list_recent()
        assert len(results) == 5  # All entries (less than default 10)

    def test_list_recent_with_limit(self, populated_db):
        """Test listing with custom limit."""
        results = populated_db.list_recent(limit=3)
        assert len(results) == 3

    def test_list_recent_ordered(self, populated_db):
        """Test that results are ordered by most recent."""
        results = populated_db.list_recent()
        # Most recent should be "Setup CI/CD pipeline" (added last)
        assert results[0]["title"] == "Setup CI/CD pipeline"

    def test_list_recent_with_project(self, populated_db):
        """Test listing recent entries for specific project."""
        results = populated_db.list_recent(project="api-service")
        assert len(results) == 2
        assert all(r["project"] == "api-service" for r in results)


class TestProjects:
    """Test project-related functionality."""

    def test_list_projects(self, populated_db):
        """Test listing all projects."""
        results = populated_db.list_projects()
        assert len(results) == 2

        # Check projects are returned with counts
        projects = {r["project"]: r["count"] for r in results}
        assert projects["my-app"] == 3
        assert projects["api-service"] == 2

    def test_list_projects_ordered_by_count(self, populated_db):
        """Test that projects are ordered by entry count."""
        results = populated_db.list_projects()
        # my-app (3) should come before api-service (2)
        assert results[0]["project"] == "my-app"
        assert results[1]["project"] == "api-service"


class TestStats:
    """Test statistics functionality."""

    def test_get_stats(self, populated_db):
        """Test getting database statistics."""
        stats = populated_db.get_stats()

        assert stats["total_entries"] == 5
        assert stats["total_projects"] == 2
        assert stats["first_entry"] is not None
        assert stats["last_entry"] is not None
        assert len(stats["entries_per_project"]) == 2

    def test_stats_entries_per_project(self, populated_db):
        """Test entries per project in stats."""
        stats = populated_db.get_stats()

        projects = {p["project"]: p["count"] for p in stats["entries_per_project"]}
        assert projects["my-app"] == 3
        assert projects["api-service"] == 2


class TestDelete:
    """Test deletion functionality."""

    def test_delete_entry(self, populated_db):
        """Test deleting a specific entry."""
        entries = populated_db.list_recent(limit=1)
        entry_id = entries[0]["id"]

        result = populated_db.delete_entry(entry_id)
        assert result is True

        # Verify entry is gone
        remaining = populated_db.list_recent()
        assert len(remaining) == 4
        assert entry_id not in [e["id"] for e in remaining]

    def test_delete_entry_not_found(self, populated_db):
        """Test deleting non-existent entry."""
        result = populated_db.delete_entry(99999)
        assert result is False

    def test_delete_by_project(self, populated_db):
        """Test deleting all entries for a project."""
        count = populated_db.delete_by_project("my-app")
        assert count == 3

        # Verify entries are gone
        remaining = populated_db.list_recent()
        assert len(remaining) == 2
        assert all(e["project"] == "api-service" for e in remaining)

    def test_delete_by_project_not_found(self, populated_db):
        """Test deleting project that doesn't exist."""
        count = populated_db.delete_by_project("nonexistent-project")
        assert count == 0


class TestImportExport:
    """Test import/export functionality."""

    def test_export_to_db(self, populated_db):
        """Test exporting database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "export.db"
            result_path = populated_db.export_to_db(str(export_path))

            assert Path(result_path).exists()

            # Verify exported database has data
            exported_db = JournalDatabase(result_path)
            entries = exported_db.list_recent()
            assert len(entries) == 5
            exported_db.close()

    def test_export_auto_filename(self, populated_db):
        """Test export with auto-generated filename."""
        result_path = populated_db.export_to_db()

        assert Path(result_path).exists()
        assert "journal_export_" in result_path

        # Clean up
        Path(result_path).unlink()

    def test_import_from_db(self, populated_db):
        """Test importing from another database."""
        # Create a new empty database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            new_db_path = f.name

        new_db = JournalDatabase(new_db_path)

        # Export populated_db
        export_path = populated_db.export_to_db("test_export.db")

        # Import into empty new_db
        count = new_db.import_from_db(export_path)
        assert count == 5

        # Verify data was imported
        entries = new_db.list_recent()
        assert len(entries) == 5

        # Clean up
        new_db.close()
        Path(new_db_path).unlink()
        Path(export_path).unlink()

    def test_import_avoids_duplicates(self, populated_db):
        """Test that importing avoids duplicate entries."""
        # Export database
        export_path = populated_db.export_to_db("test_export.db")

        # Import into same database (should skip duplicates)
        count = populated_db.import_from_db(export_path)
        assert count == 0  # No new entries imported

        # Verify no duplicates
        entries = populated_db.list_recent()
        assert len(entries) == 5

        # Clean up
        Path(export_path).unlink()

    def test_import_nonexistent_file(self, temp_db):
        """Test importing from non-existent file."""
        with pytest.raises(FileNotFoundError):
            temp_db.import_from_db("/nonexistent/path/to/file.db")
