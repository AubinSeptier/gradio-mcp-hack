"""Langchain code to orchestrate agents and produce the final workflow."""

from .state import AgentState


def build_graph():
    """Lazily import and build the workflow graph to avoid circular imports."""
    from .graph import build_graph as _build_graph

    return _build_graph()


__all__ = ["build_graph", "AgentState"]
