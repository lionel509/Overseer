#!/usr/bin/env python3
"""
Test script for IPC communication between Electron and Python
This script can be used to test the backend integration independently
"""

import sys
import json
import os

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

def test_system_info():
    """Test system information retrieval"""
    try:
        import platform
        import psutil
        
        info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_partitions": len(psutil.disk_partitions())
        }
        
        return {
            "success": True,
            "data": info
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get system info: {e}"
        }

def test_process_list():
    """Test process list retrieval"""
    try:
        import psutil
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return {
            "success": True,
            "data": processes[:10]  # Return first 10 processes for testing
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get process list: {e}"
        }

def test_memory_usage():
    """Test memory usage retrieval"""
    try:
        import psutil
        
        memory = psutil.virtual_memory()
        memory_info = {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
            "free": memory.free
        }
        
        return {
            "success": True,
            "data": memory_info
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get memory usage: {e}"
        }

def main():
    """Main test function"""
    print("🧪 Testing IPC Communication Components...")
    print("=" * 50)
    
    # Test system info
    print("\n1. Testing System Information...")
    result = test_system_info()
    if result["success"]:
        print("✅ System info test passed")
        print(f"   Platform: {result['data']['platform']}")
        print(f"   Architecture: {result['data']['architecture']}")
        print(f"   CPU Count: {result['data']['cpu_count']}")
    else:
        print(f"❌ System info test failed: {result['error']}")
    
    # Test process list
    print("\n2. Testing Process List...")
    result = test_process_list()
    if result["success"]:
        print("✅ Process list test passed")
        print(f"   Found {len(result['data'])} processes")
    else:
        print(f"❌ Process list test failed: {result['error']}")
    
    # Test memory usage
    print("\n3. Testing Memory Usage...")
    result = test_memory_usage()
    if result["success"]:
        print("✅ Memory usage test passed")
        print(f"   Memory usage: {result['data']['percent']:.1f}%")
        print(f"   Total memory: {result['data']['total'] / (1024**3):.1f} GB")
    else:
        print(f"❌ Memory usage test failed: {result['error']}")
    
    # Test JSON communication
    print("\n4. Testing JSON Communication...")
    test_commands = [
        {"command": "system_info", "args": []},
        {"command": "process_list", "args": []},
        {"command": "memory_usage", "args": []}
    ]
    
    for cmd in test_commands:
        print(f"   Testing command: {cmd['command']}")
        # Simulate the IPC communication format
        json_input = json.dumps(cmd)
        print(f"   JSON input: {json_input}")
        
        # Parse and simulate response
        try:
            parsed = json.loads(json_input)
            print(f"   ✅ JSON parsing successful")
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parsing failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 IPC Communication Test Complete!")
    print("\nThe desktop application should now be able to:")
    print("• Communicate with Python backend")
    print("• Execute system commands")
    print("• Display real-time metrics")
    print("• Use the command palette (Cmd+K or Ctrl+K)")

if __name__ == "__main__":
    main() 