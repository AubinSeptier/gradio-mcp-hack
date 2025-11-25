"""Gradio app for the Hackathon track 1: Building MCP."""  # noqa: INP001

import gradio as gr
from tools import job_search_tool, resume_extractor

DOC = """
"""
job_interface = gr.Interface(
    fn=job_search_tool,
    inputs=[
        gr.components.Dropdown(
            choices=["linkedin", "indeed", "glassdoor", "google"], multiselect=True, label="Job Sites"
        ),
        gr.components.Textbox(max_lines=3, placeholder="machine learning engineer", label="Search Terms"),
        gr.components.Textbox(max_lines=3, placeholder="", label="Google Search Term"),
        gr.components.Textbox(max_lines=1, placeholder="Paris", label="Location"),
        gr.components.Number(label="Distance (km)", placeholder="30"),
        gr.components.Dropdown(
            choices=["fulltime", "parttime", "internship", "contract", "summer"],
            multiselect=False,
            label="Job Type",
        ),
        gr.components.Checkbox(value=False, label="Remote Job"),
        gr.components.Number(label="Max jobs to retrieve", placeholder=10, maximum=25),
        gr.components.Number(label="Job posting since... (hours)", placeholder=72),
        gr.components.Checkbox(value=False, label="LinkedIn Deep Search"),
    ],
    outputs=[gr.components.JSON()],
    title="Job Search Tool",
    description="A Job Search tool using JobSpy to scrape jobs from popular employment websites.",
)

resume_interface = gr.Interface(
    fn=resume_extractor,
    inputs=[
        gr.components.File(label="Upload Resume (PDF format)", file_types=[".pdf"]),
    ],
    outputs=[gr.components.JSON()],
    title="Resume Extractor",
    description=(
        "A Resume Extractor tool using a VLM to analyze your resume and "
        "extract relevant information. ❗ Only resumes with 1 page and in PDF format are supported."
    ),
)

demo = gr.Blocks()
with demo:
    with gr.Tabs():
        with gr.TabItem("ℹ️ About"):
            gr.Markdown(DOC)
        with gr.TabItem("🔎 Job Search Tool"):
            job_interface.render()
        with gr.TabItem("📝 Resume Extractor"):
            resume_interface.render()

if __name__ == "__main__":
    demo.launch(mcp_server=True)
