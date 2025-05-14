import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ENCRYPTED_AES_KEY_PATH = "data/encrypted_aes.key"
DECRYPTED_RSA_PATH = "data/decrypted_rsa_private.pem"
ENCRYPTED_DB_PATH = "data/encrypted_db.bin"
DECRYPTED_DB_PATH = "data/decrypted_db.db"

print(f"Downloading an RSA private key from {DECRYPTED_RSA_PATH}")
with open(DECRYPTED_RSA_PATH, "rb") as f:
    private_key = RSA.import_key(f.read())

rsa_cipher = PKCS1_OAEP.new(private_key)

with open(ENCRYPTED_AES_KEY_PATH, "rb") as f:
    enc_aes_key = f.read()

if len(enc_aes_key) != 256:
    raise ValueError(f"The length of the encrypted AES key does not match that expected for an RSA key. Expected size: 256 bytes, received: {len(enc_aes_key)}")

print("Decryption of the AES key...")
try:
    aes_key = rsa_cipher.decrypt(enc_aes_key)
    print(f"The AES key has been successfully decrypted: {aes_key.hex()}")
except Exception as e:
    print(f"Error decrypting the AES key: {e}")
    exit(1)

print(f"Decrypting an encrypted database from {ENCRYPTED_DB_PATH}")
with open(ENCRYPTED_DB_PATH, "rb") as f:
    iv = f.read(16)
    ciphertext = f.read()

try:
    cipher = AES.new(aes_key, AES.MODE_CFB, iv=iv)
    decrypted_data = cipher.decrypt(ciphertext)
except Exception as e:
    print(f"Error decrypting the database: {e}")
    exit(1)

with open(DECRYPTED_DB_PATH, "wb") as f:
    f.write(decrypted_data)

print(f"The database has been successfully decrypted and saved in {DECRYPTED_DB_PATH}")
