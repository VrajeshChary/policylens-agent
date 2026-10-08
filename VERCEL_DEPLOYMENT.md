# Deploying PolicyLens to Vercel

PolicyLens is fully configured for seamless one-click deployment on **Vercel** using Vercel's Python Serverless Functions (`@vercel/python`) and global Edge Network.

---

## 🚀 Quick Start: Deploy in 3 Steps

### Step 1: Import Project to Vercel
1. Log into your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **"Add New..."** → **"Project"**.
3. Select your GitHub repository: `VrajeshChary/policylens-agent`.
4. Leave **Framework Preset** as `Other` (detected automatically via `vercel.json`).
5. Leave Root Directory as `./` (default).

### Step 2: Configure Environment Variables
In the **Environment Variables** section, add:

| Key | Value | Description |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | `Your-Google-Gemini-Key` | Required for AI reasoning |
| `GEMINI_MODEL` | `gemini-3.8-flash` | Recommended model |

*(Note: Never expose API keys publicly; Vercel encrypts these variables securely).*

### Step 3: Deploy
- Click **"Deploy"**.
- In ~1 minute, your application will be live at:
  `https://your-project.vercel.app`

---

## 🛠️ Architecture on Vercel

```
User Request
  │
  ├──> / (Root UI)               ──> Vercel Edge CDN (serves public/index.html)
  ├──> /policy-lens.png (Assets) ──> Vercel Edge CDN (serves public/policy-lens.png)
  └──> /api/analyze (API)        ──> Vercel Serverless Function (api/index.py via FastAPI)
                                          │
                                          └──> Google Gemini API (gemini-3.8-flash)
```

- **Frontend**: Ultra-fast global CDN delivery with zero serverless cold-start latency for the UI.
- **Backend**: Managed Python 3.11 Serverless Function (`api/index.py`) configured with up to 60s execution duration and 1024MB RAM.
