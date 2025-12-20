"""
PolicyLens Agent - Tools and utilities
"""
import pandas as pd
from PyPDF2 import PdfReader

def extract_policy_text(pdf_path: str) -> str:
    """Extract text from policy PDF"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""

def load_demographics(csv_path: str) -> str:
    """Load demographics data from CSV and convert to string for the agent"""
    try:
        df = pd.read_csv(csv_path)
        # Convert first few rows to string to give context, or full content if small
        return df.to_string(index=False)
    except Exception as e:
        print(f"Error loading demographics: {e}")
        return ""

def assess_policy_impact(policy_text: str):
    """
    Simulates the reasoning step for policy impact assessment.
    In a full agentic system, this would trigger specific sub-agents.
    For this hackathon, it structures the reasoning output.
    """
    print(f"Analyzing policy impact...")
    return {
        "step": "impact_reasoning",
        "status": "completed",
        "details": "Policy text analyzed against demographic markers."
    }
