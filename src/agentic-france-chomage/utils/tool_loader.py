"""Utilities for importing MCP tools with shared path setup."""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path
from typing import Any


def _ensure_tools_on_path() -> Path:
    """Add the MCP tools directory to sys.path if needed.

    Returns:
        Path: The path to the MCP tools directory.
    """
    tools_root = Path(__file__).resolve().parents[2] / "france-chomage-mcp-server"
    root_str = str(tools_root)
    if root_str not in sys.path:
        sys.path.append(root_str)
    return tools_root


def load_tool(tool_name: str) -> Any:  # noqa: ANN401
    """Import a tool callable from the shared MCP tools package.

    Args:
        tool_name (str): The name of the tool to import.

    Returns:
        Any: The imported tool callable.

    Raises:
        ImportError: If the tool cannot be imported.
    """
    _ensure_tools_on_path()
    try:
        module = import_module("tools")
        return getattr(module, tool_name)
    except Exception as exc:
        raise ImportError(f"Cannot import tool '{tool_name}'.") from exc
