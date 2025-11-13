from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
from typing import List
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from tools.file_tool import PushNotificationTool


# =========================
# Pydantic Models
# =========================

class TrendingCompany(BaseModel):
    """A company that is in the news and attracting attention"""
    name: str = Field(description="Company name")
    ticker: str = Field(description="Stock ticker symbol")
    reason: str = Field(description="Reason this company is trending in the news")


class TrendingCompanyList(BaseModel):
    """List of multiple trending companies that are in the news"""
    companies: List[TrendingCompany] = Field(description="List of companies trending in the news")


class TrendingCompanyResearch(BaseModel):
    """Detailed research on a company"""
    name: str = Field(description="Company name")
    market_position: str = Field(description="Current market position and competitive analysis")
    future_outlook: str = Field(description="Future outlook and growth prospects")
    investment_potential: str = Field(description="Investment potential and suitability for investment")


class TrendingCompanyResearchList(BaseModel):
    """A list of detailed research on all the companies"""
    research_list: List[TrendingCompanyResearch] = Field(description="Comprehensive research on all trending companies")


# =========================
# CrewBase Class
# =========================

@CrewBase
class StockPicker():
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ---------- Agents ----------

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config["trending_company_finder"],
            tools=[SerperDevTool()],
            memory=True
        )

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["financial_researcher"],
            tools=[SerperDevTool()]
        )

    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config["stock_picker"],
            tools=[PushNotificationTool()],
            memory=True
        )

    # ---------- Tasks ----------

    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config["find_trending_companies"],
            output_pydantic=TrendingCompanyList
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config["research_trending_companies"],
            output_pydantic=TrendingCompanyResearchList
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config["pick_best_company"]
        )

    # ---------- Crew Setup ----------

    @crew
    def crew(self) -> Crew:
        
        """Creates the StockPicker crew"""
        manager = Agent(
            config=self.agents_config["manager"],
            allow_delegation=True
        )

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager,
            memory=True,

            # Long-term memory (SQLite) - OK
            long_term_memory=LongTermMemory(storage=LTMSQLiteStorage(db_path="./memory/long_term_memory_storage.db")),

            # Short-term memory - FIXED
            short_term_memory=ShortTermMemory(
                storage=RAGStorage(
                    embedder_config={
                        "provider": "openai",
                        "model": "text-embedding-3-small"   # ← MOVED TO TOP LEVEL
                        # NO "config": { ... } wrapper!
                    },
                    type="short_term",
                    path="./memory/"
                )
            ),

            # Entity memory - FIXED
            entity_memory=EntityMemory(
                storage=RAGStorage(
                    embedder_config={
                        "provider": "openai",
                        "model": "text-embedding-3-small"   # ← TOP LEVEL
                    },
                    type="entities",  # ← should be "entities", not "short_term"
                    path="./memory/"
                )
            ),
        )