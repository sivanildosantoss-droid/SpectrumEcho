import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import json
import os

# Importação da Engine de PDF
from report_generator import SpectrumEchoPDFGenerator

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="SpectrumEcho - Governança Sensorial",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ESTILIZAÇÃO VISUAL SENSORIAL (CUSTOM CSS)
# ---------------------------------------------------------
st.markdown("""
    <style>
        .main {
            background-color: #0f172a;
        }
        h1, h2, h3 {
            color: #38bdf8 !important;
            font-weight: 600 !important;
        }
        div[data-testid="stForm"] {
            border: 1px solid #1e293b !important;
            border-radius: 12px !important;
            padding: 20px !important;
            background-color: #1e293b !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }
        .stButton>button {
            border-radius: 8px !important;
            font-weight: bold !important;
            transition: all 0.3s ease !important;
        }
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 10px rgba(56, 189, 248, 0.3) !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# BANCO DE DADOS (COM ISOLAMENTO POR USUÁRIO)
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            profile_type TEXT,
            support_level INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS echolalia_library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
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
            user_id TEXT NOT NULL,
            profile_id INTEGER,
            timestamp DATETIME,
            stress_level INTEGER,
            triggers TEXT,
            notes TEXT,
            FOREIGN KEY(profile_id) REFERENCES profiles(id)
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

# --- FUNÇÕES CRUD ISOLADAS ---
def get_profiles(user_id):
    conn = sqlite3.connect("spectrumecho.db")
    df = pd.read_sql_query("SELECT * FROM profiles WHERE user_id = ?", conn, params=(user_id,))
    conn.close()
    return df

def add_profile(user_id, name, age, profile_type, support_level):
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO profiles (user_id, name, age, profile_type, support_level) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, age, profile_type, support_level)
    )
    conn.commit()
    conn.close()

def delete_profile(user_id, profile_id):
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM profiles WHERE id = ? AND user_id = ?", (profile_id, user_id))
    cursor.execute("DELETE FROM echolalia_library WHERE profile_id = ? AND user_id = ?", (profile_id, user_id))
    cursor.execute("DELETE FROM sensory_logs WHERE profile_id = ? AND user_id = ?", (profile_id, user_id))
    conn.commit()
    conn.close()

def add_echolalia(user_id, profile_id, media_title, phrase, meaning_context):
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO echolalia_library (user_id, profile_id, media_title, phrase, meaning_context) VALUES (?, ?, ?, ?, ?)",
        (user_id, profile_id, media_title, phrase, meaning_context)
    )
    conn.commit()
    conn.close()

def delete_echolalia(user_id, echo_id):
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM echolalia_library WHERE id = ? AND user_id = ?", (echo_id, user_id))
    conn.commit()
    conn.close()

def get_echolalias(user_id, profile_id):
    conn = sqlite3.connect("spectrumecho.db")
    df = pd.read_sql_query("SELECT * FROM echolalia_library WHERE profile_id = ? AND user_id = ?", conn, params=(profile_id, user_id))
    conn.close()
    return df

def save_log(user_id, profile_id, stress_level, triggers, notes):
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sensory_logs (user_id, profile_id, timestamp, stress_level, triggers, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, profile_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), stress_level, ", ".join(triggers), notes)
    )
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# MOTOR DE TRADUÇÃO COMPORTAMENTAL
# ---------------------------------------------------------
def generate_behavioral_translation(phrase, media_title):
    phrase_lower = phrase.lower()
    if "sumiu" in phrase_lower or "cade" in phrase_lower or "onde" in phrase_lower:
        return (
            "🔍 **Tradução:** Expressa busca por previsibilidade ou estranhamento com mudança no ambiente.\n"
            "💡 **Ação Recomendada:** Mostrar à criança onde as coisas estão ou reestabelecer o elemento de segurança."
        )
    elif "doente" in phrase_lower or "machucou" in phrase_lower or "quebrou" in phrase_lower:
        return (
            "⚠️ **Tradução:** Expressa desconforto sensorial físico, medo ou sobrecarga que a criança não sabe nomear diretamente.\n"
            "💡 **Ação Recomendada:** Verificar estímulos (som, luz, fome, cansaço) e oferecer local de descompressão."
        )
    elif "fora dos trilhos" in phrase_lower or "perigo" in phrase_lower or "socorro" in phrase_lower:
        return (
            "🚨 **Tradução:** Expressa sensação de descontrole ou pico de sobrecarga sensorial iminente.\n"
            "💡 **Ação Recomendada:** Reduzir ruídos, afastar estímulos externos e manter tom de voz calmo."
        )
    else:
        return (
            f"🎬 **Tradução:** Ecolalia funcional associada à mídia '{media_title}'. Usada para autorregulação ou tentativa de iniciar interação.\n"
            "💡 **Ação Recomendada:** Entrar no contexto do desenho com tom acolhedor para validar a comunicação."
        )

# ---------------------------------------------------------
# GERENCIAMENTO DE SESSÃO / LOGIN
# ---------------------------------------------------------
if "user_email" not in st.session_state:
    st.session_state.user_email = None

def login_screen():
    st.title("🧩 SpectrumEcho")
    st.subheader("Plataforma Universal de Governança Sensorial")
    st.write("Por favor, acesse com sua conta do Google para garantir o isolamento e a privacidade dos seus dados.")
    
    # Campo de login simples para simulação/autenticação
    email_input = st.text_input("Digite seu e-mail do Google para entrar:", placeholder="exemplo@gmail.com")
    if st.button("🔑 Entrar no Sistema"):
        if email_input and "@" in email_input:
            st.session_state.user_email = email_input.strip().lower()
            st.rerun()
        else:
            st.error("Por favor, insira um e-mail válido.")

# ---------------------------------------------------------
# APLICAÇÃO PRINCIPAL
# ---------------------------------------------------------
if not st.session_state.user_email:
    login_screen()
else:
    user_id = st.session_state.user_email
    admin_email = st.secrets.get("admin", {}).get("email", "sivanildo.santoss@gmail.com")

    # Barra Lateral
    st.sidebar.title("🧩 SpectrumEcho")
    st.sidebar.caption(f"Conectado como:\n**{user_id}**")
    
    if st.sidebar.button("🚪 Sair / Logoff"):
        st.session_state.user_email = None
        st.rerun()

    menu_options = ["👤 Gestão de Perfis", "📚 Biblioteca de Ecolalias", "📝 Registro Sensorial", "📊 Dashboard & Análise"]
    if user_id == admin_email:
        menu_options.append("🛡️ Painel do Desenvolvedor (Admin)")

    module = st.sidebar.radio("Navegação:", menu_options)

    # --- MÓDULO 1: GESTÃO DE PERFIS ---
    if module == "👤 Gestão de Perfis":
        st.header("👤 Seus Perfis Cadastrados")
        col_add, col_list = st.columns([1, 1.2])

        with col_add:
            with st.form("new_profile_form"):
                st.subheader("Adicionar Novo Perfil")
                name = st.text_input("Nome Completo / Apelido")
                age = st.number_input("Idade", min_value=1, max_value=100, value=8)
                p_type = st.selectbox("Tipo de Perfil", ["Criança/Adolescente", "Adulto"])
                support_level = st.selectbox("Nível de Suporte (TEA)", [1, 2, 3])
                
                submit = st.form_submit_button("Salvar Perfil")
                if submit and name:
                    add_profile(user_id, name, age, p_type, support_level)
                    st.success(f"Perfil de '{name}' cadastrado!")
                    st.rerun()

        with col_list:
            st.subheader("Perfis Ativos")
            profiles_df = get_profiles(user_id)
            if profiles_df.empty:
                st.info("Nenhum perfil cadastrado na sua conta ainda.")
            else:
                for idx, row in profiles_df.iterrows():
                    with st.expander(f"📌 {row['name']} ({row['profile_type']} - {row['age']} anos)"):
                        st.write(f"**Nível de Suporte:** TEA Nível {row['support_level']}")
                        if st.button(f"🗑️ Excluir Perfil {row['name']}", key=f"del_prof_{row['id']}"):
                            delete_profile(user_id, row['id'])
                            st.warning("Perfil removido!")
                            st.rerun()

    # --- MÓDULO 2: BIBLIOTECA DE ECOLALIAS ---
    elif module == "📚 Biblioteca de Ecolalias":
        st.header("📚 Dicionário & Tradutor de Ecolalias")
        profiles_df = get_profiles(user_id)
        
        if profiles_df.empty:
            st.warning("Cadastre ao menos um perfil na aba 'Gestão de Perfis' primeiro.")
        else:
            profile_map = {f"{row['name']} (ID: {row['id']})": row['id'] for idx, row in profiles_df.iterrows()}
            selected_label = st.selectbox("Selecione o Perfil:", list(profile_map.keys()))
            selected_id = profile_map[selected_label]

            with st.form("add_echo_form"):
                st.subheader("Cadastrar & Traduzir Ecolalia")
                media_title = st.text_input("Mídias / Desenho de Origem", placeholder="Ex: Bob Esponja, Roblox...")
                phrase = st.text_input("Frase Repetida Pela Criança", placeholder="Ex: 'Patrick cadê o Bob Esponja?'")
                user_meaning = st.text_area("Observação (Opcional):")
                
                submit_echo = st.form_submit_button("🤖 Traduzir & Salvar")
                if submit_echo and phrase:
                    final_meaning = user_meaning if user_meaning.strip() else generate_behavioral_translation(phrase, media_title)
                    add_echolalia(user_id, selected_id, media_title, phrase, final_meaning)
                    st.success("Ecolalia cadastrada!")
                    st.rerun()

            st.divider()
            st.subheader("Dicionário de Ecolalias do Perfil:")
            echos_df = get_echolalias(user_id, selected_id)
            if echos_df.empty:
                st.info("Nenhuma ecolalia cadastrada para este perfil.")
            else:
                for idx, row in echos_df.iterrows():
                    col_exp, col_btn = st.columns([5, 1])
                    with col_exp:
                        with st.expander(f"🎬 {row['media_title']} — \"{row['phrase']}\""):
                            st.markdown(f"{row['meaning_context']}")
                    with col_btn:
                        if st.button("🗑️", key=f"del_echo_{row['id']}"):
                            delete_echolalia(user_id, row['id'])
                            st.rerun()

    # --- MÓDULO 3: REGISTRO SENSORIAL ---
    elif module == "📝 Registro Sensorial":
        st.header("📝 Registro de Estresse & Eventos")
        profiles_df = get_profiles(user_id)
        if profiles_df.empty:
            st.warning("Cadastre um perfil primeiro.")
        else:
            profile_map = {f"{row['name']} (ID: {row['id']})": row['id'] for idx, row in profiles_df.iterrows()}
            selected_label = st.selectbox("Selecione o Perfil:", list(profile_map.keys()))
            selected_id = profile_map[selected_label]

            stress = st.slider("Nível de Estresse / Sobrecarga Atual (0 a 100)", 0, 100, 30)
            triggers = st.multiselect(
                "Gatilhos Identificados:",
                ["Barulhos Agudos", "Barulho Contínuo", "Toque Físico Inesperado", "Quebra de Rotina", "Excesso de Conversas", "Luzes Fortes", "Textura / Fome / Cansaço"]
            )
            notes = st.text_area("Observações Adicionais / O que ajudou a acalmar?")

            if st.button("Salvar Registro"):
                save_log(user_id, selected_id, stress, triggers, notes)
                st.success("Registro diário salvo com sucesso!")

    # --- MÓDULO 4: DASHBOARD & ANÁLISE ---
    elif module == "📊 Dashboard & Análise":
        st.header("📊 Análise Sensorial & Gerador de Relatório PDF")
        profiles_df = get_profiles(user_id)
        
        if profiles_df.empty:
            st.info("Cadastre ao menos um perfil para visualizar as análises.")
        else:
            profile_map = {f"{row['name']} (ID: {row['id']})": (row['id'], row['name'], row['profile_type']) for idx, row in profiles_df.iterrows()}
            selected_label = st.selectbox("Selecione o Perfil para Análise:", list(profile_map.keys()))
            selected_id, selected_name, selected_type = profile_map[selected_label]

            conn = sqlite3.connect("spectrumecho.db")
            logs_df = pd.read_sql_query(
                "SELECT timestamp as Data_Hora, stress_level as Estresse, triggers as Gatilhos, notes as Observacoes FROM sensory_logs WHERE profile_id = ? AND user_id = ? ORDER BY timestamp ASC",
                conn,
                params=(selected_id, user_id)
            )
            conn.close()

            if logs_df.empty:
                st.info(f"Ainda não há registros sensoriais para {selected_name}.")
            else:
                col_chart1, col_chart2 = st.columns(2)
                with col_chart1:
                    st.subheader("📈 Curva de Sobrecarga Sensorial")
                    st.line_chart(logs_df, x="Data_Hora", y="Estresse")

                with col_chart2:
                    st.subheader("📊 Nível Médio de Estresse")
                    avg_stress = logs_df["Estresse"].mean()
                    st.metric(label="Média de Estresse Registrada", value=f"{avg_stress:.1f} / 100")

                st.divider()
                st.subheader("📋 Tabela de Eventos Gravados")
                st.dataframe(logs_df, use_container_width=True)

                st.divider()
                st.subheader("📄 Relatório Oficial para Médicos e Terapeutas")
                if st.button("📄 Gerar e Baixar Relatório PDF"):
                    echos_df = get_echolalias(user_id, selected_id)
                    logs_list = []
                    for idx, r in logs_df.iterrows():
                        logs_list.append({
                            "stress_level_0_to_100": r["Estresse"],
                            "triggers": [t.strip() for t in r["Gatilhos"].split(",") if t.strip()],
                            "behavioral_manifestation": {
                                "echolalia_detected": True if not echos_df.empty else False,
                                "echolalia_phrase": echos_df.iloc[0]["phrase"] if not echos_df.empty else "Nenhuma registrada",
                                "media_source": echos_df.iloc[0]["media_title"] if not echos_df.empty else "N/A"
                            }
                        })

                    data_payload = {
                        "user_profile": {
                            "patient_id": f"PAT-{selected_id:04d}",
                            "name": selected_name,
                            "mode": selected_type
                        },
                        "sensory_and_emotional_logs": logs_list
                    }

                    pdf_filename = f"relatorio_{selected_name.replace(' ', '_').lower()}.pdf"
                    pdf_gen = SpectrumEchoPDFGenerator(json_data_str=json.dumps(data_payload), filename=pdf_filename)
                    pdf_gen.generate()

                    with open(pdf_filename, "rb") as pdf_file:
                        st.download_button(
                            label="💾 Clique aqui para Baixar o PDF",
                            data=pdf_file,
                            file_name=pdf_filename,
                            mime="application/pdf"
                        )

    # --- MÓDULO EXCLUSIVO: PAINEL DO DESENVOLVEDOR ---
    elif module == "🛡️ Painel do Desenvolvedor (Admin)":
        st.header("🛡️ Painel de Visão Global (Exclusivo Desenvolvedor)")
        st.write("Visão agregada do sistema para monitoramento de uso, sem violar a privacidade individual.")

        conn = sqlite3.connect("spectrumecho.db")
        total_users = pd.read_sql_query("SELECT COUNT(DISTINCT user_id) as total FROM profiles", conn).iloc[0]['total']
        total_profiles = pd.read_sql_query("SELECT COUNT(*) as total FROM profiles", conn).iloc[0]['total']
        total_echos = pd.read_sql_query("SELECT COUNT(*) as total FROM echolalia_library", conn).iloc[0]['total']
        total_logs = pd.read_sql_query("SELECT COUNT(*) as total FROM sensory_logs", conn).iloc[0]['total']
        conn.close()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Usuários Ativos", total_users)
        col2.metric("Perfis Totais", total_profiles)
        col3.metric("Ecolalias Mapeadas", total_echos)
        col4.metric("Registros Sensoriais", total_logs)