# financial_research/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# CORRECT IMPORTS FOR crewai-tools==1.4.1
from crewai_tools import (
    DirectoryReadTool,
    FileReadTool,
    FileWriterTool,
    SerperDevTool,
    WebsiteSearchTool
)


@CrewBase
class ResearchCrew:
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            tools=[SerperDevTool(), FileWriterTool()],
            verbose=True
        )

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["analyst"],
            tools=[FileReadTool(), FileWriterTool(), SerperDevTool()],
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])

    @task
    def analysis_task(self) -> Task:
        return Task(config=self.tasks_config["analysis_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.researcher(), self.analyst()],
            tasks=[self.research_task(), self.analysis_task()],
            process=Process.sequential,
            verbose=True
        )