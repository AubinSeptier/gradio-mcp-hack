"""
Agent node that builds search queries from a profile and preferences,
then calls the job search MCP tool.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Tuple

from graph.state import AgentState
from utils import load_tool, nebius_client

job_search_tool = load_tool("job_search_tool")


# Helpers -------------
def _guess_search_terms(profile: Dict[str, Any], preferences: Dict[str, Any]) -> Tuple[str, str]:
    """Use Nebius LLM to propose search terms."""
    
    client = nebius_client()
    system_prompt = (
        "You craft concise job search queries. Those queries will be"
        "used on sites like LinkedIn to provide job recommendations"
        "Given a candidate profile and preferences, return JSON with "
        '{"search_term": str, "google_search_term": str}. '
        "Keep search_term under 6 words and avoid generic filler."
        "Return ONLY the JSON object, without any additional text."
    )
    user_payload = {"profile": profile, "preferences": preferences}
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            temperature=0.2,
            max_tokens=120,
        )
        content = (response.choices[0].message.content or "").strip()
        parsed = json.loads(content)
        search_term = parsed.get("search_term")
        google_search_term = parsed.get("google_search_term")
        if isinstance(search_term, str) and isinstance(google_search_term, str):
            return search_term.strip(), google_search_term.strip()

    except (json.JSONDecodeError, KeyError, IndexError, AttributeError, ValueError) as e:
        return {"error": f"Search term request failed: {e}"}


# Node -----------------
def researcher_node(state: AgentState) -> Dict[str, Any]:
    """Search for jobs based on the extracted profile and preferences."""
    
    profile = state.get("profil_extracted") or {}
    preferences = state.get("job_preferences") or {}
    search_term, google_search_term = _guess_search_terms(profile, preferences)

    site_name = preferences.get("site_name") or ["linkedin", "indeed"]
    location = preferences.get("location") or "France"
    distance_km = preferences.get("distance_km") or 30
    job_type = preferences.get("job_type") or ["fulltime"]
    job_type = job_type if isinstance(job_type, list) else [job_type]
    is_remote = bool(preferences.get("is_remote", False))
    results_wanted = int(preferences.get("results_wanted", 10))
    hours_old = int(preferences.get("hours_old", 72))
    linkedin_fetch_description = bool(preferences.get("linkedin_fetch_description", True))

    jobs = job_search_tool(
        site_name=site_name,
        search_term=search_term,
        google_search_term=google_search_term,
        location=location,
        distance=int(distance_km),
        job_type=job_type,
        is_remote=is_remote,
        results_wanted=results_wanted,
        hours_old=hours_old,
        linkedin_fetch_description=linkedin_fetch_description,
    )

    new_state = dict(state)
    new_state["job_search_results"] = jobs
    return new_state
