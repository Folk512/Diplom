import socket
import ssl
from Crypto.Protocol.SecretSharing import Shamir
from Crypto.Cipher import AES
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


HOST = '0.0.0.0'
PORT = 5001
THRESHOLD = 2
CERT_PATH = "data/windows_server.crt"
KEY_PATH = "data/windows_server.key"
ENCRYPTED_RSA_PATH = "data/encrypted_rsa_key.bin"
DECRYPTED_RSA_PATH = "data/decrypted_rsa_private.pem"

received_shares = []

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile=CERT_PATH, keyfile=KEY_PATH)

print(f"Waiting {THRESHOLD} shares on port {PORT}...")

while len(received_shares) < THRESHOLD:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        with context.wrap_socket(s, server_side=True) as tls_server:
            conn, addr = tls_server.accept()
            with conn:
                print(f"Connection from {addr}")
                data = conn.recv(4096)
                if not data:
                    print("Empty data")
                    continue

                try:
                    idx = data[0]
                    share_bytes = data[1:]
                    if len(share_bytes) != 16:
                        raise ValueError(f"Incorrect shares length: {len(share_bytes)} (expected 16)")
                    received_shares.append((idx, share_bytes))
                    print(f" Share received #{idx}")
                except Exception as e:
                    print(f" Processing error: {e}")

print("Shares have been received. Restoring the AES key...")
aes_key = Shamir.combine(received_shares)
print(f"The AES key has been restored: {aes_key.hex()}")

print(f"Decrypting the RSA key from {ENCRYPTED_RSA_PATH}")
with open(ENCRYPTED_RSA_PATH, "rb") as f:
    nonce = f.read(16)
    tag = f.read(16)
    ciphertext = f.read()

cipher = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
rsa_key = cipher.decrypt_and_verify(ciphertext, tag)

with open(DECRYPTED_RSA_PATH, "wb") as f:
    f.write(rsa_key)

print(f"The RSA key has been successfully restored and saved in {DECRYPTED_RSA_PATH}")
