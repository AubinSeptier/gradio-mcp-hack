---
title: France Chômage - MCP Server
emoji: 📊
colorFrom: green
colorTo: red
sdk: gradio
sdk_version: 6.0.1
app_file: app.py
pinned: false
license: mit
short_description: A gradio MCP server providing AI agents with tools to search for and analyze job offers. Created for the Gradio x MCP Hackathon.
tags:
- building-mcp-track-customer
---

# France Chômage: A MCP server to find jobs

## Introduction

**France Chômage MCP Server** offers MCP tools to help your AI agents find job offers that match your profile.
This is our Gradio app for the **MCP's 1st Birthday** Hackathon track 1: Building MCP.

This is our first MCP server project, named "France Chômage MCP Server", which aims to help job seekers in France
(and in the whole world) by providing tools to search for jobs and analyze resumes.

## 🧑‍💻 Team Members

**Team Name:**: Chicout' Green Team

**Team Members:**
- **Théophile Baudry** - [@Darkensyde](https://huggingface.co/Darkensyde) - The Tireless Coder (truly tireless!)
- **Aubin Septier** - [@Aubins](https://huggingface.co/Aubins) - The budding project "leader" (but still learning!)

## Prerequisites

You need to install `poppler` to use the MCP server locally or on your own infrastructures:

- Debian/Ubuntu:
```bash
sudo apt install poppler-utils
```

- macOS (brew):
```
brew install poppler
```

- Windows (choco):
```
choco install poppler
```

Then, install the required Python packages:
```bash
pip install -r requirements.txt
```

Rename the `.env.example` file to `.env` and set your environment variables as needed:

```bash
cp .env.example .env
```

Finally, run the MCP server:
```bash
python app.py
```

The MCP server will be accessible at `http://localhost:7860` by default.

You can also deploy it on [Hugging Face Spaces](https://huggingface.co/spaces) by pushing the code to a new Space repository.

## 🚀 Deployment on Blaxel AI

This MCP server can be deployed on [Blaxel AI](https://blaxel.ai/)! Follow these steps:

1. Create a Blaxel account if you don't have one.
2. Install the Blaxel CLI by following the instructions at https://docs.blaxel.ai/Get-started and log in with `bl login`.
3. Use the `bl deploy` command from the Blaxel CLI to deploy the MCP server on their infrastructure.
  The configuration is already set up in the `blaxel.toml` file and Dockerfile in the repository. Please free to modify
  them according to your needs.

> Note: Blaxel AI provides a free tier with $200 credits for new users, then pay-as-you-go pricing. Check their website for more details.

## 🏰 MCP Server Architecture

The MCP server codebase follows this architecture:
```
france-chomage-mcp-server/
├── app.py                  # Main Gradio app file
├── server.py               # MCP server implementation using FastMCP for Blaxel deployment
├── tools/                  # Directory containing MCP tools
│   ├── job_search_tool.py   # Job Search Tool implementation
│   └── resume_extractor.py  # Resume Extractor Tool implementation
├── requirements.txt        # Python dependencies
├── Dockerfile              # Dockerfile for Blaxel deployment
├── blaxel.toml             # Blaxel configuration file
└── README.md               # This README file
└── .env.example          # Example environment variables file
```

## 🔧 Tools included
Our MCP server includes the following tools:
- **Job Search Tool**: A Job Search tool using JobSpy to scrape jobs from popular employment
  websites (LinkedIn, Indeed, etc.).
- **Resume Extractor**: A Resume Extractor tool using a VLM to analyze your resume and
  extract relevant information in a structured format.

> Note: The Resume Extractor tool uses a VLM model provided by Nebius. Make sure to set the `NEBIUS_API_KEY` environment variable in your `.env` file to use this tool.

## 📚 Why use this MCP server ?

This MCP server is designed to help AI agents assist users in finding job offers that match their profiles.
By integrating job search and resume analysis tools, AI agents can provide personalized job recommendations
and improve the job search experience for users.

## ⚠️ Limitations
Here are some limitations to be aware of:
- The Job Search Tool may not retrieve all job listings due to website restrictions. LinkedIn is quickly blocking
  requests. Use Indeed or Glassdoor for better results and less blocking. Google Jobs search is also a good alternative
  but the search terms need to be well defined. In any case, use this tool responsibly and avoid sending too many
  requests in a short period of time.
- LinkedIn Deep Search may take longer to retrieve results as it fetches full job descriptions.
- The Job Search Tool relies on web scraping, which may be affected by changes in the target websites' structure.
- The Job Search Tool does not implement all the features, filters, and options available in JobSpy. We only implemented
  the most interesting ones from our point of view and our users' needs. Look at [JobSpy documentation](https://github.com/speedyapply/JobSpy) for more details on the job search tool
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
