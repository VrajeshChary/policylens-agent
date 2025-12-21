# PolicyLens Agent

PolicyLens is an autonomous policy impact assessment agent built using Google ADK and Gemini 2.5 Flash. It automates the analysis of policy documents to identify affected populations, assess risk levels, and recommend mitigation strategies.

## 🎯 Overview

Policy impact analysis is traditionally slow and manual, often taking weeks to complete. PolicyLens leverages agentic AI to reduce this process to seconds, enabling rapid policy assessment and decision-making.

## ❔ What it does
- Reads a policy document (PDF)
- Reads demographic data (CSV)
- Identifies affected populations
- Assesses risk level
- Recommends mitigation strategies

## ✨ Features

- **Document Processing**: Reads and analyzes policy documents (PDF format)
- **Demographic Analysis**: Processes demographic data (CSV format)
- **Population Impact Assessment**: Identifies affected populations based on policy content
- **Risk Assessment**: Evaluates and categorizes risk levels
- **Mitigation Recommendations**: Provides actionable strategies to address identified risks
- **Autonomous Operation**: Uses Google ADK for intelligent agent orchestration

## 🛠️ Tech Stack

- **Google ADK** - Agent orchestration and workflow management
- **Gemini 2.5 Flash ** - Advanced AI model via Vertex AI for document analysis
- **Python** - Core development language
- **FastAPI** - RESTful API framework
- **Google Cloud Storage** - Document and data storage
- **Google Stitch** - User interface
- **Cursor IDE** - Development environment

## 📋 Prerequisites

- Python 3.9 or higher
- Google Cloud Platform account with Vertex AI enabled
- Access to Google ADK
- Google Cloud Storage bucket configured

## 🚀 Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/VrajeshChary/policylens-agent.git
cd policylens-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export GEMINI_API_KEY=your-gemini-api-key
export GOOGLE_CLOUD_PROJECT=your-project-id  # Optional
export VERTEX_AI_LOCATION=us-central1  # Optional
export GCS_BUCKET_NAME=your-bucket-name  # Optional
```

### Usage

1. Start the FastAPI server:
```bash
uvicorn backend.main:app --reload
```

2. Upload a policy document (PDF) and demographic data (CSV) through the API or UI

3. The agent will automatically:
   - Parse the policy document
   - Analyze demographic data
   - Identify affected populations
   - Assess risk levels
   - Generate mitigation recommendations

## 🌐 Deployment

### Deploy on Render

PolicyLens is ready to deploy on Render! Follow these steps:

1. **Set up Git repository** (if not already done):
   - See `GIT_SETUP.md` for detailed instructions
   - Push your code to GitHub

2. **Deploy on Render**:
   - See `DEPLOYMENT.md` for complete deployment guide
   - Quick start: Connect your GitHub repo to Render and deploy!

3. **Required Environment Variables**:
   - `GEMINI_API_KEY`: Your Google Gemini API key (required)

The project includes:
- ✅ `Dockerfile` for Docker deployment
- ✅ `render.yaml` for Render Blueprint deployment
- ✅ All necessary configuration files

For detailed instructions, see:
- [Git Setup Guide](GIT_SETUP.md)
- [Deployment Guide](DEPLOYMENT.md)

## 📁 Project Structure

```
policylens-agent/
├── README.md
├── requirements.txt
├── .gitignore
├── main.py              # FastAPI application entry point
├── agents/              # Agent orchestration logic
├── services/            # Core business logic
├── models/              # Data models and schemas
├── utils/               # Utility functions
└── tests/               # Test files
```

## 🔧 Configuration

Configure your Google Cloud credentials and project settings in `config.py` or via environment variables.

## 📊 API Endpoints

- `POST /analyze` - Submit policy document and demographic data for analysis
- `GET /status/{job_id}` - Check the status of an analysis job
- `GET /results/{job_id}` - Retrieve analysis results

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is part of a hackathon MVP. See LICENSE file for details.

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🏆 Status

**Current Status**: Hackathon (GDG Agent-a-thon) MVP

---

Built with ❤️ using Google ADK and Gemini 3


