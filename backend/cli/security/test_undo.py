#!/usr/bin/env python3
"""
Undo System Test Script

This script demonstrates the comprehensive undo functionality
for the Overseer system.
"""

import sys
import os
import time
import tempfile
from datetime import datetime

# Add the parent directory to the path so we can import the security modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from security.undo_manager import UndoManager, UndoType

def test_undo_system():
    """Test the comprehensive undo system"""
    print("🔄 Testing Overseer Undo System")
    print("=" * 50)
    
    # Initialize undo manager
    undo_manager = UndoManager()
    
    # Test 1: Command Execution Recording
    print("\n1. Testing Command Execution Recording")
    print("-" * 40)
    
    # Record some command executions
    operation_id1 = undo_manager.record_command_execution(
        command="ls -la",
        result="Command executed successfully",
        user_id="test_user",
        session_id="test_session"
    )
    print(f"✅ Recorded command execution: {operation_id1}")
    
    operation_id2 = undo_manager.record_command_execution(
        command="mkdir test_folder",
        result="Directory created",
        user_id="test_user",
        session_id="test_session"
    )
    print(f"✅ Recorded command execution: {operation_id2}")
    
    # Test 2: File Operation Recording
    print("\n2. Testing File Operation Recording")
    print("-" * 40)
    
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Test content for undo system")
        temp_file_path = f.name
    
    print(f"📁 Created temporary file: {temp_file_path}")
    
    # Record file operation
    file_op_id = undo_manager.record_file_operation(
        operation="modify",
        file_path=temp_file_path,
        user_id="test_user",
        session_id="test_session"
    )
    print(f"✅ Recorded file operation: {file_op_id}")
    
    # Test 3: Directory Operation Recording
    print("\n3. Testing Directory Operation Recording")
    print("-" * 40)
    
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Created temporary directory: {temp_dir}")
    
    # Record directory operation
    dir_op_id = undo_manager.record_directory_operation(
        operation="create",
        dir_path=temp_dir,
        user_id="test_user",
        session_id="test_session"
    )
    print(f"✅ Recorded directory operation: {dir_op_id}")
    
    # Test 4: Permission Change Recording
    print("\n4. Testing Permission Change Recording")
    print("-" * 40)
    
    # Record permission change
    perm_op_id = undo_manager.record_permission_change(
        file_path=temp_file_path,
        old_permissions="644",
        new_permissions="755",
        user_id="test_user",
        session_id="test_session"
    )
    print(f"✅ Recorded permission change: {perm_op_id}")
    
    # Test 5: Configuration Change Recording
    print("\n5. Testing Configuration Change Recording")
    print("-" * 40)
    
    # Record configuration change
    config_op_id = undo_manager.record_configuration_change(
        config_key="debug_mode",
        old_value="false",
        new_value="true",
        user_id="test_user",
        session_id="test_session"
    )
    print(f"✅ Recorded configuration change: {config_op_id}")
    
    # Test 6: List Undoable Operations
    print("\n6. Listing Undoable Operations")
    print("-" * 40)
    
    operations = undo_manager.list_undoable_operations(hours=24)
    print(f"📋 Found {len(operations)} undoable operations:")
    
    for i, op in enumerate(operations[:5], 1):  # Show first 5
        timestamp = datetime.fromtimestamp(op['timestamp']).strftime('%H:%M:%S')
        print(f"  {i}. [{timestamp}] {op['description']} (ID: {op['operation_id'][:8]}...)")
    
    # Test 7: Undo Operations
    print("\n7. Testing Undo Operations")
    print("-" * 40)
    
    # Undo the last operation (configuration change)
    print("🔄 Undoing last operation (configuration change)...")
    result = undo_manager.undo_operation(config_op_id)
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   Message: {result['message']}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Undo file operation
    print("\n🔄 Undoing file operation...")
    result = undo_manager.undo_operation(file_op_id)
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   Message: {result['message']}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Undo directory operation
    print("\n🔄 Undoing directory operation...")
    result = undo_manager.undo_operation(dir_op_id)
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   Message: {result['message']}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Undo permission change
    print("\n🔄 Undoing permission change...")
    result = undo_manager.undo_operation(perm_op_id)
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   Message: {result['message']}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Undo command execution
    print("\n🔄 Undoing command execution...")
    result = undo_manager.undo_operation(operation_id1)
    print(f"   Result: {result['success']}")
    if result['success']:
        print(f"   Message: {result['message']}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Test 8: Undo Summary
    print("\n8. Undo System Summary")
    print("-" * 40)
    
    summary = undo_manager.get_undo_summary(hours=24)
    print(f"📊 Total operations: {summary['total_operations']}")
    print(f"📊 Operations by type: {summary['operations_by_type']}")
    print(f"📊 Operations by user: {summary['operations_by_user']}")
    
    # Test 9: Cleanup
    print("\n9. Cleanup")
    print("-" * 40)
    
    # Clean up temporary files
    try:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"🗑️  Removed temporary file: {temp_file_path}")
    except Exception as e:
        print(f"⚠️  Could not remove temporary file: {e}")
    
    try:
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
            print(f"🗑️  Removed temporary directory: {temp_dir}")
    except Exception as e:
        print(f"⚠️  Could not remove temporary directory: {e}")
    
    # Clean up old operations
    removed_count = undo_manager.cleanup_old_operations(days=1)
    print(f"🧹 Cleaned up {removed_count} old operations")
    
    print("\n🎉 Undo System Test Completed Successfully!")
    print("=" * 50)

if __name__ == "__main__":
    test_undo_system() 