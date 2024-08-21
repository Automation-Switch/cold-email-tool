import secrets

SECRET_KEY = secrets.token_hex(16)  # Generate a random 32-character hex string
print(SECRET_KEY)
