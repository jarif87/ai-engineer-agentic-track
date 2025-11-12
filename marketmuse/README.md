# Create Project Structure


```
#!/usr/bin/env python3
from pathlib import Path

# Project root and directories
PROJECT_ROOT = Path("marketmuse")
CREWAI_DIR = PROJECT_ROOT / "crewai"
TOOLS_DIR = PROJECT_ROOT / "tools"
CONFIG_DIR = PROJECT_ROOT / "config"

# Define files with minimal starter content
FILES = {
    CREWAI_DIR / "__init__.py": "",
    CREWAI_DIR / "agents.py": """# agents.py
# Define custom agent classes or wrappers here
""",
    CREWAI_DIR / "tasks.py": """# tasks.py
# Define custom task handlers or logic here
""",
    CREWAI_DIR / "crew.py": """# crew.py
# Entry point for CrewAI setup
import yaml
from pathlib import Path

def load_yaml_config():
    config_path = Path(__file__).parent.parent / 'config'
    agents = yaml.safe_load(open(config_path / 'agents.yaml'))
    tasks = yaml.safe_load(open(config_path / 'tasks.yaml'))
    return agents, tasks

def initialize_crew():
    agents, tasks = load_yaml_config()
    print("Loaded Agents:", agents)
    print("Loaded Tasks:", tasks)

if __name__ == '__main__':
    initialize_crew()
""",
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
    PROJECT_ROOT / "requirements.txt": "crewai\nyaml\npython-dotenv\n",
    PROJECT_ROOT / "main.py": """# main.py
from crewai.crew import initialize_crew

if __name__ == '__main__':
    initialize_crew()
""",
    PROJECT_ROOT / "README.md": """# DebateAI
A minimal CrewAI project using YAML configuration files.

## Structure
- `config/` → YAML configs for agents and tasks  
- `crewai/` → Core app logic  
- `tools/` → Utility tools  
""",
}

# Create directories
for directory in [CREWAI_DIR, TOOLS_DIR, CONFIG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Create files
for path, content in FILES.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("\033[92m[✔] CrewAI project structure with YAML config created successfully!\033[0m")
```
