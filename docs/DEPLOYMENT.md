# Deployment Guide

This guide covers how to deploy the Job Hunter AI application and configure the database for both production (PostgreSQL on Railway) and local development (SQLite).

## Prerequisites

-   **Node.js** (v18+)
-   **Python** (v3.10+)
-   **Git**
-   **Vercel Account** (for Frontend)
-   **Railway Account** (for Backend & Postgres Database)

---

## 1. Backend Deployment (Railway)

### A. Create Project & Database
1.  Log in to [Railway](https://railway.app/).
2.  Click **"New Project"** -> **"Provision PostgreSQL"**.
3.  Once the database is created, click on it and go to the **"Connect"** tab.
4.  Copy the **"Postgres Connection URL"**.

### B. Deploy Backend Service
1.  In the same project, click **"New"** -> **"GitHub Repo"** -> Select `job-hunter-ai`.
2.  Go to the **"Settings"** of the new service.
3.  Under **"Build Command"**, ensure it installs dependencies (Railway usually detects `requirements.txt` or `Pipfile`).
4.  Under **"Start Command"**, use:
    ```bash
    python apps/backend/scripts/start_prod.py
    ```
    *Note: This script automatically runs migrations.*

### C. Environment Variables (Backend)
Go to the **"Variables"** tab and add the following:

| Variable | Value | Description |
| :--- | :--- | :--- |
| `PORT` | `8000` | Port for the backend server |
| `DATABASE_URL` | `postgresql+asyncpg://...` | **IMPORTANT:** Paste the Railway Postgres URL here. **Replace `postgresql://` with `postgresql+asyncpg://` if needed.** |
| `SECRET_KEY` | `<your-secret-key>` | A strong random string for security |
| `OPENAI_API_KEY` | `sk-...` | Your OpenAI API Key |
| `ALLOWED_ORIGINS` | `https://<your-vercel-app>.vercel.app,http://localhost:3000` | Comma-separated list of allowed frontend origins |

---

## 2. Frontend Deployment (Vercel)

### A. Import Project
1.  Log in to [Vercel](https://vercel.com/).
2.  Click **"Add New..."** -> **"Project"**.
3.  Import the `job-hunter-ai` repository.

### B. Configure Project
1.  **Framework Preset:** Next.js
2.  **Root Directory:** `apps/frontend` (Edit the root directory setting).
3.  **Build Command:** `npm run build` (Default)
4.  **Output Directory:** `.next` (Default)

### C. Environment Variables (Frontend)
Add the following variables in the "Environment Variables" section:

| Variable | Value | Description |
| :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | `https://<your-railway-backend>.up.railway.app/api/v1` | The URL of your deployed backend |

### D. Deploy
Click **"Deploy"**. Vercel will build and deploy your frontend.

---

## 3. Local Development (SQLite)

For local development, we use SQLite to avoid the need for a running Postgres instance.

### A. Backend Setup
1.  Navigate to `apps/backend`.
2.  Create a `.env` file (or rename `.env.example`).
3.  Set `DATABASE_URL` to utilize SQLite:
    ```ini
    DATABASE_URL=sqlite+aiosqlite:///./data/database.db
    ```
    *Note: The `start_prod.py` script and `config.py` are configured to fall back to this SQLite URL if no simpler URL is provided, but explicit setting is better.*
4.  Run the backend:
    ```bash
    # Install dependencies
    pip install -r requirements.txt
    
    # Run server
    python app/main.py
    ```

### B. Frontend Setup
1.  Navigate to `apps/frontend`.
2.  Create `.env.local`.
3.  Set the API URL:
    ```ini
    NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    ```
4.  Run the frontend:
    ```bash
    npm run dev
    ```

---

## Troubleshooting

### "Attempted to call useQuery() from the server"
This error occurs in Next.js App Router when a component using React Query hooks is not marked as a client component.
**Fix:** Ensure `apps/frontend/src/app/dashboard/profile/page.tsx` has `'use client';` at the very top.

### Database Connection Issues
- **Postgres:** Ensure the connection string starts with `postgresql+asyncpg://`. SQLAlchemy requires the driver to be specified.
- **SQLite:** Ensure the `data` directory exists in `apps/backend`.

