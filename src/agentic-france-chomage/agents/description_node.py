"""Agent node that generates concise descriptions for each ranked job."""

from __future__ import annotations

import json
from typing import Any

from graph import AgentState
from pydantic import BaseModel, Field
from utils import nebius_client


class JobDescription(BaseModel):
    """Model for a single job description item."""

    index: int
    summary: str = Field(..., description="2-3 sentences describing the role for this candidate")
    positives: list[str] = Field(default_factory=list, description="Positive fit bullets")
    negatives: list[str] = Field(default_factory=list, description="Potential drawbacks or gaps")


class DescriptionResult(BaseModel):
    """Model for the LLM response containing job descriptions."""

    descriptions: list[JobDescription]


# Helpers -------------
def _llm_describe_jobs(
    jobs: list[dict[str, Any]],
    profile: dict[str, Any],
    preferences: dict[str, Any],
) -> list[JobDescription] | None:
    """Ask an LLM for per-job summaries/positives/negatives.

    Args:
        jobs (list[dict[str, Any]]): List of job dicts to describe.
        profile (dict[str, Any]): Extracted candidate profile information.
        preferences (dict[str, Any]): Candidate job preferences.

    Returns:
        list[JobDescription] | None: List of JobDescription instances or None on failure.
    """
    try:
        client = nebius_client()
        system_prompt = (
            "You are a career coach summarizing ranked job offers for a candidate. "
            "For each provided job with an 'index', return JSON: "
            '{"descriptions":[{"index":int,"summary":string,"positives":[string],'
            '"negatives":[string]}]}. '
            "summary: 2-3 concise sentences (max ~70 words) tailored to the candidate; avoid fluff. "
            "positives: 2-3 short bullet phrases (<=8 words) highlighting strongest fits. "
            "negatives: 1-2 bullet phrases (<=8 words) with risks, gaps, or drawbacks. "
            "Be direct, no markdown or numbering, keep bullets brief and scannable."
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
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, default=str)},
            ],
            response_format=DescriptionResult,
            temperature=0.25,
            max_tokens=8192,
        )
        message = response.choices[0].message
        parsed = getattr(message, "parsed", None) or DescriptionResult.model_validate_json(
            (message.content or "{}").strip()
        )
        return parsed.descriptions
    except Exception as exc:
        print(f"Error in _llm_describe_jobs: {exc}")
        return None


# Node -----------------
def description_node(state: AgentState) -> dict[str, Any]:
    """Attach concise candidate-focused descriptions to ranked jobs.

    Args:
        state (AgentState): Current agent state containing ranked jobs and candidate info.

    Returns:
        dict[str, Any]: New agent state with job descriptions added.
    """
    profile = state.get("profil_extracted") or {}
    preferences = state.get("job_preferences") or {}
    ranked = state.get("job_ranked") or {}
    jobs: list[dict[str, Any]] = ranked.get("jobs") or []

    llm_descriptions = _llm_describe_jobs(jobs, profile, preferences) or []
    mapping: dict[int, JobDescription] = {item.index: item for item in llm_descriptions if 0 <= item.index < len(jobs)}

    described_jobs: list[dict[str, Any]] = []
    descriptions_payload: list[dict[str, Any]] = []

    for idx, job in enumerate(jobs):
        job_copy = dict(job)
        if idx in mapping:
            item = mapping[idx]
            desc_payload = {
                "summary": item.summary.strip(),
                "positives": [p.strip() for p in item.positives if p.strip()],
                "negatives": [n.strip() for n in item.negatives if n.strip()],
            }
        else:
            desc_payload = {
                "summary": "No description available.",
                "positives": [],
                "negatives": [],
            }

        job_copy["match_description"] = desc_payload
        described_jobs.append(job_copy)
        descriptions_payload.append({"index": idx, **desc_payload})

    new_state = dict(state)
    new_state["job_ranked"] = {"jobs": described_jobs}
    new_state["job_descriptions"] = {"jobs": descriptions_payload}
    return new_state


__all__ = ["description_node"]
