import streamlit as st
import random

st.set_page_config(page_title="Arcade de Minijogos", page_icon="🎮", layout="centered")

st.title("🎮 Fliperama da Família")
st.write("Escolha um minijogo abaixo e divirta-se direto pelo navegador!")

# Inicializa placares e estados globais
if "cliques_p1" not in st.session_state:
    st.session_state.cliques_p1 = 0
if "cliques_p2" not in st.session_state:
    st.session_state.cliques_p2 = 0

if "secreto" not in st.session_state:
    st.session_state.secreto = random.randint(1, 20)
    st.session_state.tentativas = 0

if "placar_jokempo" not in st.session_state:
    st.session_state.placar_jokempo = {"voce": 0, "ia": 0}

# Abas para separar os jogos
aba1, aba2, aba3, aba4 = st.tabs(["🖱️ Batalha de Cliques", "🔢 Adivinhe o Número", "✂️ Jo-Ken-Pô", "🧠 Quiz Rápido"])

with aba1:
    st.subheader("Batalha de Cliques (2 Jogadores)")
    st.write("Quem clicar mais rápido no seu botão ganha pontos!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Jogador 1")
        if st.button("🔴 Clique Aqui (P1)", key="btn_c1"):
            st.session_state.cliques_p1 += 1
            
    with col2:
        st.markdown("### Jogador 2")
        if st.button("🔵 Clique Aqui (P2)", key="btn_c2"):
            st.session_state.cliques_p2 += 1
            
    st.markdown("---")
    st.write(f"**Placar:** P1: `{st.session_state.cliques_p1}` x P2: `{st.session_state.cliques_p2}`")
    
    if st.button("🔄 Zerar Placar de Cliques"):
        st.session_state.cliques_p1 = 0
        st.session_state.cliques_p2 = 0
        st.rerun()

with aba2:
    st.subheader("Adivinhe o Número Secreto")
    st.write("Tente adivinhar um número de **1 a 20** que estou pensando!")
    
    palpite = st.number_input("Digite seu palpite:", min_value=1, max_value=20, step=1, key="input_adv")
    
    if st.button("Testar Palpite"):
        st.session_state.tentativas += 1
        if palpite == st.session_state.secreto:
            st.balloons()
            st.success(f"🎉 Acertou em {st.session_state.tentativas} tentativas! O número era {st.session_state.secreto}.")
            st.session_state.secreto = random.randint(1, 20)
            st.session_state.tentativas = 0
        elif palpite < st.session_state.secreto:
            st.warning("📈 O número secreto é **maior**!")
        else:
            st.warning("📉 O número secreto é **menor**!")

with aba3:
    st.subheader("Jo-Ken-Pô (Pedra, Papel e Tesoura)")
    
    escolha_usuario = st.radio("Escolha sua jogada:", ["Pedra", "Papel", "Tesoura"], key="radio_jkp")
    
    if st.button("Jogar contra a Máquina"):
        opcoes = ["Pedra", "Papel", "Tesoura"]
        escolha_ia = random.choice(opcoes)
        
        st.write(f"🤖 A IA escolheu: **{escolha_ia}**")
        
        if escolha_usuario == escolha_ia:
            st.info("Empate!")
        elif (
            (escolha_usuario == "Pedra" and escolha_ia == "Tesoura") or
            (escolha_usuario == "Papel" and escolha_ia == "Pedra") or
            (escolha_usuario == "Tesoura" and escolha_ia == "Papel")
        ):
            st.success("Você venceu esta rodada! 🎉")
            st.session_state.placar_jokempo["voce"] += 1
        else:
            st.error("A IA venceu! 😢")
            st.session_state.placar_jokempo["ia"] += 1
            
        st.write(f"Placar -> Você: {st.session_state.placar_jokempo['voce']} | IA: {st.session_state.placar_jokempo['ia']}")

with aba4:
    st.subheader("Quiz Rápido de Cultura Pop e Jogos")
    
    pergunta = "Qual destes jogos o criador deste site mais joga/conhece bem?"
    opcoes = ["Dark Souls 2", "Tetris clássico", "Campo Minado", "Pac-Man"]
    
    resposta_usuario = st.radio(pergunta, opcoes, key="quiz_geral")
    
    if st.button("Enviar Resposta do Quiz"):
        if resposta_usuario == "Dark Souls 2":
            st.balloons()
            st.success("Exato! Mestre dos games difíceis.")
        else:
            st.error("Errou! Tente de novo.")
