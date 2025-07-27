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
from .inference.inference_local import LocalLLM
from .inference.inference_gemini import GeminiAPI
from .utils.logger import set_debug, set_log, debug, info, error

console = Console()
CONFIG_PATH = os.path.expanduser('~/.overseer/config.json')

def first_run_setup():
    print('Welcome to Overseer! Let\'s set up your preferences:')
    debug_mode = input('Enable debug mode? (yes/no): ').strip().lower() in ('yes', 'y')
    log_mode = input('Enable log mode? (yes/no): ').strip().lower() in ('yes', 'y')
    file_indexing = input('Enable file indexing? (yes/no): ').strip().lower() in ('yes', 'y')
    full_control = input('Enable full control mode by default? (yes/no): ').strip().lower() in ('yes', 'y')
    folders = input('Default folders to watch (comma-separated, e.g. ~/Downloads,~/Documents): ').strip()
    folders = [os.path.expanduser(f.strip()) for f in folders.split(',') if f.strip()]
    config = {
        'debug': debug_mode,
        'log': log_mode,
        'file_indexing': file_indexing,
        'full_control': full_control,
        'folders': folders
    }
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

def main():
    parser = argparse.ArgumentParser(description="Overseer CLI - System Assistant")
    parser.add_argument('--mode', choices=['local', 'gemini'], required=True, help='Inference mode: local or gemini')
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
        llm_backend = LocalLLM().run
    else:
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            console.print('[red]Error: GOOGLE_API_KEY environment variable not set.[/red]')
            exit(1)
        llm_backend = GeminiAPI(api_key).run

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

    # REPL mode
    console.print('[bold cyan]Overseer CLI (type "exit" to quit)[/bold cyan]')
    console.print('[bold green]overseer:[/bold green] How can I help you today?')
    console.print('  - sort files')
    console.print('  - search by tag')
    console.print('  - auto-organize')
    console.print('  - tag files')
    console.print('  - (type your request in natural language)')
    full_control_repl = False
    while True:
        try:
            user_input = Prompt.ask('[bold yellow]user[/bold yellow]')
            if user_input.strip().lower() in ('exit', 'quit'):
                break
            # Conversational intent detection
            inp = user_input.strip().lower()
            if inp == 'debug on':
                set_debug(True)
                console.print('[bold green]overseer:[/bold green] Debug mode enabled.')
                continue
            if inp == 'debug off':
                set_debug(False)
                console.print('[bold green]overseer:[/bold green] Debug mode disabled.')
                continue
            if inp == 'log on':
                set_log(True)
                console.print('[bold green]overseer:[/bold green] Log mode enabled.')
                continue
            if inp == 'log off':
                set_log(False)
                console.print('[bold green]overseer:[/bold green] Log mode disabled.')
                continue
            if inp == 'full control on':
                console.print('[red][WARNING] You are about to enable FULL CONTROL MODE! Overseer will take all actions automatically, without asking. Type YES to confirm.[/red]')
                confirm = Prompt.ask('Type YES to enable full control')
                if confirm.strip().upper() == 'YES':
                    full_control_repl = True
                    console.print('[red][WARNING] FULL CONTROL MODE ENABLED![/red]')
                else:
                    console.print('[green]Full control mode NOT enabled.[/green]')
                continue
            if inp == 'full control off':
                full_control_repl = False
                console.print('[green]Full control mode disabled.[/green]')
                continue
            if inp.startswith('sort') or 'sort' in inp:
                # Extract folder path if present
                import re
                match = re.search(r'sort (.+)', inp)
                sort_path = match.group(1).strip() if match else os.path.expanduser('~')
                if full_control_repl:
                    console.print('[red][WARNING] FULL CONTROL: No prompts. All actions will be automatic![/red]')
                console.print('[bold green]overseer:[/bold green] On it! Sorting files...')
                moved = sort_folder(
                    sort_path,
                    ask_create_folder=not full_control_repl,
                    ask_fn=Prompt.ask if not full_control_repl else None
                )
                if not moved:
                    console.print('[bold green]overseer:[/bold green] No files to sort.')
                else:
                    for src, dst in moved:
                        console.print(f'[bold green]overseer:[/bold green] Moved: {src} -> {dst}')
                    console.print(f'[bold green]overseer:[/bold green] Done! Files in {sort_path} have been sorted.')
                console.print('[bold green]overseer:[/bold green] What would you like to do next?')
                continue
            if inp.startswith('search tag') or 'search by tag' in inp:
                tag = inp.split('tag', 1)[-1].strip()
                if not tag:
                    console.print('[bold green]overseer:[/bold green] Please specify a tag to search for.')
                    continue
                console.print(f'[bold green]overseer:[/bold green] On it! Searching for files with tag: {tag}')
                results = search_by_tag(tag)
                print_file_results(results)
                console.print('[bold green]overseer:[/bold green] What would you like to do next?')
                continue
            if inp.startswith('auto-organize') or 'auto-organize' in inp:
                import re
                match = re.search(r'auto-organize(.*)', inp)
                folders = match.group(1).strip().split() if match and match.group(1).strip() else None
                if not folders:
                    home = os.path.expanduser('~')
                    folders = [home, os.path.join(home, 'Documents'), os.path.join(home, 'Downloads')]
                if full_control_repl:
                    console.print('[red][WARNING] FULL CONTROL: No prompts. All actions will be automatic![/red]')
                console.print(f'[bold green]overseer:[/bold green] On it! Auto-organizing folders: {folders}')
                moved = auto_organize(folders, llm_backend)
                if not moved:
                    console.print('[bold green]overseer:[/bold green] No files to move.')
                else:
                    for src, dst in moved:
                        console.print(f'[bold green]overseer:[/bold green] Moved: {src} -> {dst}')
                    console.print('[bold green]overseer:[/bold green] Auto-organize complete.')
                console.print('[bold green]overseer:[/bold green] What would you like to do next?')
                continue
            if inp.startswith('tag '):
                parts = user_input.strip().split(' ', 2)
                if len(parts) < 3:
                    console.print('[bold green]overseer:[/bold green] Usage: tag <file> <tags>')
                    continue
                file_path = parts[1]
                tags = parts[2]
                tag_file(file_path, tags)
                new_tags = get_tags(file_path)
                console.print(f'[bold green]overseer:[/bold green] Tagged {file_path} with: {new_tags}')
                console.print('[bold green]overseer:[/bold green] What would you like to do next?')
                continue
            if inp.startswith('find file about') or inp.startswith('where is'):
                desc = inp.split('about', 1)[-1].strip() if 'about' in inp else inp.split('where is', 1)[-1].strip()
                if not desc:
                    console.print('[bold green]overseer:[/bold green] Please describe the file you are looking for.')
                    continue
                console.print(f'[bold green]overseer:[/bold green] On it! Searching for file: {desc}')
                results = search_by_description(desc)
                print_file_results(results)
                console.print('[bold green]overseer:[/bold green] What would you like to do next?')
                continue
            # Fallback to core logic
            response = run_backend(user_input)
            console.print(f'[bold green]overseer:[/bold green] {response}')
            console.print('[bold green]overseer:[/bold green] What would you like to do next?')
        except (KeyboardInterrupt, EOFError):
            break 