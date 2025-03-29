# core/user_data.py
import os
import json
import time
from datetime import datetime
from constants import USER_DATA_FILE

def load_user_data():
    try:
        if not os.path.exists(USER_DATA_FILE):
            os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)  # Garante que o diretório existe
            with open(USER_DATA_FILE, 'w') as file:
                json.dump({}, file)
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"Erro: Arquivo de dados corrompido. Criando backup e iniciando novo arquivo.")
        if os.path.exists(USER_DATA_FILE):
            backup_name = USER_DATA_FILE + f".bak.{int(time.time())}"
            os.rename(USER_DATA_FILE, backup_name)
        with open(USER_DATA_FILE, 'w') as file:
            json.dump({}, file)
        return {}
    except Exception as e:
        print(f"Erro ao acessar arquivo de dados: {str(e)}")
        return {}

def save_user_data(user_data):
    os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)  # Garante que o diretório existe
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_data, file, indent=4)
