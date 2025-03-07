import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('API_TOKEN')
url = 'https://cepetiredcap.com.br/api/'
if not token:
    raise ValueError("Token da API não encontrado nas variáveis de ambiente.")

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

try:
    # Solicitação à API
    response = requests.post(url, data=data, timeout=200)

    print('HTTP Status:', response.status_code)

    if response.status_code == 403:
        error_message = json.loads(response.text).get('error', '')
        print(f'Erro de permissão: {error_message}')

        with open('erro.json', 'w', encoding='utf-8') as jsonfile:
            json.dump({'error': 'Erro de permissão', 'message': error_message}, jsonfile, ensure_ascii=False)
        exit()

    elif response.status_code == 200:
        with open('dados.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csvfile.write(response.text)
        print('Dados salvos com sucesso em "dados.csv".')

    else:
        print('Falha na solicitação à API. Código de status HTTP:', response.status_code)
        with open('erro.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(
                {'error': 'Falha na solicitação à API', 'status_code': response.status_code, 'message': response.text},
                jsonfile, ensure_ascii=False)

except requests.exceptions.Timeout:
    print('Ocorreu um timeout na solicitação.')
    with open('erro.json', 'w', encoding='utf-8') as jsonfile:
        json.dump({'error': 'Timeout', 'message': 'A solicitação excedeu o tempo limite'}, jsonfile, ensure_ascii=False)

except requests.exceptions.RequestException as e:
    print(f'Ocorreu um erro de conexão: {e}')
    with open('erro.json', 'w', encoding='utf-8') as jsonfile:
        json.dump({'error': 'Erro de conexão', 'message': str(e)}, jsonfile, ensure_ascii=False)
