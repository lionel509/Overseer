# Overseer Database Directory

This directory contains all database files for the Overseer system. All databases have been consolidated here for better organization and management.

## Database Files

| Database | Purpose | Size |
|----------|---------|------|
| `filesystem_info.db` | File system indexing and metadata | 6.11MB |
| `tool_database.db` | Tool recommendations and installations | 0.01MB |
| `system_knowledge.db` | System-specific knowledge base | 0.01MB |
| `tools_knowledge.db` | Tools knowledge and documentation | 0.01MB |
| `user_interactions.db` | User interaction history | 0.01MB |
| `command_templates.db` | Command templates and corrections | 0.01MB |
| `file_index.db` | File indexing and search | 0.01MB |
| `training_user_interactions.db` | Training data for ML models | 0.01MB |

## Database Consolidation Status

✅ **All databases consolidated** - All database files are now located in this directory
✅ **Path references updated** - All code references point to the correct locations
✅ **Connection tests passing** - Database connections are working properly
✅ **Ready for System Monitoring** - Infrastructure ready for new monitoring features

## Database Access

### From CLI modules:
```python
# Tool database
from cli.db.tool_recommender_db import get_connection
conn = get_connection()

# Filesystem database  
from cli.db.filesystem_db import get_connection
conn = get_connection()
```

### From Core modules:
```python
# System databases
from core.db_init import get_conn
conn, cursor = get_conn('system_knowledge.db')
```

## Testing

Run the consolidation test:
```bash
cd backend/db
python3 test_database_consolidation.py
```

## Next Steps

With databases properly consolidated, we can now build:

1. **System Monitoring Infrastructure**
   - Real-time metrics collection
   - Performance monitoring
   - Resource tracking

2. **Enhanced Tool Recommendations**
   - Context-aware suggestions
   - Performance-based recommendations
   - Learning from user behavior

3. **Alerting System**
   - Threshold-based alerts
   - Proactive notifications
   - Custom alert rules

## Notes

- The `filesystem_info.db` is the largest database (6.11MB) containing indexed file metadata
- All other databases are currently minimal size and will grow as the system is used
- Database encryption is available but disabled by default for easier development
- All databases use SQLite for simplicity and portability 