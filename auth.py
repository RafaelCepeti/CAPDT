# -*- coding: utf-8 -*-
import json
from mapeamento import mapeamento_hospital

# Função para carregar as credenciais
def load_credentials():
    with open("credentials.json", "r", encoding='utf-8') as file:
        credentials = json.load(file)
    return credentials

def check_credentials(username, password):
    credentials = load_credentials()
    print(f"Loaded credentials: {credentials}")  # Adiciona este print para debug
    if username in credentials and credentials[username]["password"] == password:
        return True
    return False

def get_user_hospitals(username):
    credentials = load_credentials()
    if username in credentials:
        if credentials[username]["hospitals"] == "all":
            return list(mapeamento_hospital.keys())
        return credentials[username]["hospitals"]
    return []
