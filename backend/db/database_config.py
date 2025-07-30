"""
Centralized database configuration for Overseer.
All database files are stored in this directory.
"""

import os
from pathlib import Path

# Base directory for all databases
DB_DIR = Path(__file__).parent

# Database file paths
DATABASES = {
    'filesystem_info': DB_DIR / 'filesystem_info.db',
    'tool_database': DB_DIR / 'tool_database.db',
    'system_knowledge': DB_DIR / 'system_knowledge.db',
    'tools_knowledge': DB_DIR / 'tools_knowledge.db',
    'user_interactions': DB_DIR / 'user_interactions.db',
    'command_templates': DB_DIR / 'command_templates.db',
    'file_index': DB_DIR / 'file_index.db',
    'training_user_interactions': DB_DIR / 'training_user_interactions.db',
}

def get_db_path(db_name: str) -> Path:
    """Get the full path for a database by name."""
    if db_name not in DATABASES:
        raise ValueError(f"Unknown database: {db_name}. Available: {list(DATABASES.keys())}")
    return DATABASES[db_name]

def get_db_connection(db_name: str):
    """Get a database connection for the specified database."""
    import sqlite3
    db_path = get_db_path(db_name)
    return sqlite3.connect(str(db_path))

def ensure_db_directory():
    """Ensure the database directory exists."""
    DB_DIR.mkdir(parents=True, exist_ok=True)

def list_all_databases():
    """List all configured databases and their status."""
    results = {}
    for name, path in DATABASES.items():
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        results[name] = {
            'path': str(path),
            'exists': exists,
            'size_bytes': size,
            'size_mb': round(size / (1024 * 1024), 2)
        }
    return results

def get_database_summary():
    """Get a summary of all databases."""
    dbs = list_all_databases()
    summary = []
    for name, info in dbs.items():
        status = "✅" if info['exists'] else "❌"
        size = f"{info['size_mb']}MB" if info['size_mb'] > 0 else "0MB"
        summary.append(f"{status} {name}: {size}")
    return '\n'.join(summary) 