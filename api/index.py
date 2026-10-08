"""
Vercel Serverless Function entry point for PolicyLens API
"""
import os
import sys

# Ensure repository root is in sys.path for backend package resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.main import app

# Export app for Vercel's ASGI runner (@vercel/python)
# __all__ = ["app"]
