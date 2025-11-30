"""Utilities for importing MCP tools with shared path setup."""

from __future__ import annotations

import base64
import json
import os
import sys
from importlib import import_module
from pathlib import Path
from typing import Any

import dotenv
import httpx

dotenv.load_dotenv()

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

    def __call__(self, *args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
        """Execute the rool remotely on the Blaxel server.

        Args:
            *args: Positional arguments to pass to the tool.
            **kwargs: Keyword arguments to pass to the tool.

        Returns:
            Any: The tool's response, parsed from JSON if applicable.

        Raises:
            TypeError: If no arguments are provided or if positional arguments are used.
            RuntimeError: If the remote tool call fails.
        """
        if not kwargs and not args:
            msg = f"Tool '{self.tool_name}' requires at least one argument."
            raise TypeError(msg)

        if args:
            msg = f"Blaxel MCP tool '{self.tool_name}' does not support positional arguments."
            raise TypeError(msg)

        processed_kwargs = self._processed_file_arguments(kwargs)

        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": self.tool_name,
                "arguments": processed_kwargs,
            },
            "id": 1,
        }

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

        try:
            with httpx.Client(timeout=BLAXEL_TIMEOUT) as client:
                response = client.post(
                    self.mcp_url,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()

                print(f"Response text: {response.text}")

                sse_data = self._parse_sse_response(response.text)

                if not sse_data:
                    msg = f"Blaxel MCP tool '{self.tool_name}' returned empty response."
                    raise RuntimeError(msg)

                result = sse_data.get("result", {})

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

    def _parse_sse_response(self, sse_text: str) -> dict:
        """Parse Server-Sent Events (SSE) reponse from Blaxel.

        Args:
            sse_text (str): The raw SSE response text.

        Returns:
            dict: The parsed JSON result from the SSE data.
        """
        lines = sse_text.strip().split("\n")
        for line in lines:
            if line.startswith("data: "):
                try:
                    return json.loads(line[6:])
                except json.JSONDecodeError:
                    continue
        return {}

    def _processed_file_arguments(self, kwargs: dict) -> dict:
        """Process arguments to convert local file paths to base64 for remote execution.

        Args:
            kwargs (dict): The original keyword arguments.

        Returns:
            dict: The processed keyword arguments with file contents in base64.
        """
        processed = {}

        for key, value in kwargs.items():
            if isinstance(value, str) and any(
                pattern in key.lower() for pattern in ["file", "path", "document", "pdf", "image"]
            ):
                if Path(value).is_file():
                    try:
                        with open(value, "rb") as f:
                            file_content = f.read()
                            base64_content = base64.b64encode(file_content).decode("utf-8")
                            processed[key] = f"data:application/pdf;base64,{base64_content}"
                    except Exception:
                        processed[key] = value
                else:
                    processed[key] = value
            else:
                processed[key] = value

        return processed


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


def _load_blaxel_tool(tool_name: str) -> BlaxelToolWrapper:
    """Load a Blaxel hosted tool as a BlaxelToolWrapper.

    Args:
        tool_name (str): The name of the tool to load.

    Returns:
        BlaxelToolWrapper: The wrapped tool callable.

    Raises:
        ValueError: If required Blaxel environment variables are not set.
    """
    if not all([BLAXEL_WORKSPACE, BLAXEL_SERVER_NAME, BLAXEL_ACCESS_TOKEN]):
        raise ValueError(
            "Blaxel environment variables BLAXEL_WORKSPACE, "
            "BLAXEL_SERVER_NAME, and BLAXEL_ACCESS_TOKEN must be set to load Blaxel tools."
        )

    mcp_url = f"{BLAXEL_BASE_URL}/{BLAXEL_WORKSPACE}/functions/{BLAXEL_SERVER_NAME}/mcp"
    return BlaxelToolWrapper(
        tool_name=tool_name,
        mcp_url=mcp_url,
        access_token=BLAXEL_ACCESS_TOKEN,
    )


def load_tool(tool_name: str, is_remote: bool = True) -> Any:  # noqa: ANN401
    """Import a tool callable with Blaxel remote support and local fallback.

    Args:
        tool_name (str): The name of the tool to import.
        is_remote (bool): Whether to load the tool as a remote Blaxel tool first.

    Returns:
        Any: The imported tool callable.

    Raises:
        RuntimeError: If the tool cannot be loaded either remotely or locally.
    """
    errors = []

    if is_remote:
        try:
            tool = _load_blaxel_tool(tool_name)
            print(f"Loaded remote Blaxel tool '{tool_name}'.")
            print(errors)
            return tool
        except Exception as e:
            errors.append(f"Remote load failed: {e}")

        try:
            tool = _load_local_tool(tool_name)
            print(f"Loaded local tool '{tool_name}'.")
            print(errors)
            return tool
        except Exception as e:
            errors.append(f"Local load failed: {e}")

    else:
        try:
            tool = _load_local_tool(tool_name)
            print(f"Loaded local tool '{tool_name}'.")
            return tool
        except Exception as e:
            errors.append(f"Local load failed: {e}")

        try:
            tool = _load_blaxel_tool(tool_name)
            print(f"Loaded remote Blaxel tool '{tool_name}'.")
            return tool
        except Exception as e:
            errors.append(f"Remote load failed: {e}")

    msg = f"Tool '{tool_name}' not found in any source.\nErrors encountered:\n" + "\n".join(f"  - {e}" for e in errors)
    raise RuntimeError(msg)
