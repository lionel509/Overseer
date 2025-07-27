import os
import sys
import typer
from getpass import getpass
import re

try:
    from pysqlcipher3 import dbapi2 as sqlite3
except ImportError:
    print("pysqlcipher3 is required. Install with: pip install pysqlcipher3")
    sys.exit(1)

try:
    import backend.core.gemma_engine as gemma_engine
except ImportError:
    import gemma_engine

app = typer.Typer()

DB_DIR = os.path.join(os.path.dirname(__file__), '../db')
DB_PASSPHRASE = os.environ.get('OVERSEER_DB_PASSPHRASE')

# Helper to parse <tool:db>query</tool> blocks
def parse_tool_use(text):
    pattern = r'<tool:(.*?)>(.*?)</tool>'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        db, query = match.group(1).strip(), match.group(2).strip()
        return db, query
    return None, None

def ensure_passphrase():
    global DB_PASSPHRASE
    if not DB_PASSPHRASE:
        DB_PASSPHRASE = getpass("Enter Overseer DB passphrase: ")
        if not DB_PASSPHRASE:
            print("Passphrase required.")
            sys.exit(1)

def get_conn(db_file):
    ensure_passphrase()
    db_path = os.path.join(DB_DIR, db_file)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA key='{DB_PASSPHRASE}';")
    return conn, cursor

# Tool-use DB handlers
def handle_tool_use(db, query):
    db_map = {
        'tools_knowledge': 'tools_knowledge.db',
        'command_templates': 'command_templates.db',
        'system_knowledge': 'system_knowledge.db',
        'user_interactions': 'user_interactions.db',
        'file_index': 'file_index.db',
    }
    db_file = db_map.get(db)
    if not db_file:
        return f"Unknown tool/db: {db}"
    conn, cursor = get_conn(db_file)
    # Simple heuristics for MVP
    if db == 'tools_knowledge':
        cursor.execute("SELECT name, install_command, description FROM tools WHERE name LIKE ? OR tags LIKE ? OR description LIKE ? LIMIT 3", (f"%{query}%", f"%{query}%", f"%{query}%"))
        rows = cursor.fetchall()
        if rows:
            result = '\n'.join([f"{name}: {desc} (install: {cmd})" for name, cmd, desc in rows])
        else:
            result = "No tools found."
    elif db == 'command_templates':
        cursor.execute("SELECT pattern, correction FROM command_templates WHERE pattern LIKE ? LIMIT 1", (f"%{query}%",))
        row = cursor.fetchone()
        if row:
            result = f"Did you mean: {row[1]}"
        else:
            result = "No correction found."
    elif db == 'system_knowledge':
        cursor.execute("SELECT topic, info FROM system_knowledge WHERE topic LIKE ? OR info LIKE ? LIMIT 1", (f"%{query}%", f"%{query}%"))
        row = cursor.fetchone()
        if row:
            result = f"{row[1]}"
        else:
            result = "No info found."
    else:
        result = f"Tool-use for {db} not implemented."
    conn.close()
    return result

@app.command()
def main(*query: str):
    """Ask Overseer anything!"""
    if not query:
        typer.echo("Ask me something, e.g. 'how do I install nvitop'")
        raise typer.Exit()
    q = ' '.join(query).strip()
    # Try LLM first
    try:
        llm_response = gemma_engine.generate_response(q)
        db, tool_query = parse_tool_use(llm_response)
        if db and tool_query:
            result = handle_tool_use(db, tool_query)
            typer.echo(result)
        else:
            typer.echo(llm_response)
    except Exception as e:
        typer.echo(f"[LLM unavailable, falling back to rules] {e}")
        # Fallback: rules (original logic)
        ql = q.lower()
        if ql.startswith("how do i install") or ql.startswith("install "):
            tool = ql.split("install", 1)[-1].strip()
            if not tool:
                typer.echo("Please specify a tool to install.")
                raise typer.Exit()
            conn, cursor = get_conn('tools_knowledge.db')
            cursor.execute("SELECT name, install_command FROM tools WHERE name LIKE ?", (f"%{tool}%",))
            row = cursor.fetchone()
            if row:
                typer.echo(f"sudo {row[1]}")
            else:
                typer.echo(f"Sorry, I don't know how to install '{tool}'.")
            conn.close()
            return
        if "recommend" in ql or "tool for" in ql:
            after_for = ql.split('for', 1)[-1] if 'for' in ql else ql
            conn, cursor = get_conn('tools_knowledge.db')
            cursor.execute("SELECT name, description, install_command FROM tools WHERE tags LIKE ? OR description LIKE ? LIMIT 3", (f"%{after_for.strip()}%", f"%{after_for.strip()}%"))
            results = cursor.fetchall()
            if results:
                for name, desc, cmd in results:
                    typer.echo(f"{name}: {desc} (install: {cmd})")
            else:
                typer.echo("No recommendations found.")
            conn.close()
            return
        if ql.startswith("fix my command:") or ql.startswith("fix command:") or ql.startswith("fix:") or ql.startswith("did you mean") or ql.startswith("correct"):
            cmd = ql.split(":", 1)[-1].strip()
            conn, cursor = get_conn('command_templates.db')
            cursor.execute("SELECT pattern, correction FROM command_templates")
            for pattern, correction in cursor.fetchall():
                if pattern in cmd:
                    typer.echo(f"Did you mean: {cmd.replace(pattern, correction)}")
                    conn.close()
                    return
            typer.echo("No correction found.")
            conn.close()
            return
        if ql.startswith("how do i") or ql.startswith("what is") or ql.startswith("show me"):
            conn, cursor = get_conn('system_knowledge.db')
            cursor.execute("SELECT topic, info FROM system_knowledge WHERE topic LIKE ?", (f"%{ql.split(' ', 3)[-1]}%",))
            row = cursor.fetchone()
            if row:
                typer.echo(f"{row[1]}")
            else:
                typer.echo("Sorry, I don't know that yet.")
            conn.close()
            return
        typer.echo("Sorry, I didn't understand your request. Try asking about installing, recommending, or fixing commands.")

if __name__ == "__main__":
    app() 