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

        commands = [
            f"git config --global --add safe.directory {dir_path}",
            f"cd {dir_path} && git fetch origin && git reset --hard origin/master",
            f"docker rmi -f job-hunter-ai_spider-worker || true",
            f"cd {dir_path} && docker-compose -f docker-compose.vps.yml build --no-cache spider-worker",
            f"cd {dir_path} && docker-compose -f docker-compose.vps.yml up --force-recreate -d spider-worker",
            f"cd {dir_path} && docker-compose -f docker-compose.vps.yml logs --tail=50 spider-worker"
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
