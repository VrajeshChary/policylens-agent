#!/bin/bash
# Startup script for PolicyLens Agent

# Set default port if not provided
PORT=${PORT:-8000}

# Run the FastAPI application
exec uvicorn backend.main:app --host 0.0.0.0 --port $PORT

