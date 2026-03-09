import paramiko

def fix_containers():
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
            "docker start 634482e5a080", # Mongo
            "docker start 3c4428af7b4b", # Redis
            "docker restart jobhunter-spider", # Restart spider to try again
            "sleep 10",
            "docker ps",
            "docker logs --tail=50 jobhunter-spider"
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
    fix_containers()
