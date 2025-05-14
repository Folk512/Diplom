import sqlite3
import os
import time
import gc
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import base64
import sys


if getattr(sys, 'frozen', False):
    import tkinter as tk
    sys.argv = sys.argv[:1]

def create_and_encrypt_db():
    os.makedirs("data", exist_ok=True)
    db_path = "data/secure_data.db"

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        full_name TEXT,
        passport_number TEXT,
        password TEXT
    );
    """)
    c.executemany("INSERT INTO users (full_name, passport_number, password) VALUES (?, ?, ?)", [
        ("Иванов Иван", "4500 123456", "qwerty123"),
        ("Петров Петр", "4700 654321", "letmein!"),
        ("Сидоров Сидор", "4800 111222", "12345678")
    ])
    conn.commit()
    c.close()
    conn.close()

    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()

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
        if os.path.exists(db_path):
            os.remove(db_path)
            print("secure_data.db successfully deleted.")
        else:
            print("secure_data.db already deleted earlier.")
    except PermissionError:
        print("The file is still busy and cannot be deleted..")

    print("The database is created, encrypted, and the AES key is encrypted using RSA.")

if __name__ == "__main__":
    create_and_encrypt_db()
