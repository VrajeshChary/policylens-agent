# PolicyLens

**AI-Powered Policy Impact Assessment for Agile Governance**

PolicyLens is an autonomous agent designed to help policymakers, NGOs, and citizens understand the real-world impact of government policies. By leveraging **Google's Gemini 1.5 Pro**, it analyzes complex policy documents against demographic data to identify affected groups, assess risks, and recommend mitigation strategies.

---

## 🚀 Problem Statement
Government policies often have unintended consequences on vulnerable populations. Analyzing these impacts requires:
- Extensive manual reading of legal documents.
- Correlation with vast demographic datasets.
- Hours or days of expert analysis.

**PolicyLens** automates this process, providing instant, data-driven impact assessments.

## 💡 Solution Overview
PolicyLens serves as an intelligent "Judge" that:
1. **Parses** complex PDF policy documents.
2. **Correlates** policy clauses with demographic data (CSV).
3. **Reasons** over potential social and economic risks.
4. **Generates** actionable mitigation recommendations.

## 🤖 Why Agentic AI?
Traditional scripts follow fixed rules. PolicyLens uses **Agentic AI** to:
- **Reason Dynamically**: It understands context, not just keywords.
- **Self-Correct**: It validates its own output structure.
- **Use Tools**: It simulates calling specialized "sub-agents" for reasoning tasks.

## 🛠️ Google Technologies Used
- **Google Gemini 1.5 Pro**: The core reasoning engine for understanding policy nuances.
- **Google Cloud Run (Ready)**: Designed for stateless, scalable deployment.
- **Python (FastAPI)**: High-performance backend framework.

## 🔄 System Workflow
1. **User Uploads**: Policy PDF and Demographics CSV.
2. **Preprocessing**: Backend extracts text and structured data.
3. **Agentic Reasoning**:
   - Step 1: **Mechanism Analysis** (What does the policy do?)
   - Step 2: **Impact Correlation** (Who does it affect?)
   - Step 3: **Risk Scoring** (How severe is the impact?)
4. **Response**: JSON structure containing affected groups, risks, and mitigations.
5. **Visualization**: Frontend displays a clear, interactive summary.

## 💻 How to Run Locally

### Prerequisites
- Python 3.9+
- A Google Cloud Project with Gemini API enabled.
- `GEMINI_API_KEY` set in your environment.

### Steps
1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-repo/policylens.git
   cd policylens
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variable**
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

4. **Run the Server**
   ```bash
   uvicorn backend.main:app --reload
   ```

5. **Access the App**
   Open `http://127.0.0.1:8000` in your browser.

## 🎯 Demo Instructions
1. Open the web interface.
2. Upload `data/sample_policy.pdf`.
3. (Optional) Upload `data/sample_demographics.csv`.
4. Click **Analyze**.
5. Watch the agent break down the policy and provide insights on "Urban Gig Workers" or "Rural Farmers".

---
*Built for the Google AI Hackathon.*
