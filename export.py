import os
import requests
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()
token = os.getenv('API_TOKEN')

# Verificar se o token foi carregado
if not token:
    raise ValueError("Token da API não encontrado. Verifique se o arquivo .env está correto.")

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

# Caminhos para salvar os arquivos
save_path = "/tmp/dados.csv"
error_path = "/tmp/erro.json"

try:
    # Solicitação à API
    response = requests.post(url, data=data, timeout=200)

    print('HTTP Status:', response.status_code)

    if response.status_code == 403:
        try:
            error_message = json.loads(response.text).get('error', 'Erro desconhecido.')
        except json.JSONDecodeError:
            error_message = "Erro desconhecido (resposta não era um JSON válido)."

        print(f'Erro de permissão: {error_message}')

        with open(error_path, 'w', encoding='utf-8') as jsonfile:
            json.dump({'error': 'Erro de permissão', 'message': error_message}, jsonfile, ensure_ascii=False)

        exit()

    elif response.status_code == 200:
        # Salvar os dados no arquivo CSV
        with open(save_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvfile.write(response.text)
        print(f'Dados salvos com sucesso em "{save_path}".')

    else:
        print('Falha na solicitação à API. Código de status HTTP:', response.status_code)

        with open(error_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(
                {
                    'error': 'Falha na solicitação à API',
                    'status_code': response.status_code,
                    'message': response.text
                },
                jsonfile,
                ensure_ascii=False
            )

except requests.exceptions.Timeout:
    print('Ocorreu um timeout na solicitação.')
    with open(error_path, 'w', encoding='utf-8') as jsonfile:
        json.dump({'error': 'Timeout', 'message': 'A solicitação excedeu o tempo limite'}, jsonfile, ensure_ascii=False)

except requests.exceptions.RequestException as e:
    print(f'Ocorreu um erro de conexão: {e}')
    with open(error_path, 'w', encoding='utf-8') as jsonfile:
        json.dump({'error': 'Erro de conexão', 'message': str(e)}, jsonfile, ensure_ascii=False)
