#!/usr/bin/env python3
from pathlib import Path

# Project root and directories
PROJECT_ROOT = Path("auto_dev_orchestrator")
APP_DIR = PROJECT_ROOT / "app"
TOOLS_DIR = PROJECT_ROOT / "tools"
CONFIG_DIR = APP_DIR / "config"  # config is now inside app/

# Define files with minimal starter content
FILES = {
    APP_DIR / "__init__.py": "",
    APP_DIR / "agents.py": """# agents.py
# Define custom agent classes or wrappers here
""",
    APP_DIR / "tasks.py": """# tasks.py
# Define custom task handlers or logic here
""",
    APP_DIR / "crew.py": '''# crew.py
# Entry point for CrewAI setup
import yaml
from pathlib import Path

def load_yaml_config():
    config_path = Path(__file__).parent / 'config'
    agents = yaml.safe_load(open(config_path / 'agents.yaml'))
    tasks = yaml.safe_load(open(config_path / 'tasks.yaml'))
    return agents, tasks

def initialize_crew():
    agents, tasks = load_yaml_config()
    print("Loaded Agents:", agents)
    print("Loaded Tasks:", tasks)

if __name__ == '__main__':
    initialize_crew()
''',
    TOOLS_DIR / "__init__.py": "",
    TOOLS_DIR / "search_tool.py": """# search_tool.py
def search(query):
    return f'Search results for: {query}'
""",
    TOOLS_DIR / "file_tool.py": """# file_tool.py
def save_file(path, content):
    with open(path, 'w') as f:
        f.write(content)
""",
    CONFIG_DIR / "agents.yaml": """# agents.yaml
agents:
  - name: DebateAgent
    role: discuss
    description: Handles logical debate responses.
  - name: ResearchAgent
    role: researcher
    description: Provides factual support for debates.
""",
    CONFIG_DIR / "tasks.yaml": """# tasks.yaml
tasks:
  - name: DebateRound
    description: Conducts a single round of argument exchange.
  - name: FactCheck
    description: Verifies facts mentioned during debate.
""",
    PROJECT_ROOT / ".env": "OPENAI_API_KEY=your_api_key_here\n",
    PROJECT_ROOT / "requirements.txt": "crewai\npyyaml\npython-dotenv\n",
    PROJECT_ROOT / "main.py": '''# main.py
from app.crew import initialize_crew

if __name__ == '__main__':
    initialize_crew()
''',
    PROJECT_ROOT / "README.md": """# DebateAI
A minimal CrewAI project using YAML configuration files.

## Structure
- app/
  - config/ → YAML configs for agents and tasks
  - crew.py → CrewAI setup and initialization
- tools/ → Utility tools
- main.py → Entry point
""",
}

# Create directories
for directory in [APP_DIR, TOOLS_DIR, CONFIG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Create files
for path, content in FILES.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")  # Ensure clean write with trailing newline

print("\033[92m[✔] CrewAI project structure (with app/ and config inside) created successfully!\033[0m")