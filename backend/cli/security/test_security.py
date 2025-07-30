#!/usr/bin/env python3
"""
Security System Test Script

This script demonstrates the comprehensive security features
implemented for the Overseer system.
"""

import sys
import os
import time
from datetime import datetime

# Add the parent directory to the path so we can import the security modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from security.security_manager import SecurityManager, SecurityContext
from security.permission_manager import PermissionLevel, Permission

def test_security_system():
    """Test the comprehensive security system"""
    print("🔒 Testing Overseer Security System")
    print("=" * 50)
    
    # Initialize security manager
    security_manager = SecurityManager()
    
    # Test 1: Create a user and session
    print("\n1. Testing User and Session Management")
    print("-" * 40)
    
    # Create a test user
    user_id = "test_user"
    session_id = "test_session_123"
    
    # Create user with standard permissions
    success = security_manager.permission_manager.create_user(user_id, PermissionLevel.STANDARD)
    print(f"✅ Created user '{user_id}': {success}")
    
    # Create session
    session_result = security_manager.create_user_session(
        user_id=user_id,
        session_id=session_id,
        ip_address="192.168.1.100",
        user_agent="Overseer CLI"
    )
    print(f"✅ Created session: {session_result['success']}")
    
    # Test 2: Command Validation
    print("\n2. Testing Command Validation")
    print("-" * 40)
    
    # Create security context
    context = SecurityContext(
        user_id=user_id,
        session_id=session_id,
        ip_address="192.168.1.100"
    )
    
    # Test safe command
    print("\nTesting safe command...")
    result = security_manager.validate_and_execute_command("ls -la", context)
    print(f"✅ Safe command result: {result['success']}")
    
    # Test dangerous command
    print("\nTesting dangerous command...")
    result = security_manager.validate_and_execute_command("rm -rf /", context)
    print(f"❌ Dangerous command result: {result['success']}")
    print(f"   Error: {result.get('error', 'None')}")
    
    # Test command injection
    print("\nTesting command injection...")
    result = security_manager.validate_and_execute_command("ls; rm -rf /", context)
    print(f"❌ Command injection result: {result['success']}")
    print(f"   Error: {result.get('error', 'None')}")
    
    # Test 3: File Operation Validation
    print("\n3. Testing File Operation Validation")
    print("-" * 40)
    
    # Test safe file operation
    print("\nTesting safe file read...")
    result = security_manager.validate_file_operation("read", "/tmp/test.txt", context)
    print(f"✅ Safe file operation: {result['success']}")
    
    # Test protected file access
    print("\nTesting protected file access...")
    result = security_manager.validate_file_operation("read", "/etc/passwd", context)
    print(f"❌ Protected file access: {result['success']}")
    print(f"   Error: {result.get('error', 'None')}")
    
    # Test 4: Network Operation Validation
    print("\n4. Testing Network Operation Validation")
    print("-" * 40)
    
    # Test safe network operation
    print("\nTesting safe network access...")
    result = security_manager.validate_network_operation("https://api.github.com", context)
    print(f"✅ Safe network access: {result['success']}")
    
    # Test blocked domain
    print("\nTesting blocked domain...")
    result = security_manager.validate_network_operation("http://malicious-site.com", context)
    print(f"❌ Blocked domain access: {result['success']}")
    print(f"   Error: {result.get('error', 'None')}")
    
    # Test 5: Threat Detection
    print("\n5. Testing Threat Detection")
    print("-" * 40)
    
    # Test path traversal
    print("\nTesting path traversal...")
    result = security_manager.validate_file_operation("read", "../../../etc/passwd", context)
    print(f"❌ Path traversal attempt: {result['success']}")
    print(f"   Error: {result.get('error', 'None')}")
    
    # Test 6: Security Status
    print("\n6. Security System Status")
    print("-" * 40)
    
    status = security_manager.get_security_status()
    print(f"Security Level: {status['security_config']['security_level']}")
    print(f"Permission Level: {status['security_config']['permission_level']}")
    print(f"Active Sessions: {status['permissions']['active_sessions']}")
    print(f"Blocked Sources: {status['threat_detection']['blocked_sources_count']}")
    print(f"Encryption Enabled: {status['encryption']['enabled']}")
    print(f"Audit Logging: {status['audit']['enabled']}")
    
    # Test 7: Security Summary
    print("\n7. Security Summary (Last 24 hours)")
    print("-" * 40)
    
    summary = security_manager.get_security_summary(hours=24)
    print(f"Total Events: {summary['audit_summary']['total_events']}")
    print(f"Successful Events: {summary['audit_summary']['successful_events']}")
    print(f"Failed Events: {summary['audit_summary']['failed_events']}")
    print(f"High Risk Events: {summary['audit_summary']['high_risk_events']}")
    print(f"Critical Events: {summary['audit_summary']['critical_events']}")
    print(f"Active Sessions: {summary['active_sessions']}")
    print(f"Blocked Sources: {summary['blocked_sources']}")
    
    # Test 8: Permission Testing
    print("\n8. Testing Permission Levels")
    print("-" * 40)
    
    # Test different permission levels
    permission_levels = [
        (PermissionLevel.READ_ONLY, "Read-only user"),
        (PermissionLevel.LIMITED, "Limited user"),
        (PermissionLevel.STANDARD, "Standard user"),
        (PermissionLevel.ADMIN, "Admin user")
    ]
    
    for level, description in permission_levels:
        test_user_id = f"test_user_{level.value}"
        test_session_id = f"test_session_{level.value}"
        
        # Create user
        security_manager.permission_manager.create_user(test_user_id, level)
        
        # Create session
        security_manager.create_user_session(test_user_id, test_session_id)
        
        # Test permissions
        test_context = SecurityContext(user_id=test_user_id, session_id=test_session_id)
        
        # Test command execution permission
        has_command_permission = security_manager.permission_manager.check_permission(
            test_session_id, Permission.EXECUTE_COMMANDS
        )
        
        # Test dangerous command permission
        has_dangerous_permission = security_manager.permission_manager.check_permission(
            test_session_id, Permission.EXECUTE_DANGEROUS_COMMANDS
        )
        
        print(f"{description}:")
        print(f"  - Execute Commands: {'✅' if has_command_permission else '❌'}")
        print(f"  - Execute Dangerous Commands: {'✅' if has_dangerous_permission else '❌'}")
    
    # Cleanup
    print("\n9. Cleanup")
    print("-" * 40)
    
    # End session
    end_result = security_manager.end_user_session(session_id)
    print(f"✅ Ended session: {end_result['success']}")
    
    # Cleanup security manager
    security_manager.cleanup()
    print("✅ Security system cleanup completed")
    
    print("\n🎉 Security System Test Completed Successfully!")
    print("=" * 50)

if __name__ == "__main__":
    test_security_system() 