import os
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
# INICIALIZAÇÃO DE ESTADO (SESSION STATE)
# -----------------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Inicio"

if "user_email" not in st.session_state:
    query_params = st.query_params
    st.session_state.user_email = query_params.get("user_email", "")

# Banco de dados simulado em SessionState com vinculação por e-mail (Isolamento de Dados)
if "profiles_db" not in st.session_state:
    st.session_state.profiles_db = [
        {"email": "sivanildo.santoss@gmail.com", "nome": "Murilo Ferreira", "idade": 8, "tipo": "Criança/Adolescente", "suporte": "Nível 2 (Moderado)"},
        {"email": "sivanildo.santoss@gmail.com", "nome": "Sivanildo Santos", "idade": 40, "tipo": "Adulto", "suporte": "Nível 1 (Leve)"}
    ]

if "ecolalias_db" not in st.session_state:
    st.session_state.ecolalias_db = [
        {
            "email": "sivanildo.santoss@gmail.com",
            "midia": "bob esponja",
            "frase": "patrick vamos caçar agua viva?",
            "traducao": "Expressa desejo de brincar, interação social direta e busca por companheirismo.",
            "acao": "Convidar a criança para uma atividade lúdica compartilhada no mesmo tema."
        },
        {
            "email": "sivanildo.santoss@gmail.com",
            "midia": "galinha pintadinha",
            "frase": "o pintinho nao quer dormir",
            "traducao": "Indicativo de resistência ao sono, agitação motora ou sobrecarga sensorial ao deitar.",
            "acao": "Iniciar rotina de desaceleração com redução de luzes e sons ambiente."
        },
        {
            "email": "sivanildo.santoss@gmail.com",
            "midia": "mc queen",
            "frase": "mamae cade o mc qeen? mamae cade o mc queen?",
            "traducao": "Expressa busca por previsibilidade, estranhamento com mudança no ambiente ou ansiedade por perda de objeto/rotina de interesse.",
            "acao": "Mostrar à criança onde as coisas estão ou reestabelecer o elemento de segurança visualmente."
        }
    ]

if "sensorial_db" not in st.session_state:
    st.session_state.sensorial_db = []

# -----------------------------------------------------------------------------
# CONEXÃO COM O GEMINI
# -----------------------------------------------------------------------------
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        client = None

# Verificação se o usuário atual é o Administrador
current_user = st.session_state.user_email.strip().lower()
is_admin = (current_user == ADMIN_EMAIL.strip().lower()) and (current_user != "")

# -----------------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("# 🧩 SpectrumEcho")
    st.caption("Plataforma Universal de Governança Sensorial")
    
    # Botão de retorno rápido para a Home
    if st.button("🏠 Ir para Início / Apresentação", use_container_width=True):
        st.session_state.page = "Inicio"
        st.rerun()

    st.markdown("---")

    # Status da IA
    if client:
        st.success("Gemini AI: Conectado 🤖")
    else:
        st.error("Gemini AI: Não Configurado ⚠️")

    st.markdown("---")

    # ÁREA DE AUTENTICAÇÃO E IDENTIFICAÇÃO (LOGIN & LOGOUT)
    st.markdown("### 👤 Conta do Usuário")
    
    if st.session_state.user_email:
        st.markdown(f"**E-mail Ativo:**\n`{st.session_state.user_email}`")
        
        if is_admin:
            st.info("👑 **Modo Administrador**\n(Acesso e gerenciamento global ativado)")
        else:
            st.success("🔒 **Sessão Protegida**\n(Seus dados estão visíveis apenas para você)")
            
        # Botão de Logout
        if st.button("🚪 Sair / Logout", type="secondary", use_container_width=True):
            st.session_state.user_email = ""
            st.query_params.clear()
            st.rerun()
    else:
        email_input = st.text_input(
            "Seu E-mail do Google:",
            value="",
            placeholder="digite.seu.email@gmail.com",
            help="Pressione Enter após digitar seu e-mail para conectar."
        )
        if email_input:
            st.session_state.user_email = email_input.strip()
            st.query_params["user_email"] = email_input.strip()
            st.rerun()
            
        st.warning("⚠️ Informe seu e-mail para carregar/salvar seus perfis de forma privativa.")

    st.markdown("---")

    # MENU DE NAVEGAÇÃO
    st.markdown("### Navegação:")
    
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

    selected = st.radio(
        "Ir para:",
        options=page_keys,
        format_func=lambda x: opcoes_nav[x],
        index=current_index,
        label_visibility="collapsed"
    )
    st.session_state.page = selected

# -----------------------------------------------------------------------------
# CONTEÚDO DAS PÁGINAS
# -----------------------------------------------------------------------------

# --- PÁGINA 1: INÍCIO / APRESENTAÇÃO ---
if st.session_state.page == "Inicio":
    st.title("🧩 Bem-vindo ao SpectrumEcho")
    st.subheader("Plataforma Universal de Governança Sensorial e Tradução de Ecolalias")

    st.markdown("---")
    
    col_about, col_info = st.columns([2, 1])

    with col_about:
        st.markdown("""
        ### 🎯 Propósito do Aplicativo
        O **SpectrumEcho** é uma solução criada para apoiar pais, familiares, cuidadores e terapeutas de pessoas no **Transtorno do Espectro Autista (TEA)**.
        
        Muitas vezes, falas repetitivas ou tiradas de desenhos, filmes e vídeos (**ecolalias**) não são apenas repetições sem sentido. Elas são formas legítimas de comunicação, autorregulação emocional e expressão de necessidades sensoriais.

        ### 🤖 Inteligência Artificial Especializada em TEA
        A plataforma conta com a integração da **Inteligência Artificial Gemini**, treinada sob diretrizes e diretivas especializadas em TEA para:
        * **Traduzir o Contexto:** Explicar o sentimento ou necessidade por trás da ecolalia.
        * **Sugerir Ações Práticas:** Orientar a família sobre como reagir no momento da crise ou autorregulação.
        * **Gerar Relatórios Estruturados:** Facilitar o diálogo com fonoaudiólogos, psicólogos e médicos.
        """)

    with col_info:
        st.info("""
        ### 🔒 Privacidade de Dados
        * **Isolamento por E-mail:** Apenas você tem acesso aos seus perfis e ecolalias registradas.
        * **Histórico Seguro:** Digite seu e-mail no menu lateral para acessar suas informações de qualquer dispositivo.
        """)
        st.success("""
        ### 🚀 Dica de Uso Rápido:
        1. Digite seu e-mail no menu lateral e pressione Enter.
        2. Acesse **Gestão de Perfis** para criar o cadastro.
        3. Vá até a **Biblioteca de Ecolalias** e faça sua primeira consulta com a IA!
        """)

# --- PÁGINA 2: GESTÃO DE PERFIS ---
elif st.session_state.page == "Gestao":
    st.title("👤 Gestão de Perfis")
    st.write("Gerencie os perfis para personalizar o acompanhamento individualizado.")

    if not st.session_state.user_email:
        st.warning("⚠️ Para visualizar ou criar perfis, por favor digite seu e-mail no menu lateral esquerdo.")
    else:
        col_cad, col_list = st.columns([1, 1])

        with col_cad:
            st.markdown("### Adicionar Novo Perfil")
            with st.form("form_novo_perfil"):
                nome = st.text_input("Nome Completo / Apelido:")
                idade = st.number_input("Idade:", min_value=1, max_value=100, value=8)
                tipo = st.selectbox("Tipo de Perfil:", ["Criança/Adolescente", "Adulto"])
                suporte = st.selectbox("Nível de Suporte (TEA):", ["Nível 1 (Leve)", "Nível 2 (Moderado)", "Nível 3 (Severo)"])
                
                btn_salvar = st.form_submit_button("➕ Salvar Perfil", type="primary")

                if btn_salvar:
                    if nome.strip():
                        st.session_state.profiles_db.append({
                            "email": current_user,
                            "nome": nome.strip(),
                            "idade": idade,
                            "tipo": tipo,
                            "suporte": suporte
                        })
                        st.success(f"Perfil de **{nome}** salvo com sucesso!")
                        st.rerun()
                    else:
                        st.error("Por favor, preencha o nome do perfil.")

        with col_list:
            st.markdown("### Perfis Cadastrados")

            # Filtro de Privacidade: Admin vê todos, usuário comum vê apenas os dele
            if is_admin:
                perfis_visiveis = st.session_state.profiles_db
                st.caption("👑 Visão de Administrador: Exibindo todos os perfis registrados no sistema.")
            else:
                perfis_visiveis = [p for p in st.session_state.profiles_db if p.get("email") == current_user]

            if not perfis_visiveis:
                st.info("Nenhum perfil cadastrado para a sua conta até o momento.")
            else:
                for idx, p in enumerate(perfis_visiveis):
                    dono_tag = f" — *(Dono: {p['email']})*" if is_admin else ""
                    with st.expander(f"📌 {p['nome']} ({p['tipo']} - {p['idade']} anos){dono_tag}"):
                        st.write(f"**Nível de Suporte:** {p['suporte']}")
                        st.write(f"**Conta Vinculada:** {p.get('email', 'Não informada')}")

# --- PÁGINA 3: BIBLIOTECA DE ECOLALIAS ---
elif st.session_state.page == "Ecolalias":
    st.title("📚 Dicionário de Tradução Ativa & Ecolalias")
    st.write("Consulte a Inteligência Artificial especializada para decodificar ecolalias e falas repetitivas.")

    if not st.session_state.user_email:
        st.warning("⚠️ Digite seu e-mail no menu lateral para acessar a biblioteca e salvar traduções.")
    else:
        # Seleção de Perfil para a Ecolalia
        perfis_usuario = [p['nome'] for p in st.session_state.profiles_db if is_admin or p.get("email") == current_user]
        if perfis_usuario:
            perfil_selecionado = st.selectbox("Selecione o Perfil:", perfis_usuario)
        else:
            st.info("💡 Recomendado: Cadastre um perfil na aba 'Gestão de Perfis' antes de traduzir.")
            perfil_selecionado = "Geral"

        st.markdown("---")
        
        with st.expander("✨ Analisar e Traduzir Nova Ecolalia", expanded=True):
            with st.form("form_ecolalia"):
                midia = st.text_input("Origem (ex: Roblox, Peppa Pig, Vídeo do YT):", placeholder="Ex: Mc Queen, Bob Esponja")
                frase = st.text_area("Frase / Fala Repetida:", placeholder="Ex: mamae cade o mc queen? mamae cade o mc queen?")
                btn_analisar = st.form_submit_button("✨ Analisar e Traduzir com Inteligência Artificial", type="primary")

            if btn_analisar:
                if not frase.strip():
                    st.warning("Por favor, digite a frase da ecolalia para ser analisada.")
                elif not client:
                    st.error("Chave de API do Gemini não configurada ou inválida.")
                else:
                    with st.spinner("IA Especialista em TEA analisando o contexto comportamental..."):
                        prompt = f"""Você é uma Inteligência Artificial especialista em Transtorno do Espectro Autista (TEA), Análise do Comportamento e Comunicação Alternativa.
                        Analise a seguinte fala repetitiva/ecolalia dita por uma pessoa autista:

                        - Mídia/Contexto de Origem: {midia}
                        - Frase Emitida: "{frase}"

                        Forneça a análise estritamente no seguinte formato:
                        🔍 **Tradução Comportamental:** (Explique o sentimento, necessidade de autorregulação ou intenção comunicativa)
                        💡 **Ação Recomendada:** (Ação prática e acolhedora para o cuidador/terapeuta)
                        """
                        
                        analise_texto = None
                        ultimo_erro = None

                        # Lista prioritária de nomes aceitos na API oficial
                        modelos_tentativa = ["gemini-2.0-flash", "gemini-1.5-flash-8b", "gemini-2.5-flash"]
                        
                        # Tenta buscar os modelos disponíveis na própria chave do usuário se os estáticos falharem
                        for mod in modelos_tentativa:
                            try:
                                response = client.models.generate_content(
                                    model=mod,
                                    contents=prompt
                                )
                                if response and response.text:
                                    analise_texto = response.text
                                    break
                            except Exception as e:
                                ultimo_erro = e
                                continue

                        # Se ainda não funcionou, faz busca dinâmica nos modelos autorizados da chave
                        if not analise_texto:
                            try:
                                for m in client.models.list():
                                    mod_name = m.name.replace("models/", "")
                                    if "generateContent" in getattr(m, "supported_generation_methods", []) or "flash" in mod_name or "pro" in mod_name:
                                        try:
                                            response = client.models.generate_content(
                                                model=mod_name,
                                                contents=prompt
                                            )
                                            if response and response.text:
                                                analise_texto = response.text
                                                break
                                        except Exception:
                                            continue
                            except Exception as e:
                                ultimo_erro = e

                        if analise_texto:
                            st.session_state.ecolalias_db.append({
                                "email": current_user,
                                "perfil": perfil_selecionado,
                                "midia": midia,
                                "frase": frase,
                                "traducao": analise_texto
                            })
                            st.success("Ecolalia analisada e salva no seu dicionário!")
                            st.rerun()
                        else:
                            st.error(f"Erro na chamada da API do Gemini: {ultimo_erro}")

        st.markdown("---")
        st.markdown("### Dicionário de Ecolalias Salvas")

        if is_admin:
            ecolalias_visiveis = st.session_state.ecolalias_db
        else:
            ecolalias_visiveis = [e for e in st.session_state.ecolalias_db if e.get("email") == current_user]

        if not ecolalias_visiveis:
            st.info("Nenhuma ecolalia cadastrada para a sua conta ainda.")
        else:
            for idx, eco in enumerate(ecolalias_visiveis):
                col_exp, col_act = st.columns([0.92, 0.08])
                with col_exp:
                    dono_str = f" [{eco.get('email')}]" if is_admin else ""
                    with st.expander(f"🎬 {eco['midia']} — \"{eco['frase']}\"{dono_str}"):
                        st.markdown(f"{eco['traducao']}")
                with col_act:
                    if st.button("🗑️", key=f"del_eco_{idx}"):
                        st.session_state.ecolalias_db.remove(eco)
                        st.rerun()

# --- PÁGINA 4: REGISTRO SENSORIAL ---
elif st.session_state.page == "Sensorial":
    st.title("📝 Registro Sensorial & Crises")
    st.write("Acompanhe episódios de sobrecarga, autorregulação e gatilhos sensoriais.")

    if not st.session_state.user_email:
        st.warning("⚠️ Digite seu e-mail no menu lateral para acessar os registros sensoriais.")
    else:
        with st.form("form_sensorial"):
            st.markdown("### Novo Registro Sensorial")
            gatilho = st.text_input("Gatilho Identificado (ex: Som alto, Luz forte, Mudança na rotina):")
            comportamento = st.text_area("Comportamento Observado:")
            intensidade = st.select_slider("Nível de Sobrecarga/Intensidade:", options=["Leve", "Moderado", "Severo"])
            estrategia = st.text_input("Estratégia de Autorregulação Utilizada (ex: Fone abafador, Espaço calmo):")
            
            btn_sensorial = st.form_submit_button("💾 Salvar Registro Sensorial", type="primary")

            if btn_sensorial:
                if comportamento.strip():
                    st.session_state.sensorial_db.append({
                        "email": current_user,
                        "gatilho": gatilho,
                        "comportamento": comportamento,
                        "intensidade": intensidade,
                        "estrategia": estrategia
                    })
                    st.success("Registro sensorial salvo com sucesso!")
                    st.rerun()
                else:
                    st.error("Por favor, descreva o comportamento observado.")

        st.markdown("---")
        st.markdown("### Histórico Sensorial")

        if is_admin:
            registros_visiveis = st.session_state.sensorial_db
        else:
            registros_visiveis = [s for s in st.session_state.sensorial_db if s.get("email") == current_user]

        if not registros_visiveis:
            st.info("Nenhum registro sensorial anotado para esta conta.")
        else:
            for idx, s in enumerate(registros_visiveis):
                dono_txt = f" ({s.get('email')})" if is_admin else ""
                with st.expander(f"⚡ Gatilho: {s['gatilho']} | Intensidade: {s['intensidade']}{dono_txt}"):
                    st.write(f"**Comportamento:** {s['comportamento']}")
                    st.write(f"**Estratégia Utilizada:** {s['estrategia']}")

# --- PÁGINA 5: DASHBOARD & ANÁLISE ---
elif st.session_state.page == "Dashboard":
    st.title("📊 Dashboard & Relatórios Estruturados")
    st.write("Gere relatórios completos para apresentação em consultas médicas ou terapêuticas.")

    if not st.session_state.user_email:
        st.warning("⚠️ Digite seu e-mail no menu lateral para gerar seus relatórios.")
    else:
        # Filtrar dados do usuário atual
        user_ecos = [e for e in st.session_state.ecolalias_db if is_admin or e.get("email") == current_user]
        user_sens = [s for s in st.session_state.sensorial_db if is_admin or s.get("email") == current_user]

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Total de Ecolalias Traduzidas", len(user_ecos))
        with col_m2:
            st.metric("Registros Sensoriais", len(user_sens))

        st.markdown("---")
        st.markdown("### Exportar Relatório Oficial (PDF)")
        st.write("O relatório reúne o histórico de ecolalias traduzidas e observações sensoriais vinculadas à sua conta.")

        if st.button("📄 Gerar Relatório Completo em PDF", type="primary"):
            try:
                pdf = SpectrumEchoPDFGenerator()
                filename = pdf.generate(st.session_state.user_email, user_ecos)
                with open(filename, "rb") as f:
                    st.download_button(
                        label="⬇️ Baixar Relatório em PDF",
                        data=f,
                        file_name=filename,
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Erro ao gerar relatório em PDF: {e}")