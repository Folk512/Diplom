
import sys
import socket
import ssl

if len(sys.argv) != 4:
    print("Using: python send_back_tls.py <ip_server> <port> <file-share>")
    sys.exit(1)

host = sys.argv[1]
port = int(sys.argv[2])
filename = sys.argv[3]

with open(filename, 'rb') as f:
    data = f.read()

context = ssl._create_unverified_context()

try:
    with socket.create_connection((host, port)) as sock:
        with context.wrap_socket(sock, server_hostname=host) as tls_sock:
            tls_sock.sendall(data)
            print("The share was successfully sent back.")
except Exception as e:
    print(f"Sending error: {e}")
