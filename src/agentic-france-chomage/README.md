---
title: France Chômage - Agentic App
emoji: 📊
colorFrom: green
colorTo: red
sdk: gradio
sdk_version: 6.0.1
app_file: app.py
pinned: false
license: mit
short_description: Search job offers matching your profile using AI agents.
tags:
- mcp-in-action-track-consumer
---

# France Chômage : A Job Search Assistant using AI Agents and MCP Tools

## Introduction

**France Chômage** is an innovative job search agentic assistant designed to help users find job offers that best match their profiles and preferences. Built using Gradio and LangGraph and leveraging the power of MCP tools, this application showcases how AI agents can streamline the job search process. This is our Gradio app for the **MCP's 1st Birthday** Hackathon track 2: MCP in Action.

This is our first agentic AI project, named "France Chômage", which aims to assist users in finding job offers in France (and in the whole world) by leveraging an agentic AI wokflow and MCP tools.

## 🧑‍💻 Team Members

**Team Name:**: Chicout' Green Team

**Team Members:**
- **Théophile Baudry** - [@Darkensyde](https://huggingface.co/Darkensyde) - The Tireless Coder (truly tireless!)
- **Aubin Septier** - [@Aubins](https://huggingface.co/Aubins) - The budding project "leader" (but still learning!)

## Prerequisites

You have to install the required Python packages:

```bash
pip install -r requirements.txt
```

Rename the `.env.example` file to `.env` and set your environment variables as needed:

```bash
mv .env.example .env
```

Finally, run the Gradio app:

```bash
python app.py
```

The app will be accessible at `http://localhost:7860` by default.

You can also deploy it on [Hugging Face Spaces](https://huggingface.co/spaces) by pushing the code to a new Space repository.

## 🚀 Deployment on Blaxel AI

_Coming soon..._

## 🏰 App Architecture

The app codebase follows this architecture:

```
agentic-france-chomage/
├── app.py                  # Main Gradio app file
├── agents/                 # Directory for agent definitions
├── graphs/                 # Directory for LangGraph graph definitions
├── utils/                  # Utility functions and helpers
├── requirements.txt        # Python dependencies
├── README.md               # This README file
└── .env.example            # Example environment variables file
```

## 🛠️ Key Features

Our app includes the following key features:

- **Resume Upload**: Users can upload their resumes in PDF format.
- **Job Preferences**: Users can specify their job search preferences, including location, job type or job websites.
- **Agentic Workflow**: The app uses an agentic AI workflow to process the resume and preferences, leveraging MCP tools to search for relevant job offers and analyze resume. Then, it ranks the job offers based on how well they match the user's profile and provides a summary of the results with explanations, pros and cons.
- **Interactive UI**: The Gradio interface provides an intuitive and user-friendly experience, displaying progress indicators and results in a clear format.

> Note: The AI agents uses LLM models provided by Nebius. Make sure to set the NEBIUS_API_KEY environment variable in your .env file to use this tool.

## 📚 Why use this app?

This app is designed to assist job seekers in efficiently finding job opportunities that align with their skills and preferences. By leveraging AI agents and MCP tools, the app automates the job search process, saving users time and effort while increasing the chances of finding suitable job offers.

## ⚠️ Limitations

Here are some limitations to be aware of:

- **Data Privacy**: Users should be cautious about uploading sensitive information in their resumes, as the app processes this data using AI agents hosted on external platforms.
- **Job Database**: The app relies on external job listing websites (LinkedIn, Indeed, Glassdoor and Google), which may not cover all available job opportunities.
- **AI Limitations**: The quality of job matching and ranking depends on the accuracy and capabilities of the underlying AI models, which may not always perfectly understand user preferences or job descriptions.
- **Applying to Jobs**: The app does not handle the actual application process for jobs; users will need to apply directly through the job listing websites. (You were not expecting an AI that applies to jobs on your behalf, right 🫣?).

## 👩🏼‍⚖️ Licence & Acknowledgements

Licence is MIT.

The project is open-source and available on [GitHub repository](https://github.com/AubinSeptier/gradio-mcp-hack).

We know this app is not perfect and has limitations. As we said before, this is our first agentic AI project, and we learned a lot during its development about AI agents, Gradio, Blaxel deployment, and more.

A big thank you to the Gradio team for creating such an amazing library, and for organizing this hackathon to celebrate MCP's first birthday!

Special thanks to LangGraph developers for their incredible tool that made building agentic workflows much easier.

Thank you to Nebius and Blaxel AI for sponsoring this hackathon and providing resources for deployment.

## 💻 Contributing
Feel free to contribute to this app by submitting issues or pull requests on the GitHub repository. You can also fork the repository and modify the code to suit your needs.

For any questions or support, please open an issue on Github.
