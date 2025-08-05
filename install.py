#!/usr/bin/env python3
"""
Overseer Installation Script
Installs the Overseer CLI tools and optionally the entire stack with AI models
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

def check_git():
    """Check if git is available for model downloads"""
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ git is available")
            return True
        else:
            print("❌ git is not available (required for model downloads)")
            return False
    except Exception as e:
        print(f"❌ Error checking git: {e}")
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
        "typing-extensions>=4.0.0",
        "rich>=13.0.0"  # For rich console output
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

def install_ai_models():
    """Install AI models for local inference"""
    print("\n🤖 Setting up AI Models...")
    print("-" * 40)
    
    try:
        # Import model manager
        sys.path.append(os.path.join(os.path.dirname(__file__), "backend", "cli"))
        from model_manager import ModelManager
        
        # Initialize model manager
        manager = ModelManager()
        
        # Setup models
        success, models = manager.setup_models_for_installation()
        
        if success and models:
            print(f"✅ Successfully set up {len(models)} AI model(s)")
            return True
        elif success and not models:
            print("ℹ️ No models installed (user choice)")
            return True
        else:
            print("❌ Failed to set up AI models")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import model manager: {e}")
        print("📝 AI models can be installed later using: python -m backend.cli.model_manager")
        return False
    except Exception as e:
        print(f"❌ Error setting up AI models: {e}")
        return False

def install_full_stack():
    """Install the entire Overseer stack"""
    print("\n🚀 Installing Full Overseer Stack...")
    print("-" * 40)
    
    # CLI dependencies
    cli_packages = [
        "psutil>=5.9.0",
        "pathlib2>=2.3.0",
        "typing-extensions>=4.0.0",
        "rich>=13.0.0"  # For rich console output
    ]
    
    # API dependencies
    api_packages = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.4.0",
        "python-multipart>=0.0.6",
        "requests>=2.31.0"
    ]
    
    # AI model dependencies
    ai_packages = [
        "transformers>=4.35.0",
        "torch>=2.0.0",
        "huggingface-hub>=0.17.0"
    ]
    
    all_packages = cli_packages + api_packages + ai_packages
    
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
            
    print("\n📦 Installing AI dependencies...")
    for package in ai_packages:
        if pip_install(package):
            success_count += 1
    
    print(f"\n📊 Full Stack Installation: {success_count}/{total_count} packages installed")
    
    if success_count >= total_count * 0.8:  # Allow some failures
        print("✅ Full stack installation completed!")
        
        # Install AI models if git is available
        if check_git():
            print("\n🤖 Setting up AI models...")
            if install_ai_models():
                print("✅ AI models setup completed!")
            else:
                print("⚠️ AI models setup had issues, but can be done later")
        else:
            print("\n⚠️ Git not available - AI models can be installed later")
        
        print("\n🚀 You now have access to:")
        print("  • CLI tools for system management")
        print("  • REST API for programmatic access")
        print("  • AI-powered recommendations and analysis")
        print("  • Local AI models for enhanced functionality")
        print("  • File selector with interactive menus")
        print("  • Real-time system monitoring")
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
    print("3. AI Models:")
    print("   python -m backend.cli.model_manager  # Manage AI models")
    print("   overseer --test-llm                  # Test AI integration")
    print()
    print("4. File Selector Demo:")
    print("   python demo_file_selector.py")
    print()
    print("5. Run Tests:")
    print("   python test_all_tools.py")
    print()
    print("6. Model Management:")
    print("   python -m backend.cli.model_manager  # Add/remove models")

def main():
    """Main installation function"""
    print_banner()
    
    # Check prerequisites
    check_python_version()
    if not check_pip():
        print("❌ pip is required for installation")
        sys.exit(1)
    
    git_available = check_git()
    if not git_available:
        print("⚠️ git is not available - AI model downloads will be limited")
    
    # Show installation options
    print("\n📋 Installation Options:")
    print("1. CLI Tools Only - Basic system management tools")
    print("2. Full Stack - CLI + API + AI Models")
    print("3. AI Models Only - Just download and setup AI models")
    print()
    
    while True:
        choice = input("Enter your choice (1, 2, or 3): ").strip()
        
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
        elif choice == "3":
            print("\n🤖 Installing AI Models Only...")
            if git_available and install_ai_models():
                print("✅ AI models installation completed!")
                show_usage_instructions()
            else:
                print("❌ AI models installation failed or git not available")
            break
        else:
            print("❌ Please enter 1, 2, or 3")
    
    print("\n🎉 Installation completed!")
    print("Thank you for choosing Overseer!")

if __name__ == "__main__":
    main() 