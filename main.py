# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv  # Carregar dotenv
import streamlit as st
import pandas as pd
from home import mostrar_home
from graficos import mostrar_graficos
from auth import get_user_hospitals  # Importa a função para obter hospitais
from mapeamento import mapeamento_hospital  # Importa o mapeamento de hospitais

# Caminhos dos arquivos
dados_csv = "/tmp/dados.csv"
data_work_csv = "/tmp/data_work.csv"

# 🔄 **Executar export.py para baixar os dados**
st.write("🔄 Obtendo dados da API...")
subprocess.run(["python", "export.py"], check=True)

# Esperar um pouco para garantir que o arquivo foi criado
time.sleep(2)

# 🚨 **Verificar se `dados.csv` foi gerado corretamente**
if not os.path.exists(dados_csv):
    st.error(f"❌ ERRO: {dados_csv} não foi gerado! Verifique `export.py`.")
    st.stop()

# 🔄 **Executar treatment.py para processar os dados**
st.write("🔄 Processando dados...")
subprocess.run(["python", "treatment.py"], check=True)

# 🚨 **Verificar se `data_work.csv` foi gerado corretamente**
if not os.path.exists(data_work_csv):
    st.error(f"❌ ERRO: {data_work_csv} não foi gerado! Verifique `treatment.py`.")
    st.stop()

# ✅ **Carregar os dados após processamento**
df = pd.read_csv(data_work_csv, encoding='utf-8')
st.write("✅ Dados carregados com sucesso!")
# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Acessar as variáveis do .env
admin_password = os.getenv("ADMIN_PASSWORD")
marcelo_password = os.getenv("MARCELO_PASSWORD")
rafael_password = os.getenv("RAFAEL_PASSWORD")
santa_casa_password = os.getenv("SANTA_CASA_PASSWORD")
inc_password = os.getenv("INC_PASSWORD")
nacoes_password = os.getenv("NACOES_PASSWORD")
instituto_password = os.getenv("INSTITUTO_PASSWORD")
vita_batel_password = os.getenv("VITA_BATEL_PASSWORD")
sao_rafael_password = os.getenv("SAO_RAFAEL_PASSWORD")
sao_lucas_password = os.getenv("SAO_LUCAS_PASSWORD")

# Configurar a página
st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed",
    page_title="CAPDT",
    page_icon="assets/favicon-qualidade.png",
)

# Mapeamento de logos de hospitais
logo_hospital = {
    "Santa Casa": "assets/santa_casa.png",
    "INC": "assets/inc.png",
    "Hospital das Nações": "assets/nacoes.png",
    "Instituto de Medicina": "assets/instituto.png",
    "Vita Batel": "assets/vita_batel.png",
    "São Rafael": "assets/sao_rafael.png",
    "São Lucas": "assets/sao_lucas.png"
}

# Inicializa o estado da sessão se necessário
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'page' not in st.session_state:
    st.session_state.page = ""

# Função de login usando credenciais do .env
def check_credentials(username, password):
    credentials = {
        "admin": {
            "password": admin_password,
            "hospitals": ["Santa Casa", "INC", "Hospital das Nações", "Instituto de Medicina", "Vita Batel",
                          "São Rafael", "São Lucas"]
        },
        "marcelo.martins@cepeti.com.br": {
            "password": marcelo_password,
            "hospitals": ["Santa Casa", "INC", "Hospital das Nações", "Instituto de Medicina", "Vita Batel",
                          "São Rafael", "São Lucas"]
        },
        "rafael.viegas@cepeti.com.br": {
            "password": rafael_password,
            "hospitals": ["Santa Casa", "INC", "Hospital das Nações", "Instituto de Medicina", "Vita Batel",
                          "São Rafael", "São Lucas"]
        },
        "santa.casa@cepeti.com.br": {
            "password": santa_casa_password,
            "hospitals": ["Santa Casa"]
        },
        "inc@cepeti.com.br": {
            "password": inc_password,
            "hospitals": ["INC"]
        },
        "nacoes@cepeti.com.br": {
            "password": nacoes_password,
            "hospitals": ["Hospital das Nações"]
        },
        "instituto.medicina@cepeti.com.br": {
            "password": instituto_password,
            "hospitals": ["Instituto de Medicina"]
        },
        "vita.batel@cepeti.com.br": {
            "password": vita_batel_password,
            "hospitals": ["Vita Batel"]
        },
        "sao.rafael@cepeti.com.br": {
            "password": sao_rafael_password,
            "hospitals": ["São Rafael"]
        },
        "sao.lucas@cepeti.com.br": {
            "password": sao_lucas_password,
            "hospitals": ["São Lucas"]
        }
    }

    # Verifica se o usuário existe e a senha está correta
    user_data = credentials.get(username)
    if user_data and user_data["password"] == password:
        return True
    return False

def on_login():
    try:
        if check_credentials(st.session_state.username, st.session_state.password):
            st.session_state.logged_in = True
            st.session_state.page = "Home"
            st.session_state.hospitals = get_user_hospitals(st.session_state.username)
            st.success(f"Bem vindo, {st.session_state.username}!")
        else:
            st.error("Usuário ou senha incorretos")
    except Exception as e:
        st.error(f"Erro durante o login: {e}")

def login():
    st.image("assets/logo-qualidade.png", width=300)
    st.write("")
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form", clear_on_submit=True):
                st.subheader("Login")
                username = st.text_input("Usuário", placeholder="Digite seu nome de usuário", key="username")
                password = st.text_input("Senha", type="password", placeholder="Digite sua senha", key="password")
                st.form_submit_button("Entrar", on_click=on_login)

 
def mostrar_creditos():
    st.title("Equipe de desenvolvimento")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("assets/membro1.png", width=200)
        st.subheader("**Marcelo José Martins Júnior**")
        st.write(" Gerente de Dados - CEPETI")
    with col3:
        st.image("assets/membro2.png", width=200)
        st.subheader("**Rafael Lucindro Viegas**")
        st.write("Desenvolvedor Full-Stack - CEPETI")

def main():
    if st.session_state.logged_in:
        st.sidebar.image("assets/logo-qualidade.png", width=250)
        st.sidebar.title("Menu")
        hospital_selecionado = st.sidebar.radio("Selecione uma página",
                                                ["Home"] + st.session_state.hospitals + ["Créditos"])
        if hospital_selecionado == "Home":
            col1, col2 = st.columns([6, 1])
            with col1:
                st.markdown("")
            with col2:
                if st.button("Logout"):
                    st.session_state.logged_in = False
                    st.session_state.username = None
            mostrar_home()
        elif hospital_selecionado == "Créditos":
            mostrar_creditos()
        else:
            logo_path = logo_hospital.get(hospital_selecionado)
            if logo_path:
                st.image(logo_path, width=300)
            utis_disponiveis = mapeamento_hospital[hospital_selecionado]
            uti_selecionada = st.selectbox("Selecione uma UTI", utis_disponiveis)
            if uti_selecionada:
                df = pd.read_csv('data_work.csv', encoding='utf-8')
                mostrar_graficos(df, uti_selecionada)
    else:
        login()

if __name__ == "__main__":
    main()
