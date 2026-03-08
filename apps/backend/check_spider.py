import paramiko

def check():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("187.77.50.247", username="root", password="beatrizPRO2@1@")
    
    print("--- DOCKER PS ---")
    stdin, stdout, stderr = client.exec_command("docker ps | grep spider")
    print(stdout.read().decode())
    
    print("--- DOCKER LOGS SUMMARY ---")
    stdin, stdout, stderr = client.exec_command("docker logs jobhunter-spider 2>&1 | grep -E 'found|✅' > /tmp/spider_stats.txt && cat /tmp/spider_stats.txt | tail -n 20")
    print(stdout.read().decode())
    
    client.close()

if __name__ == "__main__":
    check()
