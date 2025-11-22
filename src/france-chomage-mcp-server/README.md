---
title: France Chômage - MCP Server
emoji: 📊
colorFrom: green
colorTo: red
sdk: gradio
sdk_version: 6.0.0.dev4
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
