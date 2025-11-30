# Dockerfile for France Chomage MCP Server deployment on Blaxel AI
FROM python:3.12-slim

# Set working directory
WORKDIR /blaxel

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /blaxel/

RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Command to run when container starts, it need to provide a server running on port 80 for agent and MCP server
ENTRYPOINT ["python", "server.py"]
