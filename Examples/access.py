from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

server = FastMCP("exec-demo")


@server.tool()
def execute_command(
    cmd: str,
    cwd: str | None = None,
    timeout_seconds: int = 10,
) -> dict[str, Any]:
    """Executes an OS command (dangerous)."""
    working_directory = str(Path(cwd).expanduser().resolve()) if cwd else None

    try:
        process = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=working_directory,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        return {
            "ok": False,
            "cmd": cmd,
            "cwd": working_directory,
            "timeout_seconds": timeout_seconds,
            "error": f"command timed out after {exc.timeout} seconds",
        }

    return {
        "ok": process.returncode == 0,
        "cmd": cmd,
        "cwd": working_directory,
        "returncode": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
    }


@server.tool()
def describe_access_profile() -> dict[str, Any]:
    """Summarize the local access level granted by this demo server."""
    return {
        "server": "exec-demo",
        "transport": "stdio",
        "current_directory": str(Path.cwd()),
        "can_run_shell": True,
        "can_capture_stdout": True,
        "can_capture_stderr": True,
    }


if __name__ == "__main__":
    server.run()
