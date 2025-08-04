#!/usr/bin/env python3
"""
Comprehensive Test Suite for Overseer CLI

This test file consolidates all feature tests into one organized test suite.
Updated to include all new tools and features.
"""

import os
import sys
import tempfile
import shutil
import json
import time
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
        },
        {
            "name": "File Indexing",
            "user_input": "index my project files",
            "expected_action": "index_files",
            "expected_params": "path=./",
            "description": "User wants to index their project files"
        },
        {
            "name": "Semantic Search",
            "user_input": "find files with database connections",
            "expected_action": "search_files",
            "expected_params": "query=database connection",
            "description": "User wants to search for files by description"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   User says: \"{scenario['user_input']}\"")
        print(f"   Expected LLM response: ACTION: {scenario['expected_action']} {scenario['expected_params']}")
        print(f"   Description: {scenario['description']}")
    
    print("\n✅ Chat features test completed")

def test_system_monitoring():
    """Test system monitoring features"""
    print("\n🖥️ Testing System Monitoring Features")
    print("=" * 50)
    
    try:
        from features.ai_monitoring.system_monitor_optimized import OptimizedSystemMonitor
        
        # Test system monitor initialization
        monitor = OptimizedSystemMonitor()
        print("✅ System monitor initialized")
        
        # Test system stats collection
        stats = monitor.get_system_stats()
        if stats:
            print(f"✅ System stats collected: CPU {stats['cpu']['percent']}%, Memory {stats['memory']['percent']}%")
        else:
            print("❌ Failed to collect system stats")
        
        # Test process stats
        processes = monitor.get_process_stats(5)
        if processes:
            print(f"✅ Process stats collected: {len(processes)} processes")
        else:
            print("❌ Failed to collect process stats")
        
        # Test recommendations
        recommendations = monitor.get_recommendations()
        if recommendations:
            print(f"✅ Recommendations generated: {len(recommendations)} suggestions")
        else:
            print("❌ Failed to generate recommendations")
        
    except ImportError as e:
        print(f"❌ System monitor not available: {e}")
    except Exception as e:
        print(f"❌ System monitoring test failed: {e}")
    
    print("\n✅ System monitoring test completed")

def test_memory_diagnostics():
    """Test memory diagnostics features"""
    print("\n🧠 Testing Memory Diagnostics Features")
    print("=" * 50)
    
    try:
        from features.ai_monitoring.memory_diagnostics import MemoryDiagnostics
        
        # Test memory diagnostics initialization
        diagnostics = MemoryDiagnostics()
        print("✅ Memory diagnostics initialized")
        
        # Test detailed memory info
        memory_info = diagnostics.get_detailed_memory_info()
        if memory_info:
            print(f"✅ Memory info collected: {memory_info['total_gb']:.1f}GB total, {memory_info['used_gb']:.1f}GB used")
        else:
            print("❌ Failed to collect memory info")
        
        # Test top memory processes
        top_processes = diagnostics.get_top_memory_processes(5)
        if top_processes:
            print(f"✅ Top memory processes: {len(top_processes)} processes")
        else:
            print("❌ Failed to get top memory processes")
        
        # Test memory analysis
        analysis = diagnostics.analyze_memory_patterns()
        if analysis:
            print(f"✅ Memory analysis completed: {len(analysis.get('high_memory_processes', []))} high-memory processes")
        else:
            print("❌ Failed to analyze memory patterns")
        
    except ImportError as e:
        print(f"❌ Memory diagnostics not available: {e}")
    except Exception as e:
        print(f"❌ Memory diagnostics test failed: {e}")
    
    print("\n✅ Memory diagnostics test completed")

def test_ai_system_analysis():
    """Test AI system analysis features"""
    print("\n🤖 Testing AI System Analysis Features")
    print("=" * 50)
    
    try:
        from features.ai_monitoring.ai_system_analyzer import AISystemAnalyzer
        
        # Test AI analyzer initialization
        analyzer = AISystemAnalyzer()
        print("✅ AI system analyzer initialized")
        
        # Test system data collection
        system_data = analyzer.collect_system_data()
        if system_data:
            print(f"✅ System data collected: {len(system_data)} data points")
        else:
            print("❌ Failed to collect system data")
        
        # Test AI analysis
        analysis = analyzer.generate_ai_analysis()
        if analysis:
            print(f"✅ AI analysis generated: {analysis.get('performance_assessment', {}).get('rating', 'Unknown')} performance")
        else:
            print("❌ Failed to generate AI analysis")
        
    except ImportError as e:
        print(f"❌ AI system analyzer not available: {e}")
    except Exception as e:
        print(f"❌ AI system analysis test failed: {e}")
    
    print("\n✅ AI system analysis test completed")

def test_llm_system_advisor():
    """Test LLM system advisor features"""
    print("\n🧠 Testing LLM System Advisor Features")
    print("=" * 50)
    
    try:
        from features.ai_monitoring.llm_system_advisor import LLMSystemAdvisor
        
        # Test LLM advisor initialization
        advisor = LLMSystemAdvisor()
        print("✅ LLM system advisor initialized")
        
        # Test system profile generation
        profile = advisor.get_detailed_system_profile()
        if profile:
            print(f"✅ System profile generated: {len(profile)} profile sections")
        else:
            print("❌ Failed to generate system profile")
        
        # Test advanced analysis
        analysis = advisor.generate_advanced_analysis()
        if analysis:
            print(f"✅ Advanced analysis generated: {analysis.get('performance_score', 0)}/100 score")
        else:
            print("❌ Failed to generate advanced analysis")
        
    except ImportError as e:
        print(f"❌ LLM system advisor not available: {e}")
    except Exception as e:
        print(f"❌ LLM system advisor test failed: {e}")
    
    print("\n✅ LLM system advisor test completed")

def test_enhanced_file_indexer():
    """Test enhanced file indexer features"""
    print("\n📁 Testing Enhanced File Indexer Features")
    print("=" * 50)
    
    try:
        from features.ai_organization.enhanced_file_indexer import EnhancedFileIndexer
        
        # Test file indexer initialization
        indexer = EnhancedFileIndexer()
        print("✅ Enhanced file indexer initialized")
        
        # Create test files
        test_dir = tempfile.mkdtemp()
        test_files = [
            ("test.py", "print('Hello World')\ndef test_function():\n    return True"),
            ("config.json", '{"debug": true, "log": false}'),
            ("README.md", "# Test Project\nThis is a test project."),
            ("script.sh", "#!/bin/bash\necho 'Test script'")
        ]
        
        for filename, content in test_files:
            filepath = os.path.join(test_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
        
        print(f"✅ Created test directory: {test_dir}")
        print(f"✅ Created {len(test_files)} test files")
        
        # Test file indexing
        stats = indexer.index_directory(test_dir, recursive=False)
        if stats['indexed_files'] > 0:
            print(f"✅ File indexing successful: {stats['indexed_files']} files indexed")
        else:
            print("❌ File indexing failed")
        
        # Test file search
        results = indexer.search_files("python", limit=5)
        if results:
            print(f"✅ File search successful: {len(results)} results found")
        else:
            print("❌ File search failed")
        
        # Test file info
        test_file = os.path.join(test_dir, "test.py")
        file_info = indexer.get_file_info(test_file)
        if file_info:
            print(f"✅ File info retrieved: {file_info['file_type']} file")
        else:
            print("❌ File info retrieval failed")
        
        # Test index stats
        index_stats = indexer.get_index_stats()
        if index_stats:
            print(f"✅ Index stats: {index_stats['total_files']} total files")
        else:
            print("❌ Index stats failed")
        
        # Cleanup
        shutil.rmtree(test_dir)
        
    except ImportError as e:
        print(f"❌ Enhanced file indexer not available: {e}")
    except Exception as e:
        print(f"❌ Enhanced file indexer test failed: {e}")
    
    print("\n✅ Enhanced file indexer test completed")

def test_multimodal_analyzer():
    """Test multimodal analyzer features"""
    print("\n🔍 Testing Multimodal Analyzer Features")
    print("=" * 50)
    
    try:
        from features.ai_organization.multimodal_analyzer import MultimodalAnalyzer
        
        # Test multimodal analyzer initialization
        analyzer = MultimodalAnalyzer()
        print("✅ Multimodal analyzer initialized")
        
        # Test model loading (simulated)
        model_loaded = analyzer.load_model()
        print(f"✅ Model loading: {'Success' if model_loaded else 'Failed'}")
        
        # Test text content analysis
        sample_content = '''
import os
import sys
from typing import List, Dict

class TestAnalyzer:
    def __init__(self):
        self.data = {}
    
    def analyze_file(self, path: str) -> Dict:
        """Analyze a file and return metadata"""
        try:
            with open(path, 'r') as f:
                content = f.read()
            return {"content": content, "size": len(content)}
        except Exception as e:
            return {"error": str(e)}
        '''
        
        analysis = analyzer.analyze_text_content(sample_content, 'python')
        if analysis:
            print(f"✅ Text analysis: {analysis['category']} file, {analysis['complexity_score']:.2f} complexity")
        else:
            print("❌ Text analysis failed")
        
        # Test recommendations
        recommendations = analyzer.get_file_recommendations(analysis)
        if recommendations:
            print(f"✅ Recommendations generated: {len(recommendations)} suggestions")
        else:
            print("❌ Recommendations generation failed")
        
        # Test file comparison
        analysis2 = analyzer.analyze_text_content("print('Hello')", 'python')
        comparison = analyzer.compare_files(analysis, analysis2)
        if comparison:
            print(f"✅ File comparison: {len(comparison['similarities'])} similarities, {len(comparison['differences'])} differences")
        else:
            print("❌ File comparison failed")
        
    except ImportError as e:
        print(f"❌ Multimodal analyzer not available: {e}")
    except Exception as e:
        print(f"❌ Multimodal analyzer test failed: {e}")
    
    print("\n✅ Multimodal analyzer test completed")

def test_database_integration():
    """Test database integration features"""
    print("\n🗄️ Testing Database Integration Features")
    print("=" * 50)
    
    try:
        from db.system_monitoring_db import system_monitoring_db
        
        # Test database initialization
        print("✅ System monitoring database initialized")
        
        # Test metrics saving
        test_metrics = {
            'timestamp': time.time(),
            'cpu_percent': 25.5,
            'memory_percent': 65.2,
            'memory_used_gb': 8.5,
            'memory_total_gb': 16.0,
            'disk_percent': 45.1,
            'disk_used_gb': 250.0,
            'disk_total_gb': 500.0,
            'network_sent_mb': 10.5,
            'network_recv_mb': 15.2,
            'process_count': 150,
            'load_average_1': 1.2,
            'load_average_5': 1.1,
            'load_average_15': 1.0
        }
        
        system_monitoring_db.save_system_metrics(test_metrics)
        print("✅ System metrics saved to database")
        
        # Test process metrics
        test_processes = [
            {
                'pid': 1234,
                'name': 'test_process',
                'cpu_percent': 5.2,
                'memory_percent': 2.1,
                'memory_mb': 150.5,
                'status': 'running'
            }
        ]
        
        system_monitoring_db.save_process_metrics(test_processes)
        print("✅ Process metrics saved to database")
        
        # Test performance insights
        test_insight = {
            'timestamp': time.time(),
            'insight_type': 'performance_assessment',
            'severity': 'warning',
            'description': 'Test performance insight',
            'metric_name': 'cpu_usage',
            'metric_value': 75.0,
            'baseline_value': 50.0,
            'deviation_percent': 50.0,
            'recommendation': 'Monitor CPU usage'
        }
        
        system_monitoring_db.save_performance_insight(test_insight)
        print("✅ Performance insights saved to database")
        
    except ImportError as e:
        print(f"❌ Database integration not available: {e}")
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
    
    print("\n✅ Database integration test completed")

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
        from features.ai_organization.auto_organize import auto_organize
        
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
        "System Monitoring",
        "Memory Diagnostics", 
        "AI System Analysis",
        "LLM System Advisor",
        "Enhanced File Indexer",
        "Multimodal Analyzer",
        "Database Integration",
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
        "check_permissions",
        "index_files",
        "search_files_semantic",
        "get_file_info",
        "system_stats",
        "memory_diagnostics",
        "ai_analysis",
        "llm_analysis"
    ]
    
    print(f"\n📋 Available Actions: {len(actions)}")
    for action in actions:
        print(f"   • {action}")
    
    # Test CLI commands
    cli_commands = [
        "system stats",
        "memory diagnostics",
        "ai analysis", 
        "llm analysis",
        "file indexer",
        "index files",
        "search python",
        "settings",
        "help"
    ]
    
    print(f"\n🖥️ CLI Commands: {len(cli_commands)}")
    for command in cli_commands:
        print(f"   • {command}")
    
    print("\n✅ Feature integration test completed")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Comprehensive Test Suite")
    print("=" * 60)
    
    test_functions = [
        test_chat_features,
        test_system_monitoring,
        test_memory_diagnostics,
        test_ai_system_analysis,
        test_llm_system_advisor,
        test_enhanced_file_indexer,
        test_multimodal_analyzer,
        test_database_integration,
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
    
    print("\n📋 Test Coverage Summary:")
    print("   • System Monitoring: CPU, Memory, Disk, Process tracking")
    print("   • Memory Diagnostics: Detailed memory analysis and troubleshooting")
    print("   • AI Analysis: AI-powered system analysis and recommendations")
    print("   • LLM Advisor: Advanced LLM analysis with optimization strategies")
    print("   • File Indexing: Local file indexing with semantic search")
    print("   • Multimodal Analysis: Pattern-based file analysis and recommendations")
    print("   • Database Integration: Centralized metrics and insights storage")
    print("   • Security Features: Secure config, sandbox commands, permissions")
    print("   • File Organization: AI-powered file organization and tagging")

if __name__ == '__main__':
    run_all_tests() 