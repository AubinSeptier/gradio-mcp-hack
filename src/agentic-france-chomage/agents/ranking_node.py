"""
Agent node that ranks jobs in job_filtered (or raw search results) against
the profile and preferences.
"""

from __future__ import annotations

import json
from typing import Any

from graph.state import AgentState
from utils import nebius_client

NA_SCORE = -1


# Helpers -------------
def _llm_rank_jobs(
    jobs: list[dict[str, Any]],
    profile: dict[str, Any],
    preferences: dict[str, Any],
) -> list[dict[str, Any]]:
    """Ask Nebius LLM to score jobs; returns jobs with scores (NA when missing)."""
    try:
        client = nebius_client()
        system_prompt = (
            "You rank job offers for a candidate from 0 (poor fit) to 10 (perfect fit). "
            "Consider skills, experiences, seniority, location and other preferences. "
            "Return JSON: {\"scores\": [{\"index\": int, \"score\": int}, ...]} using the provided job indices."
        )
        jobs_with_indices = [{**job, "index": idx} for idx, job in enumerate(jobs)]
        user_payload = {
            "profile": profile,
            "preferences": preferences,
            "jobs": jobs_with_indices,
        }
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
            ],
            temperature=0.2,
            max_tokens=240,
        )
        content = (response.choices[0].message.content or "").strip()
        parsed = json.loads(content)
        scores = parsed.get("scores")
        mapping: dict[int, int] = {}
        if isinstance(scores, list):
            for item in scores:
                if not isinstance(item, dict):
                    continue
                idx = item.get("index")
                sc = item.get("score")
                if isinstance(idx, int) and isinstance(sc, int) and 0 <= idx < len(jobs):
                    mapping[idx] = sc
    except Exception:
        mapping = {}

    scored_jobs: list[dict[str, Any]] = []
    for idx, job in enumerate(jobs):
        score = mapping.get(idx, NA_SCORE)
        scored_jobs.append({**job, "score": int(score)})
    return scored_jobs


# Node -----------------
def ranking_node(state: AgentState) -> dict[str, Any]:
    """Rank filtered jobs with Nebius LLM; mark missing scores as N/A."""

    preferences = state.get("job_preferences") or {}
    profile = state.get("profil_extracted") or {}
    job_source = state.get("job_filtered") or state.get("job_search_results") or {}
    if isinstance(job_source, dict):
        jobs: list[dict[str, Any]] = job_source.get("jobs") or []
    else:
        jobs = job_source

    scored_jobs = _llm_rank_jobs(jobs, profile, preferences)
    scored_jobs.sort(key=lambda job: job.get("score", 0), reverse=True)
    for rank, job in enumerate(scored_jobs, start=1):
        job["rank"] = rank

    new_state = dict(state)
    new_state["job_ranked"] = {"jobs": scored_jobs}
    return new_state
