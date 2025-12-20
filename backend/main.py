# backend/main.py
import os  # <--- NEW IMPORT: Needed to find folders
from fastapi import FastAPI # pyright: ignore[reportMissingImports]
from fastapi.middleware.cors import CORSMiddleware # pyright: ignore[reportMissingImports]
from fastapi.staticfiles import StaticFiles # pyright: ignore[reportMissingImports]
from pydantic import BaseModel # pyright: ignore[reportMissingImports]
from backend.agent import PolicyImpactAgent 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = PolicyImpactAgent() 

class PolicyRequest(BaseModel):
    policy_text: str

@app.post("/analyze")
async def analyze_policy(request: PolicyRequest):

    try:
 
        print("Sending request to AI agent...")
        response = agent.run(request.policy_text)
        
    except Exception as e:
        print(f"⚠️ Error detected: {e}")
        print("Returning fallback 'Dummy' response to keep demo alive.")
        
        response = {
            "affected_groups": ["System Error (Fallback Active)"],
            "risk_level": "Unknown",
            "regions": ["N/A"],
            "recommendations": [f"The AI service is temporarily unavailable. Error: {str(e)}"]
        }

    return response
script_dir = os.path.dirname(__file__)
static_path = os.path.join(script_dir, "static")


app.mount("/", StaticFiles(directory=static_path, html=True), name="static")