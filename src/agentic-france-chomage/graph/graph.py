"""Workflow graph wiring together the agent nodes."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from agents.filtering_node import filtering_node
from agents.profiling_node import profiling_node
from agents.ranking_node import ranking_node
from agents.researcher_node import researcher_node
from graph.state import AgentState


def build_graph():
    """
    Construct the job-search pipeline graph.
    
    Profiling -> Researcher -> Filtering -> Ranking
    
    Returns:
        Compiled StateGraph instance.
    """
    
    workflow = StateGraph(AgentState)

    workflow.add_node("profiling", profiling_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("filtering", filtering_node)
    workflow.add_node("ranking", ranking_node)

    workflow.set_entry_point("profiling")
    workflow.add_edge("profiling", "researcher")
    workflow.add_edge("researcher", "filtering")
    workflow.add_edge("filtering", "ranking")
    workflow.add_edge("ranking", END)

    return workflow.compile()


__all__ = ["build_graph"]
