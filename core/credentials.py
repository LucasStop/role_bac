# core/credentials.py
import os
import json
from constants import CREDENTIALS_FILE

def initialize_credentials():
    directory = os.path.dirname(CREDENTIALS_FILE)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    if not os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'w') as file:
            json.dump({}, file)

def load_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        initialize_credentials()
    with open(CREDENTIALS_FILE, 'r') as file:
        return json.load(file)

def save_credentials(credentials):
    directory = os.path.dirname(CREDENTIALS_FILE)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    with open(CREDENTIALS_FILE, 'w') as file:
        json.dump(credentials, file, indent=4)
