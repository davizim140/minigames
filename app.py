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
        
        tipos_str = [t.lower() for t in tipos]
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
                    img_url = f"https://raw.githubusercontent.com/Repo/sprites/master/sprites/pokemon/other/official-artwork/{p_id}.png" # fallback visual
                    st.image(f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{p_id}.png", width=90)
                    if st.button(f"Ver Detalhes", key=f"btn_gen_{p_id}_{idx}"):
                        st.session_state.pokemon_selecionado = p_id
                        st.rerun()

    with aba3:
        st.subheader("🟩 Mods de Minecraft & Guia de 10 Farms")
        st.write("Explore dicas oficiais e uma lista com 10 farms dedicadas para Cobblemon e Pixelmon junto com links de guias!")

        sub_aba1, sub_aba2, sub_aba3 = st.tabs(["🟢 10 Farms de Cobblemon", "🟡 10 Farms de Pixelmon", "📚 Links Oficiais"])

        with sub_aba1:
            st.markdown("### 🟢 Top 10 Farms para Cobblemon")
            st.write("Lista detalhada de 10 automações essenciais para o seu mundo Cobblemon:")

            st.markdown("1. **Farm Automática de Apricorns**: Plantação em fileiras colhida por carrinhos com funil ou Allays.")
            st.markdown("2. **Gerador Automático de Tumblestones**: Aproveita biomas específicos para gerar pedras de evolução.")
            st.markdown("3. **Farm de Pasture / Exp Passiva**: Sistema de currais cercados para gerar XP e amizade automática.")
            st.markdown("4. **Farm de Itens de Batalha (Held Items)**: Plataforma de batalha automatizada contra monstrinhos selvagens.")
            st.markdown("5. **Farm de Frutas (Berries) com Dispensers**: Sistema de osso-farelo (bonemeal) para reprodução rápida.")
            st.markdown("6. **Arena de Treinamento de EVs Automática**: Espaço confinado com spawns específicos de tipos (ex: HP, Ataque).")
            st.markdown("7. **Farm de Apicultores e Mel para Comidas**: Útil para criar itens de cura caseiros.")
            st.markdown("8. **Farm de Drops de Cura / Medicinal Leek**: Plantações focadas em ervas medicinais do mod.")
            st.markdown("9. **Estação de Troca Automatizada**: Configuração de baús e computadores para automação de comércio local.")
            st.markdown("10. **Farm de Ovos / Incubação em Massa**: Sistema compacto com aquecedores e esteiras para chocar ovos rapidamente.")
            
            st.markdown("[🔗 Guia e Tutoriais do Cobblemon Wiki](https://wiki.cobblemon.com/)")

        with sub_aba2:
            st.markdown("### 🟡 Top 10 Farms para Pixelmon")
            st.write("Lista detalhada de 10 automações e estruturas essenciais para o Pixelmon Reforged:")

            st.markdown("1. **Farm de Apricorns com Harvester**: Colheitadeiras mecânicas colhendo frutos automaticamente.")
            st.markdown("2. **Farm de Mints e Vitaminas**: Produção em escala de itens de alteração de atributos.")
            st.markdown("3. **Spawner Automático de Bosses**: Plataforma subterrânea iluminada para forçar o nascimento de chefões.")
            st.markdown("4. **Farm de Minério de Bauxita (Alumínio)**: Mineração otimizada para criação de bases de Pokébolas.")
            st.markdown("5. **Rancho de Criação (Breeding Ranch) Automatizado**: Sistema com pastos e relógios para ovos contínuos.")
            st.markdown("6. **Farm de XP em Massa (Relearners/Tutors)**: Área de combate otimizada contra monstrinhos de alto nível.")
            st.markdown("7. **Farm de Dinheiro (PokeDollars) com Pay Day**: Batalhas automatizadas contra NPCs ou Pokémon selvagens específicos.")
            st.markdown("8. **Farm de Frutas Especiais (Berries Raras)**: Estufas com sistemas de irrigação avançados.")
            st.markdown("9. **Reciclador de Itens / Apricorn Scrap Farm**: Conversão automática de itens inúteis em recursos.")
            st.markdown("10. **Farm de Fósseis (Fossil Machine Automation)**: Sistema de esteiras e energia para restaurar fósseis em série.")

            st.markdown("[🔗 Guia e Tutoriais do Pixelmon Wiki](https://pixelmonmod.com/wiki/)")

        with sub_aba3:
            st.markdown("### 📚 Links Úteis e Comunidade")
            st.markdown("- [Site Oficial do Cobblemon](https://cobblemon.com/)")
            st.markdown("- [Wiki Oficial do Cobblemon](https://wiki.cobblemon.com/)")
            st.markdown("- [Site Oficial do Pixelmon](https://pixelmonmod.com/)")
            st.markdown("- [Wiki Oficial do Pixelmon](https://pixelmonmod.com/wiki/)")
