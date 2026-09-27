# Vercel Deployment & GitHub CI/CD Guide

This guide walks you through deploying **Active Directory Reaper** to **Vercel** with a continuous integration & continuous deployment (**CI/CD**) pipeline via **GitHub**.

---

## Architecture Overview

- **Frontend (Static CDN):** HTML5, Vanilla CSS, Cytoscape.js graph renderer, Chart.js metrics, and custom particle engines served from Vercel's Global Edge Network with instant loading.
- **Backend (Serverless API):** Python Flask WSGI app (`api/index.py`) hosted as an AWS Lambda Serverless Function under `@vercel/python`.
- **Lightweight Dependencies:** Isolated serverless dependencies in `api/requirements.txt` (`Flask`, `networkx`), avoiding heavy dependencies like PyTorch (>800MB) that exceed Vercel's 250MB Lambda package limit.
- **Data & Artifacts:** Pre-generated Active Directory topology (`data/bloodhound_export.json`) and trained RL agent metrics (`output/metrics.json`, `output/benchmark_report.json`).

---

## Method 1: Zero-Config GitHub Native Vercel Integration (Recommended)

Vercel provides native GitHub integration that automatically deploys every commit to production and every Pull Request to an isolated preview environment.

### Steps:
1. **Push your repository to GitHub** (see [Git Setup Commands](#git-setup-commands) below).
2. Go to [https://vercel.com](https://vercel.com) and log in.
3. Click **"Add New..."** -> **"Project"**.
4. Select **"Continue with GitHub"** and import your `Active_Directory_Reaper` repository.
5. In the configuration screen:
   - **Framework Preset:** Leave as `Other`.
   - **Root Directory:** `./`
   - **Build and Output Settings:** Default (Vercel automatically detects `vercel.json` and `api/index.py`).
6. Click **Deploy**.
7. Vercel will build and deploy your project in under 30 seconds!

---

## Method 2: GitHub Actions Automated CI/CD Pipeline

For production pipelines with automated testing, linting, and PR review comments, use the included GitHub Actions workflow at [`.github/workflows/vercel-cicd.yml`](../.github/workflows/vercel-cicd.yml).

### Pipeline Workflow:
1. **`test` Job:**
   - Validates JSON files (`bloodhound_export.json`, `metrics.json`, `benchmark_report.json`).
   - Runs automated API endpoint unit tests (`tests/test_api.py`).
2. **`deploy-preview` Job (Pull Requests):**
   - Builds preview artifacts using Vercel CLI.
   - Generates an isolated preview URL.
   - Automatically posts a comment on the GitHub PR with the preview link.
3. **`deploy-production` Job (Push to `main`):**
   - Automatically builds and deploys directly to your Vercel production domain.

### Required GitHub Secrets:
To enable the GitHub Actions workflow, add the following secrets in your GitHub repository (**Settings > Secrets and variables > Actions > New repository secret**):

| Secret Name | How to Get It |
|---|---|
| `VERCEL_TOKEN` | Go to [Vercel Account Tokens](https://vercel.com/account/tokens) -> Create Token. |
| `VERCEL_ORG_ID` | Run `vercel link` locally or check Project Settings -> General -> Team ID. |
| `VERCEL_PROJECT_ID` | Run `vercel link` locally or check Project Settings -> General -> Project ID. |

---

## Git Setup Commands

To initialize your local repository and push to GitHub:

```bash
# 1. Initialize git (if not already initialized)
git init

# 2. Stage all project files
git add .

# 3. Create your first commit
git commit -m "feat: configure Vercel serverless deployment and GitHub CI/CD pipeline"

# 4. Set branch to main
git branch -M main

# 5. Link your remote GitHub repository
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/Active_Directory_Reaper.git

# 6. Push code to GitHub
git push -u origin main
```

---

## Testing Locally Before Deploying

You can run the API and test suite locally:

```bash
# Run unit tests:
python -m unittest discover -s tests -p "test_*.py"

# Run the local server:
python api/index.py
```
Visit `http://localhost:8000` to interact with the dashboard.
