# PolicyLens Deployment Guide

This guide will help you deploy PolicyLens on Render.

## Prerequisites

1. A GitHub account
2. A Render account (sign up at https://render.com)
3. A Google Gemini API key (get it from https://ai.dev)

## Deployment Steps

### Option 1: Deploy using Render Dashboard (Recommended)

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Create a new Web Service on Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `policylens-agent` repository

3. **Configure the service**
   - **Name**: `policylens-agent` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Choose Starter (free tier) or higher

4. **Set Environment Variables**
   Click on "Environment" tab and add:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `GOOGLE_API_KEY`: (Optional, same as GEMINI_API_KEY if needed)
   - `PORT`: (Auto-set by Render, don't override)
   - `ENVIRONMENT`: `production`
   - `VERTEX_AI_LOCATION`: `us-central1` (optional)

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - Wait for the build to complete (usually 2-5 minutes)

6. **Access your app**
   - Once deployed, you'll get a URL like: `https://policylens-agent.onrender.com`
   - Your app will be live at this URL!

### Option 2: Deploy using render.yaml (Infrastructure as Code)

1. **Push your code to GitHub** (same as Option 1)

2. **Create a Blueprint on Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml` and configure the service

3. **Set Environment Variables**
   - Go to your service → Environment tab
   - Add `GEMINI_API_KEY` and other required variables

4. **Deploy**
   - Render will use the configuration from `render.yaml`
   - Your app will be automatically deployed

### Option 3: Deploy using Docker

1. **Build and test locally** (optional)
   ```bash
   docker build -t policylens-agent .
   docker run -p 8000:8000 -e GEMINI_API_KEY=your-key policylens-agent
   ```

2. **Deploy on Render**
   - Create a new Web Service
   - Select "Docker" as the environment
   - Render will automatically detect and use the Dockerfile
   - Set environment variables as described above

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GEMINI_API_KEY` | Yes | Your Google Gemini API key | `AIzaSy...` |
| `GOOGLE_API_KEY` | No | Alternative API key variable | `AIzaSy...` |
| `PORT` | No | Port number (auto-set by Render) | `8000` |
| `ENVIRONMENT` | No | Environment name | `production` |
| `VERTEX_AI_LOCATION` | No | Vertex AI region | `us-central1` |
| `GCS_BUCKET_NAME` | No | Google Cloud Storage bucket | `my-bucket` |

## Post-Deployment

1. **Test your deployment**
   - Visit your Render URL
   - Check the `/health` endpoint: `https://your-app.onrender.com/health`
   - Upload a test PDF to verify functionality

2. **Monitor logs**
   - Go to your service → Logs tab
   - Monitor for any errors or issues

3. **Set up custom domain** (optional)
   - Go to Settings → Custom Domains
   - Add your domain and follow DNS configuration

## Troubleshooting

### Build fails
- Check that all dependencies in `requirements.txt` are valid
- Ensure Python version is compatible (3.9+)
- Check build logs for specific errors

### App crashes on startup
- Verify `GEMINI_API_KEY` is set correctly
- Check that the start command is correct
- Review application logs

### API errors
- Verify your Gemini API key is valid and has quota
- Check API key permissions
- Review error messages in logs

### Static files not loading
- Ensure `backend/static/` directory exists
- Check file paths in the code
- Verify static file mounting in `main.py`

## Free Tier Limitations

Render's free tier has some limitations:
- Services spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Limited build minutes per month

For production use, consider upgrading to a paid plan.

## Support

For issues or questions:
- Check Render documentation: https://render.com/docs
- Review application logs in Render dashboard
- Open an issue on GitHub

