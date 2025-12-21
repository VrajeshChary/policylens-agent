# PolicyLens

PolicyLens is an autonomous policy impact assessment agent built using Google ADK and Gemini 2.5 Flash. It automates the analysis of policy documents to identify affected populations, assess risk levels, and recommend mitigation strategies.

## 🎯 Problem Statement

Policy impact analysis is traditionally slow, manual, and prone to oversight. Governance teams often struggle to rapidly identify how new policies affect specific demographic groups, leading to unintended consequences and delayed implementation.

## 💡 Solution Overview

PolicyLens leverages Agentic AI to transform this process. By autonomously reading policy documents and reasoning over demographic data, it provides instant, structured impact assessments. This enables policymakers to make data-driven decisions in seconds rather than weeks.

## 🤖 Why Agentic AI?

Traditional NLP can extract text, but it lacks reasoning. PolicyLens acts as an **agent**:
- **It Plans**: Breaks down analysis into policy parsing, demographic mapping, and risk evaluation.
- **It Reasons**: Connects policy clauses to specific population needs.
- **It Acts**: Generates structured, actionable mitigation strategies.

## 🛠️ Google Technologies Used

- **Google Gemini 2.5 Flash**: The core reasoning engine for high-speed, accurate document analysis.
- **Google Cloud Vertex AI**: Infrastructure for deploying and managing the AI models.
- **Google Project IDX / Cloud Shell**: Development environment.

## 🔄 System Workflow

1.  **Input**: User uploads a Policy PDF and (optional) Demographic CSV.
2.  **Agent Orchestration**:
    *   **Parsing**: Extracts text and structure from documents.
    *   **Reasoning**: The `PolicyImpactAgent` analyzes the policy against demographic segments.
    *   **Assessment**: Identifies risks (Low/Medium/High) and affected regions.
    *   **Recommendation**: Generates specific mitigation steps.
3.  **Output**: A structured JSON report displayed via a clean Web UI.

## 💻 How to Run Locally

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/policylens.git
    cd policylens
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment:**
    *   Get a Google Gemini API Key.
    *   Set the `GEMINI_API_KEY` environment variable:
        ```bash
        export GEMINI_API_KEY="your-api-key"
        ```

4.  **Run the Backend:**
    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```

5.  **Access the App:**
    *   Open `http://localhost:8000` in your browser.

## 🎮 Demo Instructions

1.  **Launch the App**: Ensure the server is running at `http://localhost:8000`.
2.  **Upload Policy**: Use the provided `data/sample_policy.pdf`.
3.  **Upload Demographics**: Use the provided `data/sample_demographics.csv`.
4.  **Click "Analyse"**: Watch the agent process the documents in real-time.
5.  **View Results**: Explore the identified affected groups, risk levels, and mitigation strategies.

---

**Status**: Hackathon Submission (Polished & Stable)
