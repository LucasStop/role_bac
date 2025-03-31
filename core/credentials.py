import os
import json
import time
from constants import CREDENTIALS_FILE

def initialize_credentials():
    directory = os.path.dirname(CREDENTIALS_FILE)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    try:
        if not os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, 'w') as file:
                json.dump({}, file, indent=4)
        else:
            with open(CREDENTIALS_FILE, 'r') as file:
                try:
                    json.load(file)
                except json.JSONDecodeError:
                    print(f"Arquivo de credenciais corrompido. Criando backup.")
                    backup_name = CREDENTIALS_FILE + f".bak.{int(time.time())}"
                    os.rename(CREDENTIALS_FILE, backup_name)
                    with open(CREDENTIALS_FILE, 'w') as new_file:
                        json.dump({}, new_file, indent=4)
    except Exception as e:
        print(f"Erro ao inicializar credenciais: {e}")
        with open(CREDENTIALS_FILE, 'w') as file:
            json.dump({}, file, indent=4)

def load_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        initialize_credentials()
    
    try:
        with open(CREDENTIALS_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("Erro ao decodificar arquivo de credenciais. Inicializando novo arquivo.")
        initialize_credentials()
        return {}
    except Exception as e:
        print(f"Erro ao carregar credenciais: {e}")
        return {}

def save_credentials(credentials):
    directory = os.path.dirname(CREDENTIALS_FILE)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    try:
        with open(CREDENTIALS_FILE, 'w') as file:
            json.dump(credentials, file, indent=4)
    except Exception as e:
        print(f"Erro ao salvar credenciais: {e}")
        raise e
