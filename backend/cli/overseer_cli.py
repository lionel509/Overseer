#!/usr/bin/env python3
"""
Overseer Optimized CLI - Unified system with intelligent loading
"""
import sys
import os
import time
import argparse
import json
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

# Performance tracking
_startup_time = time.time()

# Lazy loading cache
_lazy_imports = {}
_loaded_modules = set()

def lazy_import(module_path, function_name=None):
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

def get_llm_backend(config):
    """Intelligent LLM backend loading"""
    llm_mode = config.get('llm_mode', 'local')
    
    if llm_mode == 'gemini':
        api_key = config.get('gemini_api_key', os.environ.get('GOOGLE_API_KEY'))
        if not api_key:
            console.print('[red]Error: Gemini API key not configured[/red]')
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
            return LocalLLM().run
        except Exception as e:
            console.print(f'[red]Error loading local LLM: {e}[/red]')
            return None

def load_config():
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

def is_basic_command(user_input):
    """Detect if command can be handled in fast mode"""
    basic_commands = [
        'ls', 'dir', 'pwd', 'echo', 'cat', 'head', 'tail',
        'cd', 'mkdir', 'rmdir', 'touch', 'cp', 'mv', 'rm',
        'find', 'grep', 'wc', 'sort', 'uniq', 'cut', 'paste'
    ]
    
    first_word = user_input.split()[0].lower()
    return first_word in basic_commands

def is_system_command(user_input):
    """Detect system monitoring commands"""
    system_commands = [
        'system', 'stats', 'monitor', 'cpu', 'memory', 'disk',
        'process', 'top', 'ps', 'performance'
    ]
    
    user_lower = user_input.lower()
    return any(cmd in user_lower for cmd in system_commands)

def execute_basic_command(user_input):
    """Execute basic system commands"""
    import subprocess
    
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

def show_performance_stats():
    """Show performance statistics"""
    total_time = time.time() - _startup_time
    loaded_count = len(_loaded_modules)
    
    console.print(Panel(
        f"🚀 Startup: {total_time:.3f}s | 📦 Modules: {loaded_count}",
        title="Performance Stats",
        border_style="green"
    ))

def show_help():
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
• "disk usage" - Disk space monitoring
• "process list" - Top processes
• "performance" - System recommendations

[bold blue]AI Mode Commands:[/bold blue]
• "organize my files" - AI file organization
• "find python files" - Semantic file search
• "sort by type" - Smart folder sorting
• "tag important files" - File tagging

[bold yellow]Performance:[/bold yellow]
• Fast mode: < 0.1s startup
• System mode: < 0.2s startup
• AI mode: Progressive loading
• Intelligent caching

Type 'exit' to quit
    """, title="Help", border_style="blue"))

def main():
    """Main optimized CLI function"""
    parser = argparse.ArgumentParser(description='Overseer Optimized CLI')
    parser.add_argument('--version', action='store_true', help='Show version')
    parser.add_argument('--stats', action='store_true', help='Show performance stats')
    # parser.add_argument('--fast', action='store_true', help='Force fast mode only')
    parser.add_argument('--ai', action='store_true', help='Force AI mode')
    
    args, unknown = parser.parse_known_args()
    
    if args.version:
        console.print("Overseer v26.0.0 (Optimized)")
        return
    
    if args.stats:
        show_performance_stats()
        return
    
    # Load config
    config = load_config()
    
    # # Show startup performance
    # startup_time = time.time() - _startup_time
    # console.print(f"[green]🚀 Optimized startup: {startup_time:.3f}s[/green]")
    
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
                console.print("Overseer v1.0.0 (Optimized)")
                continue
            
            # Check if it's a basic command
            if is_basic_command(user_input):
                console.print(f"[blue]Fast mode: {user_input}[/blue]")
                execute_basic_command(user_input)
            elif is_system_command(user_input):
                # System monitoring mode
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
            else:
                # AI mode - load necessary modules
                console.print(f"[cyan]AI mode: {user_input}[/cyan]")
                
                # Load core processing
                process_func = get_process_user_input()
                if process_func:
                    response = process_func(user_input)
                    console.print(f"[bold green]AI:[/bold green] {response}")
                else:
                    console.print("[red]Error: Failed to load AI processing[/red]")
                    
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except EOFError:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

if __name__ == "__main__":
    import json
    sys.exit(main()) 