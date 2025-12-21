import os
import logging
import tempfile
import asyncio
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from backend.agent import PolicyImpactAgent
from backend.tools import extract_policy_text, load_demographics
from backend.config import (
    MAX_FILE_SIZE,
    ALLOWED_POLICY_EXTENSIONS,
    ALLOWED_DEMOGRAPHIC_EXTENSIONS,
    DEFAULT_TIMEOUT,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global agent instance (singleton pattern)
_agent: Optional[PolicyImpactAgent] = None


def get_agent() -> PolicyImpactAgent:
    """Get or create the agent singleton"""
    global _agent
    if _agent is None:
        try:
            _agent = PolicyImpactAgent()
        except Exception as e:
            logger.error(f"Failed to initialize PolicyImpactAgent: {e}")
            raise
    return _agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting PolicyLens API server...")
    try:
        # Initialize agent on startup
        get_agent()
    except Exception as e:
        logger.error(f"Failed to initialize agent on startup: {e}")
        raise
    yield
    # Shutdown
    logger.info("Shutting down PolicyLens API server...")


app = FastAPI(
    title="PolicyLens API",
    description="Autonomous policy impact assessment agent",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """Validate file extension"""
    if not filename:
        return False
    return any(filename.lower().endswith(ext.lower()) for ext in allowed_extensions)


def validate_file_size(size: int, max_size: int) -> bool:
    """Validate file size"""
    return size <= max_size


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": f"HTTP_{exc.status_code}"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "error_code": "INTERNAL_ERROR"
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        agent = get_agent()
        return {
            "status": "healthy",
            "service": "PolicyLens API",
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.post("/api/analyze")
async def analyze_policy(
    request: Request,
    policy_file: UploadFile = File(...),
    demographic_file: Optional[UploadFile] = File(None)
):
    """
    Analyze policy document and demographic data.
    
    - **policy_file**: PDF file containing the policy document (required)
    - **demographic_file**: CSV or XLSX file containing demographic data (optional)
    
    Returns analysis results including affected groups, risk levels, regions, and mitigations.
    """
    policy_text = ""
    demographics_text = ""
    policy_tmp_path: Optional[str] = None
    demo_tmp_path: Optional[str] = None
    
    try:
        # Validate policy file
        if not policy_file.filename:
            raise HTTPException(status_code=400, detail="Policy file is required")
        
        if not validate_file_extension(policy_file.filename, ALLOWED_POLICY_EXTENSIONS):
            raise HTTPException(
                status_code=400,
                detail=f"Policy file must be one of: {', '.join(ALLOWED_POLICY_EXTENSIONS)}"
            )
        
        # Read and validate policy file size
        policy_content = await policy_file.read()
        if not validate_file_size(len(policy_content), MAX_FILE_SIZE):
            raise HTTPException(
                status_code=400,
                detail=f"Policy file size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Save policy file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(policy_content)
            policy_tmp_path = tmp_file.name
        
        # Extract text from PDF
        try:
            policy_text = extract_policy_text(policy_tmp_path)
            if not policy_text or len(policy_text.strip()) < 10:
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract meaningful text from PDF. Please ensure the PDF contains readable text."
                )
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text from PDF: {str(e)}"
            )
        
        # Process demographic file if provided
        if demographic_file and demographic_file.filename:
            if not validate_file_extension(demographic_file.filename, ALLOWED_DEMOGRAPHIC_EXTENSIONS):
                raise HTTPException(
                    status_code=400,
                    detail=f"Demographic file must be one of: {', '.join(ALLOWED_DEMOGRAPHIC_EXTENSIONS)}"
                )
            
            # Read and validate demographic file size
            demo_content = await demographic_file.read()
            if not validate_file_size(len(demo_content), MAX_FILE_SIZE):
                raise HTTPException(
                    status_code=400,
                    detail=f"Demographic file size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024):.1f}MB"
                )
            
            # Save demographic file temporarily
            ext = '.csv' if demographic_file.filename.lower().endswith('.csv') else '.xlsx'
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
                tmp_file.write(demo_content)
                demo_tmp_path = tmp_file.name
            
            # Load demographics
            try:
                demographics_text = load_demographics(demo_tmp_path)
                if not demographics_text or "Error loading file" in demographics_text:
                    logger.warning(f"Demographic file processing issue: {demographics_text}")
                    demographics_text = "No demographic data could be extracted"
            except Exception as e:
                logger.error(f"Error loading demographics: {e}")
                demographics_text = f"Error loading demographic data: {str(e)}"
        
        if not demographics_text:
            demographics_text = "No demographic data provided"
        
        logger.info(f"Processing analysis request - Policy: {len(policy_text)} chars, Demographics: {len(demographics_text)} chars")
        
        # Get agent and run analysis with timeout
        agent = get_agent()
        
        try:
            # Run agent analysis with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(agent.analyze, policy_text, demographics_text),
                timeout=DEFAULT_TIMEOUT
            )
        except asyncio.TimeoutError:
            logger.error("Analysis request timed out")
            raise HTTPException(
                status_code=504,
                detail=f"Analysis request timed out after {DEFAULT_TIMEOUT} seconds. Please try again with a smaller document."
            )
        except Exception as e:
            logger.error(f"Agent analysis error: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {str(e)}"
            )
        
        # Validate response structure
        if not isinstance(response, dict):
            raise HTTPException(status_code=500, detail="Invalid response format from agent")
        
        # Ensure response matches expected schema
        result = {
            "affected_groups": response.get("affected_groups", []),
            "mitigations": response.get("mitigations", []),
            "reasoning_summary": response.get("reasoning_summary", "Analysis completed"),
            "error": response.get("error")
        }
        
        logger.info("Analysis completed successfully")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_policy: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
    finally:
        # Clean up temporary files
        for tmp_path in [policy_tmp_path, demo_tmp_path]:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {tmp_path}: {e}")

# Mount static files - must be last to avoid route conflicts
script_dir = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(script_dir, "static")

# Verify static directory exists
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
else:
    print(f"⚠️ Warning: Static directory not found at {static_path}")
