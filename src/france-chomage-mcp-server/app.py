"""Gradio app for the Hackathon track 1: Building MCP."""  # noqa: INP001

import gradio as gr
from tools import job_search_tool, resume_extractor

DOC = """# 🇫🇷 France Chômage MCP Server
This is our Gradio app for the **MCP's 1st Birthday** Hackathon track 1: Building MCP.

This is our first MCP server project, named "France Chômage MCP Server", which aims to help job seekers in France
(and in the whole world) by providing tools to search for jobs and analyze resumes.

## 🔧 Tools included
Our MCP server includes the following tools:
- **Job Search Tool**: A Job Search tool using JobSpy to scrape jobs from popular employment
  websites (LinkedIn, Indeed, etc.).
- **Resume Extractor**: A Resume Extractor tool using a VLM to analyze your resume and
  extract relevant information in a structured format.

## 🤔 How to use
As a MCP server, this app can be connected to any MCP-compatible client with the URL of the server (here: https://aubins-france-chomage-mcp-server.hf.space/gradio_api/mcp/).

To directly use the tools, navigate to the respective tabs in the interface.
The simple way to use the MCP server with Gradio and HF Space is to clone this repository and use this cloned version of
  the app.

> Note: Please refer to the `README.md` file in the repository for more information about this MCP server, its
  configuration and dependencies.

## 🚀 Blaxel Deployment

This MCP server can be deployed on Blaxel platform. To do so, follow these steps:
1. Create a Blaxel account if you don't have one.
2. Install the Blaxel CLI by following the instructions at https://docs.blaxel.ai/Get-started
  and log in with `bl login`.
3. Use the `bl deploy` command from the Blaxel CLI to deploy the MCP server on their infrastructure.
  The configuration is already set up in the `blaxel.toml` file and Dockerfile in the repository. Please free to modify
  them according to your needs.

> Note: The python file used is not the `app.py` file but the `server.py` file.

## ⚠️ Limitations
Here are some limitations to be aware of:
- The Job Search Tool may not retrieve all job listings due to website restrictions. LinkedIn is quickly blocking
  requests. Use Indeed or Glassdoor for better results and less blocking. Google Jobs search is also a good alternative
  but the search terms need to be well defined. In any case, use this tool responsibly and avoid sending too many
  requests in a short period of time.
- LinkedIn Deep Search may take longer to retrieve results as it fetches full job descriptions.
- The Job Search Tool relies on web scraping, which may be affected by changes in the target websites' structure.
- The Job Search Tool does not implement all the features, filters, and options available in JobSpy. We only implemented
  the most interesting ones from our point of view and our users' needs.
- Look at [JobSpy documentation](https://github.com/speedyapply/JobSpy) for more details on the job search tool
  capabilities.
- The Resume Extractor currently only supports resumes in PDF format and with a single page.

## 👩🏼‍⚖️ Licence & Acknowledgements
Licence is MIT.

The project is open-source and available on [GitHub repository](https://github.com/AubinSeptier/gradio-mcp-hack).

We know this MCP server is not perfect and has limitations. As we said before, this is our first MCP server project.
  And we have learned a lot during its development about MCP servers, Gradio, Blaxel deployment, and more.

A big thank you to the Gradio team for creating such an amazing library, and for organizing this hackathon
  to celebrate MCP's first birthday!

Special thanks to JobSpy developers for their incredible library, which made the implementation of the Job Search Tool
  possible.

Thank you to Nebius and Blaxel AI for sponsoring this hackathon and providing resources for deployment.

## 💻 Contributing
Feel free to contribute to this MCP server by submitting issues or pull requests on the GitHub repository.
  You can also fork the repository and modify the code to suit your needs.

For any questions or support, please open an issue on Github.
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
