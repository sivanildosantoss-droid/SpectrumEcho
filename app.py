import os
import json
import time
import streamlit as st
import pandas as pd
from google import genai
from report_generator import SpectrumEchoPDFGenerator

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SpectrumEcho - Governança Sensorial & TEA",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Email do Administrador Master
ADMIN_EMAIL = st.secrets.get("admin", {}).get("email", "sivanildo.santoss@gmail.com")

# -----------------------------------------------------------------------------
# SISTEMA DE PERSISTÊNCIA EM ARQUIVO LOCAL (JSON)
# -----------------------------------------------------------------------------
DB_FILE = "database.json"

def carregar_banco():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    
    dados_iniciais = {
        "profiles": [
            {"email": "sivanildo.santoss@gmail.com", "nome": "Murilo Ferreira", "idade": 8, "tipo": "Criança/Adolescente", "suporte": "Nível 2 (Moderado)"},
            {"email": "sivanildo.santoss@gmail.com", "nome": "Sivanildo Santos", "idade": 40, "tipo": "Adulto", "suporte": "Nível 1 (Leve)"}
        ],
        "ecolalias": [
            {
                "email": "sivanildo.santoss@gmail.com",
                "midia": "bob esponja",
                "frase": "patrick vamos caçar agua viva?",
                "traducao": "🔍 **Tradução Comportamental:** Expressa desejo de brincar, interação social direta e busca por companheirismo.\n💡 **Ação Recomendada:** Convidar para uma atividade lúdica compartilhada no mesmo tema."
            },
            {
                "email": "sivanildo.santoss@gmail.com",
                "midia": "galinha pintadinha",
                "frase": "o pintinho nao quer dormir",
                "traducao": "🔍 **Tradução Comportamental:** Indicativo de resistência ao sono, agitação motora ou sobrecarga sensorial ao deitar.\n💡 **Ação Recomendada:** Iniciar rotina de desaceleração com redução de luzes e sons ambiente."
            }
        ],
        "sensorial": []
    }
    salvar_banco(dados_iniciais)
    return dados_iniciais

def salvar_banco(dados):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"Erro ao salvar banco de dados: {e}")

global_db = carregar_banco()

# -----------------------------------------------------------------------------
# INICIALIZAÇÃO DE ESTADO (SESSION STATE)
# -----------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Inicio"

query_params = st.query_params
if "user_email" not in st.session_state:
    st.session_state.user_email = query_params.get("user_email", "")

if "sugestao_estrategia_temp" not in st.session_state:
    st.session_state.sugestao_estrategia_temp = ""

st.session_state.profiles_db = global_db["profiles"]
st.session_state.ecolalias_db = global_db["ecolalias"]
st.session_state.sensorial_db = global_db["sensorial"]

def atualizar_e_salvar():
    global_db["profiles"] = st.session_state.profiles_db
    global_db["ecolalias"] = st.session_state.ecolalias_db
    global_db["sensorial"] = st.session_state.sensorial_db
    salvar_banco(global_db)

# -----------------------------------------------------------------------------
# CONEXÃO COM O GEMINI (SDK MODERNO google-genai)
# -----------------------------------------------------------------------------
api_key = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY", "")

client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception:
        client = None

def chamar_ia_com_fallback(prompt, fallback_tipo="ecolalia"):
    if client:
        # Usando os nomes de modelos padrão oficiais da SDK google-genai
        modelos = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        for mod in modelos:
            try:
                response = client.models.generate_content(
                    model=mod,
                    contents=prompt
                )
                if response and hasattr(response, "text") and response.text:
                    return response.text.strip(), False
            except Exception as e:
                time.sleep(0.2)
                continue

    # Fallback caso a API falhe ou não esteja configurada
    if fallback_tipo == "ecolalia":
        return (
            "🔍 **Tradução Comportamental:** (Modo Contingência - Indisponibilidade Temporária da API)\n"
            "Esta ecolalia reflete uma tentativa legítima de autorregulação emocional, busca por previsibilidade ou expressão de interesse em um estímulo familiar.\n\n"
            "💡 **Ação Recomendada:** Acolha a fala com tom tranquilo, valide o sentimento demonstrado e ofereça um ambiente calmo."
        ), True
    else:
        return (
            "Estratégia sugerida (Modo Contingência): Reduza os estímulos sensoriais do ambiente (luzes e sons), "
            "fale em tom baixo e pausado, ofereça um objeto de conforto ou espaço seguro de descompressão."
        ), True

current_user = st.session_state.user_email.strip().lower()
is_admin = (current_user == ADMIN_EMAIL.strip().lower()) and (current_user != "")

# -----------------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("# 🧩 SpectrumEcho")
    st.caption("Plataforma Universal de Governança Sensorial")
    
    if st.button("🏠 Ir para Início / Apresentação", use_container_width=True):
        st.session_state.page = "Inicio"
        st.rerun()

    st.markdown("---")

    if client:
        st.success("Gemini AI: Conectado 🤖")
    else:
        st.error("Gemini AI: Não Configurado ⚠️")

    st.markdown("---")
    st.markdown("### 👤 Conta do Usuário")
    
    if st.session_state.user_email:
        st.markdown(f"**E-mail Ativo:**\n`{st.session_state.user_email}`")
        if is_admin:
            st.info("👑 **Modo Administrador**\n(Acesso e gerenciamento global ativado)")
        else:
            st.success("🔒 **Sessão Protegida**")
            
        if st.button("🚪 Sair / Logout", type="secondary", use_container_width=True):
            st.session_state.user_email = ""
            st.query_params.clear()
            st.rerun()
    else:
        email_input = st.text_input("Seu E-mail do Google:", placeholder="digite.seu.email@gmail.com")
        if email_input:
            user_e = email_input.strip().lower()
            st.session_state.user_email = user_e
            st.query_params["user_email"] = user_e
            st.rerun()
        st.warning("⚠️ Informe seu e-mail para carregar/salvar seus perfis.")

    st.markdown("---")
    st.markdown("### Navegação Principal:")
    
    opcoes_nav = {
        "Inicio": "🏠 Página Inicial (Apresentação)",
        "Gestao": "👤 Gestão de Perfis",
        "Ecolalias": "📚 Biblioteca de Ecolalias (com IA)",
        "Sensorial": "📝 Registro Sensorial",
        "Dashboard": "📊 Dashboard & Análise"
    }

    page_keys = list(opcoes_nav.keys())
    current_index = 0
    if st.session_state.page == "Gestao": current_index = 1
    elif st.session_state.page == "Ecolalias": current_index = 2
    elif st.session_state.page == "Sensorial": current_index = 3
    elif st.session_state.page == "Dashboard": current_index = 4

    selected = st.radio("Ir para:", options=page_keys, format_func=lambda x: opcoes_nav[x], index=current_index, label_visibility="collapsed")
    st.session_state.page = selected

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 12px;'>
            <p><b>SpectrumEcho v1.0</b></p>
            <p>© 2026 <b>Sivanildo Santos</b>.<br>Todos os direitos reservados.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------------------------------------------------------
# CONTEÚDO DAS PÁGINAS (COMPLETO)
# -----------------------------------------------------------------------------

if st.session_state.page == "Inicio":
    st.title("🧩 Bem-vindo ao SpectrumEcho")
    st.subheader("Plataforma Universal de Governança Sensorial e Tradução de Ecolalias")
    st.markdown("---")
    
    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        st.markdown("### 🎯 Propósito do Aplicativo")
        st.markdown(
            "O **SpectrumEcho** foi desenvolvido para auxiliar pais, familiares, educadores e profissionais de saúde "
            "na compreensão profunda do Transtorno do Espectro Autista (TEA), oferecendo ferramentas práticas para "
            "tradução de ecolalias, mapeamento de gatilhos sensoriais e relatórios analíticos estruturados."
        )
        st.markdown("### ✨ Funcionalidades Principais")
        st.markdown("- **Gestão de Perfis:** Cadastro individualizado por usuário e paciente.")
        st.markdown("- **Dicionário de Ecolalias:** Tradução comportamental instantânea baseada em inteligência artificial.")
        st.markdown("- **Registro Sensorial:** Acompanhamento de crises e estratégias de acolhimento.")
        st.markdown("- **Geração de Relatórios:** Exportação completa de dados analíticos em PDF.")
    
    with col_inf2:
        st.info(
            "💡 **Dica de Uso:**\n\n"
            "1. Insira seu e-mail na barra lateral para carregar seus dados.\n"
            "2. Cadastre os perfis dos dependentes ou pacientes na aba **Gestão de Perfis**.\n"
            "3. Utilize a **Biblioteca de Ecolalias** para registrar falas repetitivas e obter contexto comportamental imediato."
        )

elif st.session_state.page == "Gestao":
    st.title("👤 Gestão de Perfis")
    st.markdown("Gerencie os perfis atrelados à sua conta para personalização dos registros.")
    st.markdown("---")
    
    if not st.session_state.user_email:
        st.warning("⚠️ Por favor, digite seu e-mail do Google na barra lateral para gerenciar seus perfis.")
    else:
        col_cad, col_list = st.columns(2)
        with col_cad:
            st.markdown("### ➕ Adicionar Novo Perfil")
            with st.form("form_novo_perfil"):
                nome = st.text_input("Nome Completo / Apelido do Paciente:")
                idade = st.number_input("Idade:", min_value=1, max_value=120, value=8)
                tipo = st.selectbox("Tipo de Perfil:", ["Criança/Adolescente", "Adulto"])
                suporte = st.selectbox("Nível de Suporte (TEA):", ["Nível 1 (Leve)", "Nível 2 (Moderado)", "Nível 3 (Severo)"])
                
                submitted_perfil = st.form_submit_button("Salvar Perfil", type="primary")
                if submitted_perfil:
                    if nome.strip():
                        novo_p = {
                            "email": current_user,
                            "nome": nome.strip(),
                            "idade": idade,
                            "tipo": tipo,
                            "suporte": suporte
                        }
                        st.session_state.profiles_db.append(novo_p)
                        atualizar_e_salvar()
                        st.success(f"Perfil de **{nome}** cadastrado com sucesso!")
                        st.rerun()
                    else:
                        st.error("O nome do perfil não pode estar vazio.")

        with col_list:
            st.markdown("### 📋 Perfis Cadastrados")
            perfis_visiveis = st.session_state.profiles_db if is_admin else [p for p in st.session_state.profiles_db if p.get("email", "").lower() == current_user]
            
            if not perfis_visiveis:
                st.info("Nenhum perfil cadastrado ainda.")
            else:
                for idx, p in enumerate(perfis_visiveis):
                    with st.expander(f"👤 {p['nome']} ({p['tipo']})"):
                        st.write(f"**Idade:** {p['idade']} anos")
                        st.write(f"**Nível de Suporte:** {p['suporte']}")
                        st.write(f"**Proprietário:** `{p.get('email', 'Geral')}`")

elif st.session_state.page == "Ecolalias":
    st.title("📚 Dicionário de Tradução Ativa & Ecolalias")
    st.markdown("Traduza o significado comportamental de falas repetitivas com o auxílio da inteligência artificial.")
    st.markdown("---")
    
    if not st.session_state.user_email:
        st.warning("⚠️ Por favor, digite seu e-mail do Google na barra lateral para utilizar esta seção.")
    else:
        perfis_usuario = [p['nome'] for p in st.session_state.profiles_db if is_admin or p.get("email", "").lower() == current_user]
        perfil_selecionado = st.selectbox("Selecione o Perfil Associado:", perfis_usuario if perfis_usuario else ["Geral"])

        with st.form("form_ecolalia"):
            midia = st.text_input("Origem / Contexto (Ex: Mc Queen, Bob Esponja, Desenho, Diário):", placeholder="Ex: Mc Queen")
            frase = st.text_area("Frase / Fala Repetida (Ecolalia):", placeholder="Ex: Mamae cade o Mc Queen?")
            
            submitted_eco = st.form_submit_button("✨ Analisar com IA", type="primary")
            if submitted_eco:
                if frase.strip():
                    with st.spinner("🔄 A Inteligência Artificial está analisando o contexto comportamental..."):
                        prompt = (
                            "Você é um especialista clínico em Transtorno do Espectro Autista (TEA) e comunicação. "
                            f"Analise a seguinte ecolalia:\n"
                            f"- Origem/Mídia: {midia}\n"
                            f"- Frase repetida: '{frase}'\n\n"
                            "Forneça a resposta estritamente no seguinte formato visual limpo:\n"
                            "🔍 **Tradução Comportamental:** [Explique de forma empática e técnica o que essa ecolalia pode significar em termos de regulação, memória ou busca de conexão]\n\n"
                            "💡 **Ação Recomendada:** [Dê uma sugestão prática e acolhedora de como o cuidador deve responder ou agir no momento]"
                        )
                        analise_texto, is_contingency = chamar_ia_com_fallback(prompt, fallback_tipo="ecolalia")
                        
                        novo_registro = {
                            "email": current_user,
                            "perfil": perfil_selecionado,
                            "midia": midia.strip() if midia else "Geral",
                            "frase": frase.strip(),
                            "traducao": analise_texto
                        }
                        st.session_state.ecolalias_db.append(novo_registro)
                        atualizar_e_salvar()
                        st.success("Análise realizada e salva com sucesso!")
                        st.rerun()
                else:
                    st.error("Por favor, digite a frase repetida para análise.")

        st.markdown("---")
        st.markdown("### 🗂️ Ecolalias Salvas")
        ecolalias_visiveis = st.session_state.ecolalias_db if is_admin else [e for e in st.session_state.ecolalias_db if e.get("email", "").lower() == current_user]
        
        if not ecolalias_visiveis:
            st.info("Nenhuma ecolalia registrada até o momento.")
        else:
            for idx, eco in enumerate(ecolalias_visiveis):
                col_exp, col_act = st.columns([0.92, 0.08])
                with col_exp:
                    titulo_exp = f"🎬 {eco.get('midia', 'Geral')} — \"{eco.get('frase', '')}\""
                    with st.expander(titulo_exp):
                        st.markdown(eco.get('traducao', 'Sem tradução.'))
                        st.caption(f"Perfil vinculado: {eco.get('perfil', 'Geral')} | Registrado por: {eco.get('email', '')}")
                with col_act:
                    if st.button("🗑️", key=f"del_eco_{idx}", help="Excluir este registro"):
                        st.session_state.ecolalias_db.remove(eco)
                        atualizar_e_salvar()
                        st.rerun()

elif st.session_state.page == "Sensorial":
    st.title("📝 Registro Sensorial & Crises")
    st.markdown("Mapeie gatilhos, comportamentos e receba orientações rápidas para manejo de sobrecarga sensorial.")
    st.markdown("---")
    
    if not st.session_state.user_email:
        st.warning("⚠️ Por favor, digite seu e-mail do Google na barra lateral para utilizar esta seção.")
    else:
        gatilho_in = st.text_input("Gatilho Identificado (Ex: Barulho alto, Luz intensa, Transição brusca):")
        comportamento_in = st.text_area("Manifestação Comportamental (Ex: Agitação, silêncio seletivo, ecolalia persistente):")
        intensidade_in = st.select_slider("Nível de Intensidade:", options=["Leve", "Moderado", "Severo"])
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🤖 Sugerir Estratégia de Ação com IA", type="secondary", use_container_width=True):
                with st.spinner("Gerando estratégia..."):
                    prompt_sens = (
                        "Você é um terapeuta comportamental especialista em TEA. "
                        f"Gatilho: {gatilho_in}. Comportamento: {comportamento_in}. Intensidade: {intensidade_in}. "
                        "Forneça uma orientação direta, prática e humanizada de acolhimento imediato em até 3 frases."
                    )
                    sugestao_obtida, _ = chamar_ia_com_fallback(prompt_sens, fallback_tipo="sensorial")
                    st.session_state.sugestao_estrategia_temp = sugestao_obtida
                    st.success("Estratégia sugerida carregada abaixo!")

        estrategia_in = st.text_area("Estratégia de Manejo / Acolhimiento Aplicada:", value=st.session_state.sugestao_estrategia_temp, placeholder="Descreva ou ajuste a conduta adotada...")
        
        if st.button("💾 Salvar Registro Sensorial", type="primary"):
            if gatilho_in.strip() or comportamento_in.strip():
                novo_sens = {
                    "email": current_user,
                    "gatilho": gatilho_in,
                    "comportamento": comportamento_in,
                    "intensidade": intensidade_in,
                    "estrategia": estrategia_in
                }
                st.session_state.sensorial_db.append(novo_sens)
                st.session_state.sugestao_estrategia_temp = ""
                atualizar_e_salvar()
                st.success("Registro sensorial salvo com sucesso!")
                st.rerun()
            else:
                st.error("Preencha pelo menos o gatilho ou o comportamento.")

        st.markdown("---")
        st.markdown("### ⚡ Histórico de Ocorrências Sensoriais")
        registros_visiveis = st.session_state.sensorial_db if is_admin else [s for s in st.session_state.sensorial_db if s.get("email", "").lower() == current_user]
        
        if not registros_visiveis:
            st.info("Nenhum registro sensorial cadastrado.")
        else:
            for idx_s, s in enumerate(registros_visiveis):
                with st.expander(f"⚡ Gatilho: {s.get('gatilho', 'Geral')} [{s.get('intensidade', 'Leve')}]"):
                    st.write(f"**Comportamento:** {s.get('comportamento', '')}")
                    st.write(f"**Estratégia aplicada:** {s.get('estrategia', '')}")

elif st.session_state.page == "Dashboard":
    st.title("📊 Dashboard & Análise Consolidada")
    st.markdown("Visualize métricas gerais e exporte relatórios gerenciais completos.")
    st.markdown("---")
    
    if not st.session_state.user_email:
        st.warning("⚠️ Por favor, digite seu e-mail do Google na barra lateral para acessar o dashboard.")
    else:
        user_ecos = [e for e in st.session_state.ecolalias_db if is_admin or e.get("email") == current_user]
        user_sens = [s for s in st.session_state.sensorial_db if is_admin or s.get("email") == current_user]
        user_profs = [p for p in st.session_state.profiles_db if is_admin or p.get("email") == current_user]

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total de Ecolalias", len(user_ecos))
        col_m2.metric("Registros Sensoriais", len(user_sens))
        col_m3.metric("Perfis Vinculados", len(user_profs))

        st.markdown("---")
        st.markdown("### 📄 Geração de Relatório Profissional em PDF")
        st.markdown("Clique no botão abaixo para compilar todos os dados em um relatório estruturado pronto para impressão ou envio clínico.")
        
        if st.button("🚀 Gerar Relatório Completo em PDF", type="primary"):
            try:
                primary_profile = user_profs[0] if user_profs else {"nome": "Paciente", "tipo": "Criança"}
                sensory_logs = [{"stress_level_0_to_100": 50, "triggers": ["Ecolalia"], "behavioral_manifestation": {"echolalia_phrase": e.get("frase"), "media_source": e.get("midia")}} for e in user_ecos]
                
                report_payload = {
                    "user_profile": {"patient_id": current_user, "name": primary_profile.get("nome"), "mode": "Criança"},
                    "sensory_and_emotional_logs": sensory_logs,
                    "adult_masking_metrics": {"social_drain_score": 40, "reactivity_pico_0_100": 50, "isolation_needed_minutes": 30}
                }
                
                pdf_gen = SpectrumEchoPDFGenerator(json.dumps(report_payload, ensure_ascii=False))
                pdf_gen.generate()
                
                with open("relatorio_spectrumecho.pdf", "rb") as f:
                    st.download_button(
                        label="⬇️ Baixar Relatório em PDF",
                        data=f,
                        file_name="relatorio_spectrumecho.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Erro ao gerar o PDF do relatório: {e}")