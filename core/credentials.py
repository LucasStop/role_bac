# core/credentials.py
import os
import json

CREDENTIALS_FILE = "data/credentials.json"

def initialize_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'w') as file:
            json.dump({}, file)

def load_credentials():
    with open(CREDENTIALS_FILE, 'r') as file:
        return json.load(file)

def save_credentials(credentials):
    with open(CREDENTIALS_FILE, 'w') as file:
        json.dump(credentials, file, indent=4)
