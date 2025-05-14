import sqlite3
import os
import time
import gc
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def encrypt_existing_db(db_path):
    if not os.path.exists(db_path):
        print(f"Error: database on the way {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        c.execute("SELECT * FROM users")
        rows = c.fetchall()
    except Exception as e:
        print(f"Error reading the database: {e}")
        conn.close()
        return

    conn.close()


    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

    os.makedirs("data", exist_ok=True)

    with open("data/rsa_private.pem", "wb") as f:
        f.write(private_key)
    with open("data/rsa_public.pem", "wb") as f:
        f.write(public_key)

    aes_key = get_random_bytes(32)

    rsa_cipher = PKCS1_OAEP.new(RSA.import_key(public_key))
    enc_aes_key = rsa_cipher.encrypt(aes_key)

    with open("data/encrypted_aes.key", "wb") as f:
        f.write(enc_aes_key)

    with open(db_path, "rb") as f:
        plaintext = f.read()

    iv = get_random_bytes(16)
    aes_cipher = AES.new(aes_key, AES.MODE_CFB, iv=iv)
    ciphertext = aes_cipher.encrypt(plaintext)

    with open("data/encrypted_db.bin", "wb") as f:
        f.write(iv + ciphertext)

    try:
        time.sleep(1)
        gc.collect()
        os.remove(db_path)
        print(f"{db_path} successfully deleted.")
    except PermissionError:
        print("The file is busy and cannot be deleted.")

    print("The database is encrypted, the AES key is encrypted using RSA.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: The database path is not specified..")
        print("Using: python ReadyDB.py <путь_к_базе_данных>")
    else:
        db_path = sys.argv[1]
        encrypt_existing_db(db_path)
