# Gradio x MCP Hackathon Project

## 📋 Pre-requisites

Before starting, ensure you have the following tools installed on your machine:

- **Python 3.10-3.13** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))

> ℹ️ **Note**: Other tools (pre-commit, ruff) will be installed automatically with the project dependencies.

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/AubinSeptier/gradio-mcp-hack.git
cd gradio-mcp-hack
```

### 2. Create a virtual environment

**On Linux/macOS :**
```bash
python -m venv .venv
source .venv/bin/activate
```

**On Windows :**
```bash
python -m venv .venv
.venv\Scripts\activate
```

> ℹ️ **Note**: You can use conda or any other virtual environment manager if you prefer.

### 3. Install dependencies

**Basic installation :**
```bash
pip install -e .
```

**Installation with development tools :**
```bash
pip install -e ".[dev]"
```

### 4. Configure pre-commit

```bash
pre-commit install
```

Check that everything works by running all pre-commit hooks on all files:
```bash
pre-commit run --all-files
```

## 🛠️ Development

### Project Structure

```
gradio-mcp-hack/
├── .github/
│   └── PULL_REQUEST_TEMPLATE.md
├── src/
│   └── track1/
│       └── README.md
        └── app.py
│   └── track2/
│       └── README.md
│       └── app.py
├── .gitignore
├── pyproject.toml
├── .pre-commit-config.yaml
└── README.md
```

## 🤝 Contribution

Please check the `PULL_REQUEST_TEMPLATE.md` file in the .github folder for guidelines on how to contribute to this project.
