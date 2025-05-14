import socket
import ssl
from Crypto.Protocol.SecretSharing import Shamir
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


if len(sys.argv) != 4:
    print("Using: python SplitKeys <ip-addresses> <share_count> <threshold>")
    sys.exit(1)

ip_list = sys.argv[1].split(",")
SHARE_COUNT = int(sys.argv[2])
THRESHOLD = int(sys.argv[3])

if len(ip_list) != SHARE_COUNT:
    print("The number of IP addresses must match the number of shares!")
    sys.exit(1)

TARGETS = [(ip.strip(), 5000) for ip in ip_list]
PRIVATE_KEY_PATH = "data/rsa_private.pem"

with open(PRIVATE_KEY_PATH, "rb") as f:
    private_key = f.read()
print(f"Private RSA key: {len(private_key)} byte")

aes_key = get_random_bytes(16)
print(f"AES key: {aes_key.hex()}")

cipher = AES.new(aes_key, AES.MODE_EAX)
ciphertext, tag = cipher.encrypt_and_digest(private_key)
with open("data/encrypted_rsa_key.bin", "wb") as f:
    f.write(cipher.nonce + tag + ciphertext)
print(f"The private key is encrypted and stored in encrypted_rsa_key.bin")

shares = Shamir.split(THRESHOLD, SHARE_COUNT, aes_key)
print(f"Create {len(shares)} AES key shares")

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

print("\nSending shares using TLS...")
for (idx, share), (host, port) in zip(shares, TARGETS):
    try:
        with socket.create_connection((host, port)) as sock:
            with context.wrap_socket(sock, server_hostname=host) as tls_sock:
                tls_sock.sendall(bytes([idx]) + share)
                print(f"Share {idx} sent to {host}:{port}")
    except Exception as e:
        print(f"Error sending a share {idx} on {host}:{port}: {e}")
