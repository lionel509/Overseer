#!/usr/bin/env python3
"""
Overseer Optimized CLI - Unified system with intelligent loading
"""
import sys
import os
import time
import argparse
import json
import subprocess
from typing import Dict, Optional, Any
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

# Initialize console
console = Console()

# Performance tracking
_startup_time = time.time()

# Lazy loading cache
_lazy_imports = {}
_loaded_modules = set()

def lazy_import(module_path: str, function_name: Optional[str] = None) -> Any:
    """Intelligent lazy import with performance tracking"""
    cache_key = f"{module_path}:{function_name}" if function_name else module_path
    
    if cache_key not in _lazy_imports:
        try:
            load_start = time.time()
            
            # Add current directory to path for relative imports
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if current_dir not in sys.path:
                sys.path.insert(0, current_dir)
            
            if function_name:
                module = __import__(module_path, fromlist=[function_name])
                _lazy_imports[cache_key] = getattr(module, function_name)
            else:
                _lazy_imports[cache_key] = __import__(module_path)
            
            load_time = time.time() - load_start
            _loaded_modules.add(cache_key)
            
            if load_time > 0.1:  # Only log slow loads
                console.print(f"[yellow]Loaded {cache_key} in {load_time:.3f}s[/yellow]")
                
        except ImportError as e:
            console.print(f"[red]Failed to import {cache_key}: {e}[/red]")
            return None
        except Exception as e:
            console.print(f"[red]Error loading {cache_key}: {e}[/red]")
            return None
    
    return _lazy_imports[cache_key]

# Core function loaders
def get_process_user_input():
    """Lazy load core logic"""
    return lazy_import('core.core_logic', 'process_user_input')

def get_scan_directory():
    """Lazy load filesystem scanner"""
    return lazy_import('features.ai_organization.filesystem_scanner', 'scan_directory')

def get_sort_folder():
    """Lazy load folder sorter"""
    return lazy_import('features.ai_organization.folder_sorter', 'sort_folder')

def get_auto_organize():
    """Lazy load auto organize"""
    return lazy_import('features.ai_organization.auto_organize', 'auto_organize')

def get_db_functions():
    """Lazy load database functions"""
    db_module = lazy_import('db.filesystem_db')
    if db_module:
        return {
            'tag_file': getattr(db_module, 'tag_file', None),
            'get_tags': getattr(db_module, 'get_tags', None),
            'search_by_tag': getattr(db_module, 'search_by_tag', None),
            'search_by_description': getattr(db_module, 'search_by_description', None)
        }
    return {}

def get_gemini_api():
    """Lazy load Gemini API"""
    return lazy_import('inference.inference_gemini', 'GeminiAPI')

def get_system_monitor():
    """Lazy load system monitor"""
    return lazy_import('features.ai_monitoring.system_monitor_optimized', 'OptimizedSystemMonitor')

def get_system_monitor_class():
    """Lazy load system monitor class"""
    return lazy_import('features.ai_monitoring.system_monitor_optimized', 'OptimizedSystemMonitor')

def get_llm_backend(config: Dict) -> Optional[Any]:
    """Intelligent LLM backend loading"""
    llm_mode = config.get('llm_mode', 'local')
    
    if llm_mode == 'gemini':
        api_key = config.get('gemini_api_key', os.environ.get('GOOGLE_API_KEY'))
        if not api_key:
            console.print('[red]Error: Gemini API key not configured[/red]')
            console.print('[yellow]Configure with: overseer --settings[/yellow]')
            return None
        
        GeminiAPI_class = get_gemini_api()
        if GeminiAPI_class:
            gemini_model = config.get('gemini_model_name', 'gemini-1.5-flash')
            return GeminiAPI_class(api_key, gemini_model).run
        else:
            console.print('[red]Error: Failed to load Gemini API[/red]')
            return None
    else:
        # Local LLM
        try:
            from inference.inference_local import LocalLLM
            model_name = config.get('local_model_name', 'google/gemma-1.1-3b-it')
            LocalLLM._model_name = model_name
            
            # Try to initialize the model
            llm = LocalLLM()
            return llm.run
            
        except Exception as e:
            console.print(f'[red]Error loading local LLM: {e}[/red]')
            console.print('[yellow]💡 Try one of these solutions:[/yellow]')
            console.print('  • Download models: python -m backend.cli.model_manager setup')
            console.print('  • Use Gemini API: overseer --settings (set llm_mode to "gemini")')
            console.print('  • Install dependencies: pip install transformers torch')
            return None

def load_config() -> Dict:
    """Load configuration with fallback"""
    config_path = os.path.expanduser('~/.overseer/config.json')
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            console.print(f'[yellow]Warning: Could not load config: {e}[/yellow]')
    
    # Default config
    return {
        'llm_mode': 'local',
        'debug': False,
        'verbose_output': False,
        'show_progress': True
    }

def is_basic_command(user_input: str) -> bool:
    """Detect if command can be handled in fast mode"""
    basic_commands = [
        'ls', 'dir', 'pwd', 'echo', 'cat', 'head', 'tail',
        'cd', 'mkdir', 'rmdir', 'touch', 'cp', 'mv', 'rm',
        'find', 'grep', 'wc', 'sort', 'uniq', 'cut', 'paste'
    ]
    
    first_word = user_input.split()[0].lower()
    return first_word in basic_commands

def is_system_command(user_input: str) -> bool:
    """Detect system monitoring commands"""
    system_commands = [
        'system', 'stats', 'monitor', 'cpu', 'memory', 'disk',
        'process', 'top', 'ps', 'performance'
    ]
    
    user_lower = user_input.lower()
    return any(cmd in user_lower for cmd in system_commands)

def execute_basic_command(user_input: str) -> None:
    """Execute basic system commands"""
    try:
        result = subprocess.run(user_input.split(), 
                              capture_output=True, 
                              text=True, 
                              timeout=30)
        
        if result.returncode == 0:
            if result.stdout:
                console.print(result.stdout)
            if result.stderr:
                console.print(f"[yellow]{result.stderr}[/yellow]")
        else:
            console.print(f"[red]Command failed: {result.stderr}[/red]")
            
    except subprocess.TimeoutExpired:
        console.print("[red]Command timed out[/red]")
    except Exception as e:
        console.print(f"[red]Error executing command: {e}[/red]")

def show_performance_stats() -> None:
    """Show performance statistics"""
    total_time = time.time() - _startup_time
    loaded_count = len(_loaded_modules)
    
    console.print(Panel(
        f"🚀 Startup: {total_time:.3f}s | 📦 Modules: {loaded_count}",
        title="Performance Stats",
        border_style="green"
    ))

def handle_settings_command() -> None:
    """Handle settings command"""
    try:
        from settings_manager import AdvancedSettingsManager
        
        console.print(Panel("""
[bold yellow]Overseer Settings Manager[/bold yellow]

Available commands:
• settings show          - Show current settings
• settings edit         - Interactive settings editor
• settings advanced     - Show advanced settings
• settings reset        - Reset to defaults
• settings export       - Export configuration
• settings import       - Import configuration
• settings validate     - Validate configuration

Type 'exit' to return to main CLI
        """, title="Settings Help", border_style="yellow"))
        
        while True:
            settings_input = Prompt.ask("\n[bold yellow]Settings[/bold yellow]")
            
            if not settings_input or settings_input.strip() == '':
                continue
                
            if settings_input.lower() in ['exit', 'quit', 'q', 'back']:
                break
            elif settings_input.lower() == 'help':
                console.print(Panel("""
[bold yellow]Settings Commands:[/bold yellow]
• show          - Show current settings
• edit          - Interactive settings editor
• advanced      - Show advanced settings
• reset         - Reset to defaults
• export        - Export configuration
• import        - Import configuration
• validate      - Validate configuration
                """, title="Settings Help", border_style="yellow"))
                continue
            elif settings_input.lower() == 'show':
                settings_manager = AdvancedSettingsManager()
                settings_manager.show_settings()
            elif settings_input.lower() == 'advanced':
                settings_manager = AdvancedSettingsManager()
                settings_manager.show_settings(advanced_mode=True)
            elif settings_input.lower() == 'edit':
                settings_manager = AdvancedSettingsManager()
                settings_manager.interactive_settings_editor()
            elif settings_input.lower() == 'reset':
                settings_manager = AdvancedSettingsManager()
                settings_manager.reset_to_defaults()
            elif settings_input.lower() == 'export':
                filename = Prompt.ask("Enter filename for export")
                if filename:
                    settings_manager = AdvancedSettingsManager()
                    settings_manager.export_config(filename)
            elif settings_input.lower() == 'import':
                filename = Prompt.ask("Enter filename to import")
                if filename:
                    settings_manager = AdvancedSettingsManager()
                    settings_manager.import_config(filename)
            elif settings_input.lower() == 'validate':
                settings_manager = AdvancedSettingsManager()
                from advanced_settings import validate_config
                validate_config(settings_manager)
            else:
                console.print(f"[red]Unknown settings command: {settings_input}[/red]")
                console.print("Type 'help' for available commands")
                
    except ImportError as e:
        console.print(f"[red]Error loading settings manager: {e}[/red]")
    except Exception as e:
        console.print(f"[red]Error in settings: {e}[/red]")

def show_help() -> None:
    """Show intelligent help"""
    console.print(Panel("""
[bold cyan]Overseer Optimized CLI[/bold cyan]

[bold green]Fast Mode Commands:[/bold green]
• ls, dir, pwd, echo, cat, head, tail
• cd, mkdir, rmdir, touch, cp, mv, rm
• find, grep, wc, sort, uniq, cut, paste

[bold magenta]System Mode Commands:[/bold magenta]
• "system stats" - System performance dashboard
• "cpu usage" - CPU monitoring
• "memory usage" - Memory monitoring
• "memory diagnostics" - Detailed memory analysis and troubleshooting
• "ai analysis" - AI-powered system analysis with specialized recommendations
• "llm analysis" - Advanced LLM analysis with detailed optimization strategies
• "disk usage" - Disk space monitoring
• "process list" - Top processes
• "performance" - System recommendations

[bold blue]AI Mode Commands:[/bold blue]
• "organize my files" - AI file organization
• "find python files" - Semantic file search
• "sort by type" - Smart folder sorting
• "tag important files" - File tagging

[bold cyan]File Indexer Commands:[/bold cyan]
• "file indexer" - Enhanced local file indexing and semantic search
• "index files" - Index files in directories
• "file indexing" - Interactive file indexing interface

[bold magenta]Interactive Commands:[/bold magenta]
• "interactive commands" - Run commands with arrow key selection
• "command runner" - Interactive command execution interface
• "run commands" - Select and execute commands safely
• "recommended commands" - AI-powered system command recommendations
• "command recommendations" - Scroll through recommended system commands
• "system commands" - Interactive command recommender with analysis

[bold yellow]Settings Commands:[/bold yellow]
• "settings" - Open settings manager
• "settings show" - Show current settings
• "settings advanced" - Show advanced settings

[bold white]Performance:[/bold white]
• Fast mode: < 0.1s startup
• System mode: < 0.2s startup
• AI mode: Progressive loading
• Intelligent caching

Type 'exit' to quit
    """, title="Help", border_style="blue"))

def handle_system_monitoring(user_input: str) -> None:
    """Handle system monitoring commands"""
    console.print(f"[magenta]System mode: {user_input}[/magenta]")
    
    SystemMonitor = get_system_monitor_class()
    if SystemMonitor:
        monitor = SystemMonitor()
        monitor.display_system_dashboard()
        
        # Show recommendations
        recommendations = monitor.get_recommendations()
        if recommendations:
            console.print("\n[bold yellow]Recommendations:[/bold yellow]")
            for rec in recommendations:
                console.print(f"• {rec}")
    else:
        console.print("[red]Error: Failed to load system monitor[/red]")

def handle_ai_mode(user_input: str) -> None:
    """Handle AI mode commands"""
    console.print(f"[cyan]AI mode: {user_input}[/cyan]")
    
    # Load core processing
    process_func = get_process_user_input()
    if process_func:
        response = process_func(user_input)
        console.print(f"[bold green]AI:[/bold green] {response}")
    else:
        console.print("[red]Error: Failed to load AI processing[/red]")

def main() -> int:
    """Main optimized CLI function"""
    parser = argparse.ArgumentParser(description='Overseer Optimized CLI')
    parser.add_argument('--version', action='store_true', help='Show version')
    parser.add_argument('--stats', action='store_true', help='Show performance stats')
    parser.add_argument('--ai', action='store_true', help='Force AI mode')
    
    args, unknown = parser.parse_known_args()
    
    if args.version:
        console.print("Overseer v26.0.0 (Optimized)")
        return 0
    
    if args.stats:
        show_performance_stats()
        return 0
    
    # Load config
    config = load_config()
    
    # Interactive mode
    console.print("[bold cyan]Overseer Optimized CLI[/bold cyan]")
    console.print("Type 'help' for commands, 'exit' to quit")
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold green]Overseer[/bold green]")
            
            if not user_input or user_input.strip() == '':
                continue
                
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            elif user_input.lower() == 'help':
                show_help()
                continue
            elif user_input.lower() == 'stats':
                show_performance_stats()
                continue
            elif user_input.lower() == 'version':
                console.print("Overseer v26.0.0 (Optimized)")
                continue
            elif user_input.lower() == 'settings':
                console.print(f"[yellow]Settings mode: {user_input}[/yellow]")
                handle_settings_command()
                continue
            elif user_input.lower() in ['memory diagnostics', 'memory diag', 'mem diag']:
                console.print(f"[red]Memory diagnostics mode: {user_input}[/red]")
                try:
                    from features.ai_monitoring.memory_diagnostics import MemoryDiagnostics
                    diagnostics = MemoryDiagnostics()
                    diagnostics.display_memory_diagnostics()
                except ImportError as e:
                    console.print(f"[red]Error loading memory diagnostics: {e}[/red]")
                continue
            elif user_input.lower() in ['ai analysis', 'ai system', 'system analysis']:
                console.print(f"[blue]AI System Analysis mode: {user_input}[/blue]")
                try:
                    from features.ai_monitoring.ai_system_analyzer import AISystemAnalyzer
                    analyzer = AISystemAnalyzer()
                    analyzer.display_ai_analysis()
                except ImportError as e:
                    console.print(f"[red]Error loading AI system analyzer: {e}[/red]")
                continue
            elif user_input.lower() in ['llm analysis', 'advanced analysis', 'detailed analysis']:
                console.print(f"[purple]Advanced LLM Analysis mode: {user_input}[/purple]")
                try:
                    from features.ai_monitoring.llm_system_advisor import LLMSystemAdvisor
                    advisor = LLMSystemAdvisor()
                    advisor.display_advanced_analysis()
                except ImportError as e:
                    console.print(f"[red]Error loading LLM system advisor: {e}[/red]")
                continue
            elif user_input.lower() in ['file indexer', 'index files', 'file indexing']:
                console.print(f"[cyan]File Indexer mode: {user_input}[/cyan]")
                try:
                    from features.ai_organization.file_indexer_cli import FileIndexerCLI
                    indexer_cli = FileIndexerCLI()
                    indexer_cli.run()
                except ImportError as e:
                    console.print(f"[red]Error loading file indexer: {e}[/red]")
                continue
            elif user_input.lower() in ['interactive commands', 'command runner', 'run commands']:
                console.print(f"[magenta]Interactive Command Runner mode: {user_input}[/magenta]")
                try:
                    from features.ai_organization.simple_command_runner import SimpleCommandRunner
                    runner = SimpleCommandRunner()
                    
                    # Add some system commands
                    system_commands = [
                        {'command': 'system_profiler SPHardwareDataType', 'description': 'Get system hardware info', 'category': 'system'},
                        {'command': 'top -l 1 | head -10', 'description': 'Show top processes', 'category': 'processes'},
                        {'command': 'df -h', 'description': 'Show disk usage', 'category': 'disk'},
                        {'command': 'ps aux --sort=-%mem | head -5', 'description': 'Show memory usage', 'category': 'memory'},
                        {'command': 'ls -la ~/.overseer/', 'description': 'List config files', 'category': 'config'},
                        {'command': 'find . -name "*.py" -type f | head -10', 'description': 'Find Python files', 'category': 'files'},
                        {'command': 'git status', 'description': 'Check git status', 'category': 'git'}
                    ]
                    runner.add_commands(system_commands)
                    runner.run_interactive()
                except ImportError as e:
                    console.print(f"[red]Error loading interactive command runner: {e}[/red]")
                continue
            elif user_input.lower() in ['recommended commands', 'command recommendations', 'system commands']:
                console.print(f"[cyan]Interactive Command Recommender mode: {user_input}[/cyan]")
                try:
                    from features.ai_monitoring.interactive_command_recommender import InteractiveCommandRecommender
                    recommender = InteractiveCommandRecommender()
                    recommender.run_interactive()
                except ImportError as e:
                    console.print(f"[red]Error loading interactive command recommender: {e}[/red]")
                continue
            
            # Check if it's a basic command
            if is_basic_command(user_input):
                console.print(f"[blue]Fast mode: {user_input}[/blue]")
                execute_basic_command(user_input)
            elif is_system_command(user_input):
                handle_system_monitoring(user_input)
            else:
                handle_ai_mode(user_input)
                    
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except EOFError:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 