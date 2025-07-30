import os
import json
import argparse
from rich.console import Console
from rich.prompt import Prompt
from .core.core_logic import process_user_input
from .features.filesystem_scanner import scan_directory
from .features.folder_sorter import sort_folder
from .features.auto_organize import auto_organize
from .db.filesystem_db import tag_file, get_tags, search_by_tag, search_by_description
from .inference.inference_gemini import GeminiAPI
from .utils.logger import set_debug, set_log, debug, info, error
import sys
import questionary
import re
import platform
import time
from rich.syntax import Syntax
from rich.panel import Panel

console = Console()
CONFIG_PATH = os.path.expanduser('~/.overseer/config.json')

class SessionContext:
    def __init__(self):
        self.last_search_results = []  # List of files from last search
        self.last_selected_file = None
        self.last_command = None
        self.last_action = None
        self.history = []  # List of (user_input, action, result)

    def summary(self):
        summary = []
        if self.last_search_results:
            summary.append(f"Last search: {len(self.last_search_results)} files found")
        if self.last_selected_file:
            summary.append(f"Last selected file: {self.last_selected_file}")
        if self.last_command:
            summary.append(f"Last command: {self.last_command}")
        if self.last_action:
            summary.append(f"Last action: {self.last_action}")
        return '\n'.join(summary) if summary else 'No recent context.'

    def resolve_reference(self, ref):
        if ref in ('the first one', 'first one', 'first file') and self.last_search_results:
            return self.last_search_results[0]
        if ref in ('the last one', 'last one', 'last file') and self.last_search_results:
            return self.last_search_results[-1]
        if ref in ('those', 'them', 'these') and self.last_search_results:
            return self.last_search_results
        if ref in ('it',) and self.last_selected_file:
            return self.last_selected_file
        return None

def first_run_setup():
    import questionary
    print('Welcome to Overseer! Let\'s set up your preferences:')
    
    # Basic LLM Configuration
    llm_mode = questionary.select('Do you want to use a local LLM or the online Gemini API?', choices=['local', 'gemini'], default='gemini').ask()
    config = {}
    config['llm_mode'] = llm_mode
    
    if llm_mode == 'gemini':
        config['gemini_api_key'] = questionary.text('Gemini API key').ask()
        config['gemini_model_name'] = questionary.text('Gemini model name', default='gemini-2.5-flash-lite').ask()
        config['gemini_max_tokens'] = questionary.text('Max tokens for Gemini responses', default='2048').ask()
        config['gemini_temperature'] = questionary.text('Temperature (0.0-1.0)', default='0.7').ask()
    else:
        config['local_model_name'] = questionary.text('Local model name', default='google/gemma-1.1-3b-it').ask()
        config['local_max_tokens'] = questionary.text('Max tokens for local model', default='1024').ask()
        config['local_temperature'] = questionary.text('Temperature (0.0-1.0)', default='0.7').ask()
    
    # System Behavior Settings
    print('\n[bold cyan]System Behavior Settings:[/bold cyan]')
    config['debug'] = questionary.confirm('Enable debug mode?', default=False).ask()
    config['log'] = questionary.confirm('Enable log mode?', default=False).ask()
    config['verbose_output'] = questionary.confirm('Enable verbose output?', default=False).ask()
    config['show_progress'] = questionary.confirm('Show progress bars?', default=True).ask()
    config['auto_save'] = questionary.confirm('Auto-save session data?', default=True).ask()
    
    # File Management Settings
    print('\n[bold cyan]File Management Settings:[/bold cyan]')
    config['file_indexing'] = questionary.confirm('Enable file indexing?', default=False).ask()
    config['auto_organize_enabled'] = questionary.confirm('Enable auto-organize feature?', default=True).ask()
    config['max_files_per_folder'] = questionary.text('Max files per folder for auto-organize', default='100').ask()
    config['confirm_moves'] = questionary.confirm('Confirm file moves by default?', default=True).ask()
    config['backup_before_move'] = questionary.confirm('Create backup before moving files?', default=False).ask()
    config['scan_hidden_files'] = questionary.confirm('Include hidden files in scans?', default=False).ask()
    config['exclude_patterns'] = questionary.text('File patterns to exclude (comma-separated)', default='*.tmp,*.log,.DS_Store').ask()
    
    # Security Settings
    print('\n[bold cyan]Security Settings:[/bold cyan]')
    config['full_control'] = questionary.confirm('Enable full control mode by default?', default=False).ask()
    config['always_confirm_commands'] = questionary.confirm('Always confirm before running system/tool commands?', default=True).ask()
    config['sandbox_mode'] = questionary.select('Default sandbox mode', choices=['dry_run', 'simulation', 'isolated', 'validation'], default='simulation').ask()
    config['command_timeout'] = questionary.text('Command timeout (seconds)', default='30').ask()
    config['max_file_size'] = questionary.text('Max file size to process (MB)', default='100').ask()
    config['secure_config'] = questionary.confirm('Use secure config manager?', default=True).ask()
    
    # Search and Indexing Settings
    print('\n[bold cyan]Search and Indexing Settings:[/bold cyan]')
    config['search_depth'] = questionary.text('Search depth (levels)', default='3').ask()
    config['index_update_frequency'] = questionary.text('Index update frequency (hours)', default='24').ask()
    config['search_results_limit'] = questionary.text('Max search results', default='50').ask()
    config['fuzzy_search'] = questionary.confirm('Enable fuzzy search?', default=True).ask()
    config['search_in_content'] = questionary.confirm('Search in file contents?', default=False).ask()
    
    # UI and Interaction Settings
    print('\n[bold cyan]UI and Interaction Settings:[/bold cyan]')
    config['color_output'] = questionary.confirm('Enable colored output?', default=True).ask()
    config['show_file_icons'] = questionary.confirm('Show file type icons?', default=True).ask()
    config['compact_mode'] = questionary.confirm('Use compact display mode?', default=False).ask()
    config['auto_complete'] = questionary.confirm('Enable auto-completion?', default=True).ask()
    config['history_size'] = questionary.text('Command history size', default='100').ask()
    
    # Performance Settings
    print('\n[bold cyan]Performance Settings:[/bold cyan]')
    config['max_threads'] = questionary.text('Max concurrent threads', default='4').ask()
    config['cache_size'] = questionary.text('Cache size (MB)', default='50').ask()
    config['memory_limit'] = questionary.text('Memory limit (MB)', default='512').ask()
    config['batch_size'] = questionary.text('Batch processing size', default='100').ask()
    
    # Notification Settings
    print('\n[bold cyan]Notification Settings:[/bold cyan]')
    config['enable_notifications'] = questionary.confirm('Enable notifications?', default=False).ask()
    config['notification_sound'] = questionary.confirm('Play notification sounds?', default=False).ask()
    config['email_notifications'] = questionary.confirm('Send email notifications?', default=False).ask()
    
    # Folder Configuration
    print('\n[bold cyan]Folder Configuration:[/bold cyan]')
    folders = questionary.text('Default folders to watch (comma-separated, e.g. ~/Downloads,~/Documents)').ask()
    config['folders'] = [os.path.expanduser(f.strip()) for f in folders.split(',') if f.strip()]
    config['auto_scan_folders'] = questionary.confirm('Auto-scan watched folders?', default=True).ask()
    config['folder_scan_interval'] = questionary.text('Folder scan interval (minutes)', default='60').ask()
    
    # Advanced Settings
    print('\n[bold cyan]Advanced Settings:[/bold cyan]')
    config['log_level'] = questionary.select('Log level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO').ask()
    config['log_file'] = questionary.text('Log file path', default='~/.overseer/overseer.log').ask()
    config['temp_dir'] = questionary.text('Temporary directory', default='/tmp/overseer').ask()
    config['backup_dir'] = questionary.text('Backup directory', default='~/.overseer/backups').ask()
    
    # Convert string values to appropriate types
    config = _convert_config_types(config)
    
    # Use secure config manager to save with proper permissions
    try:
        from .security.secure_config_manager import SecureConfigManager, ConfigSecurityLevel
        config_manager = SecureConfigManager()
        success = config_manager.save_config("config.json", config, ConfigSecurityLevel.PRIVATE)
        if success:
            print(f'✅ Settings saved securely to {CONFIG_PATH}')
        else:
            print(f'⚠️  Settings saved to {CONFIG_PATH} (security protection failed)')
    except ImportError:
        # Fallback to original method
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        print(f'Settings saved to {CONFIG_PATH}.')
    
    return config

def _convert_config_types(config):
    """Convert string config values to appropriate types"""
    type_conversions = {
        'gemini_max_tokens': int,
        'gemini_temperature': float,
        'local_max_tokens': int,
        'local_temperature': float,
        'max_files_per_folder': int,
        'command_timeout': int,
        'max_file_size': int,
        'search_depth': int,
        'index_update_frequency': int,
        'search_results_limit': int,
        'history_size': int,
        'max_threads': int,
        'cache_size': int,
        'memory_limit': int,
        'batch_size': int,
        'folder_scan_interval': int,
    }
    
    for key, convert_func in type_conversions.items():
        if key in config:
            try:
                config[key] = convert_func(config[key])
            except (ValueError, TypeError):
                # Keep original value if conversion fails
                pass
    
    return config

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return first_run_setup()
    
    # Use secure config manager to load with security checks
    try:
        from .security.secure_config_manager import SecureConfigManager
        config_manager = SecureConfigManager()
        config = config_manager.load_config("config.json")
        if config is None:
            # Fallback to original method if secure loading fails
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        return config
    except ImportError:
        # Fallback to original method
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)

def print_file_results(results):
    if not results:
        console.print('[yellow]No files found.[/yellow]')
        return
    for path, ftype, size, mtime, tags in results:
        console.print(f'[blue]{path}[/blue] | type: {ftype} | size: {size} | mtime: {mtime} | tags: {tags}')

def interactive_settings_editor(config):
    print('[bold cyan]Overseer Settings Editor[/bold cyan]')
    print('=' * 50)
    
    # Load current values with defaults
    llm_mode = config.get('llm_mode', 'local')
    gemini_api_key = config.get('gemini_api_key', os.environ.get('GOOGLE_API_KEY', ''))
    local_model_name = config.get('local_model_name', 'google/gemma-1.1-3b-it')
    gemini_model_name = config.get('gemini_model_name', 'gemini-2.5-flash-lite')
    
    answers = {}
    
    # Basic LLM Configuration
    print('\n[bold yellow]Basic LLM Configuration:[/bold yellow]')
    answers['llm_mode'] = questionary.select('LLM mode', choices=['local', 'gemini'], default=llm_mode).ask()
    
    if answers['llm_mode'] == 'gemini':
        answers['gemini_api_key'] = questionary.text('Gemini API key', default=gemini_api_key).ask()
        answers['gemini_model_name'] = questionary.text('Gemini model name', default=gemini_model_name).ask()
        answers['gemini_max_tokens'] = questionary.text('Max tokens for Gemini responses', default=str(config.get('gemini_max_tokens', '2048'))).ask()
        answers['gemini_temperature'] = questionary.text('Temperature (0.0-1.0)', default=str(config.get('gemini_temperature', '0.7'))).ask()
    else:
        answers['local_model_name'] = questionary.text('Local model name', default=local_model_name).ask()
        answers['local_max_tokens'] = questionary.text('Max tokens for local model', default=str(config.get('local_max_tokens', '1024'))).ask()
        answers['local_temperature'] = questionary.text('Temperature (0.0-1.0)', default=str(config.get('local_temperature', '0.7'))).ask()
    
    # System Behavior Settings
    print('\n[bold yellow]System Behavior Settings:[/bold yellow]')
    answers['debug'] = questionary.confirm('Enable debug mode?', default=config.get('debug', False)).ask()
    answers['log'] = questionary.confirm('Enable log mode?', default=config.get('log', False)).ask()
    answers['verbose_output'] = questionary.confirm('Enable verbose output?', default=config.get('verbose_output', False)).ask()
    answers['show_progress'] = questionary.confirm('Show progress bars?', default=config.get('show_progress', True)).ask()
    answers['auto_save'] = questionary.confirm('Auto-save session data?', default=config.get('auto_save', True)).ask()
    
    # File Management Settings
    print('\n[bold yellow]File Management Settings:[/bold yellow]')
    answers['file_indexing'] = questionary.confirm('Enable file indexing?', default=config.get('file_indexing', False)).ask()
    answers['auto_organize_enabled'] = questionary.confirm('Enable auto-organize feature?', default=config.get('auto_organize_enabled', True)).ask()
    answers['max_files_per_folder'] = questionary.text('Max files per folder for auto-organize', default=str(config.get('max_files_per_folder', '100'))).ask()
    answers['confirm_moves'] = questionary.confirm('Confirm file moves by default?', default=config.get('confirm_moves', True)).ask()
    answers['backup_before_move'] = questionary.confirm('Create backup before moving files?', default=config.get('backup_before_move', False)).ask()
    answers['scan_hidden_files'] = questionary.confirm('Include hidden files in scans?', default=config.get('scan_hidden_files', False)).ask()
    answers['exclude_patterns'] = questionary.text('File patterns to exclude (comma-separated)', default=config.get('exclude_patterns', '*.tmp,*.log,.DS_Store')).ask()
    
    # Security Settings
    print('\n[bold yellow]Security Settings:[/bold yellow]')
    answers['full_control'] = questionary.confirm('Enable full control mode by default?', default=config.get('full_control', False)).ask()
    answers['always_confirm_commands'] = questionary.confirm('Always confirm before running system/tool commands?', default=config.get('always_confirm_commands', True)).ask()
    answers['sandbox_mode'] = questionary.select('Default sandbox mode', choices=['dry_run', 'simulation', 'isolated', 'validation'], default=config.get('sandbox_mode', 'simulation')).ask()
    answers['command_timeout'] = questionary.text('Command timeout (seconds)', default=str(config.get('command_timeout', '30'))).ask()
    answers['max_file_size'] = questionary.text('Max file size to process (MB)', default=str(config.get('max_file_size', '100'))).ask()
    answers['secure_config'] = questionary.confirm('Use secure config manager?', default=config.get('secure_config', True)).ask()
    
    # Search and Indexing Settings
    print('\n[bold yellow]Search and Indexing Settings:[/bold yellow]')
    answers['search_depth'] = questionary.text('Search depth (levels)', default=str(config.get('search_depth', '3'))).ask()
    answers['index_update_frequency'] = questionary.text('Index update frequency (hours)', default=str(config.get('index_update_frequency', '24'))).ask()
    answers['search_results_limit'] = questionary.text('Max search results', default=str(config.get('search_results_limit', '50'))).ask()
    answers['fuzzy_search'] = questionary.confirm('Enable fuzzy search?', default=config.get('fuzzy_search', True)).ask()
    answers['search_in_content'] = questionary.confirm('Search in file contents?', default=config.get('search_in_content', False)).ask()
    
    # UI and Interaction Settings
    print('\n[bold yellow]UI and Interaction Settings:[/bold yellow]')
    answers['color_output'] = questionary.confirm('Enable colored output?', default=config.get('color_output', True)).ask()
    answers['show_file_icons'] = questionary.confirm('Show file type icons?', default=config.get('show_file_icons', True)).ask()
    answers['compact_mode'] = questionary.confirm('Use compact display mode?', default=config.get('compact_mode', False)).ask()
    answers['auto_complete'] = questionary.confirm('Enable auto-completion?', default=config.get('auto_complete', True)).ask()
    answers['history_size'] = questionary.text('Command history size', default=str(config.get('history_size', '100'))).ask()
    
    # Performance Settings
    print('\n[bold yellow]Performance Settings:[/bold yellow]')
    answers['max_threads'] = questionary.text('Max concurrent threads', default=str(config.get('max_threads', '4'))).ask()
    answers['cache_size'] = questionary.text('Cache size (MB)', default=str(config.get('cache_size', '50'))).ask()
    answers['memory_limit'] = questionary.text('Memory limit (MB)', default=str(config.get('memory_limit', '512'))).ask()
    answers['batch_size'] = questionary.text('Batch processing size', default=str(config.get('batch_size', '100'))).ask()
    
    # Notification Settings
    print('\n[bold yellow]Notification Settings:[/bold yellow]')
    answers['enable_notifications'] = questionary.confirm('Enable notifications?', default=config.get('enable_notifications', False)).ask()
    answers['notification_sound'] = questionary.confirm('Play notification sounds?', default=config.get('notification_sound', False)).ask()
    answers['email_notifications'] = questionary.confirm('Send email notifications?', default=config.get('email_notifications', False)).ask()
    
    # Folder Configuration
    print('\n[bold yellow]Folder Configuration:[/bold yellow]')
    folders = questionary.text('Default folders to watch (comma-separated)', default=','.join(config.get('folders', []))).ask()
    answers['folders'] = [os.path.expanduser(f.strip()) for f in folders.split(',') if f.strip()]
    answers['auto_scan_folders'] = questionary.confirm('Auto-scan watched folders?', default=config.get('auto_scan_folders', True)).ask()
    answers['folder_scan_interval'] = questionary.text('Folder scan interval (minutes)', default=str(config.get('folder_scan_interval', '60'))).ask()
    
    # Advanced Settings
    print('\n[bold yellow]Advanced Settings:[/bold yellow]')
    answers['log_level'] = questionary.select('Log level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default=config.get('log_level', 'INFO')).ask()
    answers['log_file'] = questionary.text('Log file path', default=config.get('log_file', '~/.overseer/overseer.log')).ask()
    answers['temp_dir'] = questionary.text('Temporary directory', default=config.get('temp_dir', '/tmp/overseer')).ask()
    answers['backup_dir'] = questionary.text('Backup directory', default=config.get('backup_dir', '~/.overseer/backups')).ask()
    
    # Convert string values to appropriate types
    answers = _convert_config_types(answers)
    
    # Use secure config manager to save with proper permissions
    try:
        from .security.secure_config_manager import SecureConfigManager, ConfigSecurityLevel
        config_manager = SecureConfigManager()
        success = config_manager.save_config("config.json", answers, ConfigSecurityLevel.PRIVATE)
        if success:
            print(f'✅ Settings saved securely to {CONFIG_PATH}')
        else:
            print(f'⚠️  Settings saved to {CONFIG_PATH} (security protection failed)')
    except ImportError:
        # Fallback to original method
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as f:
            json.dump(answers, f, indent=2)
        print(f'Settings saved to {CONFIG_PATH}.')
    
    return answers

def extract_action(response):
    """Extracts action and parameters from LLM response, robust to format variations."""
    # Look for ACTION: <action> <params> anywhere in the response (case-insensitive)
    match = re.search(r'(?i)action:\s*([a-zA-Z_]+)\s*(.*)', response)
    if match:
        action = match.group(1).strip().lower()
        params = match.group(2).strip()
        return action, params
    # Fallback: look for just <action> <params> at the start of a line
    match2 = re.search(r'^([a-zA-Z_]+)\s+(.*)', response, re.MULTILINE)
    if match2:
        action = match2.group(1).strip().lower()
        params = match2.group(2).strip()
        return action, params
    return None, None

def extract_plan(response):
    """Extracts plan steps from LLM response."""
    # Look for PLAN: <step1> | <step2> | <step3> anywhere in the response (case-insensitive)
    match = re.search(r'(?i)plan:\s*(.*)', response)
    if match:
        plan_text = match.group(1).strip()
        # Split by | and clean up each step
        steps = [step.strip() for step in plan_text.split('|') if step.strip()]
        return steps
    return None

def get_system_info():
    os_name = platform.system()
    os_version = platform.version()
    os_release = platform.release()
    if os_name == 'Darwin':
        try:
            import subprocess
            mac_ver = subprocess.check_output(['sw_vers', '-productVersion']).decode().strip()
            return f"System info: macOS {mac_ver} (Darwin {os_release})"
        except Exception:
            return f"System info: macOS (Darwin {os_release})"
    elif os_name == 'Linux':
        try:
            import distro
            distro_name = distro.name(pretty=True)
            return f"System info: Linux {distro_name} (Kernel {os_release})"
        except Exception:
            return f"System info: Linux (Kernel {os_release})"
    elif os_name == 'Windows':
        return f"System info: Windows {os_release}"
    else:
        return f"System info: {os_name} {os_release}"

def list_folder_with_confirmation(path, db_fallback_func):
    import os
    try:
        import questionary
        confirm = questionary.confirm(f"Do you want to list the contents of {path}?").ask()
    except ImportError:
        confirm = input(f"Do you want to list the contents of {path}? (y/n): ").strip().lower() in ('y', 'yes')
    if not confirm:
        return "[Cancelled] Folder listing not performed."
    try:
        entries = os.listdir(os.path.expanduser(path))
        details = []
        for entry in entries:
            full_path = os.path.join(os.path.expanduser(path), entry)
            try:
                stat = os.stat(full_path)
                size = stat.st_size
                mtime = stat.st_mtime
                details.append(f"{entry}\t{size} bytes\tmodified: {mtime}")
            except Exception:
                details.append(f"{entry}\t[error reading details]")
        if details:
            return f"Contents of {path}:\n" + "\n".join(details)
        else:
            return f"[Empty] {path} has no files."
    except Exception as e:
        # Fallback to DB
        db_files = db_fallback_func(path)
        if db_files:
            return f"[Fallback: DB] Files in {path}:\n" + "\n".join(db_files)
        return f"[Error] Could not list {path}: {e}"

def check_proactive_suggestions():
    suggestions = []
    # Downloads cleanup trigger
    downloads = os.path.expanduser('~/Downloads')
    if os.path.isdir(downloads):
        files = [os.path.join(downloads, f) for f in os.listdir(downloads) if os.path.isfile(os.path.join(downloads, f))]
        total_size = sum(os.path.getsize(f) for f in files) if files else 0
        old_files = [f for f in files if (time.time() - os.path.getmtime(f)) > 30*24*3600]
        if total_size > 1e9 or len(old_files) > 10:
            suggestions.append({
                'message': f"Your Downloads folder is {total_size/1e9:.2f}GB and has {len(old_files)} files older than 30 days. Review and clean up?",
                'action': lambda: list_folder_with_confirmation(downloads, lambda folder_path: [])
            })
    # ...add more triggers here in the future...
    for s in suggestions:
        try:
            import questionary
            if questionary.confirm(s['message']).ask():
                s['action']()
        except ImportError:
            confirm = input(s['message'] + ' (y/n): ').strip().lower() in ('y', 'yes')
            if confirm:
                s['action']()

def run_command_with_sandbox(command, path=None, always_confirm=True):
    """Run command with sandbox protection using config settings."""
    config = load_config()
    
    # Get settings from config with defaults
    sandbox_mode = config.get('sandbox_mode', 'simulation')
    command_timeout = config.get('command_timeout', 30)
    max_file_size = config.get('max_file_size', 100)
    always_confirm_commands = config.get('always_confirm_commands', True)
    color_output = config.get('color_output', True)
    show_progress = config.get('show_progress', True)
    verbose_output = config.get('verbose_output', False)
    
    # Override with function parameter if provided
    if always_confirm:
        always_confirm_commands = always_confirm
    
    console = Console(force_terminal=color_output)
    
    if verbose_output:
        console.print(f'[cyan]Command:[/cyan] {command}')
        console.print(f'[cyan]Path:[/cyan] {path or "current directory"}')
        console.print(f'[cyan]Sandbox Mode:[/cyan] {sandbox_mode}')
        console.print(f'[cyan]Timeout:[/cyan] {command_timeout}s')
        console.print(f'[cyan]Max File Size:[/cyan] {max_file_size}MB')
    
    try:
        from .security.command_sandbox import sandbox_execute, SandboxMode
        
        # Convert string to enum
        mode_map = {
            'dry_run': SandboxMode.DRY_RUN,
            'simulation': SandboxMode.SIMULATION,
            'isolated': SandboxMode.ISOLATED,
            'validation': SandboxMode.VALIDATION
        }
        sandbox_mode_enum = mode_map.get(sandbox_mode, SandboxMode.SIMULATION)
        
        # Check if command is dangerous
        def is_dangerous_command(cmd):
            dangerous_patterns = [
                r'rm\s+-rf', r'del\s+/s', r'format', r'fdisk', r'mkfs',
                r'chmod\s+777', r'chown\s+root', r'sudo\s+rm', r'sudo\s+del',
                r'killall', r'taskkill\s+/f', r'shutdown', r'reboot',
                r'init\s+0', r'halt', r'poweroff'
            ]
            cmd_lower = cmd.lower()
            return any(re.search(pattern, cmd_lower) for pattern in dangerous_patterns)
        
        if is_dangerous_command(command):
            console.print('[bold red]⚠️  DANGEROUS COMMAND DETECTED![/bold red]')
            console.print(f'[red]Command: {command}[/red]')
            console.print('[yellow]This command could cause data loss or system damage.[/yellow]')
            
            if always_confirm_commands:
                try:
                    import questionary
                    proceed = questionary.confirm(
                        "Are you absolutely sure you want to run this dangerous command?",
                        default=False
                    ).ask()
                except ImportError:
                    proceed = input("Are you absolutely sure? (y/N): ").strip().lower() in ('y', 'yes')
                
                if not proceed:
                    console.print('[bold green]overseer:[/bold green] Command cancelled.')
                    return False
        
        # Step 1: Validation
        if show_progress:
            console.print('[cyan]🔍 Validating command...[/cyan]')
        
        validation_result = sandbox_execute(command, path, SandboxMode.VALIDATION, timeout=command_timeout)
        
        if not validation_result.success:
            console.print(f'[bold red]❌ Command validation failed:[/bold red] {validation_result.error}')
            if validation_result.warnings:
                for warning in validation_result.warnings:
                    console.print(f'[yellow]⚠️  {warning}[/yellow]')
            return False
        
        # Step 2: Dry Run
        if show_progress:
            console.print('[cyan]📋 Performing dry run...[/cyan]')
        
        dry_run_result = sandbox_execute(command, path, SandboxMode.DRY_RUN, timeout=command_timeout)
        
        if not dry_run_result.success:
            console.print(f'[bold red]❌ Dry run failed:[/bold red] {dry_run_result.error}')
            return False
        
        # Show what would happen
        if dry_run_result.files_created:
            console.print('[green]Files that would be created:[/green]')
            for file in dry_run_result.files_created:
                console.print(f'  📄 {file}')
        
        if dry_run_result.files_modified:
            console.print('[yellow]Files that would be modified:[/yellow]')
            for file in dry_run_result.files_modified:
                console.print(f'  ✏️  {file}')
        
        if dry_run_result.files_deleted:
            console.print('[red]Files that would be deleted:[/red]')
            for file in dry_run_result.files_deleted:
                console.print(f'  🗑️  {file}')
        
        # Step 3: Risk Assessment
        risk_level = 'low'
        if dry_run_result.files_deleted or is_dangerous_command(command):
            risk_level = 'high'
        elif dry_run_result.files_modified:
            risk_level = 'medium'
        
        console.print(f'[bold]Risk Level:[/bold] {risk_level.upper()}')
        
        # Step 4: User Confirmation
        if always_confirm_commands:
            try:
                import questionary
                confirm = questionary.confirm(
                    f"Execute command '{command}'?",
                    default=False
                ).ask()
            except ImportError:
                confirm = input(f"Execute '{command}'? (y/N): ").strip().lower() in ('y', 'yes')
            
            if not confirm:
                console.print('[bold green]overseer:[/bold green] Command cancelled.')
                return False
        
        # Step 5: Optional Isolated Execution
        if sandbox_mode_enum == SandboxMode.ISOLATED:
            if show_progress:
                console.print('[cyan]🔒 Running in isolated environment...[/cyan]')
            
            isolated_result = sandbox_execute(command, path, SandboxMode.ISOLATED, timeout=command_timeout)
            
            if not isolated_result.success:
                console.print(f'[bold red]❌ Isolated execution failed:[/bold red] {isolated_result.error}')
                return False
            
            # Show isolated results
            if isolated_result.files_created:
                console.print('[green]Files created in isolation:[/green]')
                for file in isolated_result.files_created:
                    console.print(f'  📄 {file}')
            
            if isolated_result.files_modified:
                console.print('[yellow]Files modified in isolation:[/yellow]')
                for file in isolated_result.files_modified:
                    console.print(f'  ✏️  {file}')
            
            if isolated_result.files_deleted:
                console.print('[red]Files deleted in isolation:[/red]')
                for file in isolated_result.files_deleted:
                    console.print(f'  🗑️  {file}')
            
            # Ask for final confirmation
            try:
                import questionary
                final_confirm = questionary.confirm(
                    "Apply these changes to the real system?",
                    default=False
                ).ask()
            except ImportError:
                final_confirm = input("Apply changes? (y/N): ").strip().lower() in ('y', 'yes')
            
            if not final_confirm:
                console.print('[bold green]overseer:[/bold green] Changes not applied.')
                return False
        
        # Step 6: Real Execution
        if show_progress:
            console.print('[cyan]🚀 Executing command...[/cyan]')
        
        real_result = sandbox_execute(command, path, SandboxMode.SIMULATION, timeout=command_timeout)
        
        if real_result.success:
            console.print('[bold green]✅ Command executed successfully![/bold green]')
            
            if real_result.output:
                console.print('[cyan]Output:[/cyan]')
                console.print(real_result.output)
            
            if real_result.files_created:
                console.print('[green]Files created:[/green]')
                for file in real_result.files_created:
                    console.print(f'  📄 {file}')
            
            if real_result.files_modified:
                console.print('[yellow]Files modified:[/yellow]')
                for file in real_result.files_modified:
                    console.print(f'  ✏️  {file}')
            
            if real_result.files_deleted:
                console.print('[red]Files deleted:[/red]')
                for file in real_result.files_deleted:
                    console.print(f'  🗑️  {file}')
            
            return True
        else:
            console.print(f'[bold red]❌ Command execution failed:[/bold red] {real_result.error}')
            if real_result.warnings:
                for warning in real_result.warnings:
                    console.print(f'[yellow]⚠️  {warning}[/yellow]')
            return False
            
    except ImportError:
        console.print('[yellow]⚠️  Sandbox not available, running command directly...[/yellow]')
        return _run_command_basic(command, path, always_confirm_commands, console)
    except Exception as e:
        console.print(f'[bold red]❌ Sandbox error:[/bold red] {e}')
        return False

def _run_command_basic(command, path, always_confirm, console):
    """Fallback basic command execution without sandbox"""
    # Fallback to basic security check
    def is_dangerous_command(cmd):
        dangerous = ['rm ', 'mv ', 'sudo ', 'apt ', 'pip install', 'docker run', 'chmod ', 'chown ', 'kill ', 'shutdown', 'reboot']
        return any(d in cmd for d in dangerous)
    
    if always_confirm or is_dangerous_command(command):
        try:
            import questionary
            confirm = questionary.confirm(f"[DANGER] This command may modify your system: {command}\nAre you sure you want to run it?").ask()
        except ImportError:
            confirm = input(f"[DANGER] This command may modify your system: {command}\nRun it? (y/n): ").strip().lower() in ('y', 'yes')
        if not confirm:
            return "[Cancelled] Command not run."
    
    env = {"PATH": "/usr/bin:/bin"}
    try:
        result = subprocess.run(
            command, shell=True, cwd=os.path.expanduser(path or '.'), capture_output=True, text=True, env=env, timeout=60
        )
        output = result.stdout or result.stderr
        if output:
            from rich.syntax import Syntax
            syntax = Syntax(output, "bash", theme="monokai", line_numbers=False)
            console.print(syntax)
            return "[Command completed]"
        else:
            return "[No output]"
    except Exception as e:
        return f"[Error] {e}"

def show_error(message, exception=None):
    from rich.console import Console
    console = Console()
    error_msg = f"[red][ERROR][/red] {message}"
    if exception:
        error_msg += f"\n[dim]{exception}[/dim]"
    console.print(Panel(error_msg, title="Error", style="red"))

def undo_last_command():
    """Undo the last command execution"""
    try:
        # Check if security manager is available
        if hasattr(run_command_with_sandbox, 'security_manager') and run_command_with_sandbox.security_manager:
            # Get the last undo operation ID
            last_undo_id = getattr(run_command_with_sandbox, 'last_undo_operation_id', None)
            
            if last_undo_id:
                result = run_command_with_sandbox.security_manager.undo_operation(last_undo_id)
                if result['success']:
                    from rich.console import Console
                    from rich.panel import Panel
                    console = Console()
                    console.print(Panel(
                        f"✅ {result['message']}",
                        title="[green]Undo Successful[/green]",
                        border_style="green"
                    ))
                    return True
                else:
                    show_error("Failed to undo command", result.get('error', 'Unknown error'))
                    return False
            else:
                show_error("No command to undo", "No recent command found")
                return False
        else:
            show_error("Undo not available", "Security system not initialized")
            return False
    except Exception as e:
        show_error("Error during undo", str(e))
        return False

def ask_retry_skip_abort():
    try:
        import questionary
        return questionary.select(
            "What would you like to do?",
            choices=["Retry", "Skip", "Abort"]
        ).ask()
    except ImportError:
        return input("Retry, Skip, or Abort? (r/s/a): ").strip().lower()

def main():
    parser = argparse.ArgumentParser(description="Overseer CLI - System Assistant")
    parser.add_argument('--mode', choices=['local', 'gemini', 'chat', 'testing'], required=False, default=None, help='Inference mode: local, gemini, chat, or testing')
    parser.add_argument('--settings', action='store_true', help='Edit all Overseer settings interactively and exit')
    parser.add_argument('--prompt', type=str, help='Single prompt to process (otherwise REPL)')
    parser.add_argument('--scan', action='store_true', help='Scan the file system before starting CLI')
    parser.add_argument('--root', type=str, help='Root directory to scan/sort (used with --scan or --sort)')
    parser.add_argument('--sort', action='store_true', help='Sort the folder before starting CLI')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be moved, but do not move files')
    parser.add_argument('--sort-by', choices=['type', 'tag', 'llm'], default='type', help='Sort by file type, tag, or LLM')
    parser.add_argument('--auto-organize', action='store_true', help='Auto-organize all watched folders using LLM')
    parser.add_argument('--folders', nargs='+', help='Folders to auto-organize (default: home, Documents, Downloads)')
    parser.add_argument('--search-tag', type=str, help='Search for files by tag')
    parser.add_argument('--multi-tag', action='store_true', help='Use all tags as nested folders (default)')
    parser.add_argument('--single-tag', action='store_true', help='Use only the first tag as folder')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--log', action='store_true', help='Enable log mode (writes to overseer.log)')
    parser.add_argument('--ask-create-folders', action='store_true', help='Ask before creating new folders')
    parser.add_argument('--find-file', type=str, help='Find file by description (semantic search)')
    parser.add_argument('--full-control', action='store_true', help='Enable full control (no user prompts, all actions automatic, DANGEROUS!)')
    args = parser.parse_args()

    if args.settings:
        config = load_config()
        interactive_settings_editor(config)
        return

    config = load_config()
    set_debug(config.get('debug', False))
    set_log(config.get('log', False))
    debug('Debug mode enabled.')
    if config.get('log', False):
        debug('Log mode enabled.')
    full_control = config.get('full_control', False) or args.full_control
    if full_control:
        console.print('[red][WARNING] FULL CONTROL MODE ENABLED! Overseer will take all actions automatically. Proceed with caution![/red]')

    # Select LLM backend for LLM-assisted sorting/auto-organize
    if args.mode == 'local':
        from .inference.inference_local import LocalLLM
        model_name = config.get('local_model_name', 'google/gemma-1.1-3b-it')
        LocalLLM._model_name = model_name
        llm_backend = LocalLLM().run
    elif args.mode == 'gemini':
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            console.print('[red]Error: GOOGLE_API_KEY environment variable not set.[/red]')
            exit(1)
        llm_backend = GeminiAPI(api_key).run
    elif args.mode == 'chat':
        # Use config to determine backend
        llm_mode = config.get('llm_mode', 'local')
        if llm_mode == 'gemini':
            api_key = config.get('gemini_api_key', os.environ.get('GOOGLE_API_KEY'))
            gemini_model = config.get('gemini_model_name', 'gemini-1.5-flash')
            llm_backend = GeminiAPI(api_key, gemini_model).run
        else:
            from .inference.inference_local import LocalLLM
            model_name = config.get('local_model_name', 'google/gemma-1.1-3b-it')
            LocalLLM._model_name = model_name
            llm_backend = LocalLLM().run
    else: # Default to chat mode if no mode is provided
        llm_mode = config.get('llm_mode', 'local')
        if llm_mode == 'gemini':
            api_key = config.get('gemini_api_key', os.environ.get('GOOGLE_API_KEY'))
            gemini_model = config.get('gemini_model_name', 'gemini-1.5-flash')
            llm_backend = GeminiAPI(api_key, gemini_model).run
        else:
            from .inference.inference_local import LocalLLM
            model_name = config.get('local_model_name', 'google/gemma-1.1-3b-it')
            LocalLLM._model_name = model_name
            llm_backend = LocalLLM().run

    # File system scan if requested
    if args.scan:
        root = args.root or os.path.expanduser('~')
        console.print(f'[cyan]Scanning file system at {root}...[/cyan]')
        scan_directory(root)
        console.print('[green]Scan complete.[/green]')

    multi_tag = not args.single_tag

    # Folder sort if requested
    if args.sort:
        root = args.root or os.path.expanduser('~')
        console.print(f'[cyan]Sorting files in {root} by {args.sort_by}...[/cyan]')
        if full_control:
            console.print('[red][WARNING] FULL CONTROL: No prompts. All actions will be automatic![/red]')
        moved = sort_folder(
            root,
            dry_run=args.dry_run,
            sort_by=args.sort_by,
            llm_backend=llm_backend if args.sort_by == 'llm' else None,
            multi_tag=multi_tag,
            ask_create_folder=not full_control and args.ask_create_folders,
            ask_fn=Prompt.ask if (not full_control and args.ask_create_folders) else None
        )
        if not moved:
            console.print('[yellow]No files to sort.[/yellow]')
        else:
            for src, dst in moved:
                console.print(f"{'[DRY RUN] ' if args.dry_run else ''}Moved: {src} -> {dst}")
        console.print('[green]Sort complete.[/green]')

    # Auto-organize if requested
    if args.auto_organize:
        if args.folders:
            folders = args.folders
        else:
            home = os.path.expanduser('~')
            folders = [os.path.join(home, 'Downloads')]  # Safer default
            console.print(f'[yellow]Using default folder: {folders[0]}[/yellow]')
            console.print('[yellow]Use --folders to specify other folders[/yellow]')
        console.print(f'[cyan]Auto-organizing folders: {folders}...[/cyan]')
        if full_control:
            console.print('[red][WARNING] FULL CONTROL: No prompts. All actions will be automatic![/red]')
        moved = auto_organize(
            folders, 
            llm_backend, 
            dry_run=args.dry_run,
            confirm_moves=not full_control,
            max_files_per_folder=100
        )
        if not moved:
            console.print('[yellow]No files to move.[/yellow]')
        else:
            for src, dst in moved:
                console.print(f"{'[DRY RUN] ' if args.dry_run else ''}Moved: {src} -> {dst}")
        console.print('[green]Auto-organize complete.[/green]')

    # Tag-based search if requested
    if args.search_tag:
        console.print(f'[cyan]Searching for files with tag: {args.search_tag}[/cyan]')
        results = search_by_tag(args.search_tag)
        print_file_results(results)
        return

    if args.find_file:
        console.print(f'[cyan]Searching for file: {args.find_file}[/cyan]')
        results = search_by_description(args.find_file)
        print_file_results(results)
        return

    def run_backend(prompt):
        return process_user_input(prompt)

    # Single prompt mode
    if args.prompt:
        response = run_backend(args.prompt)
        console.print(f'[bold green]Overseer:[/bold green] {response}')
        return

    # Add testing mode
    if args.mode == 'testing':
        console.print('[bold cyan]Overseer Testing Mode[/bold cyan]')
        results = []
        
        # Test DB
        try:
            from .db.filesystem_db import get_connection
            conn = get_connection()
            conn.close()
            results.append('[green]Database connection: OK[/green]')
        except Exception as e:
            results.append(f'[red]Database connection: FAIL ({e})[/red]')
        
        # Test LLM
        try:
            llm_mode = config.get('llm_mode', 'local')
            if llm_mode == 'gemini':
                api_key = config.get('gemini_api_key', os.environ.get('GOOGLE_API_KEY'))
                llm = GeminiAPI(api_key)
                out = llm.run('Hello')
                results.append('[green]Gemini API: OK[/green]')
            else:
                from .inference.inference_local import LocalLLM
                model_name = config.get('local_model_name', 'google/gemma-1.1-3b-it')
                LocalLLM._model_name = model_name
                llm = LocalLLM()
                out = llm.run('Hello')
                results.append('[green]Local LLM: OK[/green]')
        except Exception as e:
            results.append(f'[red]LLM: FAIL ({e})[/red]')
        
        # Test file scan
        try:
            scan_directory(os.path.expanduser('~'))
            results.append('[green]Filesystem scan: OK[/green]')
        except Exception as e:
            results.append(f'[red]Filesystem scan: FAIL ({e})[/red]')
        
        # Display test results
        for r in results:
            console.print(r)
        
        # Ask about file indexing
        console.print('\n[bold yellow]File Indexing Option:[/bold yellow]')
        try:
            import questionary
            index_files = questionary.confirm(
                "Would you like to index files for faster search?",
                default=True
            ).ask()
        except ImportError:
            index_files = input("Would you like to index files for faster search? (y/n): ").strip().lower() in ('y', 'yes')
        
        if index_files:
            console.print('[cyan]Starting file indexing...[/cyan]')
            try:
                from .features.filesystem_scanner import scan_directory
                home_dir = os.path.expanduser('~')
                console.print(f'[cyan]Indexing files in {home_dir}...[/cyan]')
                
                # Scan with progress indication
                import time
                start_time = time.time()
                scan_directory(home_dir)
                end_time = time.time()
                
                console.print(f'[green]✅ File indexing completed in {end_time - start_time:.2f} seconds[/green]')
                console.print('[green]Files are now indexed for fast search![/green]')
                
            except Exception as e:
                console.print(f'[red]❌ File indexing failed: {e}[/red]')
        else:
            console.print('[yellow]File indexing skipped. You can enable it later in settings.[/yellow]')
        
        console.print('\n[bold green]Testing mode completed![/bold green]')
        return

    check_proactive_suggestions()

    PROMPT_TEMPLATE = f'''
{get_system_info()}
You are Overseer, an AI system assistant. You can:
- Sort files (ACTION: sort_files path=<folder>)
- Search for files (ACTION: search_files query=<query>)
- Tag files (ACTION: tag_file path=<file> tags=<tags>)
- Auto-organize folders (ACTION: auto_organize folders=<folders>)
- List the contents of a folder (ACTION: list_folder path=<folder>)
- Run system/tool commands with sandbox protection (ACTION: run_command command="<cmd>" path=<folder>)
- Audit configuration security (ACTION: audit_config)
- Fix configuration security issues (ACTION: fix_config_security)
- Check file permissions (ACTION: check_permissions path=<file>)
- Answer general questions or have a conversation

When the user asks for something, reply with either:
- A conversational response (for greetings, small talk, etc.)
- A detailed plan: PLAN: <step1> | <step2> | <step3> (for complex tasks)
- An action: ACTION: <action> <params> (for simple tasks)

For complex tasks, break them into steps and ask for confirmation at each step.
Keep plans concise but clear. Use | to separate steps.

Examples:
User: hi
Overseer: Hello! How can I help you today?

User: sort my downloads
Overseer: ACTION: sort_files path=~/Downloads

User: organize my entire system
Overseer: PLAN: audit_config | auto_organize folders=~/Downloads,~/Documents,~/Desktop | fix_config_security

User: set up my development environment
Overseer: PLAN: check_permissions path=~/.ssh/id_rsa | run_command command="git config --global user.name" | run_command command="pip install numpy pandas matplotlib"

User: find my tax file
Overseer: ACTION: search_files query=tax

User: tag report.pdf as important
Overseer: ACTION: tag_file path=report.pdf tags=important

User: what is in my downloads folder
Overseer: ACTION: list_folder path=~/Downloads

User: organize my downloads folder
Overseer: ACTION: auto_organize folders=~/Downloads

User: check my git status
Overseer: ACTION: run_command command="git status" path=~/project

User: pull the latest Docker image for nginx
Overseer: ACTION: run_command command="docker pull nginx"

User: install numpy with pip
Overseer: ACTION: run_command command="pip install numpy"

User: list running Docker containers
Overseer: ACTION: run_command command="docker ps"

User: update all packages with apt
Overseer: PLAN: run_command command="sudo apt update" | run_command command="sudo apt upgrade"

User: check my config security
Overseer: ACTION: audit_config

User: fix my config security
Overseer: ACTION: fix_config_security

User: check permissions on my config file
Overseer: ACTION: check_permissions path=~/.overseer/config.json
'''

    session = SessionContext()

    # REPL mode
    if (len(sys.argv) == 1) or (args.mode == 'chat') or (args.mode is None):
        config = load_config()
        set_debug(config.get('debug', False))
        set_log(config.get('log', False))
        debug('Debug mode enabled.')
        if config.get('log', False):
            debug('Log mode enabled.')
        full_control = config.get('full_control', False) or getattr(args, 'full_control', False)
        if full_control:
            console.print('[red][WARNING] FULL CONTROL MODE ENABLED! Overseer will take all actions automatically. Proceed with caution![/red]')
        always_confirm_commands = config.get('always_confirm_commands', True)
        # Select LLM backend based on config
        llm_mode = config.get('llm_mode', 'local')
        if llm_mode == 'gemini':
            api_key = config.get('gemini_api_key', os.environ.get('GOOGLE_API_KEY'))
            gemini_model = config.get('gemini_model_name', 'gemini-1.5-flash')
            llm_backend = GeminiAPI(api_key, gemini_model).run
        else:
            from .inference.inference_local import LocalLLM
            model_name = config.get('local_model_name', 'google/gemma-1.1-3b-it')
            LocalLLM._model_name = model_name
            llm_backend = LocalLLM().run
        console.print('[bold cyan]Overseer CLI (type "exit" to quit)[/bold cyan]')
        console.print('[bold green]overseer:[/bold green] How can I help you today?')
        full_control_repl = False
        while True:
            try:
                user_input = Prompt.ask('[bold yellow]user[/bold yellow]')
                if user_input.strip().lower() in ('exit', 'quit'):
                    break
                if user_input.strip().lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    console.print('[bold cyan]Overseer CLI (type "exit" to quit)[/bold cyan]')
                    console.print('[bold green]overseer:[/bold green] How can I help you today?')
                    continue
                if user_input.strip().lower() == 'undo':
                    undo_last_command()
                    continue
                if user_input.strip().lower() == 'settings':
                    config = interactive_settings_editor(config)
                    set_debug(config.get('debug', False))
                    set_log(config.get('log', False))
                    # Update LLM backend if changed
                    llm_mode = config.get('llm_mode', 'local')
                    if llm_mode == 'gemini':
                        gemini_model = config.get('gemini_model_name', 'gemini-1.5-flash')
                        api_key = config.get('gemini_api_key', os.environ.get('GOOGLE_API_KEY'))
                        llm_backend = GeminiAPI(api_key, gemini_model).run
                    else:
                        llm_backend = LocalLLM().run
                    always_confirm_commands = config.get('always_confirm_commands', True)
                    continue
                # Compose prompt for LLM with context
                system_info = get_system_info()
                context_summary = session.summary()
                prompt = f"{system_info}\nRecent context:\n{context_summary}\n" + PROMPT_TEMPLATE + f'\nUser: {user_input}\nOverseer:'
                try:
                    response = llm_backend(prompt).strip()
                except Exception as e:
                    show_error("LLM call failed.", e)
                    continue
                # Robust action extraction
                try:
                    action, params = extract_action(response)
                    plan_steps = extract_plan(response)
                except Exception as e:
                    show_error("Failed to extract action from LLM response.", e)
                    continue
                
                # Handle plans with step-by-step confirmation
                if plan_steps:
                    debug(f"[PLAN DETECTED] {len(plan_steps)} steps")
                    console.print(f'[bold green]overseer:[/bold green] I have a {len(plan_steps)}-step plan for you:')
                    
                    for i, step in enumerate(plan_steps, 1):
                        console.print(f'  {i}. {step}')
                    
                    try:
                        import questionary
                        confirm = questionary.confirm("Should I proceed with this plan?").ask()
                    except ImportError:
                        confirm = input("Should I proceed with this plan? (y/n): ").strip().lower() in ('y', 'yes')
                    
                    if not confirm:
                        console.print('[bold green]overseer:[/bold green] Plan cancelled.')
                        continue
                    
                    # Execute plan step by step
                    for i, step in enumerate(plan_steps, 1):
                        console.print(f'\n[bold cyan]Step {i}/{len(plan_steps)}:[/bold cyan] {step}')
                        
                        # Extract action from step
                        step_action, step_params = extract_action(step)
                        if not step_action:
                            console.print(f'[bold yellow]overseer:[/bold yellow] Could not parse step {i}, skipping...')
                            continue
                        
                        # Ask for confirmation for each step
                        if not full_control_repl:
                            try:
                                import questionary
                                step_confirm = questionary.confirm(f"Execute step {i}?").ask()
                            except ImportError:
                                step_confirm = input(f"Execute step {i}? (y/n): ").strip().lower() in ('y', 'yes')
                            
                            if not step_confirm:
                                console.print(f'[bold green]overseer:[/bold green] Step {i} skipped.')
                                continue
                        
                        # Execute the step
                        try:
                            # Use the same action handling logic for each step
                            if step_action == 'sort_files':
                                match = re.search(r'path=([^ ]+)', step_params)
                                path = match.group(1).strip() if match else os.path.expanduser('~')
                                console.print(f'[bold green]overseer:[/bold green] Sorting files in {path}...')
                                moved = sort_folder(path, ask_create_folder=False, ask_fn=None)
                                if not moved:
                                    console.print('[bold green]overseer:[/bold green] No files to sort.')
                                else:
                                    for src, dst in moved:
                                        console.print(f'[bold green]overseer:[/bold green] Moved: {src} -> {dst}')
                            
                            elif step_action == 'search_files':
                                match = re.search(r'query=([^ ]+)', step_params)
                                query = match.group(1).strip() if match else ''
                                if not query:
                                    console.print('[bold red]overseer:[/bold red] No search query specified.')
                                    continue
                                from .features.file_search import search_files
                                results = search_files(query, config=config)
                                session.last_selected_file = results
                                session.last_action = f'search_files: {query}'
                                session.history.append((user_input, step_action, results))
                                console.print(f'[bold green]overseer:[/bold green] {results}')
                            
                            elif step_action == 'list_folder':
                                match = re.search(r'path=([^ ]+)', step_params)
                                folder = match.group(1).strip() if match else os.path.expanduser('~')
                                from .features.file_search import get_all_files
                                def db_fallback_func(folder_path):
                                    files = get_all_files(os.path.expanduser(folder_path))
                                    return files
                                result = list_folder_with_confirmation(folder, db_fallback_func)
                                session.last_action = f'list_folder: {folder}'
                                session.history.append((user_input, step_action, result))
                                console.print(f'[bold green]overseer:[/bold green] {result}')
                            
                            elif step_action == 'tag_file':
                                match = re.search(r'path=([^ ]+)\s+tags=([^ ]+)', step_params)
                                if match:
                                    file_path = match.group(1).strip()
                                    tags = match.group(2).strip()
                                    tag_file(file_path, tags)
                                    new_tags = get_tags(file_path)
                                    console.print(f'[bold green]overseer:[/bold green] Tagged {file_path} with: {new_tags}')
                                else:
                                    console.print('[bold green]overseer:[/bold green] Could not parse tag command.')
                            
                            elif step_action == 'auto_organize':
                                match = re.search(r'folders=([^ ]+)', step_params)
                                folders = [os.path.expanduser(f.strip()) for f in match.group(1).split(',')] if match else []
                                if not folders:
                                    home = os.path.expanduser('~')
                                    folders = [os.path.join(home, 'Downloads')]
                                    console.print(f'[yellow]Using default folder: {folders[0]}[/yellow]')
                                moved = auto_organize(
                                    folders, 
                                    llm_backend,
                                    config=config,  # Pass config to use settings
                                    dry_run=False,
                                    confirm_moves=False
                                )
                                if not moved:
                                    console.print('[bold green]overseer:[/bold green] No files to move.')
                                else:
                                    for src, dst in moved:
                                        console.print(f'[bold green]overseer:[/bold green] Moved: {src} -> {dst}')
                            
                            elif step_action == 'run_command':
                                match_cmd = re.search(r'command="([^"]+)"', step_params)
                                match_path = re.search(r'path=([^ ]+)', step_params)
                                command = match_cmd.group(1) if match_cmd else ''
                                path = match_path.group(1).strip() if match_path else None
                                result = run_command_with_sandbox(command, path, always_confirm=False)
                                session.last_command = command
                                session.last_action = f'run_command: {command}'
                                session.history.append((user_input, step_action, result))
                                console.print(f'[bold green]overseer:[/bold green] {result}')
                            
                            elif step_action == 'audit_config':
                                try:
                                    from .security.secure_config_manager import SecureConfigManager
                                    config_manager = SecureConfigManager()
                                    audit_results = config_manager.audit_config_files()
                                    secure_count = sum(1 for result in audit_results.values() if result.get('secure', False))
                                    total_count = len(audit_results)
                                    console.print(f'[bold green]overseer:[/bold green] Configuration security audit completed.')
                                    console.print(f'[bold green]overseer:[/bold green] {secure_count}/{total_count} files are secure.')
                                    if secure_count < total_count:
                                        console.print(f'[bold yellow]overseer:[/bold yellow] {total_count - secure_count} files have security issues.')
                                    session.last_action = f'audit_config: {secure_count}/{total_count} secure'
                                    session.history.append((user_input, step_action, f'{secure_count}/{total_count} secure'))
                                except ImportError:
                                    console.print('[bold red]overseer:[/bold red] Secure config manager not available.')
                                except Exception as e:
                                    console.print(f'[bold red]overseer:[/bold red] Audit failed: {e}')
                            
                            elif step_action == 'fix_config_security':
                                try:
                                    from .security.secure_config_manager import SecureConfigManager
                                    config_manager = SecureConfigManager()
                                    console.print(f'[bold green]overseer:[/bold green] Fixing configuration security issues...')
                                    success = config_manager.fix_config_security()
                                    if success:
                                        console.print(f'[bold green]overseer:[/bold green] All configuration files are now secure.')
                                    else:
                                        console.print(f'[bold yellow]overseer:[/bold yellow] Some security issues could not be fixed automatically.')
                                    session.last_action = f'fix_config_security: {"success" if success else "partial"}'
                                    session.history.append((user_input, step_action, "success" if success else "partial"))
                                except ImportError:
                                    console.print('[bold red]overseer:[/bold red] Secure config manager not available.')
                                except Exception as e:
                                    console.print(f'[bold red]overseer:[/bold red] Security fix failed: {e}')
                            
                            elif step_action == 'check_permissions':
                                match = re.search(r'path=([^ ]+)', step_params)
                                file_path = match.group(1).strip() if match else None
                                if not file_path:
                                    console.print('[bold red]overseer:[/bold red] No file path specified.')
                                    continue
                                try:
                                    from .security.secure_config_manager import SecureConfigManager
                                    config_manager = SecureConfigManager()
                                    security_status = config_manager.check_file_security(file_path)
                                    if security_status['exists']:
                                        status_icon = "✅" if security_status['secure'] else "⚠️"
                                        console.print(f'[bold green]overseer:[/bold green] {status_icon} {file_path}')
                                        console.print(f'[bold green]overseer:[/bold green] Permissions: {security_status["permissions"]}')
                                        if not security_status['secure']:
                                            console.print(f'[bold yellow]overseer:[/bold yellow] Issues:')
                                            for issue in security_status['issues']:
                                                console.print(f'[bold yellow]overseer:[/bold yellow]   - {issue}')
                                    else:
                                        console.print(f'[bold red]overseer:[/bold red] File does not exist: {file_path}')
                                    session.last_action = f'check_permissions: {file_path}'
                                    session.history.append((user_input, step_action, file_path))
                                except ImportError:
                                    console.print('[bold red]overseer:[/bold red] Secure config manager not available.')
                                except Exception as e:
                                    console.print(f'[bold red]overseer:[/bold red] Permission check failed: {e}')
                            
                            else:
                                console.print(f'[bold green]overseer:[/bold green] Unknown action in step {i}: {step_action}')
                        
                        except Exception as e:
                            console.print(f'[bold red]overseer:[/bold red] Error in step {i}: {e}')
                            choice = ask_retry_skip_abort()
                            if choice in ('Retry', 'r'):
                                i -= 1  # Retry this step
                                continue
                            elif choice in ('Skip', 's'):
                                continue
                            elif choice in ('Abort', 'a'):
                                console.print('[bold green]overseer:[/bold green] Plan aborted.')
                                break
                    
                    console.print(f'\n[bold green]overseer:[/bold green] Plan completed!')
                    continue
                
                # Reference resolution for single actions
                try:
                    if action and any(ref in params for ref in ['the first one', 'first one', 'the last one', 'last one', 'those', 'them', 'these', 'it']):
                        for ref in ['the first one', 'first one', 'the last one', 'last one', 'those', 'them', 'these', 'it']:
                            if ref in params:
                                resolved = session.resolve_reference(ref)
                                if resolved:
                                    params = params.replace(ref, str(resolved))
                except Exception as e:
                    show_error("Reference resolution failed.", e)
                    continue
                if action:
                    debug(f"[ACTION DETECTED] {action} {params}")
                    try:
                        # Folder intent follow-up: if user said 'folder' or 'directory' and LLM gave search_files, ask if they meant list_folder
                        if action == 'search_files' and any(word in user_input.lower() for word in ['folder', 'directory']):
                            likely_folder = None
                            # Try to guess the folder from the query
                            match = re.search(r'query=([^ ]+)', params)
                            query = match.group(1).strip() if match else ''
                            if 'downloads' in query:
                                likely_folder = '~/Downloads'
                            elif 'documents' in query:
                                likely_folder = '~/Documents'
                            elif 'desktop' in query:
                                likely_folder = '~/Desktop'
                            elif os.path.isdir(os.path.expanduser(query)):
                                likely_folder = query
                            if likely_folder:
                                try:
                                    import questionary
                                    confirm = questionary.confirm(f"Did you want to list the contents of {likely_folder} instead?").ask()
                                except ImportError:
                                    confirm = input(f"Did you want to list the contents of {likely_folder} instead? (y/n): ").strip().lower() in ('y', 'yes')
                                if confirm:
                                    from .features.file_search import get_all_files
                                    def db_fallback_func(folder_path):
                                        files = get_all_files(os.path.expanduser(folder_path))
                                        return files
                                    result = list_folder_with_confirmation(likely_folder, db_fallback_func)
                                    console.print(f'[bold green]overseer:[/bold green] {result}')
                                    continue
                        if action == 'sort_files':
                            match = re.search(r'path=([^ ]+)', params)
                            path = match.group(1).strip() if match else os.path.expanduser('~')
                            console.print(f'[bold green]overseer:[/bold green] Sorting files in {path}...')
                            moved = sort_folder(path, ask_create_folder=not full_control_repl, ask_fn=Prompt.ask if not full_control_repl else None)
                            if not moved:
                                console.print('[bold green]overseer:[/bold green] No files to sort.')
                            else:
                                for src, dst in moved:
                                    console.print(f'[bold green]overseer:[/bold green] Moved: {src} -> {dst}')
                            continue
                        elif action == 'search_files':
                            match = re.search(r'query=([^ ]+)', params)
                            query = match.group(1).strip() if match else ''
                            if not query:
                                console.print('[bold red]overseer:[/bold red] No search query specified.')
                                continue
                            from .features.file_search import search_files
                            results = search_files(query, config=config)
                            session.last_selected_file = results
                            session.last_action = f'search_files: {query}'
                            session.history.append((user_input, action, results))
                            console.print(f'[bold green]overseer:[/bold green] {results}')
                            continue
                        elif action == 'list_folder':
                            match = re.search(r'path=([^ ]+)', params)
                            folder = match.group(1).strip() if match else os.path.expanduser('~')
                            from .features.file_search import get_all_files
                            def db_fallback_func(folder_path):
                                files = get_all_files(os.path.expanduser(folder_path))
                                return files
                            result = list_folder_with_confirmation(folder, db_fallback_func)
                            session.last_action = f'list_folder: {folder}'
                            session.history.append((user_input, action, result))
                            console.print(f'[bold green]overseer:[/bold green] {result}')
                            break
                        elif action == 'tag_file':
                            match = re.search(r'path=([^ ]+)\s+tags=([^ ]+)', params)
                            if match:
                                file_path = match.group(1).strip()
                                tags = match.group(2).strip()
                                tag_file(file_path, tags)
                                new_tags = get_tags(file_path)
                                console.print(f'[bold green]overseer:[/bold green] Tagged {file_path} with: {new_tags}')
                            else:
                                console.print('[bold green]overseer:[/bold green] Could not parse tag command.')
                            continue
                        elif action == 'auto_organize':
                            match = re.search(r'folders=([^ ]+)', params)
                            folders = [os.path.expanduser(f.strip()) for f in match.group(1).split(',')] if match else []
                            if not folders:
                                home = os.path.expanduser('~')
                                folders = [os.path.join(home, 'Downloads')]  # Safer default
                                console.print(f'[yellow]Using default folder: {folders[0]}[/yellow]')
                            moved = auto_organize(
                                folders, 
                                llm_backend,
                                config=config,  # Pass config to use settings
                                dry_run=False,
                                confirm_moves=False
                            )
                            if not moved:
                                console.print('[bold green]overseer:[/bold green] No files to move.')
                            else:
                                for src, dst in moved:
                                    console.print(f'[bold green]overseer:[/bold green] Moved: {src} -> {dst}')
                            continue
                        elif action == 'run_command':
                            match_cmd = re.search(r'command="([^"]+)"', params)
                            match_path = re.search(r'path=([^ ]+)', params)
                            command = match_cmd.group(1) if match_cmd else ''
                            path = match_path.group(1).strip() if match_path else None
                            result = run_command_with_sandbox(command, path, always_confirm=always_confirm_commands)
                            session.last_command = command
                            session.last_action = f'run_command: {command}'
                            session.history.append((user_input, action, result))
                            console.print(f'[bold green]overseer:[/bold green] {result}')
                            break
                        elif action == 'audit_config':
                            try:
                                from .security.secure_config_manager import SecureConfigManager
                                config_manager = SecureConfigManager()
                                audit_results = config_manager.audit_config_files()
                                
                                # Count secure vs insecure files
                                secure_count = sum(1 for result in audit_results.values() if result.get('secure', False))
                                total_count = len(audit_results)
                                
                                console.print(f'[bold green]overseer:[/bold green] Configuration security audit completed.')
                                console.print(f'[bold green]overseer:[/bold green] {secure_count}/{total_count} files are secure.')
                                
                                if secure_count < total_count:
                                    console.print(f'[bold yellow]overseer:[/bold yellow] {total_count - secure_count} files have security issues.')
                                    console.print(f'[bold green]overseer:[/bold green] Use "fix my config security" to resolve issues.')
                                
                                session.last_action = f'audit_config: {secure_count}/{total_count} secure'
                                session.history.append((user_input, action, f'{secure_count}/{total_count} secure'))
                            except ImportError:
                                console.print('[bold red]overseer:[/bold red] Secure config manager not available.')
                            except Exception as e:
                                console.print(f'[bold red]overseer:[/bold red] Audit failed: {e}')
                            continue
                        elif action == 'fix_config_security':
                            try:
                                from .security.secure_config_manager import SecureConfigManager
                                config_manager = SecureConfigManager()
                                
                                console.print(f'[bold green]overseer:[/bold green] Fixing configuration security issues...')
                                success = config_manager.fix_config_security()
                                
                                if success:
                                    console.print(f'[bold green]overseer:[/bold green] All configuration files are now secure.')
                                else:
                                    console.print(f'[bold yellow]overseer:[/bold yellow] Some security issues could not be fixed automatically.')
                                
                                session.last_action = f'fix_config_security: {"success" if success else "partial"}'
                                session.history.append((user_input, action, "success" if success else "partial"))
                            except ImportError:
                                console.print('[bold red]overseer:[/bold red] Secure config manager not available.')
                            except Exception as e:
                                console.print(f'[bold red]overseer:[/bold red] Security fix failed: {e}')
                            continue
                        elif action == 'check_permissions':
                            match = re.search(r'path=([^ ]+)', params)
                            file_path = match.group(1).strip() if match else None
                            
                            if not file_path:
                                console.print('[bold red]overseer:[/bold red] No file path specified.')
                                continue
                            
                            try:
                                from .security.secure_config_manager import SecureConfigManager
                                config_manager = SecureConfigManager()
                                security_status = config_manager.check_file_security(file_path)
                                
                                if security_status['exists']:
                                    status_icon = "✅" if security_status['secure'] else "⚠️"
                                    console.print(f'[bold green]overseer:[/bold green] {status_icon} {file_path}')
                                    console.print(f'[bold green]overseer:[/bold green] Permissions: {security_status["permissions"]}')
                                    
                                    if not security_status['secure']:
                                        console.print(f'[bold yellow]overseer:[/bold yellow] Issues:')
                                        for issue in security_status['issues']:
                                            console.print(f'[bold yellow]overseer:[/bold yellow]   - {issue}')
                                else:
                                    console.print(f'[bold red]overseer:[/bold red] File does not exist: {file_path}')
                                
                                session.last_action = f'check_permissions: {file_path}'
                                session.history.append((user_input, action, file_path))
                            except ImportError:
                                console.print('[bold red]overseer:[/bold red] Secure config manager not available.')
                            except Exception as e:
                                console.print(f'[bold red]overseer:[/bold red] Permission check failed: {e}')
                            continue
                        else:
                            console.print(f'[bold green]overseer:[/bold green] {response}')
                            break
                    except Exception as e:
                        show_error(f"Error during action '{action}'.", e)
                        choice = ask_retry_skip_abort()
                        if choice in ('Retry', 'r'):
                            continue
                        elif choice in ('Skip', 's'):
                            break
                        elif choice in ('Abort', 'a'):
                            return
                        else:
                            break
            except (KeyboardInterrupt, EOFError):
                break 