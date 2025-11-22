"""
Agent node that uses the resume_extractor tool to produce profil_extracted 
from resume_file.
"""

from __future__ import annotations

from typing import Any, Dict

from graph.state import AgentState
from utils import load_tool

resume_extractor = load_tool("resume_extractor")


# Node ----------------
def profiling_node(state: AgentState) -> Dict[str, Any]:
    """Extract a structured profile from the provided resume file."""
    
    resume_file = state.get("resume_file")
    if not resume_file:
        raise ValueError("profiling_node requires a 'resume_file' path in the state.")

    extracted_profile = resume_extractor(resume_file)

    new_state = dict(state)
    new_state["profil_extracted"] = extracted_profile
    return new_state
