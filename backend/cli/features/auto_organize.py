import os
from .folder_sorter import llm_sort_files
from ..db.filesystem_db import query_file_info

def improved_llm_sort_files(files, llm_backend, config=None):
    """Improved LLM-based file sorting with better prompts and categorization"""
    if not llm_backend:
        # Fallback to type-based sorting if no LLM
        result = {}
        for path, ftype, size, mtime, tags in files:
            folder = ftype if ftype else 'Other'
            result[path] = folder
        return result
    
    # Get LLM settings from config
    if config:
        max_tokens = config.get('gemini_max_tokens', 2048) if config.get('llm_mode') == 'gemini' else config.get('local_max_tokens', 1024)
        temperature = config.get('gemini_temperature', 0.7) if config.get('llm_mode') == 'gemini' else config.get('local_temperature', 0.7)
    else:
        max_tokens = 2048
        temperature = 0.7
    
    # Create a comprehensive prompt for the LLM
    file_list = []
    for path, ftype, size, mtime, tags in files:
        filename = os.path.basename(path)
        file_list.append(f"- {filename} (type: {ftype}, size: {size} bytes)")
    
    prompt = f"""
You are a file organization expert. I have the following files that need to be organized into logical folders:

{chr(10).join(file_list)}

Please categorize these files into meaningful folders. Consider:
1. File type and purpose (documents, images, videos, etc.)
2. Content and context
3. Common organizational patterns

Respond with a JSON object where each file path maps to a folder name. Use simple, clear folder names like:
- Documents
- Images  
- Videos
- Music
- Downloads
- Work
- Personal
- Projects
- etc.

Example format:
{{
    "/path/to/file1.pdf": "Documents",
    "/path/to/file2.jpg": "Images",
    "/path/to/file3.mp4": "Videos"
}}

Only respond with the JSON object, no other text.
"""
    
    try:
        response = llm_backend(prompt)
        # Try to parse JSON response
        import json
        import re
        
        # Extract JSON from response (in case LLM adds extra text)
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            file_map = json.loads(json_match.group())
        else:
            # Fallback to type-based sorting
            file_map = {}
            for path, ftype, size, mtime, tags in files:
                folder = ftype if ftype else 'Other'
                file_map[path] = folder
        
        return file_map
    except Exception as e:
        print(f"LLM sorting failed: {e}. Falling back to type-based sorting.")
        # Fallback to type-based sorting
        result = {}
        for path, ftype, size, mtime, tags in files:
            folder = ftype if ftype else 'Other'
            result[path] = folder
        return result

def auto_organize(folders, llm_backend, config=None, dry_run=False, confirm_moves=True, max_files_per_folder=None):
    """
    Auto-organize files with improved safety and confirmation using config settings
    
    Args:
        folders: List of folders to organize
        llm_backend: LLM function for intelligent sorting
        config: Configuration dictionary with settings
        dry_run: If True, only show what would be moved
        confirm_moves: If True, ask for confirmation before moving files
        max_files_per_folder: Maximum files to process per folder (safety limit)
    """
    # Load config if not provided
    if config is None:
        try:
            from ..overseer_cli import load_config
            config = load_config()
        except ImportError:
            config = {}
    
    # Get settings from config with defaults
    auto_organize_enabled = config.get('auto_organize_enabled', True)
    max_files_per_folder = max_files_per_folder or config.get('max_files_per_folder', 100)
    confirm_moves = config.get('confirm_moves', True) if confirm_moves else confirm_moves
    backup_before_move = config.get('backup_before_move', False)
    scan_hidden_files = config.get('scan_hidden_files', False)
    exclude_patterns = config.get('exclude_patterns', '*.tmp,*.log,.DS_Store')
    verbose_output = config.get('verbose_output', False)
    show_progress = config.get('show_progress', True)
    color_output = config.get('color_output', True)
    
    if not auto_organize_enabled:
        print("Auto-organize is disabled in settings.")
        return []
    
    moved = []
    
    for folder in folders:
        if not os.path.exists(folder):
            print(f"Warning: Folder {folder} does not exist, skipping...")
            continue
            
        files = query_file_info(folder)
        if not files:
            print(f"No files found in {folder}")
            continue
        
        # Apply file filters based on settings
        filtered_files = []
        exclude_list = [pattern.strip() for pattern in exclude_patterns.split(',')]
        
        for file_info in files:
            path, ftype, size, mtime, tags = file_info
            filename = os.path.basename(path)
            
            # Skip hidden files if not enabled
            if not scan_hidden_files and filename.startswith('.'):
                continue
            
            # Skip excluded patterns
            skip_file = False
            for pattern in exclude_list:
                if pattern and filename.endswith(pattern.replace('*', '')):
                    skip_file = True
                    break
            
            if skip_file:
                continue
            
            filtered_files.append(file_info)
        
        if verbose_output:
            print(f"Processing {len(filtered_files)} files in {folder}")
        
        # Limit files per folder for safety
        if len(filtered_files) > max_files_per_folder:
            print(f"Warning: {len(filtered_files)} files found, limiting to {max_files_per_folder} for safety")
            filtered_files = filtered_files[:max_files_per_folder]
        
        if not filtered_files:
            print(f"No files to organize in {folder}")
            continue
        
        # Use LLM to sort files
        file_map = improved_llm_sort_files(filtered_files, llm_backend, config)
        
        if not file_map:
            print(f"No organization plan generated for {folder}")
            continue
        
        # Show preview
        if dry_run or confirm_moves:
            print(f"\n📋 Organization plan for {folder}:")
            folder_counts = {}
            for file_path, target_folder in file_map.items():
                if target_folder not in folder_counts:
                    folder_counts[target_folder] = 0
                folder_counts[target_folder] += 1
                print(f"  {os.path.basename(file_path)} → {target_folder}")
            
            print(f"\n📊 Summary: {len(file_map)} files will be organized into {len(folder_counts)} folders")
            for folder_name, count in folder_counts.items():
                print(f"  {folder_name}: {count} files")
        
        if dry_run:
            print("Dry run completed - no files were moved")
            continue
        
        # Ask for confirmation
        if confirm_moves:
            try:
                import questionary
                proceed = questionary.confirm(
                    f"Proceed with organizing {len(file_map)} files in {folder}?",
                    default=False
                ).ask()
            except ImportError:
                proceed = input(f"Proceed with organizing {len(file_map)} files in {folder}? (y/N): ").strip().lower() in ('y', 'yes')
            
            if not proceed:
                print(f"Skipping organization of {folder}")
                continue
        
        # Create backup if enabled
        if backup_before_move:
            backup_dir = config.get('backup_dir', '~/.overseer/backups')
            backup_dir = os.path.expanduser(backup_dir)
            os.makedirs(backup_dir, exist_ok=True)
            backup_path = os.path.join(backup_dir, f"backup_{os.path.basename(folder)}_{int(time.time())}")
            print(f"Creating backup at {backup_path}")
            # TODO: Implement backup creation
        
        # Move files
        if show_progress:
            print(f"Moving {len(file_map)} files...")
        
        for file_path, target_folder in file_map.items():
            try:
                # Create target folder if it doesn't exist
                target_path = os.path.join(folder, target_folder)
                os.makedirs(target_path, exist_ok=True)
                
                # Move file
                filename = os.path.basename(file_path)
                new_path = os.path.join(target_path, filename)
                
                # Avoid overwriting existing files
                counter = 1
                original_new_path = new_path
                while os.path.exists(new_path):
                    name, ext = os.path.splitext(original_new_path)
                    new_path = f"{name}_{counter}{ext}"
                    counter += 1
                
                os.rename(file_path, new_path)
                moved.append((file_path, new_path))
                
                if verbose_output:
                    print(f"  Moved: {filename} → {target_folder}")
                    
            except Exception as e:
                print(f"Error moving {file_path}: {e}")
        
        if show_progress:
            print(f"✅ Organized {len(moved)} files in {folder}")
    
    return moved

def main():
    import argparse
    from inference.inference_local import LocalLLM
    from inference.inference_gemini import GeminiAPI
    parser = argparse.ArgumentParser(description="Overseer Auto-Organize")
    parser.add_argument('--folders', nargs='+', help='Folders to auto-organize (default: home, Documents, Downloads)')
    parser.add_argument('--mode', choices=['local', 'gemini'], default='local', help='LLM mode')
    parser.add_argument('--dry-run', action='store_true', help='Preview only, do not move files')
    parser.add_argument('--no-confirm', action='store_true', help='Skip confirmation prompts (use with caution)')
    parser.add_argument('--max-files', type=int, default=100, help='Maximum files to process per folder (default: 100)')
    parser.add_argument('--safe-mode', action='store_true', help='Enable safe mode: dry-run by default, smaller file limits')
    args = parser.parse_args()
    
    # Safe mode overrides
    if args.safe_mode:
        if not args.dry_run:
            print("Safe mode enabled: using dry-run by default")
            args.dry_run = True
        if args.max_files > 50:
            print("Safe mode enabled: limiting to 50 files per folder")
            args.max_files = 50
    
    if args.folders:
        folders = args.folders
    else:
        home = os.path.expanduser('~')
        folders = [os.path.join(home, 'Downloads')]  # Safer default - just Downloads
        print(f"Using default folder: {folders[0]}")
        print("Use --folders to specify other folders")
    
    if args.mode == 'local':
        llm_backend = LocalLLM().run
    else:
        import os
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            print('GOOGLE_API_KEY not set!')
            return
        llm_backend = GeminiAPI(api_key).run
    
    moved = auto_organize(
        folders, 
        llm_backend, 
        dry_run=args.dry_run,
        confirm_moves=not args.no_confirm,
        max_files_per_folder=args.max_files
    )
    if not moved:
        print('No files to move.')
    else:
        for src, dst in moved:
            print(f"{'[DRY RUN] ' if args.dry_run else ''}Moved: {src} -> {dst}")

if __name__ == '__main__':
    main() 