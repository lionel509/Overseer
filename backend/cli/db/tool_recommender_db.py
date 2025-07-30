import os
import sqlite3 as sqlcipher
DB_PATH = os.path.join(os.path.dirname(__file__), '../../db/tool_database.db')
# DB_KEY = os.environ.get('OVERSEER_DB_KEY')

# if not DB_KEY:
#     raise RuntimeError('OVERSEER_DB_KEY environment variable not set!')

def get_connection():
    conn = sqlcipher.connect(DB_PATH)
    c = conn.cursor()
    # c.execute(f"PRAGMA key='{DB_KEY}';")  # Removed for standard SQLite
    # Create table if not exists
    c.execute('''CREATE TABLE IF NOT EXISTS tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        keywords TEXT,
        description TEXT,
        install_cmd TEXT
    )''')
    conn.commit()
    return conn

def add_tool(name, category, keywords, description, install_cmd):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO tools (name, category, keywords, description, install_cmd) VALUES (?, ?, ?, ?, ?)',
              (name, category, keywords, description, install_cmd))
    conn.commit()
    conn.close()

def get_recommendations(query):
    conn = get_connection()
    c = conn.cursor()
    q = f"%{query.lower()}%"
    c.execute('SELECT name, description, install_cmd FROM tools WHERE keywords LIKE ? OR name LIKE ? OR description LIKE ?', (q, q, q))
    results = c.fetchall()
    conn.close()
    if not results:
        return "No tool recommendations found for your query."
    out = []
    for name, desc, cmd in results:
        out.append(f"{name}: {desc}\nInstall: {cmd}")
    return '\n\n'.join(out) 