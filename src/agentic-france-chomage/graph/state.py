"""
Interface contract between agents, structures the data that will be passed 
from an agent to another
"""

from typing import TypedDict

class AgentState(TypedDict):
    resume_file: str
    profil_extracted: dict
    job_preferences: dict
    job_search_results: dict
    job_filtered: dict
    job_ranked: dict
    # ...