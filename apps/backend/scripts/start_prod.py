import os
import subprocess
import sys

def main():
    # Get PORT from environment or default to 8000
    port = os.getenv("PORT", "8000")
    print(f"[INFO] Starting Production Server on Port {port}...")

    # Run Database Migrations
    print("[INFO] Running Alembic Migrations...")
    try:
        # We use sys.executable to ensure we use the same python interpreter
        ret = subprocess.call([sys.executable, "-m", "alembic", "upgrade", "head"])
        if ret == 0:
            print("[INFO] Migrations SUCCESS.")
        else:
            print(f"[ERROR] Migrations failed with exit code {ret}. Continuing to start app anyway...")
    except Exception as e:
        print(f"[ERROR] Failed to run migrations: {e}")

    # Start Uvicorn
    print(f"[INFO] Executing Uvicorn on 0.0.0.0:{port}")
    
    # We use os.execvp to replace the current process with uvicorn
    # This ensures signals are handled correctly
    try:
        os.execvp("uvicorn", ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", port])
    except Exception as e:
        print(f"[FATAL] Failed to start uvicorn: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
