import os
import argparse
import time
import mimetypes
from db.filesystem_db import add_file_info

def infer_folder_tags(root):
    folder_tags = {}
    for dirpath, dirnames, filenames in os.walk(root):
        # Use folder name as tag, plus parent folder names for hierarchy
        rel_path = os.path.relpath(dirpath, root)
        if rel_path == '.':
            tags = []
        else:
            tags = [p.lower() for p in rel_path.split(os.sep) if p]
        folder_tags[dirpath] = tags
    return folder_tags

def get_content_summary(fpath):
    try:
        ext = os.path.splitext(fpath)[1].lower()
        if ext in ['.txt', '.md', '.py', '.csv', '.log', '.json', '.yaml', '.yml']:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(500)
        # Optionally, add PDF/docx support here
    except Exception:
        pass
    return ''

def scan_directory(root):
    folder_tags = infer_folder_tags(root)
    for dirpath, _, filenames in os.walk(root):
        tags = ','.join(folder_tags.get(dirpath, []))
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                stat = os.stat(fpath)
                size = stat.st_size
                mtime = stat.st_mtime
                ext = os.path.splitext(fname)[1].lower()
                mime, _ = mimetypes.guess_type(fpath)
                ftype = mime if mime else ext.lstrip('.')
                content_summary = get_content_summary(fpath)
                add_file_info(
                    path=fpath,
                    type_=ftype,
                    size=size,
                    mtime=mtime,
                    tags=tags,
                    extra='{}',
                    content_summary=content_summary
                )
            except Exception as e:
                print(f"[WARN] Could not index {fpath}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Overseer File System Scanner")
    parser.add_argument('--root', type=str, required=True, help='Root directory to scan')
    args = parser.parse_args()
    print(f"[Overseer] Scanning {args.root} ...")
    t0 = time.time()
    scan_directory(args.root)
    print(f"[Overseer] Scan complete in {time.time() - t0:.2f} seconds.")

if __name__ == '__main__':
    main() 