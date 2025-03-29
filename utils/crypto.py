# utils/crypto.py
import hashlib
import secrets

def generate_salt():
    """Gera um salt seguro aleatório."""
    return secrets.token_hex(16)

def hash_password(password, salt):
    """Retorna o hash SHA-256 de uma senha concatenada com salt."""
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(stored_hash, stored_salt, provided_password):
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    return hash_password(provided_password, stored_salt) == stored_hash
