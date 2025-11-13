# main.py
import sys
import warnings
import os
from datetime import datetime
from dotenv import load_dotenv
from app.crew import StockPicker
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

load_dotenv()


def run():
    """
    Run the research crew.
    """
    inputs = {
        'sector': 'Technology',
        "current_date": str(datetime.now())
    }

    # Create and run the crew
    result = StockPicker().crew().kickoff(inputs=inputs)

    # Print the result
    print("\n\n=== FINAL DECISION ===\n\n")
    print(result.raw)


if __name__ == "__main__":
    run()
