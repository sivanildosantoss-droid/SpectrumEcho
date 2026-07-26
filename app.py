import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import json

# Importação da nossa Engine de PDF
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
        /* Estilização Geral do Fundo e Fontes */
        .main {
            background-color: #0f172a;
        }
        
        /* Títulos Principais em Destaque Neon Suave */
        h1, h2, h3 {
            color: #38bdf8 !important;
            font-weight: 600 !important;
        }

        /* Cartões de Conteúdo e Formet */
        div[data-testid="stForm"] {
            border: 1px solid #1e293b !important;
            border-radius: 12px !important;
            padding: 20px !important;
            background-color: #1e293b !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }

        /* Expander Estilizado */
        .streamlit-expanderHeader {
            background-color: #1e293b !important;
            border-radius: 8px !important;
            color: #f8fafc !important;
        }

        /* Botões Estilizados */
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
# MOTOR DE TRADUÇÃO COMPORTAMENTAL (SPECTRUM-ECHO ENGINE)
# ---------------------------------------------------------
def generate_behavioral_translation(phrase, media_title):
    """
    Analisa a estrutura da frase/ecolalia e retorna uma tradução 
    comportamental automática orientada para a família e terapeutas.
    """
    phrase_lower = phrase.lower()
    
    if "sumiu" in phrase_lower or "cade" in phrase_lower or "onde" in phrase_lower:
        return (
            "🔍 **Tradução:** Expressa busca por previsibilidade, estranhamento com mudança no ambiente ou ansiedade por perda de objeto/rotina de interesse.\n"
            "💡 **Ação Recomendada:** Mostrar à criança onde as coisas estão ou reestabelecer o elemento de segurança visualmente."
        )
    elif "doente" in phrase_lower or "machucou" in phrase_lower or "quebrou" in phrase_lower:
        return (
            "⚠️ **Tradução:** Expressa desconforto sensorial físico, medo, sobrecarga ou mal-estar interno que a criança não sabe nomear diretamente.\n"
            "💡 **Ação Recomendada:** Verificar estímulos do ambiente (som, luz, fome, cansaço) e oferecer um local de descompressão."
        )
    elif "fora dos trilhos" in phrase_lower or "perigo" in phrase_lower or "socorro" in phrase_lower:
        return (
            "🚨 **Tradução:** Expressa sensação de descontrole, quebra severa de expectativa ou pico de sobrecarga sensorial iminente.\n"
            "💡 **Ação Recomendada:** Reduzir ruídos, afastar estímulos externos e manter tom de voz calmo sem fazer cobranças."
        )
    else:
        return (
            f"🎬 **Tradução:** Ecolalia funcional associada à mídia '{media_title}'. Usada pela criança para autorregulação, validação emocional ou tentativa de iniciar interação através de um tema de hiperfoco.\n"
            "💡 **Ação Recomendada:** Entrar no contexto do desenho com tom acolhedor para validar a comunicação."
        )

# ---------------------------------------------------------
# BANCO DE DADOS (SQLite Persistente + Funções CRUD)
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            profile_type TEXT,
            support_level INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS echolalia_library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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

def get_profiles():
    conn = sqlite3.connect("spectrumecho.db")
    df = pd.read_sql_query("SELECT * FROM profiles", conn)
    conn.close()
    return df

def delete_profile(profile_id):
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
    cursor.execute("DELETE FROM echolalia_library WHERE profile_id = ?", (profile_id,))
    cursor.execute("DELETE FROM sensory_logs WHERE profile_id = ?", (profile_id,))
    conn.commit()
    conn.close()

def add_profile(name, age, profile_type, support_level):
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO profiles (name, age, profile_type, support_level) VALUES (?, ?, ?, ?)",
        (name, age, profile_type, support_level)
    )
    conn.commit()
    conn.close()

def add_echolalia(profile_id, media_title, phrase, meaning_context):
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO echolalia_library (profile_id, media_title, phrase, meaning_context) VALUES (?, ?, ?, ?)",
        (profile_id, media_title, phrase, meaning_context)
    )
    conn.commit()
    conn.close()

def delete_echolalia(echo_id):
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM echolalia_library WHERE id = ?", (echo_id,))
    conn.commit()
    conn.close()

def get_echolalias(profile_id):
    conn = sqlite3.connect("spectrumecho.db")
    df = pd.read_sql_query("SELECT * FROM echolalia_library WHERE profile_id = ?", conn, params=(profile_id,))
    conn.close()
    return df

def save_log(profile_id, stress_level, triggers, notes):
    conn = sqlite3.connect("spectrumecho.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sensory_logs (profile_id, timestamp, stress_level, triggers, notes) VALUES (?, ?, ?, ?, ?)",
        (profile_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), stress_level, ", ".join(triggers), notes)
    )
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# INTERFACE DO USUÁRIO
# ---------------------------------------------------------
st.sidebar.title("🧩 SpectrumEcho")
st.sidebar.caption("Plataforma Universal de Governança Sensorial")

module = st.sidebar.radio(
    "Navegação:",
    ["👤 Gestão de Perfis", "📚 Biblioteca de Ecolalias", "📝 Registro Sensorial", "📊 Dashboard & Análise"]
)

# --- MÓDULO 1: GESTÃO DE PERFIS ---
if module == "👤 Gestão de Perfis":
    st.header("👤 Perfis Cadastrados")
    st.write("Gerencie os perfis para personalizar o acompanhamento individual.")

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
                add_profile(name, age, p_type, support_level)
                st.success(f"Perfil de '{name}' cadastrado!")
                st.rerun()

    with col_list:
        st.subheader("Perfis Ativos")
        profiles_df = get_profiles()
        if profiles_df.empty:
            st.info("Nenhum perfil cadastrado ainda.")
        else:
            for idx, row in profiles_df.iterrows():
                with st.expander(f"📌 {row['name']} ({row['profile_type']} - {row['age']} anos)"):
                    st.write(f"**Nível de Suporte:** TEA Nível {row['support_level']}")
                    st.write(f"**ID do Sistema:** {row['id']}")
                    if st.button(f"🗑️ Excluir Perfil {row['name']}", key=f"del_prof_{row['id']}"):
                        delete_profile(row['id'])
                        st.warning("Perfil e dados associados removidos!")
                        st.rerun()

# --- MÓDULO 2: BIBLIOTECA DE ECOLALIAS ---
elif module == "📚 Biblioteca de Ecolalias":
    st.header("📚 Dicionário & Tradutor de Ecolalias")
    st.write("Digite a frase que a criança repete para o sistema gerar a interpretação e orientação para os pais.")

    profiles_df = get_profiles()
    if profiles_df.empty:
        st.warning("Cadastre ao menos um perfil na aba 'Gestão de Perfis' primeiro.")
    else:
        profile_map = {f"{row['name']} (ID: {row['id']})": row['id'] for idx, row in profiles_df.iterrows()}
        selected_label = st.selectbox("Selecione o Perfil:", list(profile_map.keys()))
        selected_id = profile_map[selected_label]

        with st.form("add_echo_form"):
            st.subheader("Cadastrar & Traduzir Ecolalia")
            media_title = st.text_input("Mídias / Desenho de Origem", placeholder="Ex: Bob Esponja, Roblox, McQueen...")
            phrase = st.text_input("Frase Repetida Pela Criança", placeholder="Ex: 'Patrick cadê o Bob Esponja?' ou 'O Mcqueen esta doente?'")
            user_meaning = st.text_area("Observação do Pai/Mãe (Opcional - Deixe em branco para o app traduzir):")
            
            submit_echo = st.form_submit_button("🤖 Traduzir & Salvar no Dicionário")
            if submit_echo and phrase:
                final_meaning = user_meaning if user_meaning.strip() else generate_behavioral_translation(phrase, media_title)
                add_echolalia(selected_id, media_title, phrase, final_meaning)
                st.success("Ecolalia traduzida e cadastrada no dicionário!")
                st.rerun()

        st.divider()
        st.subheader("Dicionário & Tradução Ativa:")
        
        echos_df = get_echolalias(selected_id)
        if echos_df.empty:
            st.info("Nenhuma ecolalia cadastrada para este perfil ainda.")
        else:
            for idx, row in echos_df.iterrows():
                col_exp, col_btn = st.columns([5, 1])
                with col_exp:
                    with st.expander(f"🎬 {row['media_title']} — \"{row['phrase']}\""):
                        st.markdown(f"{row['meaning_context']}")
                with col_btn:
                    if st.button("🗑️", key=f"del_echo_{row['id']}", help="Excluir ecolalia"):
                        delete_echolalia(row['id'])
                        st.rerun()

# --- MÓDULO 3: REGISTRO SENSORIAL ---
elif module == "📝 Registro Sensorial":
    st.header("📝 Registro de Estresse & Eventos")
    
    profiles_df = get_profiles()
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
            save_log(selected_id, stress, triggers, notes)
            st.success("Registro diário salvo com sucesso!")

# --- MÓDULO 4: DASHBOARD & ANÁLISE ---
elif module == "📊 Dashboard & Análise":
    st.header("📊 Análise Sensorial & Gerador de Relatório PDF")
    
    profiles_df = get_profiles()
    if profiles_df.empty:
        st.info("Cadastre ao menos um perfil para visualizar as análises.")
    else:
        profile_map = {f"{row['name']} (ID: {row['id']})": (row['id'], row['name'], row['profile_type']) for idx, row in profiles_df.iterrows()}
        selected_label = st.selectbox("Selecione o Perfil para Análise:", list(profile_map.keys()))
        selected_id, selected_name, selected_type = profile_map[selected_label]

        conn = sqlite3.connect("spectrumecho.db")
        logs_df = pd.read_sql_query(
            "SELECT timestamp as Data_Hora, stress_level as Estresse, triggers as Gatilhos, notes as Observacoes FROM sensory_logs WHERE profile_id = ? ORDER BY timestamp ASC",
            conn,
            params=(selected_id,)
        )
        conn.close()

        if logs_df.empty:
            st.info(f"Ainda não há registros sensoriais salvos para {selected_name}. Faça alguns registros na aba '📝 Registro Sensorial'.")
        else:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("📈 Curva de Sobrecarga Sensorial")
                st.line_chart(logs_df, x="Data_Hora", y="Estresse")

            with col_chart2:
                st.subheader("📊 Nível Médio de Estresse")
                avg_stress = logs_df["Estresse"].mean()
                st.metric(label="Média de Estresse Registrada", value=f"{avg_stress:.1f} / 100")
                
                if avg_stress > 70:
                    st.error("⚠️ Alerta: Média de estresse elevada! Recomendado período de descompressão.")
                elif avg_stress > 40:
                    st.warning("⚡ Estresse moderado. Fique atento aos gatilhos frequentes.")
                else:
                    st.success("✅ Estresse sob controle.")

            st.divider()
            st.subheader("📋 Tabela de Eventos Gravados")
            st.dataframe(logs_df, use_container_width=True)

            st.divider()
            st.subheader("📄 Relatório Oficial para Médicos e Terapeutas")
            st.write("Gere um documento em PDF estruturado para levar às consultas de acompanhamento.")

            if st.button("📄 Gerar e Baixar Relatório PDF"):
                echos_df = get_echolalias(selected_id)
                
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
                st.success("Relatório PDF pronto para download!")