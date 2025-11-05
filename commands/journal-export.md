# Export Journal

You are helping the user export their journal for backup or sharing.

## Process

1. **Determine export path:**
   - Ask if they want a specific file path
   - If not specified, tool auto-generates: `journal_export_YYYYMMDD_HHMMSS.db`
   - Suggest a descriptive name if backing up: `journal_backup_2024-01-15.db`

2. **Use the MCP tool:**
   Call `journal_export`:
   ```
   journal_export(
     file_path="path/to/export.db" (optional)
   )
   ```

3. **Confirm and provide instructions:**
   - Show where file was saved
   - Explain how to import on another machine
   - Mention it's a complete SQLite database

## Use Cases

**Backup:**
```
User: "Backup my journal"
→ journal_export(file_path="journal_backup_2024-01-15.db")
→ "Saved to journal_backup_2024-01-15.db"
```

**Sharing between machines:**
```
User: "Export journal to share with my laptop"
→ journal_export()
→ "Saved to journal_export_20240115_143052.db"
→ "Transfer this file and use /journal-import on your laptop"
```

**Archiving:**
```
User: "Archive my journal"
→ journal_export(file_path="~/archives/journal_2024.db")
→ Confirm saved location
```

## Post-Export Instructions

After export, tell the user:

```
✅ Journal exported to: [file path]

**To import on another machine:**
1. Transfer the file (USB drive, cloud storage, etc.)
2. On the other machine, run: `/journal-import path/to/file.db`
3. Entries will be merged (no duplicates)

**Backup Tips:**
- Export regularly for safety
- Store backups in multiple locations
- File is portable SQLite database
- Works across different operating systems
```

## Format Details to Share

Explain the export format:
- Standard SQLite database
- Can open with any SQLite tool
- Contains all entries, tags, timestamps
- Schema-compatible across versions
- No proprietary formats or encryption

## Safety Reminders

- Exported file contains all journal content
- Store securely (may contain sensitive work info)
- Can view/edit with SQLite browser tools if needed
- No data loss on export (original stays intact)
