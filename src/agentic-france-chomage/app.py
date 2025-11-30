"""Gradio app for the Track 2: MCP in action."""

from __future__ import annotations

import html
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from typing import Any

import gradio as gr
from agents import description_node, filtering_node, profiling_node, ranking_node, researcher_node

APP_CSS = """
:root {
  --card-bg: #0f172a;
  --card-border: #1f2937;
  --text: #e5e7eb;
  --muted: #9ca3af;
  --accent: #8b5cf6;
  --positive: #10b981;
  --negative: #ef4444;
  --chip: #111827;
}
.gradio-container {background: radial-gradient(circle at 20% 20%, rgba(99,102,241,0.08), transparent 35%), linear-gradient(135deg,#0b1220,#0e1626);}
.main-layout {align-items: flex-start; gap: 16px;}
.results-column {display:flex; flex-direction: column; gap: 12px;}
.status-panel {color: var(--text); padding: 0;}
.status-panel > .progress-card {margin: 0;}
.matches-panel {max-height: calc(100vh - 220px); overflow-y: auto; padding-right: 8px; scrollbar-width: thin;}
.matches-panel::-webkit-scrollbar {width: 10px;}
.matches-panel::-webkit-scrollbar-thumb {background: rgba(255,255,255,0.15); border-radius: 12px;}
.jobs-grid {display: grid; gap: 12px;}
.job-card {background: linear-gradient(135deg,rgba(255,255,255,0.02),rgba(255,255,255,0)); border: 1px solid var(--card-border); border-radius: 14px; padding: 14px 16px; color: var(--text); box-shadow: 0 8px 28px rgba(0,0,0,0.25);}
.job-header {display: flex; justify-content: space-between; gap: 12px; align-items: center; flex-wrap: wrap;}
.title-stack {display:flex; gap:12px; align-items: center; flex:1 1 auto;}
.rank-chip {background: #0f172a; border:1px solid var(--card-border); border-radius: 10px; padding: 6px 10px; font-weight: 700; color: var(--accent); box-shadow: inset 0 0 0 1px rgba(139,92,246,0.3);}
.title-line {font-size: 1.05rem; font-weight: 700;}
.meta-line {color: var(--muted); font-size: 0.9rem;}
.header-actions {display:flex; gap:8px; align-items:center; flex-wrap: wrap;}
.pill {position: relative; padding: 6px 10px; border-radius: 10px; font-weight: 600; font-size: 0.9rem; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08); cursor: default;}
.pill-positive {color: #0f5132; background: rgba(16,185,129,0.16); border-color: rgba(16,185,129,0.45);}
.pill-negative {color: #7f1d1d; background: rgba(239,68,68,0.16); border-color: rgba(239,68,68,0.45);}
.pill-tooltip {position: absolute; top: 110%; right: 0; background: #0b1220; border: 1px solid var(--card-border); border-radius: 10px; padding: 10px 12px; min-width: 220px; box-shadow: 0 10px 30px rgba(0,0,0,0.4); opacity: 0; transform: translateY(6px); pointer-events: none; transition: opacity 0.12s ease, transform 0.12s ease; z-index: 5;}
.pill:hover .pill-tooltip {opacity: 1; transform: translateY(0);}
.pill-tooltip ul {margin: 0; padding-left: 18px;}
.pill-tooltip li {color: var(--text); margin: 3px 0;}
.score-chip {display:flex; align-items:center; gap:8px; padding:6px 10px; border-radius: 12px; background: var(--chip); border:1px solid var(--card-border); font-weight:700;}
.score-good {color:#16a34a; border-color:rgba(22,163,74,0.4);}
.score-mid {color:#f59e0b; border-color:rgba(245,158,11,0.4);}
.score-low {color:#f97316; border-color:rgba(249,115,22,0.4);}
.score-na {color: var(--muted);}
.score-circle {width: 36px; height: 36px;}
.score-circle .score-bg {fill: none; stroke: rgba(255,255,255,0.08); stroke-width: 6; stroke-linecap: round;}
.score-circle .score-fg {fill: none; stroke: currentColor; stroke-width: 6; stroke-linecap: round; transform: rotate(-90deg); transform-origin: 50% 50%;}
.score-text {font-size: 0.95rem;}
.job-body {display: flex; flex-direction: column; gap: 8px; margin-top: 10px;}
.job-link {display: inline-flex; align-items: center; gap: 6px; color: #93c5fd; text-decoration: none; font-weight: 600;}
.job-link:hover {text-decoration: underline;}
.summary-toggle {background: rgba(255,255,255,0.02); border: 1px solid var(--card-border); border-radius: 12px; padding: 10px 12px;}
.summary-toggle summary {list-style: none; cursor: pointer; display: flex; justify-content: space-between; align-items: center; gap: 12px; font-weight: 600;}
.summary-toggle summary::-webkit-details-marker {display:none;}
.summary-preview {color: var(--text); flex:1; transition: opacity 0.18s ease, transform 0.18s ease;}
details[open] .summary-preview {opacity: 0; transform: translateY(-6px); height: 0; max-height: 0; flex: 0; margin: 0; overflow: hidden;}
.summary-action {color: var(--accent); font-size: 0.9rem; display: inline-flex; align-items: center; gap:6px;}
.summary-action .action-open {display:none; color: var(--muted);}
details[open] .summary-action {color: var(--muted);}
details[open] .summary-action .action-open {display:inline;}
details[open] .summary-action .action-closed {display:none;}
.summary-action::before {content: "+"; font-weight: 900;}
details[open] .summary-action::before {content: "–";}
.summary-full {color: var(--muted); margin-top: 8px; line-height: 1.45; animation: fadeIn 0.22s ease;}
.empty-state {color: var(--muted); padding: 12px;}
.progress-card {background: linear-gradient(135deg,rgba(255,255,255,0.02),rgba(255,255,255,0.06)); border:1px solid var(--card-border); border-radius: 14px; padding: 12px 14px; color: var(--text);}
.progress-head {display:flex; align-items:center; gap:10px; font-weight:700;}
.progress-steps {list-style:none; margin:10px 0 0; padding:0; display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:8px;}
.progress-step {display:flex; align-items:center; gap:10px; padding:10px 12px; border-radius:12px; border:1px solid var(--card-border); background: rgba(255,255,255,0.02);}
.progress-step .dot {width:12px; height:12px; border-radius:999px; background: rgba(255,255,255,0.2); box-shadow: 0 0 0 0 rgba(255,255,255,0.14); transition: all 0.2s ease;}
.progress-step .labels {display:flex; flex-direction: column; gap: 2px;}
.progress-step .title {font-weight:700; font-size:0.95rem;}
.progress-step .desc {color: var(--muted); font-size: 0.85rem;}
.progress-step.active .dot {background: var(--accent); box-shadow: 0 0 0 6px rgba(139,92,246,0.14); animation: pulseDot 1.2s ease-in-out infinite;}
.progress-step.done .dot {background: var(--positive); box-shadow: 0 0 0 6px rgba(16,185,129,0.14);}
.progress-step.upcoming .dot, .progress-step.idle .dot {background: rgba(255,255,255,0.18);}
.loading-jobs {display:flex; align-items:center; gap:10px; color: var(--muted); padding: 12px 14px; border-radius: 12px; border:1px dashed rgba(255,255,255,0.18); background: rgba(255,255,255,0.02); margin-top: 8px;}
.loading-spinner {width:16px; height:16px; border:2px solid rgba(255,255,255,0.28); border-top-color: var(--accent); border-radius:50%; animation: spin 0.9s linear infinite;}
.status-card {background: linear-gradient(135deg,rgba(255,255,255,0.02),rgba(255,255,255,0.06)); border:1px solid var(--card-border); border-radius: 14px; padding: 12px 14px; color: var(--text); box-shadow: 0 8px 28px rgba(0,0,0,0.25);}
.status-card .title {font-weight: 700; margin-bottom: 4px;}
.status-card .subtitle {color: var(--muted); font-size: 0.95rem;}
@keyframes spin {to {transform: rotate(360deg);}}
@keyframes pulseDot {0% {transform: scale(1);} 50% {transform: scale(1.16);} 100% {transform: scale(1);}}
@keyframes fadeIn {from {opacity: 0; transform: translateY(4px);} to {opacity: 1; transform: translateY(0);}}
"""  # noqa: E501

PROGRESS_STEPS = [
    ("Profiling", "Understanding your resume"),
    ("Researching", "Searching job boards"),
    ("Filtering", "Discarding weak fits"),
    ("Ranking", "Scoring the top options"),
    ("Summarizing", "Writing the AI fit notes"),
]

_EXECUTOR = ThreadPoolExecutor(max_workers=1)

PIPELINE_NODES = [
    profiling_node,
    researcher_node,
    filtering_node,
    ranking_node,
    description_node,
]


def _first(keys: list[str], data: dict[str, Any], default: str = "") -> str:
    """Return the first non-empty value found for keys in data.

    Args:
        keys (list[str]): List of keys to check in order.
        data (dict[str, Any]): Dictionary to search.
        default (str): Default value if no keys are found.

    Returns:
        str: The first non-empty string value found, or default.
    """
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def _truncate(text: str, limit: int = 150) -> str:
    """Word-safe truncate.

    Args:
        text (str): Text to truncate.
        limit (int): Maximum length of the returned string.

    Returns:
        str: Truncated text with ellipsis if needed.
    """
    txt = (text or "").strip()
    if len(txt) <= limit:
        return txt
    cut = txt[:limit].rsplit(" ", 1)[0]
    return cut + "..."


def _score_meta(score: Any) -> tuple[str, str, float]:  # noqa: ANN401
    """Return CSS class, label, and fill percent for score.

    Args:
        score (Any): Score value to interpret.

    Returns:
        tuple[str, str, float]: (css_class, label, fill_percent)
    """
    try:
        val = float(score)
    except (TypeError, ValueError):
        return "score-na", "N/A", 0.0
    if val < 0:
        return "score-na", "N/A", 0.0
    val = max(0.0, min(10.0, val))
    if val >= 8:
        cls = "score-good"
    elif val >= 6:
        cls = "score-mid"
    else:
        cls = "score-low"
    return cls, f"{val:.0f}/10", val / 10.0


def _render_progress(active_index: int | None, headline: str, finished: bool = False) -> str:
    """Build the multi-step progress indicator shown in the status panel.

    Args:
        active_index (int | None): Index of the currently active step, or None if not started.
        headline (str): Headline text to show above the steps.
        finished (bool): Whether the process is finished.

    Returns:
        str: HTML string for the progress card.
    """
    safe_headline = html.escape(headline or "")
    items: list[str] = []
    for idx, (title, desc) in enumerate(PROGRESS_STEPS):
        if finished:
            state = "done"
        elif active_index is None:
            state = "idle"
        elif idx < active_index:
            state = "done"
        elif idx == active_index:
            state = "active"
        else:
            state = "upcoming"
        items.append(
            "<li class='progress-step {state}'>"
            "<div class='dot'></div>"
            "<div class='labels'>"
            f"<div class='title'>{html.escape(title)}</div>"
            f"<div class='desc'>{html.escape(desc)}</div>"
            "</div>"
            "</li>".format(state=state)
        )
    return (
        "<div class='progress-card'>"
        f"<div class='progress-head'>{safe_headline}</div>"
        "<ul class='progress-steps'>" + "".join(items) + "</ul>"
        "</div>"
    )


def _loading_jobs_html() -> str:
    """Small placeholder shown while waiting for job cards.

    Returns:
        str: HTML string for the loading placeholder.
    """
    return (
        "<div class='loading-jobs'>"
        "<div class='loading-spinner'></div>"
        "<div>Profiling your resume, searching boards, and ranking matches...</div>"
        "</div>"
    )


def _render_status_message(title: str, subtitle: str | None = None) -> str:
    """Simple status card without progress steps.

    Args:
        title (str): Title text.
        subtitle (str | None): Optional subtitle text.

    Returns:
        str: HTML string for the status card.
    """
    safe_title = html.escape(title or "")
    safe_sub = html.escape(subtitle or "") if subtitle else ""
    return (
        "<div class='status-card'>"
        f"<div class='title'>{safe_title}</div>"
        + (f"<div class='subtitle'>{safe_sub}</div>" if safe_sub else "")
        + "</div>"
    )


def _execute_graph(
    resume_path: str, preferences: dict[str, Any], progress_queue: Queue | None = None
) -> tuple[str, str]:
    """Run the pipeline sequentially and format outputs.

    Args:
        resume_path (str): Path to the resume file.
        preferences (dict[str, Any]): Job search preferences.
        progress_queue (Queue | None): Queue to report step completion to the UI.

    Returns:
        tuple[str, str]: Summary text and HTML for ranked jobs.
    """
    state: dict[str, Any] = {"resume_file": resume_path, "job_preferences": preferences}

    for idx, node in enumerate(PIPELINE_NODES):
        state = node(state)
        if progress_queue and idx < len(PIPELINE_NODES) - 1:
            progress_queue.put(idx + 1)

    ranked_jobs = state.get("job_ranked", {}).get("jobs") or []
    summary = (
        f"Found {len(ranked_jobs)} job(s) ranked by fit."
        if ranked_jobs
        else "No job matches returned for the given preferences."
    )
    jobs_html = _format_jobs_html(ranked_jobs)
    return summary, jobs_html


def _format_jobs_html(jobs: list[dict[str, Any]]) -> str:
    """Render ranked jobs as interactive HTML cards.

    Args:
        jobs (list[dict[str, Any]]): List of job dictionaries.

    Returns:
        str: HTML string containing job cards.
    """
    if not jobs:
        return "<div class='empty-state'>No job matches returned yet.</div>"

    cards: list[str] = []
    for job in jobs:
        title = html.escape(_first(["title", "job_title", "role", "position"], job, "Role not provided"))
        company = html.escape(_first(["company", "company_name", "employer_name"], job, "Unknown company"))
        location = html.escape(
            _first(["location", "formatted_location", "city", "country"], job, "Location not provided")
        )
        rank = html.escape(str(job.get("rank") or "?"))
        link = _first(["job_url", "url", "link", "apply_link"], job, "")
        score_cls, score_label, score_fill = _score_meta(job.get("score"))
        desc = job.get("match_description") or {}
        summary_text = (desc.get("summary") or "").strip()
        summary_text = html.escape(summary_text)
        preview_text = _truncate(summary_text, limit=120) if summary_text else "Read AI fit summary"
        positives = [html.escape(p.strip()) for p in (desc.get("positives") or []) if p.strip()]
        negatives = [html.escape(n.strip()) for n in (desc.get("negatives") or []) if n.strip()]

        positives_html = (
            "<div class='pill pill-positive'>Positives"
            f"<div class='pill-tooltip'><ul>{''.join(f'<li>{p}</li>' for p in positives)}</ul></div>"
            "</div>"
            if positives
            else ""
        )
        negatives_html = (
            "<div class='pill pill-negative'>Negatives"
            f"<div class='pill-tooltip'><ul>{''.join(f'<li>{n}</li>' for n in negatives)}</ul></div>"
            "</div>"
            if negatives
            else ""
        )

        score_circle = (
            "<div class='score-chip {cls}'>"
            "<svg viewBox='0 0 44 44' class='score-circle' aria-hidden='true'>"
            "<circle class='score-bg' cx='22' cy='22' r='18'></circle>"
            "<circle class='score-fg' cx='22' cy='22' r='18' "
            "stroke-dasharray='{dash} 113'></circle>"
            "</svg>"
            "<span class='score-text'>{label}</span>"
            "</div>"
        ).format(cls=score_cls, dash=int(113 * score_fill), label=html.escape(score_label))

        link_html = (
            f"<a class='job-link' href='{html.escape(link)}' target='_blank' rel='noreferrer'>Open job posting</a>"
            if link
            else ""
        )

        details_html = (
            "<details class='summary-toggle'>"
            f"<summary><span class='summary-preview'>{preview_text}</span>"
            "<span class='summary-action'>"
            "<span class='action-closed'>Read AI fit summary</span>"
            "<span class='action-open'>Hide AI fit summary</span>"
            "</span></summary>"
            f"<div class='summary-full'>{summary_text or 'No AI summary available yet.'}</div>"
            "</details>"
        )

        card = (
            "<div class='job-card'>"
            "<div class='job-header'>"
            "<div class='title-stack'>"
            f"<div class='rank-chip'>#{rank}</div>"
            f"<div class='title-line'>{title}</div>"
            f"<div class='meta-line'>{company} · {location}</div>"
            "</div>"
            "<div class='header-actions'>"
            f"{positives_html}{negatives_html}{score_circle}"
            "</div>"
            "</div>"
            "<div class='job-body'>"
            f"{details_html}"
            f"{link_html}"
            "</div>"
            "</div>"
        )

        cards.append(card)

    return "<div class='jobs-grid'>" + "".join(cards) + "</div>"


def _normalize_filepath(upload: Any) -> str | None:  # noqa: ANN401
    """Accept string paths or file-like objects from Gradio.

    Args:
        upload (Any): Uploaded file input.

    Returns:
        str | None: File path as string, or None if not provided.
    """
    if upload is None:
        return None
    if isinstance(upload, str):
        return upload
    return getattr(upload, "name", None)


def run_pipeline(
    resume_file: Any,  # noqa: ANN401
    location: str,
    distance_km: float,
    job_type: str,
    is_remote: bool,
    results_wanted: int,
    hours_old: int,
    site_name: list[str],
    notes: str,
) -> Any:  # noqa: ANN401
    """Execute the agentic pipeline end-to-end with a streaming progress UI.

    Args:
        resume_file (Any): Uploaded resume file.
        location (str): Preferred job location.
        distance_km (float): Search radius in kilometers.
        job_type (str): Type of job to search for.
        is_remote (bool): Whether to include remote jobs.
        results_wanted (int): Maximum results per site.
        hours_old (int): Posted within this many hours.
        site_name (list[str]): List of job boards to search.
        notes (str): Extra user preferences.

    Yields:
        Any: Generator yielding status and matches HTML.
    """
    resume_path = _normalize_filepath(resume_file)
    if not resume_path:
        yield (
            _render_status_message("Please upload a PDF resume to start the search."),
            "<div class='empty-state'>Waiting for input...</div>",
        )
        return

    preferences = {
        "location": location or "France",
        "distance_km": int(distance_km) if distance_km else 30,
        "job_type": job_type or "fulltime",
        "is_remote": bool(is_remote),
        "results_wanted": int(results_wanted) if results_wanted else 10,
        "hours_old": int(hours_old) if hours_old else 72,
        "site_name": site_name or ["linkedin", "indeed"],
        "linkedin_fetch_description": True,
    }
    if notes:
        preferences["notes"] = notes.strip()

    progress_queue: Queue = Queue()
    future = _EXECUTOR.submit(_execute_graph, resume_path, preferences, progress_queue)
    active_idx = 0
    status_text = f"{PROGRESS_STEPS[active_idx][0]} in progress..."
    yield _render_progress(active_idx, status_text), _loading_jobs_html()

    while True:
        try:
            next_idx = progress_queue.get(timeout=0.25)
        except Empty:
            next_idx = None

        if isinstance(next_idx, int) and next_idx != active_idx and 0 <= next_idx < len(PROGRESS_STEPS):
            active_idx = next_idx
            status_text = f"{PROGRESS_STEPS[active_idx][0]} in progress..."
            yield _render_progress(active_idx, status_text), _loading_jobs_html()

        if future.done() and progress_queue.empty():
            break

    try:
        summary, jobs_html = future.result()
    except Exception as exc:
        yield (
            _render_status_message("Job matching failed", str(exc)),
            "<div class='empty-state'>Could not retrieve jobs.</div>",
        )
        return

    yield _render_status_message(summary, "Adjust filters and rerun to refine results."), jobs_html


with gr.Blocks(title="France Chômage — Agentic matcher", fill_width=True) as demo:
    gr.HTML(f"<style>{APP_CSS}</style>")
    gr.Markdown(
        """
        # France Chômage — Agentic matcher
        Upload your resume and basic preferences to let our multi-agent graph extract your profile, search job boards,
        filter irrelevant offers, and rank the best matches. Make sure `NEBIUS_API_KEY` is set in your environment.
        """
    )

    with gr.Row(elem_classes=["main-layout"]):
        with gr.Column(scale=4):
            resume_file = gr.File(
                label="Resume (PDF)",
                file_count="single",
                file_types=[".pdf"],
                type="filepath",
                height=120,
            )
            site_name = gr.CheckboxGroup(
                choices=["linkedin", "indeed", "glassdoor", "google"],
                label="Job boards to search",
                value=["linkedin", "indeed"],
            )
            location = gr.Textbox(label="Preferred location", placeholder="Paris, France", value="Paris, France")
            distance_km = gr.Slider(0, 100, value=30, step=5, label="Distance radius (km)")
            job_type = gr.Radio(
                choices=["fulltime", "parttime", "internship", "contract", "summer"],
                label="Job type (single choice)",
                value="fulltime",
                info="Change and rerun the search if you want a different job type.",
            )
            is_remote = gr.Checkbox(label="Remote friendly", value=False)
            results_wanted = gr.Slider(1, 25, value=10, step=1, label="Max results per site")
            hours_old = gr.Slider(12, 168, value=72, step=12, label="Posted within (hours)")
            notes = gr.Textbox(
                label="Extra preferences",
                placeholder="Team size, industries, languages, salary expectations...",
                lines=3,
            )
            run_button = gr.Button("Find my matches", variant="primary")

        with gr.Column(scale=7, elem_classes=["results-column"]):
            status = gr.HTML(
                value=_render_status_message("Upload a resume and click Find my matches to start."),
                elem_classes=["status-panel"],
            )
            matches = gr.HTML(value="<div class='empty-state'>No results yet.</div>", elem_classes=["matches-panel"])

    run_button.click(
        fn=run_pipeline,
        inputs=[
            resume_file,
            location,
            distance_km,
            job_type,
            is_remote,
            results_wanted,
            hours_old,
            site_name,
            notes,
        ],
        outputs=[status, matches],
    )


if __name__ == "__main__":
    demo.launch()
