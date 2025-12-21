"""
PolicyLens Policy Impact Assessment Agent

This module defines the PolicyImpactAgent, an autonomous agent that uses Google's Gemini model
to analyze policy documents against demographic data. It follows a step-wise reasoning process:
1. Parse Policy & Demographics
2. Reason over Impact
3. Assess Risk
4. Generate Recommendations

The agent is designed to provide deterministic, structured JSON output for downstream consumption.
"""

import os
import json
import logging
import re
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class PolicyImpactAgent:
    """
    Autonomous agent for assessing policy impact on demographic groups.
    """

    def __init__(self):
        # Securely get API key from environment variable
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            logger.error("❌ Critical: GEMINI_API_KEY not found in environment variables.")
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
            
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

        self.system_prompt = """
You are PolicyLens, an autonomous policy impact assessment agent.

You will be given:
- A policy description (text)
- Demographic data (text summary)

Your mission is to analyze the policy's potential impact on specific demographic groups.

Follow this step-wise reasoning process:
1. **Analyze Policy**: Understand the core objectives and mechanisms of the policy.
2. **Analyze Demographics**: Identify key population segments in the provided data.
3. **Assess Impact**: Determine how the policy affects each group (positively or negatively).
4. **Evaluate Risk**: Assign a risk level (Low, Medium, High) based on potential negative impact.
5. **Recommend Mitigations**: Propose actionable steps to reduce negative impact.

Output rules (STRICT AND NON-NEGOTIABLE):
- Output VALID JSON only.
- Do not include any text outside the JSON.
- Follow the exact JSON schema provided.
- Use short, clear, non-technical phrases.
- Identify a maximum of 3 affected groups.
- Use ONLY these risk labels: Low, Medium, High.
- Regions must be Indian state or district names only (if applicable).
- Do NOT use city, zone, or metro names.
- If demographic data mentions cities, map them to the corresponding state.
- reasoning_summary must be a single paragraph under 35 words.
- Do not include line breaks in reasoning_summary.

JSON Schema (must match exactly):
{
  "affected_groups": [
    {
      "group": "Name of the group",
      "risk_level": "Low/Medium/High",
      "regions": ["Region1", "Region2"]
    }
  ],
  "mitigations": ["Mitigation 1", "Mitigation 2"],
  "reasoning_summary": "Concise summary of the reasoning."
}
        """

    def analyze(self, policy_text: str, demographics_text: str):
        """
        Analyzes the policy text against demographics text to determine impact.

        Args:
            policy_text (str): The extracted text from the policy document.
            demographics_text (str): The summary of demographic data.

        Returns:
            dict: A structured dictionary containing affected groups, risk levels, and mitigations.
        """
        # Truncate inputs if too long to fit context window/avoid excessive costs
        if len(policy_text) > 20000:
            logger.warning(f"Policy text truncated from {len(policy_text)} to 20000 characters")
            policy_text = policy_text[:20000]
        
        if len(demographics_text) > 5000:
            logger.warning(f"Demographics text truncated from {len(demographics_text)} to 5000 characters")
            demographics_text = demographics_text[:5000]
        
        prompt = f"Analyze this policy: {policy_text}\n\nAgainst these demographics: {demographics_text}"
        
        try:
            logger.info("Sending request to gemini-2.5-flash for analysis")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    response_mime_type="application/json"
                )
            )

            if response.text:
                # Parse JSON response
                try:
                    result = json.loads(response.text)
                except json.JSONDecodeError as e:
                    # Try to extract JSON from markdown code blocks if present
                    text = response.text.strip()
                    # Remove markdown code blocks if present
                    if text.startswith("```"):
                        text = re.sub(r'^```(?:json)?\s*\n', '', text)
                        text = re.sub(r'\n```\s*$', '', text)
                    try:
                        result = json.loads(text)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse JSON response: {e}")
                        logger.error(f"Response text: {response.text[:500]}")
                        raise ValueError(f"Invalid JSON response from model: {str(e)}")
                
                # Validate response structure
                if not isinstance(result, dict):
                    raise ValueError("Response is not a dictionary")
                
                # Ensure required fields exist
                if "affected_groups" not in result:
                    result["affected_groups"] = []
                if "mitigations" not in result:
                    result["mitigations"] = []
                if "reasoning_summary" not in result:
                    result["reasoning_summary"] = "Analysis completed"
                
                logger.info("Analysis completed successfully")
                return result
            
            # Handle empty response
            logger.warning("Model returned empty response")
            return {
                "affected_groups": [],
                "mitigations": [],
                "reasoning_summary": "Model returned no text."
            }

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Response text: {response.text if 'response' in locals() else 'No response'}")
            return {
                "affected_groups": [{"group": "Error parsing response", "risk_level": "Unknown", "regions": []}],
                "mitigations": ["Please try again. The AI response was invalid."],
                "reasoning_summary": "Error occurred while parsing AI response."
            }
        except Exception as e:
            logger.error(f"Agent Error: {e}", exc_info=True)
            return {
                "affected_groups": [{"group": "Error analyzing data", "risk_level": "Unknown", "regions": []}],
                "mitigations": [f"Please try again. Error: {str(e)}"],
                "reasoning_summary": f"An error occurred: {str(e)}"
            }
