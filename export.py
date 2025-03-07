import os
import requests
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
token = os.getenv('API_TOKEN')

# 🚨 Debug: Verificar se a variável foi carregada corretamente
if not token:
    print("❌ ERRO: API_TOKEN não foi encontrado! Verifique o arquivo .env ou as variáveis de ambiente.")
    exit(1)

# URL da API
url = 'https://cepetiredcap.com.br/api/'

# Parâmetros da requisição
data = {
    'token': token,
    'content': 'record',
    'format': 'csv',
    'type': 'flat',
    'forms[0]': 'cadastro',
    'forms[1]': 'internao',
    'forms[2]': 'comorbidades',
    'forms[3]': 'apache_ii',
    'forms[4]': 'escores_dirios',
    'forms[5]': 'desfecho_da_uti',
    'forms[6]': 'transferncia',
    'rawOrLabel': 'label',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'false',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json'
}

# Caminho para salvar os arquivos (usar /tmp/)
save_path = "/tmp/dados.csv"
error_path = "/tmp/erro.json"

try:
    print("🔄 Enviando requisição para a API...")
    response = requests.post(url, data=data, timeout=200)
    print(f"🔍 Status HTTP: {response.status_code}")

    if response.status_code == 403:
        try:
            error_message = json.loads(response.text).get('error', 'Erro desconhecido.')
        except json.JSONDecodeError:
            error_message = "Erro desconhecido (resposta não era um JSON válido)."

        print(f"❌ Erro de permissão: {error_message}")
        with open(error_path, 'w', encoding='utf-8') as jsonfile:
            json.dump({'error': 'Erro de permissão', 'message': error_message}, jsonfile, ensure_ascii=False)
        exit(1)

    elif response.status_code == 200:
        print("✅ Dados recebidos com sucesso! Salvando...")
        with open(save_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvfile.write(response.text)
        print(f"📂 Dados salvos com sucesso em: {save_path}")

    else:
        print(f"❌ Falha na requisição! Status HTTP: {response.status_code}")
        with open(error_path, 'w', encoding='utf-8') as jsonfile:
            json.dump({'error': 'Falha na requisição', 'status_code': response.status_code, 'message': response.text}, jsonfile, ensure_ascii=False)
        exit(1)

except requests.exceptions.Timeout:
    print("❌ Ocorreu um timeout na solicitação.")
    with open(error_path, 'w', encoding='utf-8') as jsonfile:
        json.dump({'error': 'Timeout', 'message': 'A solicitação excedeu o tempo limite'}, jsonfile, ensure_ascii=False)
    exit(1)

except requests.exceptions.RequestException as e:
    print(f"❌ Ocorreu um erro de conexão: {e}")
    with open(error_path, 'w', encoding='utf-8') as jsonfile:
        json.dump({'error': 'Erro de conexão', 'message': str(e)}, jsonfile, ensure_ascii=False)
    exit(1)
