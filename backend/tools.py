import logging
import pandas as pd
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


def extract_policy_text(pdf_path: str) -> str:
    """Extract text from policy PDF"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        logger.info(f"Successfully extracted {len(text)} characters from {len(reader.pages)} pages")
        return text
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def load_demographics(csv_path: str) -> str:
    """Load demographics data from CSV and return as text summary"""
    try:
        # Try to read as CSV first
        if csv_path.endswith('.csv'):
            df = pd.read_csv(csv_path)
        elif csv_path.endswith('.xlsx') or csv_path.endswith('.xls'):
            df = pd.read_excel(csv_path)
        else:
            return "Error loading file: Unsupported file format"
        
        # Convert to a text summary
        summary = f"Demographic data with {len(df)} rows and {len(df.columns)} columns.\n"
        summary += f"Columns: {', '.join(df.columns.tolist())}\n"
        summary += f"Sample data:\n{df.head().to_string()}"
        
        logger.info(f"Successfully loaded demographic data: {len(df)} rows")
        return summary
    except Exception as e:
        logger.error(f"Error loading demographics: {e}")
        return f"Error loading file: {str(e)}"


def assess_policy_impact(policy_text: str):
    """
    Tool function for the AI agent to assess policy impact.
    This is used by the agent's tool system.
    """
    # This function is called by the AI agent as a tool
    # The actual implementation is in the agent's system prompt
    return "Policy impact assessment tool"
