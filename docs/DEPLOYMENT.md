# Deployment Guide

This guide covers how to deploy the Job Hunter AI application and configure the database for both production (PostgreSQL on Railway) and local development (SQLite).

## Prerequisites

-   **Node.js** (v18+)
-   **Python** (v3.10+)
-   **Git**
-   **Vercel Account** (for Frontend)
-   **Railway Account** (for Backend & Postgres Database)

---

## 1. Backend Deployment (Railway) - Step by Step

### A. Create Project & Database
1.  Log in to [Railway](https://railway.app/).
2.  Click **"New Project"** -> **"Provision PostgreSQL"**.
3.  Once the database is created, click on it and go to the **"Connect"** tab.
4.  Copy the **"Postgres Connection URL"**. It looks like `postgresql://postgres:PASSWORD@roundhouse.proxy.rlwy.net:PORT/railway`.

### B. Deploy Backend Service
1.  In the same project, click **"New"** -> **"GitHub Repo"** -> Select `job-hunter-ai`.
2.  Go to the **"Settings"** of the new service.
3.  Under **"Build Command"**, ensure it is empty (Railway usually detects `requirements.txt`).
4.  Under **"Start Command"**, use:
    ```bash
    python apps/backend/scripts/start_prod.py
    ```

### C. Environment Variables (Backend)
Go to the **"Variables"** tab and add the following strictly as shown:

| Variable | Value Example | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | Port for the backend server |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:PASSWORD@roundhouse...` | **IMPORTANT:** Paste the Railway Postgres URL. **YOU MUST REPLACE** `postgresql://` with `postgresql+asyncpg://` at the beginning. |
| `SECRET_KEY` | `change_this_to_something_random` | A random string for security |
| `OPENAI_API_KEY` | `sk-...` | Your OpenAI API Key (starts with sk-) |
| `ALLOWED_ORIGINS` | `*` | **CRITICAL:** Start with `*` or a comma-separated list like `https://myapp.vercel.app,http://localhost:3000`. Do NOT use `["..."]` JSON syntax here unless experienced. |
| `SCRAPER_PROXY_URL` | `http://user:pass@proxy.example.com:8080` | **Optional:** A proxy URL to route web scraping requests through. Highly recommended for production to avoid IP bans (e.g., from Indeed/LinkedIn). |
| `ENABLE_JOBSPY` | `false` | **CRITICAL FOR RAILWAY:** Set to `false` in production if you do *not* have a proxy. JobSpy on Railway without a proxy will get IP-banned, hang for a long time, and cause a "Network Error" on Vercel. |
| `ADZUNA_APP_ID` | `...` | Get a free API ID from [developer.adzuna.com](https://developer.adzuna.com/). Highly recommended fallback if JobSpy is disabled. |
| `ADZUNA_APP_KEY` | `...` | Get a free API Key from [developer.adzuna.com](https://developer.adzuna.com/). |

---

## 2. Frontend Deployment (Vercel) - Step by Step

### A. Import Project
1.  Log in to [Vercel](https://vercel.com/).
2.  Click **"Add New..."** -> **"Project"**.
3.  Import the `job-hunter-ai` repository.

### B. Configure Project (SCREEN: "Configure Project")
1.  **Framework Preset:** Select `Next.js`.
2.  **Root Directory:** Click "Edit" and select `apps/frontend`.
3.  **Build Command:** Leave as `npm run build`.
4.  **Output Directory:** Leave as `.next`.
5.  **Environment Variables:** Expand this section.

### C. Environment Variables (Frontend)
Add the following variable:

| Variable | Value Example | Description |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `https://job-hunter-ai-production.up.railway.app/api/v1` | **IMPORTANT:** This is the URL of your Railway Backend Service (get this from Railway -> Settings -> Networking -> Public Domain). Ensure it ends with `/api/v1`. |

### D. Deploy
Click **"Deploy"**. Vercel will build and deploy your frontend.
If you see "Build Error", check the logs. We recently fixed a `useQuery` error (ensure `apps/frontend/src/app/dashboard/profile/page.tsx` has `'use client';` at the top).

---

## 3. Local Development (SQLite)

For local development, use SQLite.

### A. Backend Setup
1.  Navigate to `apps/backend`.
2.  Unique command for Windows PowerShell:
    ```powershell
    $env:DATABASE_URL="sqlite+aiosqlite:///./data/database.db"
    python apps/backend/scripts/start_prod.py
    ```

### B. Frontend Setup
1.  Navigate to `apps/frontend`.
2.  Create `.env.local`:
    ```ini
    NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    ```
3.  Run: `npm run dev`

---

## Summary for Screens (Railway)

**Screen: Variables**
-   `DATABASE_URL`: `postgresql+asyncpg://...` (Make sure `asyncpg` is there!)
-   `ALLOWED_ORIGINS`: `*` (Simple star for testing)

**Screen: Settings**
-   **Start Command:** `python apps/backend/scripts/start_prod.py` (This runs migrations automatically)
