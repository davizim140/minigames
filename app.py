import streamlit as st
import requests

st.set_page_config(page_title="Pokédex Oficial", page_icon="🔴", layout="centered")

st.title("🔴 Pokédex Interativa")
st.write("Pesquise por qualquer Pokémon ou navegue pelas informações oficiais!")

# Caixa de pesquisa para o usuário digitar o nome ou número do Pokémon
nome_ou_id = st.text_input("Digite o nome ou ID do Pokémon (ex: pikachu, charizard, 1):", value="pikachu").lower().strip()

if nome_ou_id:
    # URL da PokeAPI oficial
    url = f"https://pokeapi.co/api/v2/pokemon/{nome_ou_id}"
    
    try:
        resposta = requests.get(url)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            
            # Extraindo informações principais
            nome = dados['name'].capitalize()
            id_pkmn = dados['id']
            peso = dados['weight'] / 10  # Convertendo para kg
            altura = dados['height'] / 10 # Convertendo para metros
            
            # Imagem oficial do Pokémon
            imagem = dados['sprites']['other']['official-artwork']['front_default']
            if not imagem:
                imagem = dados['sprites']['front_default']
                
            # Tipos
            tipos = [t['type']['name'].capitalize() for t in dados['types']]
            
            # Layout em colunas
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if imagem:
                    st.image(imagem, width=200)
                st.markdown(f"### **#{id_pkmn} - {nome}**")
                st.write(f"**Tipo(s):** {', '.join(tipos)}")
                st.write(f"**Altura:** {altura} m")
                st.write(f"**Peso:** {peso} kg")
                
            with col2:
                st.markdown("### 📊 Status de Batalha")
                stats = dados['stats']
                for s in stats:
                    nome_stat = s['stat']['name'].upper()
                    valor_stat = s['base_stat']
                    st.progress(min(valor_stat, 100), text=f"{nome_stat}: {valor_stat}")
                    
            # Habilidades
            st.markdown("---")
            st.markdown("### ⚡ Habilidades")
            habilidades = [h['ability']['name'].capitalize() for h in dados['abilities']]
            st.write(", ".join(habilidades))
            
        else:
            st.error("Pokémon não encontrado! Verifique o nome ou número digitado.")
            
    except Exception as e:
        st.error(f"Erro ao conectar com a API de Pokémon: {e}")
