# core/credentials.py
import os
import json

CREDENTIALS_FILE = "data/credentials.json"

def initialize_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'w') as file:
            json.dump({}, file)

def load_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'w') as file:
            json.dump({}, file)
    try:
        with open(CREDENTIALS_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        with open(CREDENTIALS_FILE, 'w') as file:
            json.dump({}, file)
        return {}


def save_credentials(credentials):
    with open(CREDENTIALS_FILE, 'w') as file:
        json.dump(credentials, file, indent=4)
