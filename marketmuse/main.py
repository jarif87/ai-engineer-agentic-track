import os
from dotenv import load_dotenv
from financial_research.crew import ResearchCrew

# Load environment variables from .env file
load_dotenv()

# Verify that the API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("❌ OPENAI_API_KEY not found in .env file!")

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

def run():
    """
    Run the research crew using the company name as input.
    """
    inputs = {'company': 'Apple'}

    # Initialize and run the crew
    crew_instance = ResearchCrew().crew()
    result = crew_instance.kickoff(inputs=inputs)

    # Display results
    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    print("\n\n✅ Report has been saved to output/report.md")

if __name__ == "__main__":
    run()
