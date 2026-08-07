import streamlit as st
import requests

st.set_page_config(page_title="Pokédex Oficial", page_icon="🔴", layout="centered")

st.title("🔴 Pokédex Interativa")
st.write("Pesquise por nome, letras, geração ou explore o conteúdo de Cobblemon, Pixelmon e Farms completas!")

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
        st.markdown("### 🔴 Pokébola Sugerida (Cobblemon & Pixelmon)")
        st.info("💡 **Dica de Captura:** Nos mods de Minecraft, qualquer Pokébola padrão funciona para capturar a maioria dos Pokémon, mas tipos específicos ajudam dependendo do peso, velocidade ou ambiente do Pokémon!")
        
        if 'Water' in tipos or 'Água' in tipos:
            bola_sugerida = "Dive Ball / Lure Ball (Excelente para Pokémon aquáticos ou pescados)"
        elif peso > 200:
            bola_sugerida = "Heavy Ball (Ideal para Pokémon muito pesados)"
        elif any(t in ['Flying', 'Electric'] for t in tipos):
            bola_sugerida = "Fast Ball (Ótima para Pokémon rápidos)"
        else:
            bola_sugerida = "Poke Ball / Great Ball / Ultra Ball (Padrão para qualquer espécie)"
            
        st.success(f"**Recomendação:** {bola_sugerida}")
                
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
        st.subheader("🟩 Mods de Minecraft & Tutoriais em Vídeo de Farms")
        st.write("Explore a lista completa de 10 farms para cada mod com links diretos de tutoriais do YouTube inseridos em cada item!")

        sub_aba1, sub_aba2 = st.tabs(["🟢 10 Farms de Cobblemon (com YouTube)", "🟡 10 Farms de Pixelmon (com YouTube)"])

        with sub_aba1:
            st.markdown("### 🟢 Top 10 Farms para Cobblemon e Tutoriais")
            
            st.markdown("1. **Farm Automática de Apricorns**")
            st.markdown("   - *Descrição:* Plantação em fileiras colhida por carrinhos com funil ou Allays.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/watch?v=YPVa-ejpbMg)")
            
            st.markdown("2. **Gerador Automático de Tumblestones**")
            st.markdown("   - *Descrição:* Aproveita biomas específicos para gerar pedras de evolução.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/watch?v=hQ8t3CMhEFs)")
            
            st.markdown("3. **Farm de Pasture / Exp Passiva**")
            st.markdown("   - *Descrição:* Sistema de currais cercados para gerar XP e amizade automática.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/watch?v=5PG0fVHx0Ns)")
            
            st.markdown("4. **Farm de Itens de Batalha (Held Items)**")
            st.markdown("   - *Descrição:* Plataforma de batalha automatizada contra monstrinhos selvagens.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/results?search_query=cobblemon+held+items+farm+tutorial)")
            
            st.markdown("5. **Farm de Frutas (Berries) com Dispensers**")
            st.markdown("   - *Descrição:* Sistema de osso-farelo (bonemeal) para reprodução rápida.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/results?search_query=cobblemon+berry+farm+tutorial)")
            
            st.markdown("6. **Arena de Treinamento de EVs Automática**")
            st.markdown("   - *Descrição:* Espaço confinado com spawns específicos de tipos.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/results?search_query=cobblemon+ev+training+farm)")
            
            st.markdown("7. **Farm de Apicultores e Mel para Comidas**")
            st.markdown("   - *Descrição:* Útil para criar itens de cura caseiros.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/results?search_query=minecraft+automatic+honey+farm)")
            
            st.markdown("8. **Farm de Drops de Cura / Medicinal Leek**")
            st.markdown("   - *Descrição:* Plantações focadas em ervas medicinais do mod.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/results?search_query=cobblemon+medicinal+leek+farm)")
            
            st.markdown("9. **Estação de Troca Automatizada**")
            st.markdown("   - *Descrição:* Configuração de baús e computadores para comércio local.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/results?search_query=cobblemon+trade+station+setup)")
            
            st.markdown("10. **Farm de Ovos / Incubação em Massa**")
            st.markdown("   - *Descrição:* Sistema compacto com aquecedores e esteiras para chocar ovos.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/results?search_query=cobblemon+egg+hatchery+farm)")

        with sub_aba2:
            st.markdown("### 🟡 Top 10 Farms para Pixelmon e Tutoriais")
            
            st.markdown("1. **Farm de Apricorns com Harvester**")
            st.markdown("   - *Descrição:* Colheitadeiras mecânicas colhendo frutos automaticamente.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/watch?v=Pl_v3wdKSiI)")
            
            st.markdown("2. **Farm de Mints e Vitaminas**")
            st.markdown("   - *Descrição:* Produção em escala de itens de alteração de atributos.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/watch?v=GzAGLoOC0fk)")
            
            st.markdown("3. **Spawner Automático de Bosses**")
            st.markdown("   - *Descrição:* Plataforma subterrânea iluminada para forçar o nascimento de chefões.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/results?search_query=pixelmon+boss+spawner+farm)")
            
            st.markdown("4. **Farm de Minério de Bauxita (Alumínio)**")
            st.markdown("   - *Descrição:* Mineração otimizada para bases de Pokébolas.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/results?search_query=pixelmon+bauxite+ore+farm)")
            
            st.markdown("5. **Rancho de Criação (Breeding Ranch) Automatizado**")
            st.markdown("   - *Descrição:* Sistema com pastos e relógios para ovos contínuos.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/watch?v=jGgccjYes2M)")
            
            st.markdown("6. **Farm de XP em Massa (Relearners/Tutors)**")
            st.markdown("   - *Descrição:* Área de combate otimizada contra monstrinhos de alto nível.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/results?search_query=pixelmon+xp+farm+tutorial)")
            
            st.markdown("7. **Farm de Dinheiro (PokeDollars) com Pay Day**")
            st.markdown("   - *Descrição:* Batalhas automatizadas contra NPCs ou selvagens.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/results?search_query=pixelmon+money+farm+pay+day)")
            
            st.markdown("8. **Farm de Frutas Especiais (Berries Raras)**")
            st.markdown("   - *Descrição:* Estufas com sistemas de irrigação avançados.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/results?search_query=pixelmon+rare+berry+farm)")
            
            st.markdown("9. **Reciclador de Itens / Apricorn Scrap Farm**")
            st.markdown("   - *Descrição:* Conversão automática de itens inúteis em recursos.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/results?search_query=pixelmon+recycler+farm)")
            
            st.markdown("10. **Farm de Fósseis (Fossil Machine Automation)**")
            st.markdown("   - *Descrição:* Sistema de esteiras e energia para restaurar fósseis em série.")
            st.markdown("   - [📺 Assistir Tutorial no YouTube](https://www.youtube.com/results?search_query=pixelmon+fossil+machine+setup)")
