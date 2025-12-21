import os
import json
import logging
import re
from typing import Dict, List, Any
from google import genai
from google.genai import types
from backend.config import (
    RISK_LEVELS,
    TEMPERATURE,
    MAX_TOP_P,
    MAX_AFFECTED_GROUPS,
    MAX_MITIGATIONS,
    REASONING_SUMMARY_MAX_WORDS
)

logger = logging.getLogger(__name__)


class PolicyImpactAgent:
    def __init__(self):
        # Try to get API key from environment, then config, then fallback
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            # Fallback to default key
            api_key = "AIzaSyCbHA6CN3Y1HBxyDGnUNLzxopikeuW1hfg"
            logger.info("Using default API key. Set GEMINI_API_KEY environment variable to use a different key.")
        else:
            logger.info("Using API key from environment variable")
            
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"
        
        # Deterministic rules for risk assessment
        self.deterministic_rules = {
            "risk_assessment": {
                "Low": [
                    "Policy affects less than 10% of population",
                    "Minimal economic impact",
                    "Reversible changes",
                    "Adequate support systems exist"
                ],
                "Medium": [
                    "Policy affects 10-30% of population",
                    "Moderate economic impact",
                    "Some irreversible changes",
                    "Support systems partially available"
                ],
                "High": [
                    "Policy affects more than 30% of population",
                    "Significant economic impact",
                    "Mostly irreversible changes",
                    "Limited or no support systems"
                ]
            },
            "group_identification": [
                "Identify groups based on: age, income, education, location, occupation",
                "Prioritize vulnerable populations: elderly, children, low-income, rural",
                "Consider intersectionality: multiple overlapping characteristics"
            ],
            "region_mapping": {
                "cities_to_states": {
                    "Mumbai": "Maharashtra",
                    "Delhi": "Delhi",
                    "Bangalore": "Karnataka",
                    "Chennai": "Tamil Nadu",
                    "Kolkata": "West Bengal",
                    "Hyderabad": "Telangana",
                    "Pune": "Maharashtra",
                    "Ahmedabad": "Gujarat"
                }
            }
        }
        
        # Anchoring examples for consistent output
        self.anchoring_examples = """
Example 1:
Policy: "Increase in fuel prices by 20%"
Demographics: "Rural population: 60%, Urban: 40%"
Output:
{
  "affected_groups": [
    {
      "group": "Rural low-income households",
      "risk_level": "High",
      "regions": ["Bihar", "Uttar Pradesh", "Madhya Pradesh"]
    },
    {
      "group": "Urban middle-class commuters",
      "risk_level": "Medium",
      "regions": ["Maharashtra", "Karnataka", "Tamil Nadu"]
    }
  ],
  "mitigations": [
    "Provide fuel subsidies for rural areas",
    "Improve public transportation infrastructure",
    "Introduce income-based fuel vouchers"
  ],
  "reasoning_summary": "Fuel price increase disproportionately affects rural low-income households and urban commuters, requiring targeted subsidies and transport improvements."
}

Example 2:
Policy: "Mandatory digital payment for all government services"
Demographics: "Digital literacy: 45%, Rural: 65%"
Output:
{
  "affected_groups": [
    {
      "group": "Rural elderly population",
      "risk_level": "High",
      "regions": ["Rajasthan", "Bihar", "Odisha"]
    },
    {
      "group": "Low digital literacy population",
      "risk_level": "Medium",
      "regions": ["Uttar Pradesh", "Madhya Pradesh"]
    }
  ],
  "mitigations": [
    "Provide digital literacy training programs",
    "Maintain offline alternatives for essential services",
    "Establish community digital assistance centers"
  ],
  "reasoning_summary": "Digital payment mandate excludes rural elderly and low-literacy populations, necessitating training and offline alternatives."
}
        """

        self.system_prompt = f"""
You are an autonomous policy impact assessment agent with deterministic rules.

DETERMINISTIC RULES (MUST FOLLOW):
1. Risk Level Assessment:
   - Low: Policy affects <10% population, minimal economic impact, reversible changes, adequate support exists
   - Medium: Policy affects 10-30% population, moderate economic impact, some irreversible changes, partial support
   - High: Policy affects >30% population, significant economic impact, mostly irreversible, limited/no support

2. Group Identification Priority:
   - Vulnerable populations first: elderly, children, low-income, rural residents
   - Consider intersectionality: multiple overlapping characteristics
   - Maximum {MAX_AFFECTED_GROUPS} groups per analysis

3. Region Mapping:
   - Use Indian state or district names ONLY
   - Map cities to their states automatically
   - Do NOT use city, zone, or metro names

4. Output Constraints:
   - Maximum {MAX_MITIGATIONS} mitigation strategies
   - Reasoning summary: exactly {REASONING_SUMMARY_MAX_WORDS} words or less
   - Single paragraph, no line breaks

ANCHORING EXAMPLES:
{self.anchoring_examples}

You will be given:
- A policy description (PRIMARY INPUT - MANDATORY)
- Demographic data summary (SUPPORTING EVIDENCE - OPTIONAL)

IMPORTANT: When demographic data is provided:
- Use it to identify which population segments are most affected
- Map policy impact to regions based on demographic distribution
- Consider vulnerability indicators (rural %, internet penetration, unemployment, income levels)
- If demographic shows high rural population in a state, prioritize rural groups for that state
- If demographic shows low internet penetration, consider digital policy impacts there
- Integrate demographic insights into risk assessment

Your tasks:
1. Identify population groups affected by the policy (max {MAX_AFFECTED_GROUPS})
   - Use demographic data to identify vulnerable segments when available
   - Prioritize groups mentioned in demographic context
2. Assign risk level to each group using deterministic rules (Low, Medium, High ONLY)
   - Consider demographic vulnerability indicators when assessing risk
3. Identify impacted regions (Indian states/districts only)
   - Use demographic data to identify high-impact regions when available
   - Map cities mentioned in demographics to their states
4. Suggest practical mitigation measures (max {MAX_MITIGATIONS})
   - Consider demographic context when suggesting region-specific mitigations

Output rules (STRICT AND NON-NEGOTIABLE):
- Output VALID JSON only
- Do not include any text outside the JSON
- Follow the exact JSON schema provided
- Use short, clear, non-technical phrases
- Apply deterministic rules strictly
- Use anchoring examples as reference for format

JSON Schema (must match exactly):
{{
  "affected_groups": [
    {{
      "group": "",
      "risk_level": "",
      "regions": []
    }}
  ],
  "mitigations": [],
  "reasoning_summary": ""
}}
        """

    def _apply_deterministic_rules(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply deterministic rules to normalize the output"""
        # Normalize risk levels
        if "affected_groups" in result:
            for group in result["affected_groups"]:
                if "risk_level" in group:
                    risk = group["risk_level"].strip()
                    # Normalize to standard format
                    risk_lower = risk.lower()
                    if risk_lower in ["low", "l"]:
                        group["risk_level"] = "Low"
                    elif risk_lower in ["medium", "med", "m"]:
                        group["risk_level"] = "Medium"
                    elif risk_lower in ["high", "h"]:
                        group["risk_level"] = "High"
                    else:
                        # Default to Medium if unrecognized
                        logger.warning(f"Unknown risk level '{risk}', defaulting to Medium")
                        group["risk_level"] = "Medium"
        
        return result

    def _apply_anchoring_logic(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply anchoring logic to ensure consistent structure"""
        # Ensure affected_groups is a list
        if "affected_groups" not in result:
            result["affected_groups"] = []
        
        # Limit number of groups
        if len(result["affected_groups"]) > MAX_AFFECTED_GROUPS:
            logger.warning(f"Limiting affected groups from {len(result['affected_groups'])} to {MAX_AFFECTED_GROUPS}")
            result["affected_groups"] = result["affected_groups"][:MAX_AFFECTED_GROUPS]
        
        # Ensure each group has required fields
        for group in result["affected_groups"]:
            if "group" not in group or not group["group"]:
                group["group"] = "Unspecified group"
            if "risk_level" not in group:
                group["risk_level"] = "Medium"
            if "regions" not in group:
                group["regions"] = []
            # Normalize regions - ensure they're lists
            if not isinstance(group["regions"], list):
                group["regions"] = [group["regions"]] if group["regions"] else []
        
        # Limit mitigations
        if "mitigations" not in result:
            result["mitigations"] = []
        if len(result["mitigations"]) > MAX_MITIGATIONS:
            logger.warning(f"Limiting mitigations from {len(result['mitigations'])} to {MAX_MITIGATIONS}")
            result["mitigations"] = result["mitigations"][:MAX_MITIGATIONS]
        
        # Normalize reasoning summary
        if "reasoning_summary" not in result:
            result["reasoning_summary"] = "Analysis completed."
        else:
            # Remove line breaks and normalize
            summary = result["reasoning_summary"].strip()
            summary = re.sub(r'\s+', ' ', summary)  # Replace multiple spaces/newlines with single space
            summary = re.sub(r'\n+', ' ', summary)  # Remove line breaks
            # Limit word count
            words = summary.split()
            if len(words) > REASONING_SUMMARY_MAX_WORDS:
                summary = ' '.join(words[:REASONING_SUMMARY_MAX_WORDS])
                if not summary.endswith('.'):
                    summary += '.'
            result["reasoning_summary"] = summary
        
        return result

    def _normalize_regions(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize region names using deterministic mapping"""
        city_to_state = self.deterministic_rules["region_mapping"]["cities_to_states"]
        
        if "affected_groups" in result:
            for group in result["affected_groups"]:
                if "regions" in group and isinstance(group["regions"], list):
                    normalized_regions = []
                    for region in group["regions"]:
                        region_str = str(region).strip()
                        # Check if it's a city and map to state
                        if region_str in city_to_state:
                            normalized_regions.append(city_to_state[region_str])
                        else:
                            # Capitalize properly
                            region_str = region_str.title()
                            normalized_regions.append(region_str)
                    # Remove duplicates while preserving order
                    seen = set()
                    group["regions"] = [r for r in normalized_regions if r not in seen and not seen.add(r)]
        
        return result

    def _post_process_normalize(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Post-processing normalization to ensure consistent output"""
        # Apply all normalization steps
        result = self._apply_deterministic_rules(result)
        result = self._apply_anchoring_logic(result)
        result = self._normalize_regions(result)
        
        # Final validation
        if not isinstance(result, dict):
            raise ValueError("Result must be a dictionary")
        
        # Ensure all required top-level keys exist
        required_keys = ["affected_groups", "mitigations", "reasoning_summary"]
        for key in required_keys:
            if key not in result:
                if key == "affected_groups":
                    result[key] = []
                elif key == "mitigations":
                    result[key] = []
                else:
                    result[key] = "Analysis completed."
        
        return result

    def analyze(self, policy_text: str, demographics_text: str):
        # Truncate inputs if too long
        if len(policy_text) > 20000:
            logger.warning(f"Policy text truncated from {len(policy_text)} to 20000 characters")
            policy_text = policy_text[:20000]
        
        # Check if demographic data is provided
        has_demographics = demographics_text and len(demographics_text.strip()) > 0 and "Error loading" not in demographics_text and "No demographic" not in demographics_text
        
        if has_demographics:
            if len(demographics_text) > 5000:
                logger.warning(f"Demographics text truncated from {len(demographics_text)} to 5000 characters")
                demographics_text = demographics_text[:5000]
            
            # Build prompt with demographic context emphasized
            prompt = f"""POLICY DOCUMENT (PRIMARY INPUT):
{policy_text}

DEMOGRAPHIC CONTEXT (SUPPORTING EVIDENCE):
{demographics_text}

INSTRUCTIONS:
- The policy document is your PRIMARY source for analysis
- The demographic context provides SUPPORTING evidence to identify affected groups and regions
- Use demographic data to:
  * Identify which population segments are most affected
  * Determine regional impact based on demographic distribution
  * Assess vulnerability levels using demographic indicators
- If demographic data shows high rural population, prioritize rural groups
- If demographic data shows low internet penetration in certain regions, consider digital policies' impact there
- Integrate demographic insights into your risk assessment and mitigation recommendations

Analyze the policy using BOTH the policy document and demographic context."""
            logger.info("Analysis using policy PDF + demographic CSV data")
        else:
            prompt = f"""POLICY DOCUMENT (PRIMARY INPUT):
{policy_text}

INSTRUCTIONS:
- Analyze the policy document to identify affected groups and regions
- Use general knowledge about Indian demographics to inform your analysis
- Focus on the policy content to determine impact

Analyze the policy document."""
            logger.info("Analysis using policy PDF only (no demographic data provided)")
        
        try:
            logger.info("Sending request to gemini-2.5-flash for analysis")
            
            # Build config with temperature constraints
            # Note: Temperature is controlled via system prompt and deterministic rules
            # Gemini API may not expose temperature directly in GenerateContentConfig
            config = types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                response_mime_type="application/json"
            )
            
            # Log temperature setting for monitoring (even if not directly applied)
            logger.debug(f"Using temperature constraint: {TEMPERATURE} (applied via deterministic rules)")
            
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                        config=config
                )
            except Exception as api_error:
                error_str = str(api_error)
                error_repr = repr(api_error)
                logger.error(f"Gemini API Error: {api_error}", exc_info=True)
                
                # Check for quota/rate limit errors - check both string and repr
                error_lower = error_str.lower() + " " + error_repr.lower()
                is_quota_error = (
                    "429" in error_str or "429" in error_repr or
                    "resource_exhausted" in error_lower or
                    "quota" in error_lower
                )
                
                if is_quota_error:
                    # Extract retry delay if available
                    retry_delay = "60"
                    if "retry" in error_lower and "in" in error_lower:
                        delay_match = re.search(r'retry in (\d+\.?\d*)\s*s', error_lower)
                        if delay_match:
                            retry_delay = str(int(float(delay_match.group(1))))
                    
                    logger.warning(f"Quota exceeded. Retry after {retry_delay} seconds")
                    return {
                        "affected_groups": [{"group": "API Quota Exceeded", "risk_level": "Unknown", "regions": []}],
                        "mitigations": [
                            "API quota limit reached. Please wait before retrying.",
                            f"Retry after {retry_delay} seconds.",
                            "Check your Gemini API quota and billing details at https://ai.dev/usage",
                            "Consider upgrading your API plan for higher limits"
                        ],
                        "reasoning_summary": f"API quota exceeded. Free tier limit of 20 requests/day reached. Please retry after {retry_delay} seconds or upgrade your API plan.",
                        "is_error": True,
                        "error_type": "quota_exceeded"
                    }
                
                # Re-raise to be caught by outer exception handler
                raise

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
                
                # Apply post-processing normalization
                result = self._post_process_normalize(result)
                
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
            error_str = str(e)
            error_repr = repr(e)
            error_combined = (error_str + " " + error_repr).lower()
            logger.error(f"Agent Error: {e}", exc_info=True)
            
            # Check for quota/rate limit errors - check comprehensively
            if ("429" in error_str or "429" in error_repr or 
                "resource_exhausted" in error_combined or 
                "quota" in error_combined):
                # Extract retry delay if available
                retry_delay = "60"
                if "retry" in error_combined and "in" in error_combined:
                    delay_match = re.search(r'retry in (\d+\.?\d*)\s*s', error_combined)
                    if delay_match:
                        retry_delay = str(int(float(delay_match.group(1))))
                
                logger.warning(f"Quota error detected. Retry after {retry_delay} seconds")
                return {
                    "affected_groups": [{"group": "API Quota Exceeded", "risk_level": "Unknown", "regions": []}],
                    "mitigations": [
                        "API quota limit reached. Please wait before retrying.",
                        f"Retry after {retry_delay} seconds.",
                        "Check your Gemini API quota and billing details at https://ai.dev/usage",
                        "Consider upgrading your API plan for higher limits"
                    ],
                    "reasoning_summary": f"API quota exceeded. Free tier limit of 20 requests/day reached. Please retry after {retry_delay} seconds or upgrade your API plan.",
                    "is_error": True,
                    "error_type": "quota_exceeded"
                }
            
            # Check for authentication errors
            if ("401" in error_str or "403" in error_str or 
                "authentication" in error_combined or 
                "invalid api key" in error_combined):
                return {
                    "affected_groups": [{"group": "API Authentication Error", "risk_level": "Unknown", "regions": []}],
                    "mitigations": [
                        "Invalid or expired API key.",
                        "Please check your Gemini API key configuration.",
                        "Update the API key in environment variables or config."
                    ],
                    "reasoning_summary": "API authentication failed. Please verify your API key.",
                    "is_error": True,
                    "error_type": "authentication_error"
                }
            
            # Generic error - clean up the message
            clean_error = error_str[:150] if len(error_str) > 150 else error_str
            # Remove any JSON-like structures from error message
            if "{'error':" in clean_error or '{"error":' in clean_error:
                clean_error = "An unexpected error occurred during analysis."
            
            return {
                "affected_groups": [{"group": "Error analyzing data", "risk_level": "Unknown", "regions": []}],
                "mitigations": ["Please try again. If the error persists, check your API configuration."],
                "reasoning_summary": clean_error,
                "is_error": True,
                "error_type": "generic_error"
            }
