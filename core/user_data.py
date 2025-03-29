# core/user_data.py
import os
import json
import time
from datetime import datetime
from constants import USER_DATA_FILE

def load_user_data():
    try:
        directory = os.path.dirname(USER_DATA_FILE)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        if not os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'w') as file:
                json.dump({}, file, indent=4)
            return {}
            
        if os.path.getsize(USER_DATA_FILE) == 0:
            with open(USER_DATA_FILE, 'w') as file:
                json.dump({}, file, indent=4)
            return {}
                
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Erro: Arquivo de dados corrompido. Criando backup e iniciando novo arquivo. Erro: {e}")
        if os.path.exists(USER_DATA_FILE):
            backup_name = USER_DATA_FILE + f".bak.{int(time.time())}"
            os.rename(USER_DATA_FILE, backup_name)
        with open(USER_DATA_FILE, 'w') as file:
            json.dump({}, file, indent=4)
        return {}
    except Exception as e:
        print(f"Erro ao acessar arquivo de dados: {str(e)}")
        directory = os.path.dirname(USER_DATA_FILE)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(USER_DATA_FILE, 'w') as file:
            json.dump({}, file, indent=4)
        return {}

def save_user_data(user_data):
    try:
        directory = os.path.dirname(USER_DATA_FILE)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(USER_DATA_FILE, 'w') as file:
            json.dump(user_data, file, indent=4)
    except Exception as e:
        print(f"Erro ao salvar dados do usuário: {e}")
        raise e
