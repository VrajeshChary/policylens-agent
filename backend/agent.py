<<<<<<< HEAD
import os
import json
from google import genai
from google.genai import types # <--- You need this import for the config  # pyright: ignore[reportMissingImports]
from backend.tools import assess_policy_impact

class PolicyImpactAgent:
    def __init__(self):
        # 1. FIX: Put quotes around your key to make it a string
        api_key = "AIzaSyBUG3v6aBlszVfIUPR3ZzJNclyqKBWoOBc"
        
        if not api_key:
            print("⚠️ Warning: GEMINI_API_KEY not found.")
            
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-1.5-flash"

        # 2. DEFINITION: System prompt
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

    # I renamed this to 'analyze' because your main.py likely calls agent.analyze()
    def analyze(self, policy_text: str, demographics_text: str):
        prompt = f"Analyze this policy: {policy_text[:20000]}... against these demographics: {demographics_text[:5000]}..."
        
        try:
            # 3. FIX: Use 'self.client.models' and pass the configuration
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt, # <--- Pass prompt here
                    tools=[assess_policy_impact],          # <--- Pass tool here
                    response_mime_type="application/json"  # <--- Force JSON here
                )
            )

            # 4. Return the text (parsed as JSON)
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
=======
import os
import json
from google import genai
from google.genai import types # <--- You need this import for the config  # pyright: ignore[reportMissingImports]
from backend.tools import assess_policy_impact

class PolicyImpactAgent:
    def __init__(self):
        # 1. FIX: Put quotes around your key to make it a string
        api_key = "AIzaSyBUG3v6aBlszVfIUPR3ZzJNclyqKBWoOBc"
        
        if not api_key:
            print("⚠️ Warning: GEMINI_API_KEY not found.")
            
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-1.5-flash"

        # 2. DEFINITION: System prompt
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

    # I renamed this to 'analyze' because your main.py likely calls agent.analyze()
    def analyze(self, policy_text: str, demographics_text: str):
        prompt = f"Analyze this policy: {policy_text[:20000]}... against these demographics: {demographics_text[:5000]}..."
        
        try:
            # 3. FIX: Use 'self.client.models' and pass the configuration
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt, # <--- Pass prompt here
                    tools=[assess_policy_impact],          # <--- Pass tool here
                    response_mime_type="application/json"  # <--- Force JSON here
                )
            )

            # 4. Return the text (parsed as JSON)
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
>>>>>>> 46c1933 (Initial commit)
            }