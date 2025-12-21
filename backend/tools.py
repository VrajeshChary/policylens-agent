import logging
import pandas as pd
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


def extract_policy_text(pdf_path: str) -> str:
    """
    Step 1: Policy Parsing
    Extracts text from the provided policy PDF file.
    """
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
    """
    Step 2: Demographic Parsing
    Loads demographics data from CSV/Excel and converts it to a text summary for the agent.
    """
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
