"""
Agent node that filters irrelevant or not higly relevant jobs from
job_search_results to produce job_filtered.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel
from graph import AgentState
from utils import nebius_client


class FilteringResult(BaseModel):
    keep_indices: list[int]


# Helpers -------------
def _llm_filter_jobs(
    jobs: list[dict[str, Any]], 
    profile: dict[str, Any], 
    preferences: dict[str, Any]
) -> list[int] | None:
    """Ask Nebius LLM which jobs to keep; returns indices to keep or None on failure."""
    try:
        client = nebius_client()
        system_prompt = (
            "You select relevant job offers for a candidate. "
            "Consider skills, experiences, location, and other preferences. "
            "Return JSON: {\"keep_indices\": [int, ...]} using the provided job indices."
        )
        jobs_with_indices = [{**job, "index": idx} for idx, job in enumerate(jobs)]
        user_payload = {
            "profile": profile,
            "preferences": preferences,
            "jobs": jobs_with_indices,
        }
        response = client.chat.completions.parse(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            response_format=FilteringResult,
            temperature=0.15,
            max_tokens=200,
        )
        message = response.choices[0].message
        parsed = (
            getattr(message, "parsed", None)
            or FilteringResult.model_validate_json((message.content or "{}").strip())
        )
        keep = [i for i in parsed.keep_indices if 0 <= i < len(jobs)]
        return keep
    except Exception:
        return None
    return None


# Node -----------------
def filtering_node(state: AgentState) -> dict[str, Any]:
    """Filter job results using Nebius LLM."""

    preferences = state.get("job_preferences") or {}
    profile = state.get("profil_extracted") or {}
    job_results = state.get("job_search_results") or []
    jobs: list[dict[str, Any]]
    if isinstance(job_results, dict): # metadata about the search could be added later
        jobs = job_results.get("jobs") or []
    else:
        jobs = job_results

    keep_indices = _llm_filter_jobs(jobs, profile, preferences)
    if keep_indices is not None:
        filtered_jobs = [jobs[i] for i in keep_indices if 0 <= i < len(jobs)]
    else:
        filtered_jobs = jobs

    new_state = dict(state)
    new_state["job_filtered"] = {"jobs": filtered_jobs, "dropped": len(jobs) - len(filtered_jobs)}
    return new_state
