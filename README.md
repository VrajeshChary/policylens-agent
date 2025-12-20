# PolicyLens Agent

PolicyLens is an autonomous policy impact assessment agent built using Google ADK and Gemini 3. It automates the analysis of policy documents to identify affected populations, assess risk levels, and recommend mitigation strategies.

## 🎯 Overview

Policy impact analysis is traditionally slow and manual, often taking weeks to complete. PolicyLens leverages agentic AI to reduce this process to seconds, enabling rapid policy assessment and decision-making.

## ✨ Features

- **Document Processing**: Reads and analyzes policy documents (PDF format)
- **Demographic Analysis**: Processes demographic data (CSV format)
- **Population Impact Assessment**: Identifies affected populations based on policy content
- **Risk Assessment**: Evaluates and categorizes risk levels
- **Mitigation Recommendations**: Provides actionable strategies to address identified risks
- **Autonomous Operation**: Uses Google ADK for intelligent agent orchestration

## 🛠️ Tech Stack

- **Google ADK** - Agent orchestration and workflow management
- **Gemini 3** - Advanced AI model via Vertex AI for document analysis
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
export GOOGLE_CLOUD_PROJECT=your-project-id
export VERTEX_AI_LOCATION=us-central1
export GCS_BUCKET_NAME=your-bucket-name
```

### Usage

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Upload a policy document (PDF) and demographic data (CSV) through the API or UI

3. The agent will automatically:
   - Parse the policy document
   - Analyze demographic data
   - Identify affected populations
   - Assess risk levels
   - Generate mitigation recommendations

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

**Current Status**: Hackathon MVP

---

Built with ❤️ using Google ADK and Gemini 3

