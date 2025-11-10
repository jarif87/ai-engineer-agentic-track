from crewai import Crew, Process
from crewai.project import CrewBase, agent, crew, task

from debate.agents import create_debater, create_judge
from debate.tasks import create_propose_task, create_oppose_task, create_decide_task

@CrewBase
class Debate:

    @agent
    def debater(self):
        return create_debater()

    @agent
    def judge(self):
        return create_judge()

    @task
    def propose(self):
        return create_propose_task()

    @task
    def oppose(self):
        return create_oppose_task()

    @task
    def decide(self):
        return create_decide_task()

    @crew
    def crew(self):
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
