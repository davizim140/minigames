import streamlit as st
import requests

st.set_page_config(page_title="Pokédex Oficial", page_icon="🔴", layout="centered")

st.title("🔴 Pokédex Interativa")
st.write("Pesquise por nome, letras, geração ou explore o conteúdo de Cobblemon, Pixelmon e Farms!")

@st.cache_data
def carregar_todos_pokemons():
    url = "https://pokeapi.co/api/v2/pokemon?limit=1025"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        return resposta.json()['results']
    return []

todos_os_pokemons = carregar_todos_pokemons()

@st.cache_data(ttl=3600)
def obter_cadeia_evolucao(especie_nome):
    url_especie = f"https://pokeapi.co/api/v2/pokemon-species/{especie_nome}"
    resp_especie = requests.get(url_especie)
    if resp_especie.status_code != 200:
        return []
    
    url_evolucao = resp_especie.json()['evolution_chain']['url']
    resp_evo = requests.get(url_evolucao)
    if resp_evo.status_code != 200:
        return []
    
    dados_evo = resp_evo.json()['chain']
    lista_etapas = []
    
    def processar_etapa(node):
        nome_poke = node['species']['name']
        id_poke = node['species']['url'].split('/')[-2]
        
        detalhes_metodo = []
        if node['evolution_details']:
            detalhe = node['evolution_details'][0]
            if detalhe['min_level']:
                detalhes_metodo.append(f"Nível {detalhe['min_level']}")
            if detalhe['item']:
                detalhes_metodo.append(f"Uso de {detalhe['item']['name'].replace('-', ' ').capitalize()}")
            if detalhe['trigger']:
                trigger_name = detalhe['trigger']['name']
                if trigger_name == 'trade':
                    detalhes_metodo.append("Troca")
                elif trigger_name == 'friendship':
                    detalhes_metodo.append("Felicidade alta")
        
        metodo_str = " / ".join(detalhes_metodo) if detalhes_metodo else "Condição especial"
        lista_etapas.append({'nome': nome_poke.capitalize(), 'id': id_poke, 'metodo': metodo_str})
        
        for proximo in node['evolves_to']:
            processar_etapa(proximo)
            
    processar_etapa(dados_evo)
    return lista_etapas

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
        st.markdown("### 🧬 Guia de Evolução")
        
        etapas_evolucao = obter_cadeia_evolucao(nome_original)
        if etapas_evolucao:
            cols_evo = st.columns(len(etapas_evolucao))
            for idx, evo in enumerate(etapas_evolucao):
                with cols_evo[idx]:
                    st.markdown(f"**#{evo['id']} - {evo['nome']}**")
                    img_evo = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{evo['id']}.png"
                    st.image(img_evo, width=100)
                    if idx > 0:
                        st.caption(f"⬆️ {evo['metodo']}")
                    else:
                        st.caption("Forma Base")
                        
                    if st.button("Ver", key=f"btn_evo_{evo['id']}"):
                        st.session_state.pokemon_selecionado = evo['id']
                        st.rerun()
        else:
            st.write("Este Pokémon não possui evoluções registradas ou ocorreu um erro ao buscar.")
    else:
        st.error("Erro ao carregar os dados do Pokémon.")

if "pokemon_selecionado" not in st.session_state:
    st.session_state.pokemon_selecionado = None

if "geracao_atual" not in st.session_state:
    st.session_state.geracao_atual = None

if st.session_state.pokemon_selecionado:
    mostrar_detalhes_pokemon(st.session_state.pokemon_selecionado)
else:
    aba1, aba2, aba3 = st.tabs(["🔍 Pesquisa por Nome ou Letras", "🌍 Pesquisar por Geração", "🟩 Cobblemon, Pixelmon & Farms"])

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

    with aba3:
        st.subheader("🟩 Mods de Minecraft & Guia de Farms")
        st.write("Explore dicas para Cobblemon/Pixelmon e tutoriais rápidos para as melhores farms do Minecraft!")

        sub_aba1, sub_aba2, sub_aba3 = st.tabs(["🟢 Cobblemon", "🟡 Pixelmon", "⚙️ Guia de Farms"])

        with sub_aba1:
            st.markdown("### 🟢 Sobre o Cobblemon")
            st.write("O **Cobblemon** é um mod moderno focado em integração total com o estilo visual do Minecraft.")
            st.markdown("#### 🛠️ Comandos Úteis")
            st.code("/cobblemon give [jogador] [pokemon]\n/spawnpokemon\n/pokegive", language="text")
            st.markdown("- [Site Oficial do Cobblemon](https://cobblemon.com/)")
            st.markdown("- [Wiki Oficial](https://wiki.cobblemon.com/)")

        with sub_aba2:
            st.markdown("### 🟡 Sobre o Pixelmon (Pixelmon Reforged)")
            st.write("O **Pixelmon** traz a experiência clássica dos jogos para o Minecraft com modelos 3D completos.")
            st.markdown("#### 🛠️ Comandos Úteis")
            st.code("/pokegive [jogador] [pokemon]\n/pokespawn [pokemon]\n/pokeheal", language="text")
            st.markdown("- [Site Oficial do Pixelmon](https://pixelmonmod.com/)")
            st.markdown("- [Wiki Oficial do Pixelmon](https://pixelmonmod.com/wiki/)")

        with sub_aba3:
            st.markdown("### ⚙️ Guia de Tutoriais de Farms no Minecraft")
            st.write("Dicas essenciais para construir as automações mais úteis no seu mundo survival:")

            st.markdown("#### 1. 🌾 Farm de Ferro Automática (Iron Farm)")
            st.write("- **Como funciona:** Utiliza um aldeão assustado por um zumbi para gerar Golems de Ferro continuamente.")
            st.write("- **Requisitos:** 3 Aldeões, 1 Zumbi com identificador (name tag), camas e uma plataforma de queda com lava e funis.")
            st.write("- **Dica:** Mantenha a farm longe de vilas ativas para evitar interferências no spawn dos Golems.")

            data_separator = "---"
            st.markdown(data_separator)

            st.markdown("#### 2. 🎣 Farm de pesca AFK")
            st.write("- **Como funciona:** Permite pescar automaticamente itens valiosos (como livros encantados, arcos e varas) sem esforço manual.")
            st.write("- **Requisitos:** Bloco de nota, gancho de armadilha, fio, água e um peso/macro para segurar o botão direito do mouse.")

            st.markdown(data_separator)

            st.markdown("#### 3. 🧪 Farm de XP e Ouro (Portal do Nether)")
            st.write("- **Como funciona:** Constrói portais gigantes no Nether linkados para gerar quantidades massivas de Piglins Zumbificados.")
            st.write("- **Vantagem:** Excelente para subir do nível 0 ao 30 em segundos e coletar pepitas/lingotes de ouro.")
