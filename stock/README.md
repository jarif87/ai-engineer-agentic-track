# StockPickerAI

**StockPickerAI** is an AI-powered financial analysis CrewAI project that identifies trending companies in the news, conducts detailed research, and picks the best investment opportunity. It leverages multiple AI agents, task orchestration, and memory storage for persistent knowledge.

---

## 🚀 Features

- **Trending Company Finder**: Identifies companies currently trending in financial news.
- **Financial Researcher**: Provides detailed analysis of trending companies, including market position, future outlook, and investment potential.
- **Stock Picker**: Chooses the best company to invest in based on research findings and sends notifications.
- **Manager Agent**: Delegates tasks efficiently and oversees the crew operations.
- **Memory**: Supports short-term, long-term, and entity memory to maintain context across sessions.
- **Push Notifications**: Sends alerts when the best company for investment is selected.

---

## 🗂 Project Structure

```
stock/
├─ app/
│ ├─ config/
│ │ ├─ agents.yaml
│ │ └─ tasks.yaml
│ ├─ crew.py
│ ├─ init.py
│ └─ tasks.py
├─ tools/
│ ├─ file_tool.py
│ └─ search_tool.py
├─ memory/
├─ main.py
├─ requirements.txt
└─ .env
```


- `agents.yaml` – Defines AI agents and their roles.
- `tasks.yaml` – Defines tasks, outputs, and which agent executes them.
- `crew.py` – CrewAI setup with agents, tasks, and memory configuration.
- `file_tool.py` – Custom tools (e.g., PushNotificationTool).
- `.env` – Stores API keys for OpenAI, Serper, etc.

---

## ⚡ Setup

1. **Clone the repository**
```
git clone https://github.com/jarif87/ai-engineer-agentic-track.git
cd stock
```

2. Install dependencies
```
pip install -r requirements.txt

```
3. Create .env file in the project root:
```
OPENAI_API_KEY=""
PUSHOVER_USER=""
PUSHOVER_TOKEN=""
SERPER_API_KEY=""
CHROMA_OPENAI_API_KEY=""
```
4. Run the project
```
python main.py
```
# How It Works
- Find Trending Companies – trending_company_finder reads the latest news in a sector and outputs 2–3 trending companies.
- Research Companies – financial_researcher produces a detailed report for each trending company.
- Pick the Best Company – stock_picker analyzes the research, selects the best investment, sends a push notification, and produces a detailed report.
- Manager Agent – Coordinates tasks and agents to ensure the workflow is efficient and no duplicate companies are picked.
- Memory – Tracks knowledge over time using:
    - Short-Term Memory: Current session knowledge
    - Long-Term Memory: Persistent storage in SQLite
    - Entity Memory: Tracks companies, sectors, and other key entities


# 🛠 Technology Stack
- CrewAI – Agent orchestration framework
- OpenAI GPT-4o-mini – LLM for analysis and reasoning
- SerperDevTool – Real-time web search
- SQLite + RAG – Memory and knowledge storage
- Pydantic – Structured input/output for tasks

# 📁 Outputs
- output/trending_companies.json – List of trending companies
- output/research_report.json – Detailed research on trending companies
- output/decision.md – Final investment decision with rationale