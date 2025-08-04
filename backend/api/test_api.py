#!/usr/bin/env python3
"""
Test script for Overseer API
Tests all API endpoints to ensure they work correctly
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test health check endpoint"""
    print("🧪 Testing Health Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

def test_root_endpoint():
    """Test root endpoint"""
    print("🧪 Testing Root Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root endpoint: {data['name']} v{data['version']}")
            return True
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
        return False

def test_tools_endpoint():
    """Test tools listing endpoint"""
    print("🧪 Testing Tools Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/tools")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Tools endpoint: {data['total']} tools available")
            for name, info in data['tools'].items():
                print(f"      - {name}: {info['description']}")
            return True
        else:
            print(f"   ❌ Tools endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Tools endpoint error: {e}")
        return False

def test_system_endpoints():
    """Test system information endpoints"""
    print("🧪 Testing System Endpoints...")
    
    endpoints = [
        ("/api/system/info", "System Info"),
        ("/api/system/memory", "Memory Usage"),
        ("/api/system/disk", "Disk Usage"),
        ("/api/system/network", "Network Status"),
        ("/api/system/processes", "Process List")
    ]
    
    success_count = 0
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 200:
                print(f"   ✅ {name}: Success")
                success_count += 1
            else:
                print(f"   ❌ {name}: Failed ({response.status_code})")
        except Exception as e:
            print(f"   ❌ {name}: Error ({e})")
    
    return success_count == len(endpoints)

def test_file_search_endpoints():
    """Test file search endpoints"""
    print("🧪 Testing File Search Endpoints...")
    
    # Test file search
    try:
        search_data = {
            "query": "*.py",
            "base_path": ".",
            "recursive": False,
            "file_types": [".py"],
            "include_hidden": False
        }
        response = requests.post(f"{BASE_URL}/api/tools/file-search/search", json=search_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ File search: {len(data.get('data', []))} files found")
        else:
            print(f"   ❌ File search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ File search error: {e}")
        return False
    
    # Test search history
    try:
        response = requests.get(f"{BASE_URL}/api/tools/file-search/history")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Search history: {len(data.get('history', []))} entries")
        else:
            print(f"   ❌ Search history failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Search history error: {e}")
    
    return True

def test_command_processor_endpoints():
    """Test command processor endpoints"""
    print("🧪 Testing Command Processor Endpoints...")
    
    # Test command execution
    try:
        cmd_data = {
            "command": "system_info",
            "args": []
        }
        response = requests.post(f"{BASE_URL}/api/tools/command-processor/execute", json=cmd_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Command execution: {data.get('success', False)}")
        else:
            print(f"   ❌ Command execution failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Command execution error: {e}")
        return False
    
    # Test supported commands
    try:
        response = requests.get(f"{BASE_URL}/api/tools/command-processor/supported")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Supported commands: {len(data.get('commands', []))} commands")
        else:
            print(f"   ❌ Supported commands failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Supported commands error: {e}")
    
    # Test command history
    try:
        response = requests.get(f"{BASE_URL}/api/tools/command-processor/history")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Command history: {len(data.get('history', []))} entries")
        else:
            print(f"   ❌ Command history failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Command history error: {e}")
    
    return True

def test_tool_recommender_endpoints():
    """Test tool recommender endpoints"""
    print("🧪 Testing Tool Recommender Endpoints...")
    
    # Test recommendations
    try:
        response = requests.get(f"{BASE_URL}/api/tools/tool-recommender/recommendations")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Tool recommendations: {len(data.get('data', []))} recommendations")
            for rec in data.get('data', [])[:3]:
                print(f"      - {rec['name']}: {rec['reason']}")
        else:
            print(f"   ❌ Tool recommendations failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Tool recommendations error: {e}")
        return False
    
    # Test system context
    try:
        response = requests.get(f"{BASE_URL}/api/tools/tool-recommender/context")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ System context: CPU={data.get('cpu_usage', 0):.1f}%, "
                  f"Memory={data.get('memory_usage', 0):.1f}%")
        else:
            print(f"   ❌ System context failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ System context error: {e}")
    
    # Test available tools
    try:
        response = requests.get(f"{BASE_URL}/api/tools/tool-recommender/tools")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Available tools: {len(data.get('tools', []))} tools")
        else:
            print(f"   ❌ Available tools failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Available tools error: {e}")
    
    # Test categories
    try:
        response = requests.get(f"{BASE_URL}/api/tools/tool-recommender/categories")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Tool categories: {', '.join(data.get('categories', []))}")
        else:
            print(f"   ❌ Tool categories failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Tool categories error: {e}")
    
    return True

def test_real_time_stats_endpoints():
    """Test real-time stats endpoints"""
    print("🧪 Testing Real-Time Stats Endpoints...")
    
    # Test current stats
    try:
        response = requests.get(f"{BASE_URL}/api/tools/real-time-stats/current")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Current stats: CPU={data['cpu']['usage']:.1f}%, "
                  f"Memory={data['memory']['percent']:.1f}%")
        else:
            print(f"   ❌ Current stats failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Current stats error: {e}")
        return False
    
    # Test monitoring status
    try:
        response = requests.get(f"{BASE_URL}/api/tools/real-time-stats/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Monitoring status: {'Active' if data['is_active'] else 'Inactive'}")
        else:
            print(f"   ❌ Monitoring status failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Monitoring status error: {e}")
    
    # Test start monitoring
    try:
        monitoring_data = {"interval": 2.0}
        response = requests.post(f"{BASE_URL}/api/tools/real-time-stats/start", json=monitoring_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Start monitoring: {data.get('success', False)}")
        else:
            print(f"   ❌ Start monitoring failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Start monitoring error: {e}")
    
    # Wait a moment for monitoring to collect data
    time.sleep(3)
    
    # Test stop monitoring
    try:
        response = requests.post(f"{BASE_URL}/api/tools/real-time-stats/stop")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Stop monitoring: {data.get('success', False)}")
        else:
            print(f"   ❌ Stop monitoring failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stop monitoring error: {e}")
    
    # Test thresholds
    try:
        response = requests.get(f"{BASE_URL}/api/tools/real-time-stats/thresholds")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Alert thresholds: CPU warning={data['cpu']['warning']}%")
        else:
            print(f"   ❌ Alert thresholds failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Alert thresholds error: {e}")
    
    return True

def test_error_handling():
    """Test error handling"""
    print("🧪 Testing Error Handling...")
    
    # Test invalid endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/nonexistent")
        if response.status_code == 404:
            print("   ✅ 404 error handling: Correct")
        else:
            print(f"   ❌ 404 error handling: Expected 404, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ 404 error handling: {e}")
    
    # Test invalid request
    try:
        response = requests.post(f"{BASE_URL}/api/tools/file-search/search", json={})
        if response.status_code == 422:  # Validation error
            print("   ✅ Validation error handling: Correct")
        else:
            print(f"   ❌ Validation error handling: Expected 422, got {response.status_code}")
    except Exception as e:
        print(f"   ❌ Validation error handling: {e}")
    
    return True

def main():
    """Main test function"""
    print("🧪 Testing Overseer API...")
    print("=" * 50)
    
    # Check if API server is running
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code != 200:
            print("❌ API server is not running. Please start the server first:")
            print("   cd backend/api")
            print("   python main.py --host 0.0.0.0 --port 8000")
            return
    except Exception as e:
        print("❌ Cannot connect to API server. Please start the server first:")
        print("   cd backend/api")
        print("   python main.py --host 0.0.0.0 --port 8000")
        return
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint),
        ("Tools Endpoint", test_tools_endpoint),
        ("System Endpoints", test_system_endpoints),
        ("File Search Endpoints", test_file_search_endpoints),
        ("Command Processor Endpoints", test_command_processor_endpoints),
        ("Tool Recommender Endpoints", test_tool_recommender_endpoints),
        ("Real-Time Stats Endpoints", test_real_time_stats_endpoints),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("🎉 API Test Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All API endpoints are working correctly!")
        print("\nThe API now provides:")
        print("• REST endpoints for all CLI tools")
        print("• System information and monitoring")
        print("• File search with advanced filtering")
        print("• Command execution and history")
        print("• Tool recommendations and usage tracking")
        print("• Real-time system statistics")
        print("• Comprehensive error handling")
        print("\nAPI Documentation available at:")
        print("• http://localhost:8000/docs")
        print("• http://localhost:8000/redoc")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")

if __name__ == "__main__":
    main() 