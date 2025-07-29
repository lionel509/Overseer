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
    llm_mode = questionary.select('Do you want to use a local LLM or the online Gemini API?', choices=['local', 'gemini'], default='gemini').ask()
    config = {}
    config['llm_mode'] = llm_mode
    if llm_mode == 'gemini':
        config['gemini_api_key'] = questionary.text('Gemini API key').ask()
        config['gemini_model_name'] = questionary.text('Gemini model name', default='gemini-1.5-flash').ask()
    else:
        config['local_model_name'] = questionary.text('Local model name', default='google/gemma-1.1-3b-it').ask()
    debug_mode = questionary.confirm('Enable debug mode?', default=False).ask()
    log_mode = questionary.confirm('Enable log mode?', default=False).ask()
    file_indexing = questionary.confirm('Enable file indexing?', default=False).ask()
    full_control = questionary.confirm('Enable full control mode by default?', default=False).ask()
    folders = questionary.text('Default folders to watch (comma-separated, e.g. ~/Downloads,~/Documents)').ask()
    folders = [os.path.expanduser(f.strip()) for f in folders.split(',') if f.strip()]
    config.update({
        'debug': debug_mode,
        'log': log_mode,
        'file_indexing': file_indexing,
        'full_control': full_control,
        'folders': folders
    })
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    print(f'Settings saved to {CONFIG_PATH}.')
    return config

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return first_run_setup()
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def print_file_results(results):
    if not results:
        console.print('[yellow]No files found.[/yellow]')
        return
    for path, ftype, size, mtime, tags in results:
        console.print(f'[blue]{path}[/blue] | type: {ftype} | size: {size} | mtime: {mtime} | tags: {tags}')

def interactive_settings_editor(config):
    llm_mode = config.get('llm_mode', 'local')
    gemini_api_key = config.get('gemini_api_key', os.environ.get('GOOGLE_API_KEY', ''))
    local_model_name = config.get('local_model_name', 'google/gemma-1.1-3b-it')
    gemini_model_name = config.get('gemini_model_name', 'gemini-1.5-flash')
    answers = {}
    answers['debug'] = questionary.confirm('Enable debug mode?', default=config.get('debug', False)).ask()
    answers['log'] = questionary.confirm('Enable log mode?', default=config.get('log', False)).ask()
    answers['file_indexing'] = questionary.confirm('Enable file indexing?', default=config.get('file_indexing', False)).ask()
    answers['full_control'] = questionary.confirm('Enable full control mode by default?', default=config.get('full_control', False)).ask()
    answers['always_confirm_commands'] = questionary.confirm('Always confirm before running system/tool commands?', default=config.get('always_confirm_commands', True)).ask()
    folders = questionary.text('Default folders to watch (comma-separated)', default=','.join(config.get('folders', []))).ask()
    answers['folders'] = [os.path.expanduser(f.strip()) for f in folders.split(',') if f.strip()]
    answers['llm_mode'] = questionary.select('LLM mode', choices=['local', 'gemini'], default=llm_mode).ask()
    if answers['llm_mode'] == 'gemini':
        answers['gemini_api_key'] = questionary.text('Gemini API key', default=gemini_api_key).ask()
        answers['gemini_model_name'] = questionary.text('Gemini model name', default=gemini_model_name).ask()
    else:
        answers['local_model_name'] = questionary.text('Local model name', default=local_model_name).ask()
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
    import subprocess, os
    import shlex
    from rich.console import Console
    console = Console()
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
            folders = [home, os.path.join(home, 'Documents'), os.path.join(home, 'Downloads')]
        console.print(f'[cyan]Auto-organizing folders: {folders}...[/cyan]')
        if full_control:
            console.print('[red][WARNING] FULL CONTROL: No prompts. All actions will be automatic![/red]')
        moved = auto_organize(folders, llm_backend, dry_run=args.dry_run)
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
        for r in results:
            console.print(r)
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
- Run system/tool commands (ACTION: run_command command="<cmd>" path=<folder>)
- Answer general questions or have a conversation

When the user asks for something, reply with either:
- A conversational response (for greetings, small talk, etc.)
- An action in the format: ACTION: <action> <params>

Examples:
User: hi
Overseer: Hello! How can I help you today?
User: sort my downloads
Overseer: ACTION: sort_files path=~/Downloads
User: find my tax file
Overseer: ACTION: search_files query=tax
User: tag report.pdf as important
Overseer: ACTION: tag_file path=report.pdf tags=important
User: what is in my downloads folder
Overseer: ACTION: list_folder path=~/Downloads
User: check my git status
Overseer: ACTION: run_command command="git status" path=~/project
User: pull the latest Docker image for nginx
Overseer: ACTION: run_command command="docker pull nginx"
User: install numpy with pip
Overseer: ACTION: run_command command="pip install numpy"
User: list running Docker containers
Overseer: ACTION: run_command command="docker ps"
User: update all packages with apt
Overseer: ACTION: run_command command="sudo apt update && sudo apt upgrade"
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
                except Exception as e:
                    show_error("Failed to extract action from LLM response.", e)
                    continue
                # Reference resolution
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
                            from .features.file_search import search_files
                            results = search_files(query)
                            files = [r for r in results.split('\n') if r and 'No matching files found' not in r]
                            session.last_search_results = files
                            session.last_selected_file = files[0] if files else None
                            session.last_action = f'search_files: {query}'
                            print_file_results([(r, '', '', '', '') for r in files])
                            session.history.append((user_input, action, files))
                            break
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
                                folders = [home, os.path.join(home, 'Documents'), os.path.join(home, 'Downloads')]
                            moved = auto_organize(folders, llm_backend)
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