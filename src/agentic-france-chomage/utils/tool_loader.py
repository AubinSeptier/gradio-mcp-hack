"""Utilities for importing MCP tools with shared path setup."""

from __future__ import annotations

import json
import os
import sys
from importlib import import_module
from pathlib import Path
from typing import Any

import httpx

BLAXEL_BASE_URL = os.getenv("BLAXEL_BASE_URL", "https://run.blaxel.ai")
BLAXEL_WORKSPACE = os.getenv("BLAXEL_WORKSPACE")
BLAXEL_SERVER_NAME = os.getenv("BLAXEL_SERVER_NAME")
BLAXEL_ACCESS_TOKEN = os.getenv("BLAXEL_ACCESS_TOKEN")
BLAXEL_TIMEOUT = float(os.getenv("BLAXEL_TIMEOUT", "120"))


class BlaxelToolWrapper:
    """A wrapper for calling tools hosted on a Blaxel server.

    Args:
        tool_name (str): Name of the tool to call.
        mcp_url (str): Full URL to the MCP server.
        access_token (str): Access token for authentication.
    """

    def __init__(self, tool_name: str, mcp_url: str, access_token: str) -> None:
        self.tool_name = tool_name
        self.mcp_url = mcp_url
        self.access_token = access_token

    def __call__(self, **kwargs: Any) -> Any:  # noqa: ANN401
        """Execute the rool remotely on the Blaxel server.

        Args:
            **kwargs: Arguments to pass to the tool.

        Returns:
            Any: The tool's response, parsed from JSON if applicable.

        Raises:
            RuntimeError: If the remote tool call fails.
        """
        payload = {
            "name": self.tool_name,
            "arguments": kwargs,
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=BLAXEL_TIMEOUT) as client:
                response = client.post(
                    self.mcp_url,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                result = response.json()

                if result.get("isError"):
                    error_msg = "Unknown error"
                    if "content" in result and result["content"]:
                        error_msg = result["content"][0].get("text", error_msg)
                    raise RuntimeError(f"Blaxel remote tool error: {error_msg}")

                content = result.get("content", [])
                if not content:
                    return {}

                text_content = None
                for item in content:
                    if item.get("type") == "text":
                        text_content = item.get("text", "")
                        break

                if text_content is None:
                    return {}

                try:
                    return json.loads(text_content)
                except json.JSONDecodeError:
                    return text_content

        except httpx.HTTPError as e:
            msg = f"Blaxel MCP tool '{self.tool_name}' failed with status {e.response.status_code}: {e.response.text}"
            raise RuntimeError(msg) from e

        except httpx.RequestError as e:
            msg = f"Blaxel MCP tool '{self.tool_name}' request failed: {e}"
            raise RuntimeError(msg) from e

        except json.JSONDecodeError as e:
            msg = f"Blaxel MCP tool '{self.tool_name}' returned invalid JSON: {e}"
            raise RuntimeError(msg) from e

        except Exception as e:
            msg = f"Blaxel MCP tool '{self.tool_name}' encountered an unexpected error: {e}"
            raise RuntimeError(msg) from e


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


def _load_local_tool(tool_name: str) -> Any:  # noqa: ANN401
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
