import streamlit as st

st.set_page_config(page_title="Arcade Multiplayer Streamlit", page_icon="🎮", layout="centered")

# Inicializa o estado global da partida (simulando uma sala compartilhada)
if "pontos_jogador1" not in st.session_state:
    st.session_state.pontos_jogador1 = 0
if "pontos_jogador2" not in st.session_state:
    st.session_state.pontos_jogador2 = 0
if "turno" not in st.session_state:
    st.session_state.turno = "Jogador 1"

st.title("🎮 Mini Arena Multiplayer (Streamlit)")
st.write("Um espaço simples para jogar com a galera na mesma rede ou via link compartilhado!")

# Sistema de abas para escolher o minijogo
aba1, aba2 = st.tabs(["⚔️ Batalha de Cliques", "🧠 Quiz Rápido"])

with aba1:
    st.subheader("Batalha de Cliques")
    st.write("Quem clicar mais rápido ganha pontos!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Jogador 1")
        if st.button("🔴 Marcar Ponto (P1)", key="btn_p1"):
            st.session_state.pontos_jogador1 += 1
            st.success("Ponto para o Jogador 1!")
            
    with col2:
        st.markdown("### Jogador 2")
        if st.button("🔵 Marcar Ponto (P2)", key="btn_p2"):
            st.session_state.pontos_jogador2 += 1
            st.success("Ponto para o Jogador 2!")
            
    st.markdown("---")
    st.markdown(f"### 🏆 Placar Atual:")
    st.write(f"**Jogador 1:** {st.session_state.pontos_jogador1} pontos")
    st.write(f"**Jogador 2:** {st.session_state.pontos_jogador2} pontos")
    
    if st.button("🔄 Reinicar Jogo"):
        st.session_state.pontos_jogador1 = 0
        st.session_state.pontos_jogador2 = 0
        st.rerun()

with aba2:
    st.subheader("Quiz em Turnos")
    st.write(f"Vez de: **{st.session_state.turno}**")
    
    pergunta = "Qual linguagem usamos para criar este site?"
    opcoes = ["Python (Streamlit)", "JavaScript puro", "C++", "Java"]
    
    st.write(f"**Pergunta:** {pergunta}")
    escolha = st.radio("Escolha a resposta:", opcoes, key="resposta_quiz")
    
    if st.button("Enviar Resposta"):
        if escolha == "Python (Streamlit)":
            st.balloons()
            st.success(f"Acertou! Parabéns {st.session_state.turno}!")
        else:
            st.error("Errou feio!")
            
        # Alterna o turno
        st.session_state.turno = "Jogador 2" if st.session_state.turno == "Jogador 1" else "Jogador 1"
        st.rerun()
