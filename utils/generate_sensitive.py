from cryptography.fernet import Fernet
from config import config

cipher_suite = Fernet(config.KEY_GENERATE_ENCRYPT)

def encrypt_value(value: str) -> str:
    encrypted_value = cipher_suite.encrypt(value.encode())
    return encrypted_value.decode()  # Store as a string in the database

def decrypt_value(encrypted_value: str) -> str:
    decrypted_value = cipher_suite.decrypt(encrypted_value.encode())
    return decrypted_value.decode()  # Convert back to the original value