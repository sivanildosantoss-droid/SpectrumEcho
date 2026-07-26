import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="SpectrumEcho",
    page_icon="🧩",
    layout="wide"
)

# E-mail do Administrador / Desenvolvedor
ADMIN_EMAIL = "sivanildo.santoss@gmail.com"

# ---------------------------------------------------------
# BANCO DE DADOS (INICIALIZAÇÃO E MIGRAÇÃO AUTOMÁTICA)
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    
    # Tabela de Perfis
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
    try:
        cursor.execute("ALTER TABLE profiles ADD COLUMN user_id TEXT DEFAULT 'legacy'")
    except sqlite3.OperationalError:
        pass

    # Tabela da Biblioteca de Ecolalias
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
    try:
        cursor.execute("ALTER TABLE echolalia_library ADD COLUMN user_id TEXT DEFAULT 'legacy'")
    except sqlite3.OperationalError:
        pass

    # Tabela de Registros Sensoriais
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
    try:
        cursor.execute("ALTER TABLE sensory_logs ADD COLUMN user_id TEXT DEFAULT 'legacy'")
    except sqlite3.OperationalError:
        pass
    
    # Migra registros antigos ('legacy') para o e-mail do admin para não perder nada
    cursor.execute("UPDATE profiles SET user_id = ? WHERE user_id = 'legacy'", (ADMIN_EMAIL,))
    cursor.execute("UPDATE echolalia_library SET user_id = ? WHERE user_id = 'legacy'", (ADMIN_EMAIL,))
    cursor.execute("UPDATE sensory_logs SET user_id = ? WHERE user_id = 'legacy'", (ADMIN_EMAIL,))

    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# FUNÇÕES DE MANIPULAÇÃO DE DADOS
# ---------------------------------------------------------
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

# Funções exclusivas do Admin/Dev
def get_all_global_profiles():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM profiles", conn)
    conn.close()
    return df

# ---------------------------------------------------------
# AUTENTICAÇÃO / LOGIN
# ---------------------------------------------------------
if "user_email" not in st.session_state:
    st.session_state.user_email = None

st.sidebar.title("🧩 SpectrumEcho")

if st.session_state.user_email is None:
    st.title("🧩 SpectrumEcho - Acesso de Usuário")
    st.subheader("Por favor, faça login com seu e-mail para acessar seus dados com privacidade.")
    
    email_input = st.text_input("Seu E-mail do Google:")
    if st.button("Entrar", type="primary"):
        if email_input and "@" in email_input:
            st.session_state.user_email = email_input.strip().lower()
            st.rerun()
        else:
            st.error("Por favor, insira um e-mail válido.")
    st.stop()

# Usuário Ativo
current_user = st.session_state.user_email
st.sidebar.write(f"Conectado como: **{current_user}**")
if st.sidebar.button("🚪 Sair / Logoff"):
    st.session_state.user_email = None
    st.rerun()

st.sidebar.markdown("---")

# ---------------------------------------------------------
# MENU NAVEGAÇÃO
# ---------------------------------------------------------
menu_options = ["👤 Gestão de Perfis", "🗣️ Biblioteca de Ecolalias", "📊 Registro Sensorial", "📈 Dashboard & Análise"]

# Se for o e-mail do Desenvolvedor, libera a visão global
if current_user == ADMIN_EMAIL:
    menu_options.append("👑 Painel Dev / Admin")

page = st.sidebar.radio("Navegação:", menu_options)

# ---------------------------------------------------------
# TELA 1: GESTÃO DE PERFIS
# ---------------------------------------------------------
if page == "👤 Gestão de Perfis":
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

# ---------------------------------------------------------
# TELA 2: BIBLIOTECA DE ECOLALIAS
# ---------------------------------------------------------
elif page == "🗣️ Biblioteca de Ecolalias":
    st.header("🗣️ Dicionário de Tradução Ativa & Ecolalias")
    profiles_df = get_profiles(current_user)
    
    if profiles_df.empty:
        st.warning("Você precisa cadastrar pelo menos um perfil antes de registrar ecolalias.")
    else:
        profile_map = {row['name']: row['id'] for idx, row in profiles_df.iterrows()}
        selected_profile_name = st.selectbox("Selecione o Perfil:", list(profile_map.keys()))
        selected_profile_id = profile_map[selected_profile_name]

        with st.expander("➕ Nova Ecolalia / Fala Repetida", expanded=True):
            with st.form("add_echo_form"):
                media_title = st.text_input("Origem (ex: Desenho, Filme, Vídeo do YT)")
                phrase = st.text_input("Frase / Fala Repetida")
                meaning_context = st.text_area("O que isso realmente significa / O que a pessoa quer comunicar?")
                submit_echo = st.form_submit_button("Cadastrar Tradução")
                
                if submit_echo:
                    if phrase.strip() and meaning_context.strip():
                        add_echolalia(current_user, selected_profile_id, media_title, phrase, meaning_context)
                        st.success("Ecolalia cadastrada com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Preencha a frase e o significado.")

        st.subheader(f"Ecolalias Mapeadas para {selected_profile_name}")
        echolalias_df = get_echolalias(current_user, selected_profile_id)
        if not echolalias_df.empty:
            for idx, row in echolalias_df.iterrows():
                with st.container():
                    col_txt, col_del = st.columns([4, 1])
                    with col_txt:
                        st.write(f"🗣️ **\"{row['phrase']}\"**")
                        st.caption(f"Origem: {row['media_title'] if row['media_title'] else 'Não informada'}")
                        st.write(f"💡 **Significado / Ação sugerida:** {row['meaning_context']}")
                    with col_del:
                        if st.button("🗑️ Apagar", key=f"del_echo_{row['id']}"):
                            delete_echolalia(row['id'])
                            st.success("Excluído!")
                            st.rerun()
                st.markdown("---")
        else:
            st.write("Nenhuma ecolalia cadastrada para este perfil ainda.")

# ---------------------------------------------------------
# TELA 3: REGISTRO SENSORIAL
# ---------------------------------------------------------
elif page == "📊 Registro Sensorial":
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

# ---------------------------------------------------------
# TELA 4: DASHBOARD & ANÁLISE
# ---------------------------------------------------------
elif page == "📈 Dashboard & Análise":
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

# ---------------------------------------------------------
# TELA 5: PAINEL DEV / ADMIN (EXCLUSIVO DO CRIADOR)
# ---------------------------------------------------------
elif page == "👑 Painel Dev / Admin":
    st.header("👑 Visão Global do Desenvolvedor")
    st.warning("Esta aba é visível exclusivamente para a conta de administrador.")
    
    st.subheader("Todos os Perfis no Banco de Dados (Global)")
    global_profiles = get_all_global_profiles()
    st.dataframe(global_profiles, use_container_width=True)