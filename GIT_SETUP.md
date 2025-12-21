# Git Repository Setup Guide

Follow these steps to convert your code into a Git repository and push it to GitHub.

## Step 1: Initialize Git Repository

Open your terminal in the project directory and run:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: PolicyLens Agent ready for deployment"
```

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository:
   - **Repository name**: `policylens-agent` (or any name you prefer)
   - **Description**: "Autonomous policy impact assessment agent"
   - **Visibility**: Public or Private (your choice)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)

3. Click "Create repository"

## Step 3: Connect and Push to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/policylens-agent.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 4: Verify

1. Go to your GitHub repository page
2. Verify all files are uploaded
3. Check that these files are present:
   - `Dockerfile`
   - `render.yaml`
   - `requirements.txt`
   - `backend/` directory with all Python files
   - `DEPLOYMENT.md`

## Next Steps

After pushing to GitHub, follow the instructions in `DEPLOYMENT.md` to deploy on Render.

## Troubleshooting

### If you get "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/policylens-agent.git
```

### If you need to update files later
```bash
git add .
git commit -m "Your commit message"
git push
```

### If you want to check status
```bash
git status
```

