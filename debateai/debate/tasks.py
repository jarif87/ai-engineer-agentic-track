# debate/tasks.py
from debate.agents import create_debater, create_judge
from crewai import Task

def create_propose_task():
    return Task(
        description=(
            "You are proposing the motion: {motion}. "
            "Come up with a clear argument in favor of the motion. "
            "Be very convincing."
        ),
        expected_output="Your clear argument in favor of the motion, in a concise manner.",
        agent=create_debater(),   # ✅ pass the actual Agent object
        output_file="output/propose.md",
        verbose=True
    )

def create_oppose_task():
    return Task(
        description=(
            "You are in opposition to the motion: {motion}. "
            "Come up with a clear argument against the motion. "
            "Be very convincing."
        ),
        expected_output="Your clear argument against the motion, in a concise manner.",
        agent=create_debater(),  # ✅ pass the actual Agent object
        output_file="output/oppose.md",
        verbose=True
    )

def create_decide_task():
    return Task(
        description="Review the arguments presented by the debaters and decide which side is more convincing.",
        expected_output="Your decision on which side is more convincing, and why.",
        agent=create_judge(),  # ✅ pass the actual Agent object
        output_file="output/decide.md",
        verbose=True
    )
