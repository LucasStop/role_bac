import hashlib
import secrets

def generate_salt():
    return secrets.token_hex(16)

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(stored_hash, stored_salt, provided_password):
    return hash_password(provided_password, stored_salt) == stored_hash
