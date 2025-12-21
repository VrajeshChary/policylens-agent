"""
Configuration settings for PolicyLens Agent
"""

import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# Google Gemini API Key (required for google-generativeai)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    # Don't raise error, use default if available
    GEMINI_API_KEY = None

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Gemini Model Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# File Upload Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_POLICY_EXTENSIONS = [".pdf"]
ALLOWED_DEMOGRAPHIC_EXTENSIONS = [".csv", ".xlsx", ".xls"]

# Analysis Configuration
RISK_LEVELS = ["low", "medium", "high", "critical"]
DEFAULT_TIMEOUT = 300  # 5 minutes

# CORS Configuration
CORS_ORIGINS = ["*"]

# Rate Limiting (disabled by default)
RATE_LIMIT_ENABLED = False
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW = 60  # seconds

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
