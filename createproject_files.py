#!/usr/bin/env python3
from pathlib import Path

# Project root and directories
PROJECT_ROOT = Path("debateai")
CREWAI_DIR = PROJECT_ROOT / "crewai"
TOOLS_DIR = PROJECT_ROOT / "tools"

# Define files to create (empty or minimal content)
FILES = {
    CREWAI_DIR / "__init__.py": "",
    CREWAI_DIR / "agents.py": "",
    CREWAI_DIR / "tasks.py": "",
    CREWAI_DIR / "crew.py": "",
    TOOLS_DIR / "__init__.py": "",
    TOOLS_DIR / "search_tool.py": "",
    TOOLS_DIR / "file_tool.py": "",
    PROJECT_ROOT / ".env.example": "",
    PROJECT_ROOT / "requirements.txt": "",
    PROJECT_ROOT / "main.py": "",
    PROJECT_ROOT / "README.md": "",
}

# Create directories
CREWAI_DIR.mkdir(parents=True, exist_ok=True)
TOOLS_DIR.mkdir(parents=True, exist_ok=True)

# Create files
for path, content in FILES.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Minimal CrewAI project structure created successfully!")
