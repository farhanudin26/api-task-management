from cryptography.fernet import Fernet

# Generate a new key
new_key = Fernet.generate_key()

# Print the new key (in bytes)
print(new_key)
