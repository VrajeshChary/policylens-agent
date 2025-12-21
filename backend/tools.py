"""
PolicyLens Agent - Tools and utilities
"""
import logging
import pandas as pd
from PyPDF2 import PdfReader
from typing import Dict, List

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


def generate_demographic_summary(df: pd.DataFrame) -> str:
    """Generate a semantic summary of demographic data"""
    summary_parts = []
    
    # Basic statistics
    total_rows = len(df)
    summary_parts.append(f"Total records: {total_rows}")
    
    # Analyze columns for key demographic indicators
    columns = df.columns.str.lower().tolist()
    
    # Population distribution
    if any('population' in col or 'pop' in col for col in columns):
        pop_col = next((col for col in df.columns if 'population' in col.lower() or 'pop' in col.lower()), None)
        if pop_col:
            total_pop = df[pop_col].sum() if df[pop_col].dtype in ['int64', 'float64'] else None
            if total_pop:
                summary_parts.append(f"Total population: {int(total_pop):,}")
    
    # Rural/Urban distribution
    if any('rural' in col or 'urban' in col for col in columns):
        rural_col = next((col for col in df.columns if 'rural' in col.lower()), None)
        urban_col = next((col for col in df.columns if 'urban' in col.lower()), None)
        if rural_col and urban_col:
            rural = df[rural_col].sum() if df[rural_col].dtype in ['int64', 'float64'] else 0
            urban = df[urban_col].sum() if df[urban_col].dtype in ['int64', 'float64'] else 0
            total = rural + urban
            if total > 0:
                rural_pct = (rural / total) * 100
                urban_pct = (urban / total) * 100
                summary_parts.append(f"Rural population: {rural_pct:.1f}%")
                summary_parts.append(f"Urban population: {urban_pct:.1f}%")
    
    # Income brackets
    if any('income' in col or 'wage' in col or 'salary' in col for col in columns):
        income_col = next((col for col in df.columns if any(x in col.lower() for x in ['income', 'wage', 'salary'])), None)
        if income_col and df[income_col].dtype in ['int64', 'float64']:
            avg_income = df[income_col].mean()
            median_income = df[income_col].median()
            summary_parts.append(f"Average income: ₹{avg_income:,.0f}")
            summary_parts.append(f"Median income: ₹{median_income:,.0f}")
    
    # Education levels
    if any('education' in col or 'literacy' in col or 'literate' in col for col in columns):
        edu_col = next((col for col in df.columns if any(x in col.lower() for x in ['education', 'literacy', 'literate'])), None)
        if edu_col:
            if df[edu_col].dtype in ['int64', 'float64']:
                avg_literacy = df[edu_col].mean()
                summary_parts.append(f"Average literacy/education level: {avg_literacy:.1f}%")
            else:
                # Count unique education levels
                unique_edu = df[edu_col].value_counts().head(3)
                summary_parts.append(f"Top education levels: {', '.join(unique_edu.index.astype(str).tolist())}")
    
    # Region analysis
    region_cols = [col for col in df.columns if any(x in col.lower() for x in ['region', 'state', 'district', 'area', 'location'])]
    if region_cols:
        region_col = region_cols[0]
        top_regions = df[region_col].value_counts().head(5)
        summary_parts.append(f"Top regions by data points: {', '.join(top_regions.index.astype(str).tolist())}")
    
    # Vulnerability indicators
    vulnerability_keywords = ['unemployment', 'poverty', 'vulnerable', 'disability', 'elderly', 'children']
    for keyword in vulnerability_keywords:
        matching_cols = [col for col in df.columns if keyword in col.lower()]
        if matching_cols:
            col = matching_cols[0]
            if df[col].dtype in ['int64', 'float64']:
                avg_value = df[col].mean()
                summary_parts.append(f"Average {keyword} rate: {avg_value:.1f}%")
            else:
                top_values = df[col].value_counts().head(3)
                summary_parts.append(f"Top {keyword} categories: {', '.join(top_values.index.astype(str).tolist())}")
    
    # Internet/Technology access
    tech_keywords = ['internet', 'digital', 'technology', 'mobile', 'smartphone']
    for keyword in tech_keywords:
        matching_cols = [col for col in df.columns if keyword in col.lower()]
        if matching_cols:
            col = matching_cols[0]
            if df[col].dtype in ['int64', 'float64']:
                avg_value = df[col].mean()
                summary_parts.append(f"Average {keyword} penetration: {avg_value:.1f}%")
    
    # Employment status
    if any('employment' in col or 'employed' in col or 'job' in col for col in columns):
        emp_col = next((col for col in df.columns if any(x in col.lower() for x in ['employment', 'employed', 'job'])), None)
        if emp_col:
            if df[emp_col].dtype in ['int64', 'float64']:
                avg_emp = df[emp_col].mean()
                summary_parts.append(f"Average employment rate: {avg_emp:.1f}%")
            else:
                emp_dist = df[emp_col].value_counts()
                summary_parts.append(f"Employment distribution: {', '.join([f'{k}: {v}%' for k, v in emp_dist.head(3).items()])}")
    
    return "\n".join(summary_parts) if summary_parts else "Demographic data loaded but no key indicators identified."


def load_demographics(csv_path: str) -> str:
    """Load demographics data from CSV/Excel and return semantic summary"""
    try:
        # Read the file
        if csv_path.endswith('.csv'):
            df = pd.read_csv(csv_path)
        elif csv_path.endswith('.xlsx') or csv_path.endswith('.xls'):
            df = pd.read_excel(csv_path)
        else:
            return "Error loading file: Unsupported file format"
        
        logger.info(f"Successfully loaded demographic data: {len(df)} rows, {len(df.columns)} columns")
        
        # Generate semantic summary
        summary = generate_demographic_summary(df)
        
        # Add column info for context
        summary = f"Demographic Context:\n{summary}\n\nAvailable data columns: {', '.join(df.columns.tolist())}"
        
        return summary
    except Exception as e:
        logger.error(f"Error loading demographics: {e}")
        return f"Error loading file: {str(e)}"


def assess_policy_impact(policy_text: str):
    """
    Tool function for the AI agent to assess policy impact.
    This is used by the agent's tool system.
    """
    return "Policy impact assessment tool"
