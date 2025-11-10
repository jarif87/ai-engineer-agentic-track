import sys
import warnings
from datetime import datetime
import os
from debate.crew import Debate  
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the Debate crew.
    """
    inputs = {
        "motion": "There needs to be strict laws to regulate LLMs",
    }

    try:
        debate_crew = Debate().crew()
        result = debate_crew.kickoff(inputs=inputs)
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

if __name__ == "__main__":
    run()
