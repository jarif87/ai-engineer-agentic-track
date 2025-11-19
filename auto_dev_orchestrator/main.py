#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime
from app.crew import EngineeringTeam
from dotenv import load_dotenv
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

load_dotenv()

os.makedirs('output', exist_ok=True)

requirements = """
A simple library management system.
The system should allow users to register as members and manage their accounts.
The system should allow adding new books to the library and removing books.
The system should allow members to borrow and return books.
The system should track due dates and calculate fines for overdue books.
The system should provide reports on which books are borrowed, by whom, and overdue books.
The system should prevent borrowing of unavailable books and returning of books not borrowed.
"""

module_name = "library.py"
class_name = "Library"

def run():
    inputs = {'requirements': requirements,'module_name': module_name,'class_name': class_name}
    result = EngineeringTeam().crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    run()
