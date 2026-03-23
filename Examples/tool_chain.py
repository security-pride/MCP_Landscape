from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

server = FastMCP("tool-chain-demo")
DEMO_DB = Path(__file__).with_name("tool_chain_demo.sqlite3")


def _resolve_path(path: str) -> Path:
    return Path(path).expanduser().resolve()


def _ensure_demo_db(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL
            )
            """
        )
        row_count = connection.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        if row_count == 0:
            connection.executemany(
                "INSERT INTO notes(title, body) VALUES(?, ?)",
                [
                    ("welcome", "This database exists to demonstrate tool chaining."),
                    ("warning", "File and database tools together widen the attack surface."),
                ],
            )


@server.tool()
def list_files(path: str) -> list[str]:
    """List files under the given path."""
    target = _resolve_path(path)
    return sorted(child.name for child in target.iterdir())


@server.tool()
def read_file(path: str) -> str:
    """Read file content."""
    return _resolve_path(path).read_text(encoding="utf-8")


@server.tool()
def execute_query(connection: str, query: str) -> list[dict[str, Any]]:
    """Run a SQL query using a SQLite database path or the built-in demo database."""
    database_path = DEMO_DB if connection == "demo" else _resolve_path(connection)
    _ensure_demo_db(database_path)

    with sqlite3.connect(database_path) as database:
        database.row_factory = sqlite3.Row
        cursor = database.execute(query)
        if cursor.description:
            return [dict(row) for row in cursor.fetchmany(50)]

        database.commit()
        return [{"rows_affected": cursor.rowcount}]


@server.tool()
def write_file(path: str, content: str) -> str:
    """Write file to the local system."""
    target = _resolve_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return str(target)


if __name__ == "__main__":
    server.run()
