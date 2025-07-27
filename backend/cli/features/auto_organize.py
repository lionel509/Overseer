import os
from features.folder_sorter import llm_sort_files
from db.filesystem_db import query_file_info

def auto_organize(folders, llm_backend, dry_run=False):
    moved = []
    for folder in folders:
        files = query_file_info(folder)
        if not files:
            continue
        file_map = llm_sort_files(files, llm_backend)
        for path, ftype, size, mtime, tags in files:
            if not os.path.isfile(path):
                continue
            correct_folder = file_map.get(path, 'Other')
            dest_dir = os.path.join(folder, correct_folder)
            dest_path = os.path.join(dest_dir, os.path.basename(path))
            if os.path.abspath(path) == os.path.abspath(dest_path):
                continue  # Already in place
            if not dry_run:
                os.makedirs(dest_dir, exist_ok=True)
                os.rename(path, dest_path)
            moved.append((path, dest_path))
    return moved

def main():
    import argparse
    from inference.inference_local import LocalLLM
    from inference.inference_gemini import GeminiAPI
    parser = argparse.ArgumentParser(description="Overseer Auto-Organize")
    parser.add_argument('--folders', nargs='+', help='Folders to auto-organize (default: home, Documents, Downloads)')
    parser.add_argument('--mode', choices=['local', 'gemini'], default='local', help='LLM mode')
    parser.add_argument('--dry-run', action='store_true', help='Preview only, do not move files')
    args = parser.parse_args()
    if args.folders:
        folders = args.folders
    else:
        home = os.path.expanduser('~')
        folders = [home, os.path.join(home, 'Documents'), os.path.join(home, 'Downloads')]
    if args.mode == 'local':
        llm_backend = LocalLLM().run
    else:
        import os
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            print('GOOGLE_API_KEY not set!')
            return
        llm_backend = GeminiAPI(api_key).run
    moved = auto_organize(folders, llm_backend, dry_run=args.dry_run)
    if not moved:
        print('No files to move.')
    else:
        for src, dst in moved:
            print(f"{'[DRY RUN] ' if args.dry_run else ''}Moved: {src} -> {dst}")

if __name__ == '__main__':
    main() 