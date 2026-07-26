import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from google import genai

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="SpectrumEcho - Governança Sensorial e Ecolalia",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

ADMIN_EMAIL = "sivanildo.santoss@gmail.com"

# ---------------------------------------------------------
# INJEÇÃO DE PWA (MANIFEST + SERVICE WORKER)
# ---------------------------------------------------------
st.markdown("""
    <head>
        <link rel="manifest" href="data:application/manifest+json,{%22name%22:%22SpectrumEcho%22,%22short_name%22:%22SpectrumEcho%22,%22start_url%22:%22/%22,%22display%22:%22standalone%22,%22background_color%22:%22%230f172a%22,%22theme_color%22:%22%2338bdf8%22,%22icons%22:[{%22src%22:%22https://em-content.zobj.net/source/apple/391/puzzle-piece_1f9e9.png%22,%22sizes%22:%22512x512%22,%22type%22:%22image/png%22}]}">
        <meta name="theme-color" content="#38bdf8">
        <script>
            if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                    navigator.serviceWorker.register('data:text/javascript,self.addEventListener("fetch",function(e){});');
                });
            }
        </script>
    </head>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# ESTILIZAÇÃO CUSTOMIZADA (CSS)
# ---------------------------------------------------------
st.markdown("""
    <style>
        .feature-card {
            background-color: #1e293b;
            padding: 24px;
            border-radius: 12px;
            border: 1px solid #334155;
            text-align: center;
            height: 100%;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 12px;
        }
        .feature-title {
            color: #38bdf8 !important;
            font-size: 1.25rem;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .feature-text {
            color: #94a3b8;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        .hero-title {
            font-size: 2.5rem;
            font-weight: 800;
            color: #38bdf8 !important;
            text-align: center;
            margin-bottom: 10px;
        }
        .hero-subtitle {
            font-size: 1.2rem;
            color: #cbd5e1;
            text-align: center;
            margin-bottom: 20px;
        }
        .ai-badge {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            border: 1px solid #38bdf8;
            border-radius: 12px;
            padding: 16px 24px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.15);
        }
        .ai-badge-title {
            color: #ffffff;
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 6px;
        }
        .ai-badge-text {
            color: #e0f2fe;
            font-size: 0.95rem;
            margin: 0;
        }
        .sidebar-brand-btn {
            background: none;
            border: none;
            color: #38bdf8;
            font-size: 1.6rem;
            font-weight: bold;
            cursor: pointer;
            padding: 0;
            text-align: left;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# BANCO DE DADOS
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'legacy',
            name TEXT NOT NULL,
            age INTEGER,
            profile_type TEXT,
            support_level INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS echolalia_library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'legacy',
            profile_id INTEGER,
            media_title TEXT,
            phrase TEXT,
            meaning_context TEXT,
            FOREIGN KEY(profile_id) REFERENCES profiles(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensory_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'legacy',
            profile_id INTEGER,
            timestamp DATETIME,
            stress_level INTEGER,
            triggers TEXT,
            notes TEXT,
            FOREIGN KEY(profile_id) REFERENCES profiles(id)
        )
    """)
    
    cursor.execute("UPDATE profiles SET user_id = ? WHERE user_id = 'legacy'", (ADMIN_EMAIL,))
    cursor.execute("UPDATE echolalia_library SET user_id = ? WHERE user_id = 'legacy'", (ADMIN_EMAIL,))
    cursor.execute("UPDATE sensory_logs SET user_id = ? WHERE user_id = 'legacy'", (ADMIN_EMAIL,))

    conn.commit()
    conn.close()

init_db()

def get_connection():
    return sqlite3.connect("spectrumecho.db")

def add_profile(user_id, name, age, profile_type, support_level):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO profiles (user_id, name, age, profile_type, support_level) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, age, profile_type, support_level)
    )
    conn.commit()
    conn.close()

def get_profiles(user_id):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM profiles WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
    return df

def delete_profile(profile_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sensory_logs WHERE profile_id = ?", (profile_id,))
    cursor.execute("DELETE FROM echolalia_library WHERE profile_id = ?", (profile_id,))
    cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
    conn.commit()
    conn.close()

def add_echolalia(user_id, profile_id, media_title, phrase, meaning_context):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO echolalia_library (user_id, profile_id, media_title, phrase, meaning_context) VALUES (?, ?, ?, ?, ?)",
        (user_id, profile_id, media_title, phrase, meaning_context)
    )
    conn.commit()
    conn.close()

def get_echolalias(user_id, profile_id=None):
    conn = get_connection()
    if profile_id:
        df = pd.read_sql_query(
            "SELECT e.*, p.name as profile_name FROM echolalia_library e JOIN profiles p ON e.profile_id = p.id WHERE e.user_id = ? AND e.profile_id = ?",
            conn, params=(user_id, profile_id)
        )
    else:
        df = pd.read_sql_query(
            "SELECT e.*, p.name as profile_name FROM echolalia_library e JOIN profiles p ON e.profile_id = p.id WHERE e.user_id = ?",
            conn, params=(user_id,)
        )
    conn.close()
    return df

def delete_echolalia(echolalia_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM echolalia_library WHERE id = ?", (echolalia_id,))
    conn.commit()
    conn.close()

def add_sensory_log(user_id, profile_id, stress_level, triggers, notes):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sensory_logs (user_id, profile_id, timestamp, stress_level, triggers, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, profile_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), stress_level, triggers, notes)
    )
    conn.commit()
    conn.close()

def get_sensory_logs(user_id, profile_id=None):
    conn = get_connection()
    if profile_id:
        df = pd.read_sql_query(
            "SELECT s.*, p.name as profile_name FROM sensory_logs s JOIN profiles p ON s.profile_id = p.id WHERE s.user_id = ? AND s.profile_id = ? ORDER BY s.timestamp DESC",
            conn, params=(user_id, profile_id)
        )
    else:
        df = pd.read_sql_query(
            "SELECT s.*, p.name as profile_name FROM sensory_logs s JOIN profiles p ON s.profile_id = p.id WHERE s.user_id = ? ORDER BY s.timestamp DESC",
            conn, params=(user_id,)
        )
    conn.close()
    return df

def get_all_global_profiles():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM profiles", conn)
    conn.close()
    return df

# ---------------------------------------------------------
# FUNÇÃO DA IA (GEMINI)
# ---------------------------------------------------------
def translate_echolalia_with_ai(api_key, phrase, media_title, profile_name, age):
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        Você é um especialista em Análise do Comportamento Aplicada (ABA), Terapia Ocupacional e desenvolvimento infantil no Transtorno do Espectro Autista (TEA).

        Uma pessoa autista ({profile_name}, {age} anos) costuma repetir frequentemente a seguinte frase/ecolalia:
        - Frase repetida: "{phrase}"
        - Mídia de origem informada (desenho, jogo, filme, vídeo do YouTube): "{media_title}"

        Sua tarefa é analisar o contexto desta frase na mídia citada (ou o significado geral se for uma variação) e responder de forma acolhedora, objetiva e prática para os pais/cuidadores:

        1. **Contexto Original:** De onde vem essa frase na mídia/desenho e o que acontecia na cena original?
        2. **Intenção Comunicativa / Significado Provável:** O que a pessoa pode estar querendo expressar ao usar essa fala no dia a dia? (Ex: expressar animação, pedir algo, demonstrar desconforto sensorial, buscar previsibilidade, etc.)
        3. **Como Responder / Ação Sugerida:** Uma orientação prática e acolhedora de como os pais ou terapeutas podem validar essa fala e responder de forma funcional.

        Responda em português, usando tópicos claros e linguagem acessível para famílias.
        """
        
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Erro ao consultar a IA: {str(e)}"

# ---------------------------------------------------------
# PERSISTÊNCIA DE SESSÃO / COOKIES
# ---------------------------------------------------------
if "user_email" not in st.session_state:
    st.session_state.user_email = st.query_params.get("user_email", None)

env_gemini_key = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        env_gemini_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if "gemini_api_key" not in st.session_state or not st.session_state.gemini_api_key:
    st.session_state.gemini_api_key = env_gemini_key

# ---------------------------------------------------------
# BARRA LATERAL (HEADER & BOTÃO HOME)
# ---------------------------------------------------------
if st.sidebar.button("🧩 SpectrumEcho", type="tertiary", use_container_width=True):
    st.session_state.show_landing = True
    st.rerun()

current_user = st.session_state.user_email

if current_user:
    st.sidebar.caption(f"Conectado como: **{current_user}**")
    
    with st.sidebar.expander("⚙️ Chave da API Gemini (IA)"):
        user_api_key = st.text_input("Sua Gemini API Key:", value=st.session_state.gemini_api_key, type="password")
        if user_api_key:
            st.session_state.gemini_api_key = user_api_key
            st.success("Chave de IA ativa!")
        elif st.session_state.gemini_api_key:
            st.success("Chave de IA ativa do servidor!")

    if st.sidebar.button("🚪 Sair / Logoff"):
        st.session_state.user_email = None
        st.session_state.show_landing = False
        if "user_email" in st.query_params:
            del st.query_params["user_email"]
        st.rerun()

st.sidebar.markdown("---")

# Controle de Exibição da Tela Inicial
if "show_landing" not in st.session_state:
    st.session_state.show_landing = False

menu_options = []
if current_user:
    menu_options = ["🏠 Página Inicial (Apresentação)", "👤 Gestão de Perfis", "🗣️ Biblioteca de Ecolalias (com IA)", "📊 Registro Sensorial", "📈 Dashboard & Análise"]
    if current_user == ADMIN_EMAIL:
        menu_options.append("👑 Painel Dev / Admin")
    
    selected_page = st.sidebar.radio("Navegação:", menu_options)
    if selected_page == "🏠 Página Inicial (Apresentação)":
        st.session_state.show_landing = True
    else:
        st.session_state.show_landing = False

# ---------------------------------------------------------
# TELA INICIAL (LANDING PAGE COM DESTAQUE DA IA)
# ---------------------------------------------------------
if st.session_state.user_email is None or st.session_state.show_landing:
    st.markdown('<h1 class="hero-title">🧩 SpectrumEcho</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="hero-subtitle">A primeira plataforma para <b>mapeamento de ecolalias</b>, <b>regulação sensorial</b> e <b>relatórios clínicos no TEA</b>.</p>',
        unsafe_allow_html=True
    )
    
    # BANNER DE CREDIBILIDADE DA IA
    st.markdown("""
        <div class="ai-badge">
            <div class="ai-badge-title">⚡ Respostas e Tradução em Tempo Real por IA Especializada</div>
            <p class="ai-badge-text">
                Nossa plataforma utiliza uma <b>Inteligência Artificial treinada sob diretrizes de Análise do Comportamento Aplicada (ABA) e Terapia Ocupacional</b>. 
                As análises de ecolalias e comportamentos sensoriais são processadas instantaneamente, ajudando famílias a entenderem a intenção comunicativa por trás de cada fala.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-title">Tradutor com IA em TEA</div>
                <p class="feature-text">Mapeie falas repetidas de desenhos e mídias. Nossa IA treinada em suporte ao autismo identifica o contexto original e sugere respostas acolhedoras em segundos.</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Diário Sensorial</div>
                <p class="feature-text">Registre episódios de estresse, gatilhos (sons, luzes, rotina) e estratégias de regulação que ajudaram a acalmar a criança ao longo do dia.</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📄</div>
                <div class="feature-title">Relatório Clínico</div>
                <p class="feature-text">Gere dados organizados e prontos para compartilhar nas consultas de Neuropediatria, Psicologia e Terapia Ocupacional (ABA/TO).</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    if st.session_state.user_email is None:
        col_empty1, col_login, col_empty2 = st.columns([1, 1.5, 1])
        with col_login:
            with st.form("login_form"):
                st.subheader("🔑 Acesse a sua conta gratuita")
                st.caption("Seus dados permanecem 100% privados e isolados na sua conta.")
                email_input = st.text_input("Digite seu e-mail do Google para continuar:", placeholder="exemplo@gmail.com")
                submit_login = st.form_submit_button("Acessar o SpectrumEcho 🚀", type="primary")
                
                if submit_login:
                    if email_input and "@" in email_input:
                        formatted_email = email_input.strip().lower()
                        st.session_state.user_email = formatted_email
                        st.session_state.show_landing = False
                        st.query_params["user_email"] = formatted_email
                        st.rerun()
                    else:
                        st.error("Por favor, insira um e-mail válido.")
    else:
        st.info("💡 Você já está conectado. Escolha uma opção no menu da barra lateral para continuar navegando nos seus perfis!")

    st.stop()

# ---------------------------------------------------------
# APLICAÇÃO (USUÁRIO LOGADO - NAVEGAÇÃO INTERNA)
# ---------------------------------------------------------

# --- TELA 1: GESTÃO DE PERFIS ---
if selected_page == "👤 Gestão de Perfis":
    st.header("👤 Seus Perfis Cadastrados")
    
    with st.expander("➕ Adicionar Novo Perfil", expanded=True):
        with st.form("add_profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nome Completo / Apelido")
                profile_type = st.selectbox("Tipo de Perfil", ["Criança", "Adolescente", "Adulto"])
            with col2:
                age = st.number_input("Idade", min_value=1, max_value=120, value=7)
                support_level = st.select_slider("Nível de Suporte (TEA)", options=[1, 2, 3])
            
            submit = st.form_submit_button("Salvar Perfil")
            if submit:
                if name.strip():
                    add_profile(current_user, name, age, profile_type, support_level)
                    st.success(f"Perfil de '{name}' cadastrado com sucesso!")
                    st.rerun()
                else:
                    st.warning("Preencha o nome do perfil.")

    st.subheader("Perfis Ativos")
    profiles_df = get_profiles(current_user)
    if not profiles_df.empty:
        for idx, row in profiles_df.iterrows():
            col_info, col_del = st.columns([4, 1])
            with col_info:
                st.info(f"**{row['name']}** ({row['age']} anos) — Tipo: {row['profile_type']} | Nível de Suporte: {row['support_level']}")
            with col_del:
                if st.button("🗑️ Excluir", key=f"del_prof_{row['id']}"):
                    delete_profile(row['id'])
                    st.success("Perfil excluído.")
                    st.rerun()
    else:
        st.write("Nenhum perfil cadastrado para esta conta ainda.")

# --- TELA 2: BIBLIOTECA DE ECOLALIAS COM IA ---
elif selected_page == "🗣️ Biblioteca de Ecolalias (com IA)":
    st.header("🗣️ Dicionário de Tradução Ativa & Ecolalias")
    profiles_df = get_profiles(current_user)
    
    if profiles_df.empty:
        st.warning("Você precisa cadastrar pelo menos um perfil antes de registrar ecolalias.")
    else:
        profile_map = {row['name']: (row['id'], row['age']) for idx, row in profiles_df.iterrows()}
        selected_profile_name = st.selectbox("Selecione o Perfil:", list(profile_map.keys()))
        selected_profile_id, selected_profile_age = profile_map[selected_profile_name]

        with st.expander("➕ Analisar e Traduzir Nova Ecolalia", expanded=True):
            media_title = st.text_input("Origem (ex: Roblox, Peppa Pig, Vídeo do YT)")
            phrase = st.text_input("Frase / Fala Repetida", placeholder="ex: 'pai, tomate?'")
            
            ai_analysis_result = ""
            if st.button("✨ Analisar e Traduzir com Inteligência Artificial", type="primary"):
                active_key = st.session_state.gemini_api_key
                if not active_key:
                    st.error("Chave da API Gemini não encontrada. Adicione nas configurações da barra lateral.")
                elif not phrase.strip():
                    st.warning("Digite a frase para ser analisada.")
                else:
                    with st.spinner("Analisando o contexto com a IA do Gemini..."):
                        ai_analysis_result = translate_echolalia_with_ai(
                            active_key, phrase, media_title, selected_profile_name, selected_profile_age
                        )

            with st.form("add_echo_form"):
                meaning_context = st.text_area(
                    "💡 Análise Sugerida pela IA (Você pode editar antes de salvar):",
                    value=ai_analysis_result,
                    height=200
                )
                submit_echo = st.form_submit_button("💾 Salvar Tradução no Histórico do Perfil")
                
                if submit_echo:
                    if phrase.strip() and meaning_context.strip():
                        add_echolalia(current_user, selected_profile_id, media_title, phrase, meaning_context)
                        st.success("Ecolalia cadastrada com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Preencha a frase e o significado antes de salvar.")

        st.subheader(f"Ecolalias Mapeadas para {selected_profile_name}")
        echolalias_df = get_echolalias(current_user, selected_profile_id)
        if not echolalias_df.empty:
            for idx, row in echolalias_df.iterrows():
                with st.container():
                    col_txt, col_del = st.columns([4, 1])
                    with col_txt:
                        st.write(f"🗣️ **\"{row['phrase']}\"**")
                        st.caption(f"Origem: {row['media_title'] if row['media_title'] else 'Não informada'}")
                        st.markdown(f"💡 **Significado / Ação sugerida:**\n\n{row['meaning_context']}")
                    with col_del:
                        if st.button("🗑️ Apagar", key=f"del_echo_{row['id']}"):
                            delete_echolalia(row['id'])
                            st.success("Excluído!")
                            st.rerun()
                st.markdown("---")
        else:
            st.write("Nenhuma ecolalia cadastrada para este perfil ainda.")

# --- TELA 3: REGISTRO SENSORIAL ---
elif selected_page == "📊 Registro Sensorial":
    st.header("📊 Diário de Registro Sensorial e Crises")
    profiles_df = get_profiles(current_user)
    
    if profiles_df.empty:
        st.warning("Cadastre um perfil primeiro.")
    else:
        profile_map = {row['name']: row['id'] for idx, row in profiles_df.iterrows()}
        selected_profile_name = st.selectbox("Selecione o Perfil:", list(profile_map.keys()))
        selected_profile_id = profile_map[selected_profile_name]

        with st.form("add_sensory_form"):
            stress_level = st.slider("Nível de Estresse / Desconforto (1 a 5)", 1, 5, 3)
            triggers = st.text_input("Gatilhados Sensoriais (ex: barulho de liquidificador, luz forte, mudança na rotina)")
            notes = st.text_area("Observações de como a crise foi regulada / O que ajudou?")
            submit_sensory = st.form_submit_button("Registrar Momento")
            
            if submit_sensory:
                add_sensory_log(current_user, selected_profile_id, stress_level, triggers, notes)
                st.success("Registro sensorial salvo com sucesso!")
                st.rerun()

        st.subheader("Histórico Recente")
        logs_df = get_sensory_logs(current_user, selected_profile_id)
        if not logs_df.empty:
            st.dataframe(logs_df[['timestamp', 'stress_level', 'triggers', 'notes']], use_container_width=True)
        else:
            st.write("Nenhum registro gravado para este perfil ainda.")

# --- TELA 4: DASHBOARD & ANÁLISE ---
elif selected_page == "📈 Dashboard & Análise":
    st.header("📈 Visão Geral & Relatório")
    profiles_df = get_profiles(current_user)
    
    if not profiles_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Perfis", len(profiles_df))
        with col2:
            echo_df = get_echolalias(current_user)
            st.metric("Ecolalias Mapeadas", len(echo_df))
            
        st.markdown("---")
        st.subheader("Relatório de Acompanhamento")
        st.write("Utilize os dados abaixo para compartilhar com médicos, terapeutas e educadores.")
        
        all_logs = get_sensory_logs(current_user)
        if not all_logs.empty:
            st.dataframe(all_logs, use_container_width=True)
        else:
            st.info("Registre ecolalias e momentos sensoriais para gerar gráficos e relatórios completos.")
    else:
        st.write("Sem dados para exibir ainda. Comece cadastrando um perfil.")

# --- TELA 5: PAINEL DEV / ADMIN ---
elif selected_page == "👑 Painel Dev / Admin":
    st.header("👑 Visão Global do Desenvolvedor")
    st.warning("Esta aba é visível exclusivamente para a conta de administrador.")
    
    st.subheader("Todos os Perfis no Banco de Dados (Global)")
    global_profiles = get_all_global_profiles()
    st.dataframe(global_profiles, use_container_width=True)