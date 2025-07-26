import os
import sys
import shutil
import tempfile
import pytest  # type: ignore
from unittest.mock import patch, MagicMock

pytest.importorskip("pysqlcipher3")  # type: ignore
pytest.importorskip("typer")  # type: ignore

from typer.testing import CliRunner  # type: ignore
import importlib.util

# Import the CLI app
cli_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../core/cli.py"))
spec = importlib.util.spec_from_file_location("cli", cli_path)
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)

runner = CliRunner()

test_passphrase = "testpass123"

def setup_test_dbs(tmp_path):
    # Copy the real db files to a temp dir for isolated testing
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    real_db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../db"))
    for db_file in ["tools_knowledge.db", "command_templates.db", "system_knowledge.db", "user_interactions.db", "file_index.db"]:
        src = os.path.join(real_db_dir, db_file)
        dst = db_dir / db_file
        shutil.copyfile(src, dst)
    return db_dir

@pytest.fixture(autouse=True)
def patch_env_and_db(monkeypatch, tmp_path):
    db_dir = setup_test_dbs(tmp_path)
    monkeypatch.setenv("OVERSEER_DB_PASSPHRASE", test_passphrase)
    # Patch DB_DIR in cli module
    if hasattr(cli, "DB_DIR"):
        cli.DB_DIR = str(db_dir)
    yield

def test_llm_success_with_tool_use():
    with patch('backend.core.gemma_engine.generate_response') as mock_generate:
        mock_generate.return_value = "<tool:tools_knowledge>find nvitop</tool>"
        result = runner.invoke(cli.app, ["how do I install nvitop"])
        assert result.exit_code == 0
        assert "nvitop" in result.output.lower()

def test_llm_success_without_tool_use():
    with patch('backend.core.gemma_engine.generate_response') as mock_generate:
        mock_generate.return_value = "You can install nvitop using: sudo apt install nvitop"
        result = runner.invoke(cli.app, ["how do I install nvitop"])
        assert result.exit_code == 0
        assert "install" in result.output.lower()

def test_llm_failure_fallback():
    with patch('backend.core.gemma_engine.generate_response') as mock_generate:
        mock_generate.side_effect = Exception("Model not found")
        result = runner.invoke(cli.app, ["how do I install nvitop"])
        assert result.exit_code == 0
        assert "LLM unavailable" in result.output or "install" in result.output.lower()

def test_tool_use_parsing():
    # Test the parse_tool_use function directly
    from backend.core.cli import parse_tool_use
    db, query = parse_tool_use("<tool:tools_knowledge>find nvitop</tool>")
    assert db == "tools_knowledge"
    assert query == "find nvitop"

def test_tool_use_handling():
    with patch('backend.core.gemma_engine.generate_response') as mock_generate:
        mock_generate.return_value = "<tool:command_templates>git pus</tool>"
        result = runner.invoke(cli.app, ["fix my command: git pus"])
        assert result.exit_code == 0
        assert "git push" in result.output.lower()

def test_unknown_tool_use():
    with patch('backend.core.gemma_engine.generate_response') as mock_generate:
        mock_generate.return_value = "<tool:unknown_db>query</tool>"
        result = runner.invoke(cli.app, ["test query"])
        assert result.exit_code == 0
        assert "Unknown tool" in result.output

def test_install_query_fallback():
    with patch('backend.core.gemma_engine.generate_response') as mock_generate:
        mock_generate.side_effect = Exception("Model error")
        result = runner.invoke(cli.app, ["how do I install nvitop"])
        assert result.exit_code == 0
        assert "install" in result.output.lower() or "sudo" in result.output.lower()

def test_recommend_query_fallback():
    with patch('backend.core.gemma_engine.generate_response') as mock_generate:
        mock_generate.side_effect = Exception("Model error")
        result = runner.invoke(cli.app, ["recommend a tool for monitoring gpu"])
        assert result.exit_code == 0
        assert "nvitop" in result.output.lower() or "nvidia" in result.output.lower()

def test_fix_command_fallback():
    with patch('backend.core.gemma_engine.generate_response') as mock_generate:
        mock_generate.side_effect = Exception("Model error")
        result = runner.invoke(cli.app, ["fix my command: git pus origin main"])
        assert result.exit_code == 0
        assert "git push origin main" in result.output.lower()

def test_system_knowledge_fallback():
    with patch('backend.core.gemma_engine.generate_response') as mock_generate:
        mock_generate.side_effect = Exception("Model error")
        result = runner.invoke(cli.app, ["how do I list files"])
        assert result.exit_code == 0
        assert "ls -la" in result.output.lower() or "list" in result.output.lower()

def test_unknown_query_fallback():
    with patch('backend.core.gemma_engine.generate_response') as mock_generate:
        mock_generate.side_effect = Exception("Model error")
        result = runner.invoke(cli.app, ["what is the airspeed velocity of an unladen swallow"])
        assert result.exit_code == 0
        assert "don't know" in result.output.lower() or "sorry" in result.output.lower() 