import os
import sqlite3 as sqlcipher
import numpy as np

DB_PATH = os.path.join(os.path.dirname(__file__), 'filesystem_info.db')
# DB_KEY = os.environ.get('OVERSEER_DB_KEY')

# if not DB_KEY:
#     raise RuntimeError('OVERSEER_DB_KEY environment variable not set!')

def get_connection():
    conn = sqlcipher.connect(DB_PATH)
    c = conn.cursor()
    # c.execute(f"PRAGMA key='{DB_KEY}';")  # Removed for standard SQLite
    # Create table if not exists, add content_summary if missing
    c.execute('''CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT,
        type TEXT,
        size INTEGER,
        mtime REAL,
        tags TEXT,
        extra TEXT,
        content_summary TEXT,
        embedding BLOB
    )''')
    # Try to add new columns if not present
    try:
        c.execute('ALTER TABLE files ADD COLUMN content_summary TEXT')
    except Exception:
        pass
    try:
        c.execute('ALTER TABLE files ADD COLUMN embedding BLOB')
    except Exception:
        pass
    conn.commit()
    return conn

def add_file_info(path, type_, size, mtime, tags='', extra='', content_summary='', embedding=None):
    conn = get_connection()
    c = conn.cursor()
    # Convert embedding to bytes if present
    emb_bytes = embedding.tobytes() if embedding is not None else None
    c.execute('INSERT INTO files (path, type, size, mtime, tags, extra, content_summary, embedding) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
              (path, type_, size, mtime, tags, extra, content_summary, emb_bytes))
    conn.commit()
    conn.close()

def query_file_info(query):
    conn = get_connection()
    c = conn.cursor()
    q = f"%{query.lower()}%"
    c.execute('SELECT path, type, size, mtime, tags FROM files WHERE path LIKE ? OR tags LIKE ?', (q, q))
    results = c.fetchall()
    conn.close()
    return results

def tag_file(path, tags):
    conn = get_connection()
    c = conn.cursor()
    c.execute('UPDATE files SET tags = ? WHERE path = ?', (tags, path))
    conn.commit()
    conn.close()

def get_tags(path):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT tags FROM files WHERE path = ?', (path,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else ''

def search_by_tag(tag):
    conn = get_connection()
    c = conn.cursor()
    q = f"%{tag.lower()}%"
    c.execute('SELECT path, type, size, mtime, tags FROM files WHERE LOWER(tags) LIKE ?', (q,))
    results = c.fetchall()
    conn.close()
    return results

def search_by_description(query):
    conn = get_connection()
    c = conn.cursor()
    q = f"%{query.lower()}%"
    c.execute('SELECT path, type, size, mtime, tags, content_summary FROM files WHERE LOWER(path) LIKE ? OR LOWER(tags) LIKE ? OR LOWER(content_summary) LIKE ?', (q, q, q))
    results = c.fetchall()
    conn.close()
    return results 

def get_all_file_embeddings():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT path, embedding FROM files WHERE embedding IS NOT NULL')
    results = c.fetchall()
    conn.close()
    # Return list of (path, np.array embedding)
    return [(path, np.frombuffer(emb, dtype=np.float32)) for path, emb in results if emb is not None] 