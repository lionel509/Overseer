import os
import shutil
import argparse
from db.filesystem_db import query_file_info, tag_file

def llm_sort_files(files, llm_backend):
    # files: list of (path, type, size, mtime, tags)
    # llm_backend: function that takes a prompt and returns a response
    # For now, stub: group by type
    # In real use, construct a prompt and parse LLM output
    result = {}
    for path, ftype, size, mtime, tags in files:
        folder = ftype if ftype else 'Other'
        result[path] = folder
    return result

def infer_tags_from_path(path, root):
    rel_path = os.path.relpath(path, root)
    parts = [p.lower() for p in rel_path.split(os.sep) if p]
    return ','.join(parts) if parts else ''

def sort_folder(root, dry_run=False, sort_by='type', llm_backend=None, multi_tag=True, ask_create_folder=False, ask_fn=None):
    files = query_file_info(root)
    moved = []
    always = False
    never = False
    if ask_fn is None:
        ask_fn = input
    if sort_by == 'llm' and llm_backend:
        # Use LLM to recommend folders
        file_map = llm_sort_files(files, llm_backend)
        for path, ftype, size, mtime, tags in files:
            if not path.startswith(root):
                continue
            if not os.path.isfile(path):
                continue
            subfolder = file_map.get(path, 'Other')
            dest_dir = os.path.join(root, subfolder)
            dest_path = os.path.join(dest_dir, os.path.basename(path))
            if os.path.abspath(path) == os.path.abspath(dest_path):
                continue
            if not dry_run:
                if not os.path.exists(dest_dir):
                    if never:
                        continue
                    if not always and ask_create_folder:
                        resp = ask_fn(f"Do you want to create the folder '{dest_dir}'? (yes/no/always/never): ").strip().lower()
                        if resp == 'always':
                            always = True
                        elif resp == 'never':
                            never = True
                            continue
                        elif resp not in ('yes', 'y'):
                            continue
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(path, dest_path)
                # Auto-tag with destination folder tags
                folder_tags = infer_tags_from_path(dest_dir, root)
                tag_file(dest_path, folder_tags)
            moved.append((path, dest_path))
        return moved
    # Default: type or tag
    for path, ftype, size, mtime, tags in files:
        if not path.startswith(root):
            continue
        if not os.path.isfile(path):
            continue
        if sort_by == 'tag' and tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            if multi_tag and tag_list:
                subfolder = os.path.join(*tag_list)
            else:
                subfolder = tag_list[0] if tag_list else 'Other'
        else:
            subfolder = ftype if ftype else 'Other'
        dest_dir = os.path.join(root, subfolder)
        dest_path = os.path.join(dest_dir, os.path.basename(path))
        if os.path.abspath(path) == os.path.abspath(dest_path):
            continue
        if not dry_run:
            if not os.path.exists(dest_dir):
                if never:
                    continue
                if not always and ask_create_folder:
                    resp = ask_fn(f"Do you want to create the folder '{dest_dir}'? (yes/no/always/never): ").strip().lower()
                    if resp == 'always':
                        always = True
                    elif resp == 'never':
                        never = True
                        continue
                    elif resp not in ('yes', 'y'):
                        continue
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(path, dest_path)
            # Auto-tag with destination folder tags
            folder_tags = infer_tags_from_path(dest_dir, root)
            tag_file(dest_path, folder_tags)
        moved.append((path, dest_path))
    return moved

def main():
    parser = argparse.ArgumentParser(description="Overseer Folder Sorter")
    parser.add_argument('--root', type=str, required=True, help='Folder to sort')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be moved, but do not move files')
    parser.add_argument('--sort-by', choices=['type', 'tag', 'llm'], default='type', help='Sort by file type, tag, or LLM')
    parser.add_argument('--multi-tag', action='store_true', help='Use all tags as nested folders (default)')
    parser.add_argument('--single-tag', action='store_true', help='Use only the first tag as folder')
    args = parser.parse_args()
    multi_tag = not args.single_tag
    moved = sort_folder(args.root, dry_run=args.dry_run, sort_by=args.sort_by, multi_tag=multi_tag)
    if not moved:
        print("No files to sort.")
    else:
        for src, dst in moved:
            print(f"{'[DRY RUN] ' if args.dry_run else ''}Moved: {src} -> {dst}")

if __name__ == '__main__':
    main() 