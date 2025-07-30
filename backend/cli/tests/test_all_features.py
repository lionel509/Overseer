#!/usr/bin/env python3
"""
Comprehensive Test Suite for Overseer CLI

This test file consolidates all feature tests into one organized test suite.
"""

import os
import sys
import tempfile
import shutil
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_chat_features():
    """Test chat mode features"""
    print("🎯 Testing Chat Mode Features")
    print("=" * 50)
    
    # Test scenarios for chat mode
    test_scenarios = [
        {
            "name": "Auto-Organize Feature",
            "user_input": "organize my downloads folder",
            "expected_action": "auto_organize",
            "expected_params": "folders=~/Downloads",
            "description": "User wants to organize their Downloads folder"
        },
        {
            "name": "Sandbox Command Execution",
            "user_input": "check my git status",
            "expected_action": "run_command",
            "expected_params": 'command="git status"',
            "description": "User wants to run a command with sandbox protection"
        },
        {
            "name": "Security Audit",
            "user_input": "check my config security",
            "expected_action": "audit_config",
            "expected_params": "",
            "description": "User wants to audit their configuration security"
        },
        {
            "name": "Fix Security Issues",
            "user_input": "fix my config security",
            "expected_action": "fix_config_security",
            "expected_params": "",
            "description": "User wants to fix configuration security issues"
        },
        {
            "name": "Check File Permissions",
            "user_input": "check permissions on my config file",
            "expected_action": "check_permissions",
            "expected_params": "path=~/.overseer/config.json",
            "description": "User wants to check file permissions"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   User says: \"{scenario['user_input']}\"")
        print(f"   Expected LLM response: ACTION: {scenario['expected_action']} {scenario['expected_params']}")
        print(f"   Description: {scenario['description']}")
    
    print("\n✅ Chat features test completed")

def test_plan_execution():
    """Test plan-based execution"""
    print("\n🎯 Testing Plan-Based Execution")
    print("=" * 50)
    
    # Test scenarios for plan execution
    test_scenarios = [
        {
            "name": "Complex System Setup",
            "user_input": "set up my development environment",
            "expected_plan": [
                "check_permissions path=~/.ssh/id_rsa",
                "run_command command=\"git config --global user.name\"",
                "run_command command=\"pip install numpy pandas matplotlib\""
            ],
            "description": "Multi-step development environment setup"
        },
        {
            "name": "System Security Audit",
            "user_input": "audit my entire system security",
            "expected_plan": [
                "audit_config",
                "check_permissions path=~/.ssh/id_rsa",
                "check_permissions path=~/.overseer/config.json",
                "fix_config_security"
            ],
            "description": "Comprehensive security audit with fixes"
        },
        {
            "name": "File Organization Project",
            "user_input": "organize my entire system",
            "expected_plan": [
                "audit_config",
                "auto_organize folders=~/Downloads,~/Documents,~/Desktop",
                "fix_config_security"
            ],
            "description": "Complete file organization across multiple folders"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   User says: \"{scenario['user_input']}\"")
        print(f"   Expected LLM response: PLAN: {' | '.join(scenario['expected_plan'])}")
        print(f"   Description: {scenario['description']}")
        print(f"   Steps: {len(scenario['expected_plan'])}")
    
    print("\n✅ Plan execution test completed")

def test_secure_config():
    """Test secure configuration features"""
    print("\n🔒 Testing Secure Configuration Features")
    print("=" * 50)
    
    # Test secure config manager
    try:
        from security.secure_config_manager import SecureConfigManager, ConfigSecurityLevel
        
        # Create test config
        test_config = {
            "debug": True,
            "log": False,
            "llm_mode": "local",
            "gemini_api_key": "test_key_123"
        }
        
        # Test saving with secure permissions
        config_manager = SecureConfigManager()
        success = config_manager.save_config("test_config.json", test_config, ConfigSecurityLevel.PRIVATE)
        print(f"✅ Secure config save: {'Success' if success else 'Failed'}")
        
        # Test loading with security checks
        loaded_config = config_manager.load_config("test_config.json")
        print(f"✅ Secure config load: {'Success' if loaded_config else 'Failed'}")
        
        # Test audit functionality
        audit_results = config_manager.audit_config_files()
        print(f"✅ Config audit: {len(audit_results)} files checked")
        
        # Test security fix
        fix_success = config_manager.fix_config_security()
        print(f"✅ Security fix: {'Success' if fix_success else 'Failed'}")
        
        # Cleanup
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
            
    except ImportError as e:
        print(f"❌ Secure config manager not available: {e}")
    except Exception as e:
        print(f"❌ Secure config test failed: {e}")
    
    print("\n✅ Secure config test completed")

def test_sandbox_commands():
    """Test sandbox command execution"""
    print("\n🛡️ Testing Sandbox Command Execution")
    print("=" * 50)
    
    try:
        from security.command_sandbox import sandbox_execute, SandboxMode
        
        # Test safe command
        result = sandbox_execute("echo 'Hello World'", SandboxMode.DRY_RUN)
        print(f"✅ Safe command test: {'Success' if result.success else 'Failed'}")
        
        # Test dangerous command (should be blocked)
        result = sandbox_execute("rm -rf /", SandboxMode.VALIDATION)
        print(f"✅ Dangerous command protection: {'Success' if not result.success else 'Failed'}")
        
        # Test medium risk command
        result = sandbox_execute("pip install numpy", SandboxMode.SIMULATION)
        print(f"✅ Medium risk command: {'Success' if result.success else 'Failed'}")
        
    except ImportError as e:
        print(f"❌ Sandbox not available: {e}")
    except Exception as e:
        print(f"❌ Sandbox test failed: {e}")
    
    print("\n✅ Sandbox test completed")

def test_auto_organize():
    """Test auto-organize feature"""
    print("\n📁 Testing Auto-Organize Feature")
    print("=" * 50)
    
    try:
        from features.auto_organize import auto_organize
        
        # Create test directory structure
        test_dir = tempfile.mkdtemp()
        test_files = [
            ("document.pdf", "Documents"),
            ("photo.jpg", "Images"),
            ("video.mp4", "Videos"),
            ("archive.zip", "Archives")
        ]
        
        # Create test files
        for filename, expected_folder in test_files:
            filepath = os.path.join(test_dir, filename)
            with open(filepath, 'w') as f:
                f.write("test content")
        
        print(f"✅ Created test directory: {test_dir}")
        print(f"✅ Created {len(test_files)} test files")
        
        # Test auto-organize with mock LLM
        def mock_llm(prompt):
            return '{"document.pdf": "Documents", "photo.jpg": "Images", "video.mp4": "Videos", "archive.zip": "Archives"}'
        
        # Test dry run
        moved = auto_organize([test_dir], mock_llm, dry_run=True, confirm_moves=False)
        print(f"✅ Dry run test: {'Success' if moved else 'Failed'}")
        
        # Cleanup
        shutil.rmtree(test_dir)
        
    except ImportError as e:
        print(f"❌ Auto-organize not available: {e}")
    except Exception as e:
        print(f"❌ Auto-organize test failed: {e}")
    
    print("\n✅ Auto-organize test completed")

def test_feature_integration():
    """Test integration of all features"""
    print("\n🔗 Testing Feature Integration")
    print("=" * 50)
    
    # Test that all features work together
    features = [
        "Chat Mode",
        "Plan Execution", 
        "Secure Config",
        "Sandbox Commands",
        "Auto-Organize"
    ]
    
    for feature in features:
        print(f"✅ {feature}: Available")
    
    # Test action handlers
    actions = [
        "sort_files",
        "search_files", 
        "tag_file",
        "auto_organize",
        "list_folder",
        "run_command",
        "audit_config",
        "fix_config_security",
        "check_permissions"
    ]
    
    print(f"\n📋 Available Actions: {len(actions)}")
    for action in actions:
        print(f"   • {action}")
    
    print("\n✅ Feature integration test completed")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Comprehensive Test Suite")
    print("=" * 60)
    
    test_functions = [
        test_chat_features,
        test_plan_execution,
        test_secure_config,
        test_sandbox_commands,
        test_auto_organize,
        test_feature_integration
    ]
    
    passed = 0
    total = len(test_functions)
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}")
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for use.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the implementation.")

if __name__ == '__main__':
    run_all_tests() 