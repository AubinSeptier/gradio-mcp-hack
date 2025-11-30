"""Langchain code to orchestrate agents and produce the final workflow."""

from typing import Any

from .state import AgentState


def build_graph() -> Any:  # noqa: ANN401
    """Lazily import and build the workflow graph to avoid circular imports.

    Returns:
        Any: Compiled StateGraph instance.
    """
    from .graph import build_graph as _build_graph

    return _build_graph()


__all__ = ["build_graph", "AgentState"]
