"""
PolicyLens: Autonomous Policy Impact Assessment Agent.

This module defines the PolicyImpactAgent, which uses Google's Gemini models to
autonomously analyze policy documents, assess their impact on various demographic groups,
and recommend mitigation strategies. It follows a step-wise reasoning process:
1. Parse Policy & Demographics
2. Reason over Impact
3. Assess Risk
4. Generate Recommendations
"""

import json
from google import genai
from google.genai import types
from backend.tools import assess_policy_impact
from backend.config import GEMINI_API_KEY, GEMINI_MODEL

class PolicyImpactAgent:
    """
    An autonomous agent that analyzes policy documents and demographic data
    to assess social impact and risk.
    """
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
        You are PolicyLens, an autonomous policy impact assessment agent.

        Your Goal: Analyze policy documents to identify social risks and impacts on specific demographic groups.

        Input:
        1. Policy Text
        2. Demographic Data Context (if available)

        Execution Steps:
        1. ANALYZE the policy to understand its core mechanisms.
        2. CORRELATE policy mechanisms with demographic data.
        3. IDENTIFY specific affected groups (e.g., "Low-income farmers", "Urban gig workers").
        4. ASSESS risk levels (High/Medium/Low) based on economic or social vulnerability.
        5. GENERATE mitigation strategies.

        Constraint Checklist & Confidence Score:
        1. Output must be strictly valid JSON.
        2. Identify MAX 3 key affected groups.
        3. Risk levels must be exactly: High, Medium, or Low.
        4. impacted_regions must be specific states or districts (e.g. "Karnataka", "Mumbai Suburban").
        5. Do NOT output markdown code blocks. Output ONLY raw JSON.

        Output JSON Schema (Strictly Enforced):
        {
          "affected_groups": ["Group Name 1", "Group Name 2"],
          "risk_level": "High/Medium/Low",
          "impacted_regions": ["Region1", "Region2"],
          "recommendations": [
            "Actionable recommendation 1",
            "Actionable recommendation 2"
          ]
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
                "impacted_regions": [],
                "recommendations": ["API Key missing or invalid. Please configure GEMINI_API_KEY."]
            }

        demographics_part = f" against these demographics: {demographics_text[:5000]}..." if demographics_text else ""
        prompt = f"Analyze this policy: {policy_text[:20000]}...{demographics_part}"
        
        try:
            # Explicit Step-by-Step Execution for Visibility
            print("Step 1: Parsing policy and demographics...")
            # (Parsing happened in main.py before calling run, but we acknowledge it here)

            print("Step 2: Impact Reasoning (Agentic Step)...")
            # We explicitly call the tool here to show "reasoning" logic,
            # even though Gemini does the heavy lifting.
            # In a more complex agent, this would be a separate LLM call or RAG lookup.
            impact_check = assess_policy_impact(policy_text)
            print(f"      -> {impact_check['details']}")

            print("Step 3: Risk Assessment & Recommendation Generation (Gemini)...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    # We keep the tool available to the model if it chooses to use it,
                    # but we also forced a step above for visibility.
                    tools=[assess_policy_impact],
                    response_mime_type="application/json"
                )
            )

            print("Step 4: validating Output...")
            if response.text:
                cleaned_text = response.text.strip()
                # Remove markdown code blocks if present
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.startswith("```"):
                    cleaned_text = cleaned_text[3:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]

                return json.loads(cleaned_text.strip())
            
            # Handle empty response (rare)
            return {
                "affected_groups": [],
                "risk_level": "Error",
                "impacted_regions": [],
                "recommendations": ["Model returned no text."]
            }

        except Exception as e:
            print(f"Agent Error: {e}")
            return {
                "affected_groups": [],
                "risk_level": "Unknown",
                "impacted_regions": [],
                "recommendations": [f"Please try again. Error: {str(e)}"]
            }
