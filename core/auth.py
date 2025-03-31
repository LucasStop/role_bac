from datetime import datetime
from core.credentials import load_credentials, save_credentials
from core.user_data import load_user_data, save_user_data
from core.security import check_account_locked, reset_failed_attempts, increment_failed_attempts
from utils.crypto import generate_salt, hash_password, verify_password
from constants import AUTH_SUCCESS, AUTH_LOCKED, AUTH_NOT_FOUND, AUTH_WRONG_PASSWORD, MAX_LOGIN_ATTEMPTS

def register_user(username, password, permissions):
    if len(password) < 6:
        return False, "Senha muito curta. Use pelo menos 6 caracteres."

    credentials = load_credentials()
    if username in credentials:
        return False, "Usuário já existe!"

    salt = generate_salt()
    password_hash = hash_password(password, salt)
    credentials[username] = {
        "password": password_hash,
        "salt": salt
    }
    save_credentials(credentials)

    user_data = load_user_data()
    if permissions is None:
        permissions = {"leitura": False, "escrita": False, "remocao": False}

    user_data[username] = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": "",
        "login_count": 0,
        "notes": [],
        "settings": {"theme": "light"},
        "security": {
            "failed_attempts": 0,
            "is_locked": False,
            "lock_time": None
        },
        "permissions": permissions
    }
    save_user_data(user_data)
    return True, f"Usuário '{username}' registrado com sucesso!"

def authenticate_user(username, password):
    print(f"[{datetime.now()}] Tentativa de login: {username}")

    credentials = load_credentials()

    if check_account_locked(username):
        print(f"[{datetime.now()}] Login bloqueado: {username}")
        return False, AUTH_LOCKED

    if username in credentials:
        password_matched = False
        user_record = credentials[username]

        if isinstance(user_record, dict):
            if "salt" in user_record:
                stored_hash = user_record["password"]
                stored_salt = user_record["salt"]
                password_matched = verify_password(stored_hash, stored_salt, password)
            else:
                stored_password = user_record["password"]
                salt = generate_salt()
                password_hash = hash_password(stored_password, salt)
                credentials[username] = {"password": password_hash, "salt": salt}
                save_credentials(credentials)
                password_matched = (stored_password == password)
        else:
            stored_password = user_record
            salt = generate_salt()
            password_hash = hash_password(stored_password, salt)
            credentials[username] = {"password": password_hash, "salt": salt}
            save_credentials(credentials)
            password_matched = (stored_password == password)

        if password_matched:
            user_data = load_user_data()
            if username in user_data:
                user_data[username]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                user_data[username]["login_count"] += 1
                save_user_data(user_data)

            reset_failed_attempts(username)
            print(f"[{datetime.now()}] Login bem-sucedido: {username}")
            return True, AUTH_SUCCESS

        attempts = increment_failed_attempts(username)
        remaining = MAX_LOGIN_ATTEMPTS - attempts
        print(f"[{datetime.now()}] Senha incorreta para {username}. Restantes: {remaining}")

        if remaining <= 0:
            return False, AUTH_LOCKED
        else:
            return False, f"{AUTH_WRONG_PASSWORD}:{remaining}"

    print(f"[{datetime.now()}] Usuário não encontrado: {username}")
    return False, AUTH_NOT_FOUND
