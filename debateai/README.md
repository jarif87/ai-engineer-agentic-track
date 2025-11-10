# DebateAI

**DebateAI** is an AI-powered debate platform that leverages Large Language Models (LLMs) to generate, analyze and evaluate arguments on any motion.

## Features
- **Propose Arguments**: AI generates compelling arguments in favor of a motion.
- **Oppose Arguments**: AI generates clear arguments against a motion.
- **Decide Winner**: AI evaluates arguments and determines the most convincing side.

## Installation
```
git clone https://github.com/jarif87/ai-engineer-agentic-track.git
cd my_crew_project
pip install -r requirements.txt
```

## Setup

1. Create a .env file in the project root:
```
OPENAI_API_KEY=<your_openai_key>
GEMINI_API_KEY=<your_gemini_key>
```
2. Ensure your virtual environment is activated:
```
virtualenv venv
.\venv\Scripts\activate
```
3. Usage
```
python main.py
```
## Project Structure

```
my_crew_project/
├── crewai/
│   ├── __init__.py
│   ├── agents.py
│   ├── tasks.py
│   └── crew.py
├── tools/
│   ├── __init__.py
│   ├── search_tool.py
│   └── file_tool.py
├── .env
├── requirements.txt
├── main.py
└── README.md
```