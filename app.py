import streamlit as st
import requests
import uuid

RASA_URL = 'http://localhost:5005/webhooks/rest/webhook'

# config da página no navegador (Título da aba)
st.set_page_config(page_title="Biblioteca")
st.title("Biblioteca Comunitária")
st.caption("Conectado ao Rasa open source") # legenda informativa (subtitulo)

# inicialização do estado da sessão (memória do navegador)

# verifica se já existe um ID de usuário nesta sessão, caso não, cria um novo uuid
if 'sender_id' not in st.session_state:
    st.session_state.sender_id = str(uuid.uuid4())

# verifica se a lista de histórico de mensagens existe, caso não, inicia uma lista vazia
if 'messages' not in st.session_state:
    st.session_state.messages = []

# exibição do histórico 

# percorre todas as mensagens armazenadas e as renderiza na tela conforme o papel (usuário ou bot)
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# campo de entrada de texto

# cria caixa de texto no rodapé. o operador := captura o texto e verifica se não está vazio
if prompt := st.chat_input('Digite sua mensagem'):
    # adiciona a mensagem digitada pelo usuário ao histórico da sessão
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    # renderiza a mensagem do usuário imediatamente no chat
    with st.chat_message('user'):
        st.markdown(prompt)

# comunicação com o servidor do rasa
    try:
        # envia uma requisição para o rasa com o id do remetente e o texto da mensagem
        response = requests.post(
            RASA_URL,
            json={'sender': st.session_state.sender_id, 'message': prompt},
            timeout=30 # espera a resposta por no máximo 5 segundos
        )

        # converte a resposta do servidor em uma lista de objetos python
        bot_msgs = response.json()

        # se o bot retornar mensagens, percorre a lista
        if bot_msgs:
            for bot_msg in bot_msgs:
                text = bot_msg.get('text', '') # extrai o campo de texto da resposta
                if text:
                    # adiciona a resposta do assistente ao histórico da sessão
                    st.session_state.messages.append({'role': 'assistant', 'content': text})
                    # renderiza resposta assistente visualmente no chat
                    with st.chat_message('assistant'):
                        st.markdown(text)
        else:
            # caso o rasa retorne uma lista vazia
            st.session_state.messages.append({'role': 'assistant', 'content': '(Bot não respondeu)'})
            with st.chat_message('assistant'):
                st.markdown('(Bot não respondeu)')

    # tratamento de erros de conexão
    except requests.exceptions.ConnectionError:
        # exibe um alerta vermelho se o servidor do rasa estiver desligado
        st.error('Não foi possível conectar ao Rasa')
    except requests.exceptions.Timeout:
        # exibi um alerta se o rasa demorar a responder
        st.error('O Rasa demorou a responder...')

# botão para limpar a conversa

# botão limpa histórico
if st.button('Limpar Conversa'):
    st.session_state.messages = []
    st.session_state.sender_id = str(uuid.uuid4()) # gera um novo id
    st.rerun() # recarrega o app do streamlit para aplicar as mudanças visuais