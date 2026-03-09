import paramiko

def rename_containers():
    host = "187.77.50.247"
    port = 22
    username = "root"
    password = "beatrizPRO2@1@"

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"Connecting to {host} via SSH...")
        client.connect(hostname=host, port=port, username=username, password=password)
        
        commands = [
            "docker stop 634482e5a080_jobhunter-mongo 3c4428af7b4b_jobhunter-redis || true",
            "docker rename 634482e5a080_jobhunter-mongo jobhunter-mongo || true",
            "docker rename 3c4428af7b4b_jobhunter-redis jobhunter-redis || true",
            "docker start jobhunter-mongo jobhunter-redis",
            "docker restart jobhunter-spider",
            "sleep 5",
            "docker exec jobhunter-spider getent hosts jobhunter-mongo",
            "docker exec jobhunter-spider getent hosts jobhunter-redis",
        ]
        
        for cmd in commands:
            print(f"> {cmd}")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode('utf-8')
            err = stderr.read().decode('utf-8')
            if out: print(out.strip())
            if err: print(f"ERROR: {err.strip()}")

    except Exception as e:
        print(f"Error connecting: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    rename_containers()
