import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os

# Carrega as variaveis de ambiente do .env
load_dotenv()

if 'config' not in st.session_state:
    st.session_state.config = {
        'BASE_URL': os.getenv('BASE_URL', 'http://localhost:3001/api/v1'),
        'CHAVE_API': os.getenv('CHAVE_API', '')
    }

# Funções para interagir com a API
def fazer_requisicao(endpoint, metodo='GET', dados=None):
    url = f"{st.session_state.config['BASE_URL']}/{endpoint}"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {st.session_state.config['CHAVE_API']}"
    }
    try:
        if metodo == 'GET':
            resposta = requests.get(url, headers=headers)
        elif metodo == 'POST':
            resposta = requests.post(url, json=dados, headers=headers)
        resposta.raise_for_status()
        return resposta.json()
    except requests.RequestException as e:
        st.error(f"Erro na requisição: {str(e)}")
        return None

def obter_workspaces():
    resposta = fazer_requisicao('workspaces')
    if resposta and isinstance(resposta, list):
        return resposta
    elif resposta and isinstance(resposta, dict):
        return resposta.get('workspaces', [])
    else:
        st.error("Formato de resposta inesperado ao obter workspaces")
        return []

def fazer_pergunta_llm(workspace, pergunta):
    dados = {
        "message": pergunta,
        "mode": "chat"
    }
    return fazer_requisicao(f'workspace/{workspace}/chat', metodo='POST', dados=dados)

# Interface Streamlit
st.set_page_config(page_title="IA Waukesha Agente de Suporte", layout="wide")
st.title("IA Waukesha Agente de Suporte")

# Sidebar para seleção de workspace e upload de documentos
with st.sidebar:
    st.header("Configurações")
    workspaces = obter_workspaces()
    if workspaces:
        workspace_nomes = [w.get('name', str(w)) for w in workspaces]
        workspace_selecionado = st.selectbox("Selecione o Workspace", workspace_nomes)
    else:
        st.error("Não foi possível obter a lista de workspaces.")

# Área principal
col1 = st.columns(1)[0]

with col1:
    st.subheader("Chat com IA")
    pergunta_usuario = st.text_area("Faça sua pergunta:")
    if st.button('Enviar'):
        if pergunta_usuario and workspace_selecionado:
            with st.spinner('Processando sua pergunta...'):
                resposta = fazer_pergunta_llm(workspace_selecionado, pergunta_usuario)
                if resposta:
                    st.write(resposta.get('textResponse', 'Resposta não encontrada.'))
                else:
                    st.error("Não foi possível obter uma resposta.")
        else:
            st.warning("Por favor, selecione um workspace e digite uma pergunta.")

# Área de configurações avançadas
with st.expander("Configurações Avançadas"):
    nova_url_api = st.text_input("URL da API", value=st.session_state.config['BASE_URL'])
    nova_chave_api = st.text_input("Chave da API", value=st.session_state.config['CHAVE_API'], type="password")
    if st.button("Atualizar Configurações"):
        st.session_state.config['BASE_URL'] = nova_url_api
        st.session_state.config['CHAVE_API'] = nova_chave_api
        st.success("Configurações atualizadas com sucesso!")