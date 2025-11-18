# app/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, task, crew

@CrewBase
class Coder:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def coder(self) -> Agent:
        return Agent(config=self.agents_config["coder"],verbose=True,allow_code_execution=False,max_execution_time=120,
            max_retry_limit=5)

    @task
    def coding_task(self) -> Task:
        return Task(config=self.tasks_config["coding_task"],output_file="output/result.py")

    @crew
    def crew(self) -> Crew:
        return Crew(agents=self.agents,tasks=self.tasks,process=Process.sequential,verbose=True)