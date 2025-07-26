import os
import sys

try:
    from pysqlcipher3 import dbapi2 as sqlite3
except ImportError:
    print("pysqlcipher3 is required. Install with: pip install pysqlcipher3")
    sys.exit(1)

DB_DIR = os.path.join(os.path.dirname(__file__), '../db')
os.makedirs(DB_DIR, exist_ok=True)

# Get passphrase from environment variable
DB_PASSPHRASE = os.environ.get('OVERSEER_DB_PASSPHRASE')
if not DB_PASSPHRASE:
    print("Error: OVERSEER_DB_PASSPHRASE environment variable not set.")
    sys.exit(1)

def get_conn(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA key='{DB_PASSPHRASE}';")
    return conn, cursor

# 1. User Interactions DB
def init_user_interactions_db():
    db_path = os.path.join(DB_DIR, 'user_interactions.db')
    conn, cursor = get_conn(db_path)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_input TEXT,
            ai_response TEXT,
            user_feedback INTEGER,
            context TEXT,
            success BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

# 2. Tools Knowledge Base
def init_tools_knowledge_db():
    db_path = os.path.join(DB_DIR, 'tools_knowledge.db')
    conn, cursor = get_conn(db_path)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            category TEXT,
            install_command TEXT,
            doc_url TEXT,
            tags TEXT
        )
    ''')
    # Prefill with example tools
    tools = [
        ("nvitop", "Interactive GPU monitoring tool", "monitoring", "pip install nvitop", "https://github.com/LeoCavaille/nvitop", "gpu,monitoring,cli"),
        ("nvidia-smi", "NVIDIA driver command line tool", "monitoring", "nvidia-smi", "https://developer.nvidia.com/nvidia-system-management-interface", "gpu,monitoring,cli"),
        ("htop", "Interactive process viewer", "monitoring", "brew install htop", "https://htop.dev/", "cpu,monitoring,cli")
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO tools (name, description, category, install_command, doc_url, tags)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', tools)
    conn.commit()
    conn.close()

# 3. Command Templates & Fixes
def init_command_templates_db():
    db_path = os.path.join(DB_DIR, 'command_templates.db')
    conn, cursor = get_conn(db_path)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS command_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT,
            correction TEXT,
            description TEXT,
            usage_example TEXT
        )
    ''')
    # Prefill with example command templates
    templates = [
        ("git pus", "git push", "Corrects common git typo", "git pus origin main -> git push origin main"),
        ("grpe", "grep", "Corrects common grep typo", "grpe 'foo' file.txt -> grep 'foo' file.txt"),
        ("tial", "tail", "Corrects common tail typo", "tial -f log.txt -> tail -f log.txt"),
        ("killl", "kill", "Corrects common kill typo", "killl 1234 -> kill 1234")
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO command_templates (pattern, correction, description, usage_example)
        VALUES (?, ?, ?, ?)
    ''', templates)
    conn.commit()
    conn.close()

# 4. System Knowledge Base
def init_system_knowledge_db():
    db_path = os.path.join(DB_DIR, 'system_knowledge.db')
    conn, cursor = get_conn(db_path)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            os_type TEXT,
            topic TEXT,
            info TEXT
        )
    ''')
    # Prefill with example system knowledge
    knowledge = [
        ("linux", "list files", "Use 'ls -la' to list all files including hidden ones."),
        ("macos", "show system info", "Use 'system_profiler' for detailed system information."),
        ("windows", "list processes", "Use 'tasklist' to list running processes.")
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO system_knowledge (os_type, topic, info)
        VALUES (?, ?, ?)
    ''', knowledge)
    conn.commit()
    conn.close()

# 5. File Index/Metadata DB
def init_file_index_db():
    db_path = os.path.join(DB_DIR, 'file_index.db')
    conn, cursor = get_conn(db_path)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT,
            file_hash TEXT,
            tags TEXT,
            last_indexed DATETIME,
            embedding BLOB
        )
    ''')
    conn.commit()
    conn.close()

def init_all_dbs():
    init_user_interactions_db()
    init_tools_knowledge_db()
    init_command_templates_db()
    init_system_knowledge_db()
    init_file_index_db()
    print('All encrypted DBs initialized in backend/db/')

if __name__ == '__main__':
    init_all_dbs() 