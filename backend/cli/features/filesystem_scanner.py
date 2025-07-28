import os
import argparse
import time
import mimetypes
from ..db.filesystem_db import add_file_info

try:
    from sentence_transformers import SentenceTransformer
    _semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    _semantic_model = None

from rich.progress import Progress
from rich.console import Console

# --- File system watching ---
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    Observer = None
    FileSystemEventHandler = object

class IndexUpdateHandler(FileSystemEventHandler):
    def __init__(self, root):
        self.root = root
        self.console = Console()
    def on_any_event(self, event):
        # Only handle file create/modify/delete
        if event.is_directory:
            return
        self.console.print(f"[yellow][Overseer] Detected change: {event.event_type} {event.src_path}. Updating index...[/yellow]")
        # Re-index just the changed file
        try:
            fpath = event.src_path
            if not os.path.exists(fpath):
                return  # File was deleted
            stat = os.stat(fpath)
            size = stat.st_size
            mtime = stat.st_mtime
            ext = os.path.splitext(fpath)[1].lower()
            mime, _ = mimetypes.guess_type(fpath)
            ftype = mime if mime else ext.lstrip('.')
            content_summary = get_content_summary(fpath)
            embedding = get_file_embedding(os.path.basename(fpath), content_summary)
            add_file_info(
                path=fpath,
                type_=ftype,
                size=size,
                mtime=mtime,
                tags='',
                extra='{}',
                content_summary=content_summary,
                embedding=embedding
            )
            self.console.print(f"[green][Overseer] Index updated for {fpath}.[/green]")
        except Exception as e:
            self.console.print(f"[red][Overseer] Failed to update index for {event.src_path}: {e}[/red]")

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

def get_file_embedding(fname, summary):
    if not _semantic_model:
        return None
    text = fname
    if summary:
        text += ' ' + summary
    emb = _semantic_model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
    return emb.astype('float32')

def start_file_watcher(root):
    if Observer is None:
        print("[WARN] watchdog not installed. Real-time index updates are disabled.")
        return
    event_handler = IndexUpdateHandler(root)
    observer = Observer()
    observer.schedule(event_handler, path=root, recursive=True)
    observer.start()
    print(f"[Overseer] File system watcher started for {root}.")

def scan_directory(root):
    folder_tags = infer_folder_tags(root)
    # Count total files for progress bar
    total_files = sum(len(filenames) for _, _, filenames in os.walk(root))
    processed = 0
    with Progress() as progress:
        task = progress.add_task("Indexing files...", total=total_files)
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
                    embedding = get_file_embedding(fname, content_summary)
                    add_file_info(
                        path=fpath,
                        type_=ftype,
                        size=size,
                        mtime=mtime,
                        tags=tags,
                        extra='{}',
                        content_summary=content_summary,
                        embedding=embedding
                    )
                except Exception as e:
                    print(f"[WARN] Could not index {fpath}: {e}")
                processed += 1
                progress.update(task, advance=1)
    print(f"[Overseer] Scan complete. Indexed {processed} files.")
    # Start file watcher after initial scan
    start_file_watcher(root)

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