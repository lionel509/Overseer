#!/usr/bin/env python3
"""
Overseer Installation Script
Installs the Overseer CLI tools and optionally the entire stack
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def print_banner():
    """Print installation banner"""
    print("=" * 60)
    print("🎯 Overseer Installation")
    print("=" * 60)
    print("AI-powered system management and automation tools")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")

def check_pip():
    """Check if pip is available"""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ pip is available")
            return True
        else:
            print("❌ pip is not available")
            return False
    except Exception as e:
        print(f"❌ Error checking pip: {e}")
        return False

def pip_install(package_or_file):
    """Install package or requirements file using pip"""
    try:
        print(f"📦 Installing: {package_or_file}")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_or_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Successfully installed: {package_or_file}")
            return True
        else:
            print(f"❌ Failed to install: {package_or_file}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing {package_or_file}: {e}")
        return False

def install_cli_only():
    """Install only the CLI tools"""
    print("\n🔧 Installing CLI Tools Only...")
    print("-" * 40)
    
    # Core dependencies for CLI tools
    cli_packages = [
        "psutil>=5.9.0",
        "pathlib2>=2.3.0",
        "typing-extensions>=4.0.0"
    ]
    
    success_count = 0
    total_count = len(cli_packages)
    
    for package in cli_packages:
        if pip_install(package):
            success_count += 1
    
    print(f"\n📊 CLI Installation: {success_count}/{total_count} packages installed")
    
    if success_count == total_count:
        print("✅ CLI tools installation completed successfully!")
        print("\n🚀 You can now use the Overseer CLI tools:")
        print("  • File search with advanced filtering")
        print("  • Command processing and history management")
        print("  • Tool recommendations based on system context")
        print("  • Real-time system monitoring and statistics")
        print("  • Interactive file selection with menu interface")
        return True
    else:
        print("❌ Some packages failed to install. Please check the errors above.")
        return False

def install_full_stack():
    """Install the entire Overseer stack"""
    print("\n🚀 Installing Full Overseer Stack...")
    print("-" * 40)
    
    # CLI dependencies
    cli_packages = [
        "psutil>=5.9.0",
        "pathlib2>=2.3.0",
        "typing-extensions>=4.0.0"
    ]
    
    # API dependencies
    api_packages = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.4.0",
        "python-multipart>=0.0.6",
        "requests>=2.31.0"
    ]
    
    # Desktop app Python dependencies (if any)
    desktop_packages = [
        "electron-builder>=24.0.0"  # For building desktop app
    ]
    
    all_packages = cli_packages + api_packages + desktop_packages
    
    success_count = 0
    total_count = len(all_packages)
    
    print("📦 Installing CLI dependencies...")
    for package in cli_packages:
        if pip_install(package):
            success_count += 1
    
    print("\n📦 Installing API dependencies...")
    for package in api_packages:
        if pip_install(package):
            success_count += 1
    
    print("\n📦 Installing Desktop app dependencies...")
    for package in desktop_packages:
        if pip_install(package):
            success_count += 1
    
    print(f"\n📊 Full Stack Installation: {success_count}/{total_count} packages installed")
    
    if success_count == total_count:
        print("✅ Full stack installation completed successfully!")
        print("\n🚀 You now have access to:")
        print("  • CLI tools for system management")
        print("  • REST API for programmatic access")
        print("  • Desktop app for GUI interface")
        print("  • File selector with interactive menus")
        print("  • Real-time system monitoring")
        print("  • Tool recommendations")
        return True
    else:
        print("❌ Some packages failed to install. Please check the errors above.")
        return False

def test_installation():
    """Test if the installation was successful"""
    print("\n🧪 Testing Installation...")
    print("-" * 40)
    
    try:
        # Test importing CLI tools
        from cli.tools import (
            FileSearchTool, 
            CommandProcessorTool, 
            ToolRecommenderTool, 
            RealTimeStatsTool,
            FileSelector
        )
        print("✅ CLI tools imported successfully")
        
        # Test creating tool instances
        file_search = FileSearchTool()
        cmd_processor = CommandProcessorTool()
        tool_recommender = ToolRecommenderTool()
        stats_tool = RealTimeStatsTool()
        file_selector = FileSelector()
        print("✅ All tool instances created successfully")
        
        # Test basic functionality
        result = file_search.search_files("*.py", ".", recursive=False)
        if result['success']:
            print("✅ File search tool working")
        
        result = cmd_processor.execute_command('system_info')
        if result['success']:
            print("✅ Command processor working")
        
        result = tool_recommender.generate_recommendations()
        if result['success']:
            print("✅ Tool recommender working")
        
        stats = stats_tool.get_current_stats()
        if 'cpu' in stats:
            print("✅ Real-time stats tool working")
        
        result = file_selector.get_directory_contents(".")
        if result['success']:
            print("✅ File selector working")
        
        print("\n🎉 All tests passed! Installation is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def show_usage_instructions():
    """Show usage instructions after installation"""
    print("\n📚 Usage Instructions:")
    print("=" * 40)
    print("1. CLI Tools:")
    print("   python -c \"from cli.tools import FileSearchTool; print('CLI working')\"")
    print()
    print("2. API Server:")
    print("   cd backend/api")
    print("   python main.py --host 0.0.0.0 --port 8000")
    print()
    print("3. Desktop App:")
    print("   cd desktop-app")
    print("   npm install")
    print("   npm run dev")
    print()
    print("4. File Selector Demo:")
    print("   python demo_file_selector.py")
    print()
    print("5. Run Tests:")
    print("   python test_all_tools.py")

def main():
    """Main installation function"""
    print_banner()
    
    # Check prerequisites
    check_python_version()
    if not check_pip():
        print("❌ pip is required for installation")
        sys.exit(1)
    
    # Show installation options
    print("\n📋 Installation Options:")
    print("1. CLI Tools Only - Basic system management tools")
    print("2. Full Stack - CLI + API + Desktop App")
    print()
    
    while True:
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == "1":
            print("\n🎯 Installing CLI Tools Only...")
            if install_cli_only():
                if test_installation():
                    show_usage_instructions()
            break
        elif choice == "2":
            print("\n🚀 Installing Full Stack...")
            if install_full_stack():
                if test_installation():
                    show_usage_instructions()
            break
        else:
            print("❌ Please enter 1 or 2")
    
    print("\n🎉 Installation completed!")
    print("Thank you for choosing Overseer!")

if __name__ == "__main__":
    main() 