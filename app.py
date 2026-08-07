import streamlit as st
import requests

st.set_page_config(page_title="Pokédex Oficial", page_icon="🔴", layout="centered")

st.title("🔴 Pokédex Interativa")
st.write("Explore os Pokémon por nome, letras específicas ou selecione uma geração!")

# Cache para carregar a lista de todos os nomes apenas uma vez (deixa o site muito mais rápido)
@st.cache_data
def carregar_todos_pokemons():
    url = "https://pokeapi.co/api/v2/pokemon?limit=1025"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        return resposta.json()['results']
    return []

todos_os_pokemons = carregar_todos_pokemons()

aba1, aba2 = st.tabs(["🔍 Pesquisa por Nome ou Letras", "🌍 Pesquisar por Geração"])

with aba1:
    termo_busca = st.text_input("Digite o nome ou letras do Pokémon (ex: 'cha', 'pikachu', 'saur'):").lower().strip()

    if termo_busca:
        # Filtra na lista todos os Pokémon que contêm as letras digitadas
        pokemons_filtrados = [p for p in todos_os_pokemons if termo_busca in p['name']]

        if pokemons_filtrados:
            st.info(f"Encontrados {len(pokemons_filtrados)} Pokémon com o termo '{termo_busca}':")
            
            # Exibe os resultados em mini cards organizados em colunas
            cols = st.columns(3)
            for idx, poke in enumerate(pokemons_filtrados[:30]): # Mostra até 30 resultados para não travar a tela
                p_nome = poke['name'].capitalize()
                p_id = poke['url'].split('/')[-2]
                
                with cols[idx % 3]:
                    st.markdown(f"**#{p_id}** - {p_nome}")
                    img_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{p_id}.png"
                    st.image(img_url, width=90)
            
            if len(pokemons_filtrados) > 30:
                st.warning("Mostrando apenas os primeiros 30 resultados. Seja mais específico na busca se necessário!")
        else:
            st.error("Nenhum Pokémon encontrado com essas letras.")

with aba2:
    st.subheader("Escolha a Geração")
    
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
                species_list = sorted(dados_gen['pokemon_species'], key=lambda x: int(x['url'].split('/')[-2]))
                
                st.success(f"Encontrados {len(species_list)} Pokémon nesta geração!")
                
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
