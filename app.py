import streamlit as st
import requests

st.set_page_config(page_title="Pokédex Oficial", page_icon="🔴", layout="centered")

st.title("🔴 Pokédex Interativa")
st.write("Pesquise por nome, letras ou geração, e clique para ver os detalhes e ataques!")

@st.cache_data
def carregar_todos_pokemons():
    url = "https://pokeapi.co/api/v2/pokemon?limit=1025"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        return resposta.json()['results']
    return []

todos_os_pokemons = carregar_todos_pokemons()

def mostrar_detalhes_pokemon(poke_id_ou_nome):
    url = f"https://pokeapi.co/api/v2/pokemon/{poke_id_ou_nome}"
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
        
        if st.button("⬅️ Voltar para a Pesquisa"):
            st.session_state.pokemon_selecionado = None
            st.rerun()
            
        st.markdown(f"## 🌟 #{id_pkmn} - {nome}")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if imagem:
                st.image(imagem, width=220)
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
        st.markdown("### ⚔️ Ataques por Nível (A partir do Nível 2)")
        
        movimentos_nivel = []
        for m in dados['moves']:
            for details in m['version_group_details']:
                if details['move_learn_method']['name'] == 'level-up':
                    lvl = details['level_learned_at']
                    if lvl > 1:
                        movimentos_nivel.append({
                            'nivel': lvl,
                            'nome': m['move']['name'].replace('-', ' ').capitalize()
                        })
        
        movimentos_unicos = {}
        for mov in movimentos_nivel:
            nome_mov = mov['nome']
            nivel_mov = mov['nivel']
            if nome_mov not in movimentos_unicos or nivel_mov < movimentos_unicos[nome_mov]:
                movimentos_unicos[nome_mov] = nivel_mov
                
        movimentos_ordenados = sorted([{'nome': k, 'nivel': v} for k, v in movimentos_unicos.items()], key=lambda x: x['nivel'])
        
        if movimentos_ordenados:
            dados_tabela = [{"Nível": m['nivel'], "Ataque": m['nome']} for m in movimentos_ordenados]
            st.dataframe(dados_tabela, use_container_width=True, hide_index=True)
        else:
            st.write("Nenhum ataque por nível superior encontrado para este Pokémon.")
    else:
        st.error("Erro ao carregar os dados do Pokémon.")

if "pokemon_selecionado" not in st.session_state:
    st.session_state.pokemon_selecionado = None

if "geracao_atual" not in st.session_state:
    st.session_state.geracao_atual = None

if st.session_state.pokemon_selecionado:
    mostrar_detalhes_pokemon(st.session_state.pokemon_selecionado)
else:
    aba1, aba2 = st.tabs(["🔍 Pesquisa por Nome ou Letras", "🌍 Pesquisar por Geração"])

    with aba1:
        termo_busca = st.text_input("Digite o nome ou letras do Pokémon (ex: 'cha', 'pikachu'):").lower().strip()

        if termo_busca:
            pokemons_filtrados = [p for p in todos_os_pokemons if termo_busca in p['name']]

            if pokemons_filtrados:
                st.info(f"Encontrados {len(pokemons_filtrados)} Pokémon. Clique em um para ver os detalhes:")
                
                cols = st.columns(3)
                for idx, poke in enumerate(pokemons_filtrados[:30]):
                    p_nome = poke['name'].capitalize()
                    p_id = poke['url'].split('/')[-2]
                    
                    with cols[idx % 3]:
                        st.markdown(f"**#{p_id}** - {p_nome}")
                        img_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{p_id}.png"
                        st.image(img_url, width=80)
                        if st.button(f"Ver Detalhes", key=f"btn_nome_{p_id}_{idx}"):
                            st.session_state.pokemon_selecionado = p_id
                            st.rerun()
            else:
                st.error("Nenhum Pokémon encontrado.")

    with aba2:
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
            with st.spinner("Buscando Pokémon..."):
                url_gen = f"https://pokeapi.co/api/v2/generation/{gen_id}"
                resp_gen = requests.get(url_gen)
                
                if resp_gen.status_code == 200:
                    species_list = sorted(resp_gen.json()['pokemon_species'], key=lambda x: int(x['url'].split('/')[-2]))
                    st.session_state.geracao_atual = species_list
                else:
                    st.error("Erro ao carregar os dados da geração.")

        if st.session_state.geracao_atual:
            st.success(f"Encontrados {len(st.session_state.geracao_atual)} Pokémon!")
            cols = st.columns(3)
            for idx, pokemon in enumerate(st.session_state.geracao_atual):
                p_nome = pokemon['name'].capitalize()
                p_id = pokemon['url'].split('/')[-2]
                
                with cols[idx % 3]:
                    st.markdown(f"**#{p_id}** - {p_nome}")
                    img_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{p_id}.png"
                    st.image(img_url, width=90)
                    if st.button(f"Ver Detalhes", key=f"btn_gen_{p_id}_{idx}"):
                        st.session_state.pokemon_selecionado = p_id
                        st.rerun()
