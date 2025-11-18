#!/usr/bin/env python
import os
from dotenv import load_dotenv
from app.crew import Coder

# Load environment variables
load_dotenv()

# Verify that the API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("❌ OPENAI_API_KEY not found in .env file")

# Ensure output directory exists
os.makedirs('output', exist_ok=True)

# The assignment to give to the agent
assignment = """
Implement a high-precision approximation of π using the Chudnovsky algorithm 
(with at least 100 correct decimal places) in pure Python (no external libraries except math).

Requirements:
1. Use only built-in Python types (int, float, decimal is NOT allowed)
2. Implement arbitrary-precision arithmetic yourself using integers only
3. Compute at least 100 decimal places of π (bonus: 200+)
4. Use the full Chudnovsky series with binary splitting for O(n log n³) speed
5. Include a progress bar and estimated time remaining
6. At the end, compare your result with math.pi (truncated) and show:
   - First 100 correct digits
   - Total digits computed
   - Time taken
   - Digits per second achieved

Formula reminder:
π = 426880 × √10005 / Σ[k=0 to n] [ (6k)! × (545140134k + 13591409) / ((3k)! × (k!)³ × (-640320)³ᵏ) ]

Extra challenge:
After computing π, verify correctness by calculating:
sin(π) ≈ 0.0  (within 1e-90 or better)
and print the residual |sin(π)| as final proof.

This is one of the fastest known series for π — used by real world record holders.
"""

def run():
    """
    Run the crew with dynamic input
    """
    # Initialize crew
    crew_instance = Coder().crew()
    
    # Kickoff the crew, passing inputs that match placeholders in tasks.yaml
    result = crew_instance.kickoff(inputs={"assignment": assignment})
    
    # Print the raw output from the agent
    print("✅ Raw Output:\n", result.raw)
    
    print("✅ Check output/code_output.txt for saved results")

if __name__ == "__main__":
    run()
