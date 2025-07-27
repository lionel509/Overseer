import os
import sys
import tempfile
import shutil
import pytest  # type: ignore

pytest.importorskip("pysqlcipher3")  # type: ignore
try:
    from pysqlcipher3 import dbapi2 as sqlite3  # type: ignore
except ImportError:
    pytest.skip("pysqlcipher3 not installed", allow_module_level=True)

import importlib.util
import types

test_passphrase = "testpass123"

def run_db_init_with_tempdir(monkeypatch, tmp_path):
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    monkeypatch.setenv("OVERSEER_DB_PASSPHRASE", test_passphrase)
    db_init_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../core/db_init.py"))
    spec = importlib.util.spec_from_file_location("db_init", db_init_path)
    if spec is None or spec.loader is None:
        pytest.skip("Could not import db_init.py", allow_module_level=True)
    db_init = importlib.util.module_from_spec(spec)
    loader = spec.loader
    assert loader is not None
    loader.exec_module(db_init)
    # Patch DB_DIR if possible
    if hasattr(db_init, "DB_DIR"):
        db_init.DB_DIR = str(db_dir)
    db_init.init_all_dbs()
    return db_dir

def get_conn(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA key='{test_passphrase}';")
    return conn, cursor

def test_db_files_created(monkeypatch, tmp_path):
    db_dir = run_db_init_with_tempdir(monkeypatch, tmp_path)
    files = set(os.listdir(db_dir))
    assert {"user_interactions.db", "tools_knowledge.db", "command_templates.db", "system_knowledge.db", "file_index.db"}.issubset(files)

def test_encryption(monkeypatch, tmp_path):
    db_dir = run_db_init_with_tempdir(monkeypatch, tmp_path)
    db_path = os.path.join(db_dir, "user_interactions.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    with pytest.raises(sqlite3.DatabaseError):
        cursor.execute("PRAGMA key='wrongpass';")
        cursor.execute("SELECT count(*) FROM sqlite_master;")
    conn.close()

def test_prefill_data(monkeypatch, tmp_path):
    db_dir = run_db_init_with_tempdir(monkeypatch, tmp_path)
    db_path = os.path.join(db_dir, "command_templates.db")
    conn, cursor = get_conn(db_path)
    cursor.execute("SELECT pattern, correction FROM command_templates;")
    rows = cursor.fetchall()
    assert ("git pus", "git push") in rows
    conn.close()
    db_path = os.path.join(db_dir, "tools_knowledge.db")
    conn, cursor = get_conn(db_path)
    cursor.execute("SELECT name FROM tools;")
    names = [r[0] for r in cursor.fetchall()]
    assert "nvitop" in names
    conn.close()
    db_path = os.path.join(db_dir, "system_knowledge.db")
    conn, cursor = get_conn(db_path)
    cursor.execute("SELECT os_type FROM system_knowledge;")
    os_types = [r[0] for r in cursor.fetchall()]
    assert "linux" in os_types
    conn.close()

def test_crud_operations(monkeypatch, tmp_path):
    db_dir = run_db_init_with_tempdir(monkeypatch, tmp_path)
    db_path = os.path.join(db_dir, "user_interactions.db")
    conn, cursor = get_conn(db_path)
    cursor.execute("INSERT INTO user_interactions (user_input, ai_response, user_feedback, context, success) VALUES (?, ?, ?, ?, ?)",
                   ("test input", "test response", 1, "{}", True))
    conn.commit()
    cursor.execute("SELECT user_input, ai_response FROM user_interactions WHERE user_input='test input';")
    row = cursor.fetchone()
    assert row == ("test input", "test response")
    cursor.execute("UPDATE user_interactions SET user_feedback=0 WHERE user_input='test input';")
    conn.commit()
    cursor.execute("SELECT user_feedback FROM user_interactions WHERE user_input='test input';")
    assert cursor.fetchone()[0] == 0
    cursor.execute("DELETE FROM user_interactions WHERE user_input='test input';")
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM user_interactions WHERE user_input='test input';")
    assert cursor.fetchone()[0] == 0
    conn.close() 