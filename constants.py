# constants.py

# Caminhos dos arquivos
CREDENTIALS_FILE = "data/credentials.json"
USER_DATA_FILE = "data/user_data.json"

# Configurações de segurança
MAX_LOGIN_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 15

# Códigos de autenticação
AUTH_SUCCESS = "success"
AUTH_LOCKED = "locked"
AUTH_NOT_FOUND = "not_found"
AUTH_WRONG_PASSWORD = "wrong_password"
