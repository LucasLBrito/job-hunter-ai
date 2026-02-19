import socket
import sys

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

backend_up = check_port(8000)
frontend_up = check_port(3000)

print(f"BACKEND_UP={backend_up}")
print(f"FRONTEND_UP={frontend_up}")
