#!/usr/bin/env python3
"""
Test script to verify database consolidation.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

def test_database_consolidation():
    """Test that all databases are properly consolidated."""
    
    print("🔍 Testing Database Consolidation...")
    print("=" * 50)
    
    # Check that all databases are in the correct location
    db_dir = Path(__file__).parent
    expected_dbs = [
        'filesystem_info.db',
        'tool_database.db', 
        'system_knowledge.db',
        'tools_knowledge.db',
        'user_interactions.db',
        'command_templates.db',
        'file_index.db',
        'training_user_interactions.db'
    ]
    
    print(f"📁 Database directory: {db_dir}")
    print()
    
    # Check each database
    all_good = True
    for db_name in expected_dbs:
        db_path = db_dir / db_name
        if db_path.exists():
            size_mb = db_path.stat().st_size / (1024 * 1024)
            print(f"✅ {db_name}: {size_mb:.2f}MB")
        else:
            print(f"❌ {db_name}: Missing")
            all_good = False
    
    print()
    
    # Test database connections
    print("🔌 Testing Database Connections...")
    print("-" * 30)
    
    try:
        # Test tool database
        from cli.db.tool_recommender_db import get_connection as get_tool_conn
        conn = get_tool_conn()
        conn.close()
        print("✅ Tool database connection: OK")
    except Exception as e:
        print(f"❌ Tool database connection: {e}")
        all_good = False
    
    try:
        # Test filesystem database (without numpy)
        from cli.db.filesystem_db import get_connection as get_fs_conn
        conn = get_fs_conn()
        conn.close()
        print("✅ Filesystem database connection: OK")
    except Exception as e:
        print(f"❌ Filesystem database connection: {e}")
        all_good = False
    
    print()
    
    if all_good:
        print("🎉 All databases are properly consolidated!")
        print("📊 Summary:")
        print(f"   - All {len(expected_dbs)} databases are in {db_dir}")
        print("   - Database connections are working")
        print("   - Ready for System Monitoring & Tool Recommendations")
    else:
        print("⚠️  Some issues found. Please check the errors above.")
    
    return all_good

if __name__ == "__main__":
    test_database_consolidation() 