import sqlite3
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

def get_db_path() -> Path:
    db_dir = Path.home() / ".tflow" / "data"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "e2e_tests.db"

def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # tables: test_cases, test_runs, tools, case_tools
    c.executescript("""
        CREATE TABLE IF NOT EXISTS test_cases (
            id TEXT PRIMARY KEY,
            project TEXT,
            name TEXT,
            pattern TEXT,
            file_path TEXT,
            code TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS test_runs (
            id TEXT PRIMARY KEY,
            case_id TEXT,
            passed BOOLEAN,
            error_msg TEXT,
            duration_ms INTEGER,
            run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS tools (
            id TEXT PRIMARY KEY,
            name TEXT,
            system TEXT,
            type TEXT,
            config TEXT,
            params_schema TEXT
        );
        CREATE TABLE IF NOT EXISTS case_tools (
            id TEXT PRIMARY KEY,
            case_id TEXT,
            tool_id TEXT,
            phase TEXT,
            purpose TEXT,
            params TEXT
        );
    """)
    conn.commit()
    conn.close()

def save_case(case_data: dict) -> str:
    conn = get_connection()
    c = conn.cursor()
    
    case_id = case_data.get("id", str(uuid.uuid4()))
    project = case_data.get("project", "")
    name = case_data.get("name", "")
    pattern = case_data.get("pattern", "")
    file_path = case_data.get("file_path", "")
    code = case_data.get("code", "")
    status = case_data.get("status", "pending")
    
    c.execute("""
        INSERT INTO test_cases (id, project, name, pattern, file_path, code, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            project=excluded.project,
            name=excluded.name,
            pattern=excluded.pattern,
            file_path=excluded.file_path,
            code=excluded.code,
            status=excluded.status
    """, (case_id, project, name, pattern, file_path, code, status))
    conn.commit()
    conn.close()
    return case_id

def query_cases(project: Optional[str] = None, pattern: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    query = "SELECT * FROM test_cases WHERE 1=1"
    params = []
    if project:
        query += " AND project = ?"
        params.append(project)
    if pattern:
        query += " AND pattern = ?"
        params.append(pattern)
    if status:
        query += " AND status = ?"
        params.append(status)
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_tool(tool_data: dict) -> str:
    conn = get_connection()
    c = conn.cursor()
    tool_id = tool_data.get("id", str(uuid.uuid4()))
    c.execute("""
        INSERT INTO tools (id, name, system, type, config, params_schema)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name=excluded.name,
            system=excluded.system,
            type=excluded.type,
            config=excluded.config,
            params_schema=excluded.params_schema
    """, (
        tool_id,
        tool_data.get("name", ""),
        tool_data.get("system", ""),
        tool_data.get("type", "api"),
        tool_data.get("config", "{}"),
        tool_data.get("params_schema", "{}")
    ))
    conn.commit()
    conn.close()
    return tool_id

def get_tool(tool_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM tools WHERE id = ?", (tool_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def list_tools() -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM tools")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_test_run(run_data: dict) -> str:
    conn = get_connection()
    c = conn.cursor()
    run_id = str(uuid.uuid4())
    c.execute("""
        INSERT INTO test_runs (id, case_id, passed, error_msg, duration_ms)
        VALUES (?, ?, ?, ?, ?)
    """, (
        run_id,
        run_data.get("case_id"),
        run_data.get("passed", False),
        run_data.get("error_msg", ""),
        run_data.get("duration_ms", 0)
    ))
    conn.commit()
    conn.close()
    return run_id

def calculate_reusability_score(case_id: str) -> float:
    # Example logic: percentage of successful runs
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*), SUM(CASE WHEN passed THEN 1 ELSE 0 END) FROM test_runs WHERE case_id = ?", (case_id,))
    row = c.fetchone()
    total = row[0] if row else 0
    passed = row[1] if row and len(row) > 1 and row[1] is not None else 0
    conn.close()
    if not total:
        return 0.0
    return (float(passed) / total) * 100.0
