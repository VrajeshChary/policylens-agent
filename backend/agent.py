import os
import json
from google import genai
from google.genai import types
from backend.tools import assess_policy_impact
from backend.config import GEMINI_API_KEY, GEMINI_MODEL

class PolicyImpactAgent:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.client = None
        
        if not self.api_key:
            print("⚠️ Warning: GEMINI_API_KEY not found. Agent will run in mock mode or fail gracefully.")
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"⚠️ Error initializing Gemini client: {e}")

        self.model_name = GEMINI_MODEL

        # System prompt
        self.system_prompt = """
        You are an autonomous policy impact assessment agent.

You will be given:
- A policy description
- Demographic data (text or CSV)

Your tasks:
1. Identify population groups affected by the policy
2. Assign a risk level to each group (Low, Medium, High)
3. Identify impacted regions
4. Suggest practical mitigation measures

Output rules (STRICT AND NON-NEGOTIABLE):
- Output VALID JSON only
- Do not include any text outside the JSON
- Follow the exact JSON schema provided
- Use short, clear, non-technical phrases
- Identify a maximum of 3 affected groups
- Use ONLY these risk labels: Low, Medium, High
- Regions must be Indian state or district names only
- Do NOT use city, zone, or metro names
- If demographic data mentions cities, map them to the corresponding state
- reasoning_summary must be a single paragraph under 35 words
- Do not include line breaks in reasoning_summary

JSON Schema (must match exactly):
{
  "affected_groups": [
    {
      "group": "",
      "risk_level": "",
      "regions": []
    }
  ],
  "mitigations": [],
  "reasoning_summary": ""
}
        """

    def run(self, policy_text: str, demographics_text: str = ""):
        """
        Analyzes the policy text and demographics (optional) to assess impact.
        """
        if not self.client:
            return {
                "affected_groups": ["System Configuration Error"],
                "risk_level": "Unknown",
                "regions": ["N/A"],
                "recommendations": ["API Key missing or invalid. Please configure GEMINI_API_KEY."]
            }

        demographics_part = f" against these demographics: {demographics_text[:5000]}..." if demographics_text else ""
        prompt = f"Analyze this policy: {policy_text[:20000]}...{demographics_part}"
        
        try:
            print("Step 1: Parsing policy and demographics...")
            print("Step 2: Sending to Gemini for reasoning...")

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    tools=[assess_policy_impact],
                    response_mime_type="application/json"
                )
            )

            print("Step 3: Received response, parsing JSON...")
            if response.text:
                return json.loads(response.text)
            
            # Handle empty response (rare)
            return {
                "affected_groups": [],
                "risk_level": "Error",
                "regions": [],
                "recommendations": ["Model returned no text."]
            }

        except Exception as e:
            print(f"Agent Error: {e}")
            return {
                "affected_groups": ["Error analyzing data"],
                "risk_level": "Unknown",
                "regions": [],
                "recommendations": [f"Please try again. Error: {str(e)}"]
            }
