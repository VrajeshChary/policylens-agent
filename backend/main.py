# backend/main.py
import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from backend.agent import PolicyImpactAgent
from backend.tools import extract_policy_text, load_demographics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = PolicyImpactAgent() 

# Keep the old model for backward compatibility if needed, but we will mostly use the file upload endpoint
class PolicyRequest(BaseModel):
    policy_text: str

@app.post("/analyze")
async def analyze_policy_files(
    policy_file: UploadFile = File(...),
    demographics_file: Optional[UploadFile] = File(None)
):
    try:
        # Create a temporary directory to store uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Handle Policy PDF
            policy_path = os.path.join(temp_dir, policy_file.filename)
            with open(policy_path, "wb") as buffer:
                shutil.copyfileobj(policy_file.file, buffer)

            policy_text = extract_policy_text(policy_path)
            if not policy_text:
                raise ValueError("Could not extract text from policy PDF.")

            # Handle Demographics CSV
            demographics_text = ""
            if demographics_file:
                demographics_path = os.path.join(temp_dir, demographics_file.filename)
                with open(demographics_path, "wb") as buffer:
                    shutil.copyfileobj(demographics_file.file, buffer)
                demographics_text = load_demographics(demographics_path)

            print("Sending request to AI agent...")
            response = agent.run(policy_text, demographics_text)
            return response

    except Exception as e:
        print(f"⚠️ Error detected: {e}")
        return {
            "affected_groups": ["System Error"],
            "risk_level": "Unknown",
            "regions": ["N/A"],
            "recommendations": [f"Error processing files: {str(e)}"]
        }

@app.post("/analyze-text")
async def analyze_policy_text(request: PolicyRequest):
    """Fallback endpoint for text-only analysis"""
    try:
        print("Sending request to AI agent (Text Mode)...")
        response = agent.run(request.policy_text, "")
        return response
    except Exception as e:
         print(f"⚠️ Error detected: {e}")
         return {
            "affected_groups": ["System Error"],
            "risk_level": "Unknown",
            "regions": ["N/A"],
            "recommendations": [f"Error: {str(e)}"]
        }

script_dir = os.path.dirname(__file__)
static_path = os.path.join(script_dir, "static")
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
