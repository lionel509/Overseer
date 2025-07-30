# Overseer CLI - Quick Reference Guide

## 🚀 **Quick Start**
```bash
# Start the optimized CLI
python overseer_cli.py

# Check performance
python overseer_cli.py --stats

# Show version
python overseer_cli.py --version
```

## 📋 **Available Commands**

### **Fast Mode** (< 0.1s response)
```bash
# Basic system commands
ls, dir, pwd, echo, cat, head, tail
cd, mkdir, rmdir, touch, cp, mv, rm
find, grep, wc, sort, uniq, cut, paste
```

### **System Mode** (< 0.2s response)
```bash
# System monitoring
"system stats"          # Performance dashboard
"cpu usage"            # CPU monitoring
"memory usage"         # Memory monitoring
"disk usage"           # Disk space monitoring
"process list"         # Top processes
"performance"          # System recommendations
```

### **AI Mode** (Progressive loading)
```bash
# File organization
"organize my files"    # Auto-organize files by type
"sort by type"         # Smart folder sorting
"find python files"    # Semantic file search
"tag important files"  # File tagging system

# System analysis
"analyze system"       # LLM-powered system diagnosis
"tool recommendations" # AI tool suggestions
"performance analysis" # Advanced performance insights
```

## 🛠️ **Core Functions**

### **Main CLI Functions**
```python
# Core CLI functions
main()                          # Main entry point
lazy_import()                   # Intelligent lazy loading
load_config()                   # Load configuration
is_basic_command()              # Detect basic commands
is_system_command()             # Detect system commands
execute_basic_command()         # Execute system commands
show_performance_stats()        # Show performance metrics
show_help()                     # Show help information
```

### **Lazy Loading Functions**
```python
# Lazy loading functions
get_process_user_input()        # Load core AI processing
get_scan_directory()            # Load filesystem scanner
get_sort_folder()               # Load folder sorter
get_auto_organize()            # Load auto-organize
get_db_functions()              # Load database functions
get_gemini_api()               # Load Gemini API
get_system_monitor_class()      # Load system monitor
get_llm_backend()              # Load LLM backend
```

## 📁 **Feature Functions**

### **AI Core Features**
```python
# llm_advisor.py
LLMAdvisor.diagnose_system_problems()    # System problem diagnosis
LLMAdvisor.suggest_solutions()           # AI solution suggestions
LLMAdvisor.analyze_performance()         # Performance analysis

# enhanced_tool_recommender.py
EnhancedToolRecommender.recommend_tools() # AI tool recommendations
EnhancedToolRecommender.analyze_context() # Context analysis
EnhancedToolRecommender.suggest_alternatives() # Alternative suggestions
```

### **File Organization Features**
```python
# auto_organize.py
auto_organize()                # AI-powered file organization
categorize_files()             # File categorization
create_folders()               # Smart folder creation
move_files()                   # Intelligent file moving

# file_search.py
search_files()                 # AI-enhanced file search
semantic_file_search()         # Semantic search
get_all_files()               # Get all files

# folder_sorter.py
sort_folder()                  # Intelligent folder sorting
analyze_content()              # Content analysis
create_categories()            # Category creation

# filesystem_scanner.py
scan_directory()               # Smart filesystem scanning
analyze_structure()            # Structure analysis
index_files()                  # File indexing

# tool_recommender.py
recommend_tools()              # Basic tool recommendations

# command_corrector.py
correct_command()              # AI command correction
```

### **System Monitoring Features**
```python
# system_monitor_optimized.py
OptimizedSystemMonitor.get_system_stats()           # Get system statistics
OptimizedSystemMonitor.display_system_dashboard()   # Show system dashboard
OptimizedSystemMonitor.get_process_stats()          # Get process statistics
OptimizedSystemMonitor.get_recommendations()        # System recommendations
OptimizedSystemMonitor._get_trend()                 # Calculate trends

# advanced_process_manager.py
AdvancedProcessManager.analyze_processes()          # Process analysis
AdvancedProcessManager.optimize_performance()       # Performance optimization
AdvancedProcessManager.manage_resources()           # Resource management
```

## 🔧 **Configuration**

### **Config File Location**
```bash
~/.overseer/config.json
```

### **Key Settings**
```json
{
  "llm_mode": "local",           # "local" or "gemini"
  "debug": false,                # Debug mode
  "verbose_output": false,        # Verbose output
  "show_progress": true,          # Show progress bars
  "auto_save": true,             # Auto-save session data
  "file_indexing": false,        # Enable file indexing
  "auto_organize_enabled": true, # Enable auto-organize
  "max_files_per_folder": 100,   # Max files per folder
  "confirm_moves": true,         # Confirm file moves
  "backup_before_move": false,   # Create backup before move
  "scan_hidden_files": false,    # Include hidden files
  "exclude_patterns": "*.tmp,*.log,.DS_Store"
}
```

### **Environment Variables**
```bash
# Gemini API
export GOOGLE_API_KEY="your_api_key_here"

# Local LLM
export OLLAMA_HOST="http://localhost:11434"
```

## 📊 **Performance Metrics**

### **Startup Times**
- **Fast Mode**: < 0.1s (basic commands only)
- **System Mode**: < 0.2s (monitoring + basic)
- **AI Mode**: Progressive loading (AI features as needed)

### **Memory Usage**
- **Before**: 500MB (all modules loaded)
- **After**: 50MB (lazy loading)
- **Improvement**: 90% memory reduction

### **Feature Coverage**
- **Core AI**: 2/4 features (50%)
- **File Organization**: 6/6 features (100%)
- **System Monitoring**: 2/6 features (33%)
- **Performance Tools**: 1/3 features (33%)
- **Analytics**: 0/4 features (0%)

## ❌ **Missing Features**

### **High Priority (Recommended to Re-add)**
1. **`machine_learning_integration.py`** - ML-powered system analysis
2. **`predictive_analytics.py`** - AI-driven performance prediction
3. **`performance_optimizer.py`** - AI-assisted system optimization
4. **`unified_system_monitor.py`** - Comprehensive system monitoring

### **Medium Priority**
5. **`alert_manager.py`** - Intelligent alert system
6. **`custom_alert_rules.py`** - LLM-assisted alert rules
7. **`monitoring_dashboard.py`** - Intelligent dashboard
8. **`export_reporting.py`** - AI-powered report generation

### **Low Priority**
9. **`demo_mode.py`** - Interactive demo mode
10. **`demo_cli.py`** - Demo CLI interface
11. **`dashboard_demo.py`** - Dashboard demonstration

## 🎯 **Usage Examples**

### **Basic Usage**
```bash
# Start interactive mode
python overseer_cli.py

# Use fast mode commands
ls
pwd
echo "hello"

# Use system monitoring
"system stats"
"cpu usage"

# Use AI features
"organize my files"
"find python files"
"analyze system"
```

### **Programmatic Usage**
```python
# Import functions
from overseer_cli import get_process_user_input, get_system_monitor_class

# Use AI processing
process_func = get_process_user_input()
response = process_func("organize my files")

# Use system monitoring
SystemMonitor = get_system_monitor_class()
monitor = SystemMonitor()
monitor.display_system_dashboard()
```

---

**Quick Reference**: The system provides immediate response for basic tasks while progressively loading advanced features as needed. Use `help` in interactive mode to see all available commands. 