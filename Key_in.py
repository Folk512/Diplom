import socket
import ssl
import sys
import os

HOST = '0.0.0.0'
PORT = 5000
CERT_PATH = "data/server.crt"
KEY_PATH = "data/server.key"

def save_share(data, filename):
    with open(filename, 'wb') as f:
        f.write(data)
    print(f"Share save in {filename}")

def main():
    if len(sys.argv) != 2:
        print("Using: python3 receiver_tls.py <output_filename>")
        sys.exit(1)

    output_file = sys.argv[1]

    if not os.path.exists(CERT_PATH) or not os.path.exists(KEY_PATH):
        print(f"The certificate or key was not found in '{CERT_PATH}' и '{KEY_PATH}'")
        sys.exit(1)

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERT_PATH, keyfile=KEY_PATH)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
        sock.bind((HOST, PORT))
        sock.listen(5)
        print(f"The TLS server listens on {HOST}:{PORT}...")

        with context.wrap_socket(sock, server_side=True) as ssock:
            conn, addr = ssock.accept()
            with conn:
                print(f"Connection from {addr}")
                data = conn.recv(1024)
                if not data:
                    print("Empty data is received")
                    return
                save_share(data, output_file)

if __name__ == "__main__":
    main()
