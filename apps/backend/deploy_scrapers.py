import paramiko
import sys

def deploy():
    host = "187.77.50.247"
    port = 22
    username = "root"
    password = "beatrizPRO2@1@"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"Connecting to {host}...")
        client.connect(hostname=host, port=port, username=username, password=password)
        
        # Find directory
        stdin, stdout, stderr = client.exec_command("find /home /root -type d -name 'job-hunter-ai' 2>/dev/null | head -n 1")
        dir_path = stdout.read().decode().strip()
        print(f"Found project at: {dir_path}")

        if not dir_path:
            print("Could not find project directory!")
            return

        # Load local .env keys to inject into VPS
        import os
        from dotenv import load_dotenv
        load_dotenv("apps/backend/.env")
        tavily_key = os.getenv("TAVILY_API_KEY", "")
        firecrawl_key = os.getenv("FIRECRAWL_API_KEY", "")
        exa_key = os.getenv("EXA_API_KEY", "")

        commands = [
            f"git config --global --add safe.directory {dir_path}",
            f"cd {dir_path} && git fetch origin && git reset --hard origin/master",
            f"grep -q 'TAVILY_API_KEY' {dir_path}/apps/backend/.env || echo 'TAVILY_API_KEY={tavily_key}' >> {dir_path}/apps/backend/.env",
            f"grep -q 'FIRECRAWL_API_KEY' {dir_path}/apps/backend/.env || echo 'FIRECRAWL_API_KEY={firecrawl_key}' >> {dir_path}/apps/backend/.env",
            f"grep -q 'EXA_API_KEY' {dir_path}/apps/backend/.env || echo 'EXA_API_KEY={exa_key}' >> {dir_path}/apps/backend/.env",
            f"docker rmi -f job-hunter-ai_spider-worker || true",
            f"cd {dir_path} && docker-compose -f docker-compose.vps.yml build --no-cache spider-worker",
            f"docker stop jobhunter-spider || true",
            f"docker rm jobhunter-spider || true",
            f"cd {dir_path} && docker run -d --name jobhunter-spider --network job-hunter-ai_jobhunter-net --env-file ./apps/backend/.env -e MONGO_URI=mongodb://root:rootpassword@jobhunter-mongo:27017/ -e MONGO_DB_NAME=job_lake -e REDIS_URL=redis://jobhunter-redis:6379/0 -e ENVIRONMENT=production job-hunter-ai_spider-worker sh -c \"while true; do echo 'Starting Job Spider...'; python -m app.services.jobsearch.spider --limit 50 --concurrency 5; sleep 10800; done\"",
            f"docker logs --tail=50 jobhunter-spider"
        ]

        for cmd in commands:
            print(f"\n>>> Executing: {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            
            for line in iter(stdout.readline, ""):
                print(line, end="")
            for line in iter(stderr.readline, ""):
                print(line, end="")
            
            status = stdout.channel.recv_exit_status()
            print(f">>> Exit status: {status}")
            if status != 0 and "logs" not in cmd:
                print("Command failed! Aborting.")
                break
            
            print("Done.\n")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    deploy()
