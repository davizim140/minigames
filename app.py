import streamlit as st
import requests

st.set_page_config(page_title="Pokédex Oficial", page_icon="🔴", layout="centered")

st.title("🔴 Pokédex Interativa")
st.write("Explore o mundo Pokémon por nome ou selecione uma geração inteira!")

# Sistema de Abas para organizar a pesquisa
aba1, aba2 = st.tabs(["🔍 Pesquisar por Nome/ID", "🌍 Pesquisar por Geração"])

with aba1:
    nome_ou_id = st.text_input("Digite o nome ou ID do Pokémon:", value="pikachu").lower().strip()

    if nome_ou_id:
        url = f"https://pokeapi.co/api/v2/pokemon/{nome_ou_id}"
        try:
            resposta = requests.get(url)
            if resposta.status_code == 200:
                dados = resposta.json()
                nome = dados['name'].capitalize()
                id_pkmn = dados['id']
                peso = dados['weight'] / 10
                altura = dados['height'] / 10
                
                imagem = dados['sprites']['other']['official-artwork']['front_default']
                if not imagem:
                    imagem = dados['sprites']['front_default']
                    
                tipos = [t['type']['name'].capitalize() for t in dados['types']]
                
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
                    for s in dados['stats']:
                        nome_stat = s['stat']['name'].upper()
                        valor_stat = s['base_stat']
                        st.progress(min(valor_stat, 100), text=f"{nome_stat}: {valor_stat}")
                
                st.markdown("---")
                st.markdown("### ⚡ Habilidades")
                habilidades = [h['ability']['name'].capitalize() for h in dados['abilities']]
                st.write(", ".join(habilidades))
            else:
                st.error("Pokémon não encontrado!")
        except Exception as e:
            st.error(f"Erro ao conectar com a API: {e}")

with aba2:
    st.subheader("Escolha a Geração")
    
    # Dicionário com as gerações oficiais da PokeAPI
    geracoes = {
        "Geração 1 (Kanto - 1 a 151)": 1,
        "Geração 2 (Johto - 152 a 251)": 2,
        "Geração 3 (Hoenn - 252 a 386)": 3,
        "Geração 4 (Sinnoh - 387 a 493)": 4,
        "Geração 5 (Unova - 494 a 649)": 5,
        "Geração 6 (Kalos - 650 a 721)": 6,
        "Geração 7 (Alola - 722 a 809)": 7,
        "Geração 8 (Galar - 810 a 905)": 8,
        "Geração 9 (Paldea - 906 a 1025)": 9
    }
    
    gen_escolhida = st.selectbox("Selecione a região/geração:", list(geracoes.keys()))
    gen_id = geracoes[gen_escolhida]
    
    if st.button("Carregar Pokémon da Geração"):
        with st.spinner("Buscando Pokémon da região..."):
            url_gen = f"https://pokeapi.co/api/v2/generation/{gen_id}"
            resp_gen = requests.get(url_gen)
            
            if resp_gen.status_code == 200:
                dados_gen = resp_gen.json()
                # Ordena os Pokémon pelo ID oficial da Pokédex
                species_list = sorted(dados_gen['pokemon_species'], key=lambda x: int(x['url'].split('/')[-2]))
                
                st.success(f"Encontrados {len(species_list)} Pokémon nesta geração!")
                
                # Exibe em grade (grid de 3 colunas)
                cols = st.columns(3)
                for idx, pokemon in enumerate(species_list):
                    p_nome = pokemon['name'].capitalize()
                    p_id = pokemon['url'].split('/')[-2]
                    
                    with cols[idx % 3]:
                        st.markdown(f"**#{p_id}** - {p_nome}")
                        img_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{p_id}.png"
                        st.image(img_url, width=100)
            else:
                st.error("Erro ao carregar os dados da geração.")
