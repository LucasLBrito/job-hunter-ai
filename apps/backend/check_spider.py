import paramiko

def check_spider_logs():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("187.77.50.247", username="root", password="beatrizPRO2@1@")
    
    stdin, stdout, stderr = client.exec_command("docker logs --tail=500 jobhunter-spider")
    
    with open("spider_dump.log", "wb") as f:
        f.write(stdout.read())
        f.write(stderr.read())
        
    print("Logs saved to spider_dump.log")
    client.close()

if __name__ == "__main__":
    check_spider_logs()
