import streamlit as st
from streamlit_lottie import st_lottie
import requests

# Função para carregar animação Lottie
def load_lottie_url (url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Função para mostrar a página principal
def mostrar_home ( ):
    # Carregar animação Lottie
    lottie_url = "https://lottie.host/96a1c4bf-1d7b-4f86-a0e5-2fe229091be3/MJWdTwFZlC.json"
    lottie_animation = load_lottie_url(lottie_url)

    # Centralizar o conteúdo
    st.markdown("""
        <div style="text-align: center;"> 
            <h1>CAPTURE DATA</h1>
        </div>
        <div style="text-align: justified;">
            <h4>Bem-vindo ao CAPDT, uma plataforma de visualização e análise de dados hospitalares.</h4>
            <h4>Navegue por gráficos, matrizes e mapas detalhados para obter insights precisos sobre os dados da sua UTI.</h4>
        </div>
    """, unsafe_allow_html = True)

    # Verificar se a animação foi carregada corretamente
    if lottie_animation:
        st_lottie(lottie_animation, height = 300, key = "animation")
    else:
        st.error("Erro ao carregar a animação. Por favor, tente novamente mais tarde.")


# Chama a função para mostrar o conteúdo da página principal
if __name__ == "__main__":
    mostrar_home()
