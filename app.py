import streamlit as st
import requests
from bs4 import BeautifulSoup

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

@st.cache_data(ttl=3600)
def buscar_ataques_pokemondb(nome_pokemon):
    nome_formatado = nome_pokemon.lower()
    url = f"https://pokemondb.net/pokedex/{nome_formatado}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    resposta = requests.get(url, headers=headers)
    ataques_por_metodo = {
        'Por Nível': [],
        'Por MT / HM (Máquina)': [],
        'Por Ovo (Breeding)': [],
        'Por Tutor': []
    }
    
    if resposta.status_code != 200:
        return ataques_por_metodo
        
    soup = BeautifulSoup(resposta.text, 'html.parser')
    
    # Mapeamento das tabelas do PokémonDB baseadas nos títulos das seções
    tabelas = soup.find_all('table', {'class': 'data-table'})
    
    for tabela in tabelas:
        # Tenta achar o título anterior para saber qual é o método
        h3 = tabela.find_previous('h3')
        if not h3:
            continue
        titulo_secao = h3.text.lower()
        
        # Identifica a categoria
        categoria = None
        if 'level' in titulo_secao:
            categoria = 'Por Nível'
        elif 'machine' in titulo_secao or 'tm' in titulo_secao:
            categoria = 'Por MT / HM (Máquina)'
        elif 'egg' in titulo_secao:
            categoria = 'Por Ovo (Breeding)'
        elif 'tutor' in titulo_secao:
            categoria = 'Por Tutor'
            
        if not categoria:
            continue
            
        linhas = tabela.find_all('tr')
        for linha in linhas[1:]:  # Pula o cabeçalho
            colunas = linha.find_all('td')
            if len(colunas) >= 2:
                if categoria == 'Por Nível':
                    nivel = colunas[0].text.strip()
                    nome_ataque = colunas[1].text.strip()
                    if nivel and nome_ataque:
                        item = f"{nome_ataque} (Nível {nivel})"
                        if item not in ataques_por_metodo[categoria]:
                            ataques_por_metodo[categoria].append(item)
                else:
                    nome_ataque = colunas[0].text.strip()
                    if nome_ataque and nome_ataque not in ataques_por_metodo[categoria]:
                        ataques_por_metodo[categoria].append(nome_ataque)
                        
    return ataques_por_metodo

def mostrar_detalhes_pokemon(poke_id_ou_nome):
    url = f"https://pokeapi.co/api/v2/pokemon/{poke_id_ou_nome}"
    resposta = requests.get(url)
    
    if resposta.status_code == 200:
        dados = resposta.json()
        nome_original = dados['name']
        nome = nome_original.capitalize()
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
        st.markdown("### ⚔️ Ataques por Forma (PokémonDB)")
        
        with st.spinner("Buscando ataques direto do PokémonDB..."):
            movimentos_por_metodo = buscar_ataques_pokemondb(nome_original)
            
        abas_metodos = st.tabs(list(movimentos_por_metodo.keys()))
        
        for tab, (metodo, lista_ataques) in zip(abas_metodos, movimentos_por_metodo.items()):
            with tab:
                if lista_ataques:
                    if metodo == 'Por Nível':
                        lista_ataques_ordenados = sorted(lista_ataques, key=lambda x: int(x.split('Nível ')[1].split(')')[0]) if 'Nível ' in x else 0)
                        for atq in lista_ataques_ordenados:
                            st.write(f"• {atq}")
                    else:
                        for atq in sorted(lista_ataques):
                            st.write(f"• {atq}")
                else:
                    st.write("Nenhum ataque encontrado nesta categoria para este Pokémon.")
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
