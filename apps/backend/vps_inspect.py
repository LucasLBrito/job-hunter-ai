import paramiko

def inspect_vps():
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
            "docker network ls",
            "docker ps -a"
        ]
        
        for cmd in commands:
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
    inspect_vps()
