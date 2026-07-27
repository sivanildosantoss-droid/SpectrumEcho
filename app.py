import os
import json
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
# ARMAZENAMENTO PERSISTENTE ENTRE SESSÕES (CACHE GLOBAL DE DADOS)
# -----------------------------------------------------------------------------
@st.cache_resource
def get_global_db():
    return {
        "profiles": [
            {"email": "sivanildo.santoss@gmail.com", "nome": "Murilo Ferreira", "idade": 8, "tipo": "Criança/Adolescente", "suporte": "Nível 2 (Moderado)"},
            {"email": "sivanildo.santoss@gmail.com", "nome": "Sivanildo Santos", "idade": 40, "tipo": "Adulto", "suporte": "Nível 1 (Leve)"}
        ],
        "ecolalias": [
            {
                "email": "sivanildo.santoss@gmail.com",
                "midia": "bob esponja",
                "frase": "patrick vamos caçar agua viva?",
                "traducao": "🔍 **Tradução Comportamental:** Expressa desejo de brincar, interação social direta e busca por companheirismo.\n💡 **Ação Recomendada:** Convidar para uma atividade lúdica compartilhada no mesmo tema.",
                "acao": "Convidar a criança para uma atividade lúdica compartilhada no mesmo tema."
            },
            {
                "email": "sivanildo.santoss@gmail.com",
                "midia": "galinha pintadinha",
                "frase": "o pintinho nao quer dormir",
                "traducao": "🔍 **Tradução Comportamental:** Indicativo de resistência ao sono, agitação motora ou sobrecarga sensorial ao deitar.\n💡 **Ação Recomendada:** Iniciar rotina de desaceleração com redução de luzes e sons ambiente.",
                "acao": "Iniciar rotina de desaceleração com redução de luzes e sons ambiente."
            },
            {
                "email": "sivanildo.santoss@gmail.com",
                "midia": "mc queen",
                "frase": "mamae cade o mc qeen? mamae cade o mc queen?",
                "traducao": "🔍 **Tradução Comportamental:** Expressa busca por previsibilidade, estranhamento com mudança no ambiente ou ansiedade por perda de objeto/rotina de interesse.\n💡 **Ação Recomendada:** Mostrar onde as coisas estão ou reestabelecer o elemento de segurança visualmente.",
                "acao": "Mostrar à criança onde as coisas estão ou reestabelecer o elemento de segurança visualmente."
            }
        ],
        "sensorial": []
    }

global_db = get_global_db()

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

# -----------------------------------------------------------------------------
# CONEXÃO COM O GEMINI & FUNÇÃO DE FALLBACK SEGURO
# -----------------------------------------------------------------------------
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

client = None
if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception:
        client = None

def chamar_ia_com_fallback(prompt, fallback_tipo="ecolalia"):
    """Tenta chamar a API do Gemini com múltiplos modelos. Se esgotar a cota (429), 
    retorna uma resposta inteligente padrão para não travar o aplicativo."""
    
    if client:
        modelos = ["gemini-1.5-flash", "gemini-1.5-flash-8b", "gemini-2.0-flash"]
        for mod in modelos:
            try:
                response = client.models.generate_content(model=mod, contents=prompt)
                if response and response.text:
                    return response.text.strip(), False
            except Exception as e:
                # Se for erro 429 ou outro erro de API, continua testando os outros modelos
                continue

    # Se todos falharem ou não houver chave/cota, retorna resposta de contingência especializada
    if fallback_tipo == "ecolalia":
        return (
            "🔍 **Tradução Comportamental:** (Modo Contingência - Cota de IA Temporariamente Esgotada)\n"
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
            st.success("🔒 **Sessão Protegida**\n(Seus dados estão visíveis apenas para você)")
            
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
            user_e = email_input.strip().lower()
            st.session_state.user_email = user_e
            st.query_params["user_email"] = user_e
            st.rerun()
            
        st.warning("⚠️ Informe seu e-mail para carregar/salvar seus perfis de forma privativa.")

    st.markdown("---")

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
                        novo_perfil = {
                            "email": current_user,
                            "nome": nome.strip(),
                            "idade": idade,
                            "tipo": tipo,
                            "suporte": suporte
                        }
                        st.session_state.profiles_db.append(novo_perfil)
                        st.success(f"Perfil de **{nome}** salvo com sucesso!")
                        st.rerun()
                    else:
                        st.error("Por favor, preencha o nome do perfil.")

        with col_list:
            st.markdown("### Perfis Cadastrados")

            if is_admin:
                perfis_visiveis = st.session_state.profiles_db
                st.caption("👑 Visão de Administrador: Exibindo todos os perfis registrados no sistema.")
            else:
                perfis_visiveis = [p for p in st.session_state.profiles_db if p.get("email", "").lower() == current_user]

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
        perfis_usuario = [p['nome'] for p in st.session_state.profiles_db if is_admin or p.get("email", "").lower() == current_user]
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
                        
                        analise_texto, em_contingencia = chamar_ia_com_fallback(prompt, fallback_tipo="ecolalia")

                        if em_contingencia:
                            st.warning("⚠️ Cota gratuita da API esgotada temporariamente (Erro 429). Gerada resposta de contingência especializada.")

                        st.session_state.ecolalias_db.append({
                            "email": current_user,
                            "perfil": perfil_selecionado,
                            "midia": midia,
                            "frase": frase,
                            "traducao": analise_texto
                        })
                        st.success("Ecolalia analisada e salva no seu dicionário!")
                        st.rerun()

        st.markdown("---")
        st.markdown("### Dicionário de Ecolalias Salvas")

        if is_admin:
            ecolalias_visiveis = st.session_state.ecolalias_db
        else:
            ecolalias_visiveis = [e for e in st.session_state.ecolalias_db if e.get("email", "").lower() == current_user]

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

# --- PÁGINA 4: REGISTRO SENSORIAL & AUTORREGULAÇÃO ---
elif st.session_state.page == "Sensorial":
    st.title("📝 Registro Sensorial & Crises")
    st.write("Acompanhe episódios de sobrecarga, autorregulação e obtenha orientações da IA para momentos de crise.")

    if not st.session_state.user_email:
        st.warning("⚠️ Digite seu e-mail no menu lateral para acessar os registros sensoriais.")
    else:
        st.markdown("### Novo Registro Sensorial e de Crise")
        
        gatilho_in = st.text_input("Gatilho Identificado (ex: Som alto do interfone, Fim do tempo do celular):")
        comportamento_in = st.text_area("Comportamento Observado (ex: Tampou os ouvidos, Fez birra e se jogou no chão):")
        intensidade_in = st.select_slider("Nível de Sobrecarga/Intensidade:", options=["Leve", "Moderado", "Severo"])

        # Botão para pedir apoio à IA
        col_ia_btn, col_blank = st.columns([1, 1])
        with col_ia_btn:
            if st.button("🤖 Sugerir Estratégia de Ação com IA", type="secondary", use_container_width=True):
                if not comportamento_in.strip():
                    st.warning("Descreva o comportamento observado para a IA sugerir uma estratégia apropriada.")
                else:
                    with st.spinner("IA calculando melhor estratégia de acolhimento e regulação..."):
                        prompt_sens = f"""Você é um terapeuta ocupacional e psicólogo especialista em Transtorno do Espectro Autista (TEA).
                        Um pai/mãe está registrando um episódio de sobrecarga/crise do filho:
                        - Gatilho: {gatilho_in}
                        - Comportamento: {comportamento_in}
                        - Intensidade: {intensidade_in}

                        Forneça uma instrução direta, curta e extremamente prática para os pais aplicarem no momento ou após a crise para autorregulação. 
                        Seja acolhedor e objetivo (no máximo 3 frases concisas).
                        """
                        
                        sugestao_obtida, em_contingencia = chamar_ia_com_fallback(prompt_sens, fallback_tipo="sensorial")

                        if em_contingencia:
                            st.warning("⚠️ Cota gratuita da API esgotada temporariamente (Erro 429). Carregada estratégia de contingência padrão.")

                        st.session_state.sugestao_estrategia_temp = sugestao_obtida
                        st.success("Estratégia de regulação carregada no campo abaixo!")

        # Campo da Estratégia (preenchido pela IA ou editável pelos pais)
        estrategia_in = st.text_area(
            "Estratégia de Autorregulação / Ação Adotada:",
            value=st.session_state.sugestao_estrategia_temp,
            placeholder="Ex: Reduzimos a luz, oferecemos fone abafador e aguardamos no canto de descompressão.",
            help="Você pode usar a sugestão da IA acima ou escrever como agiu na situação."
        )

        if st.button("💾 Salvar Registro Sensorial", type="primary"):
            if comportamento_in.strip():
                st.session_state.sensorial_db.append({
                    "email": current_user,
                    "gatilho": gatilho_in,
                    "comportamento": comportamento_in,
                    "intensidade": intensidade_in,
                    "estrategia": estrategia_in if estrategia_in.strip() else "Nenhuma registrada"
                })
                st.session_state.sugestao_estrategia_temp = "" # Limpa a sugestão temporária
                st.success("Registro sensorial e estratégia salvos com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, descreva o comportamento observado antes de salvar.")

        st.markdown("---")
        st.markdown("### Histórico Sensorial")

        if is_admin:
            registros_visiveis = st.session_state.sensorial_db
        else:
            registros_visiveis = [s for s in st.session_state.sensorial_db if s.get("email", "").lower() == current_user]

        if not registros_visiveis:
            st.info("Nenhum registro sensorial anotado para esta conta.")
        else:
            for idx, s in enumerate(registros_visiveis):
                dono_txt = f" ({s.get('email')})" if is_admin else ""
                with st.expander(f"⚡ Gatilho: {s['gatilho']} | Intensidade: {s['intensidade']}{dono_txt}"):
                    st.write(f"**Comportamento:** {s['comportamento']}")
                    st.write(f"**Estratégia / Ação:** {s['estrategia']}")

# --- PÁGINA 5: DASHBOARD & ANÁLISE ---
elif st.session_state.page == "Dashboard":
    st.title("📊 Dashboard & Relatórios Estruturados")
    st.write("Gere relatórios completos para apresentação em consultas médicas ou terapêuticas.")

    if not st.session_state.user_email:
        st.warning("⚠️ Digite seu e-mail no menu lateral para gerar seus relatórios.")
    else:
        user_ecos = [e for e in st.session_state.ecolalias_db if is_admin or e.get("email", "").lower() == current_user]
        user_sens = [s for s in st.session_state.sensorial_db if is_admin or s.get("email", "").lower() == current_user]
        user_profs = [p for p in st.session_state.profiles_db if is_admin or p.get("email", "").lower() == current_user]

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
                # 1. Perfil Principal
                primary_profile = user_profs[0] if user_profs else {
                    "email": st.session_state.user_email,
                    "nome": "Usuário",
                    "idade": "-",
                    "tipo": "Criança/Adolescente",
                    "suporte": "-"
                }

                p_nome = primary_profile.get("nome", "Usuário")
                p_tipo = primary_profile.get("tipo", "Criança/Adolescente")

                # 2. Formatação dos logs conforme a classe SpectrumEchoPDFGenerator espera
                sensory_logs = []
                for eco in user_ecos:
                    sensory_logs.append({
                        "stress_level_0_to_100": 50,
                        "triggers": ["Comunicação / Ecolalia"],
                        "behavioral_manifestation": {
                            "echolalia_phrase": eco.get("frase", "Nenhuma registrada"),
                            "media_source": eco.get("midia", "Não informada")
                        }
                    })

                for sens in user_sens:
                    intensidade_map = {"Leve": 30, "Moderado": 60, "Severo": 90}
                    nivel_estresse = intensidade_map.get(sens.get("intensidade"), 50)
                    
                    sensory_logs.append({
                        "stress_level_0_to_100": nivel_estresse,
                        "triggers": [sens.get("gatilho", "Não informado")],
                        "behavioral_manifestation": {
                            "echolalia_phrase": sens.get("comportamento", "Comportamento observado"),
                            "media_source": f"Estratégia: {sens.get('estrategia', 'Nenhuma')}"
                        }
                    })

                # 3. Payload exato esperado pelo report_generator.py
                report_payload = {
                    "user_profile": {
                        "patient_id": st.session_state.user_email if st.session_state.user_email else "paciente_anonimo",
                        "name": p_nome,
                        "mode": "Criança" if "Criança" in str(p_tipo) else "Adulto"
                    },
                    "sensory_and_emotional_logs": sensory_logs,
                    "adult_masking_metrics": {
                        "social_drain_score": 40,
                        "reactivity_pico_0_100": 50,
                        "isolation_needed_minutes": 30
                    }
                }
                
                json_str = json.dumps(report_payload, ensure_ascii=False)
                
                # Instancia e gera o PDF chamando .generate()
                pdf_gen = SpectrumEchoPDFGenerator(json_str)
                pdf_gen.generate()
                
                filename = "relatorio_spectrumecho.pdf"

                with open(filename, "rb") as f:
                    st.download_button(
                        label="⬇️ Baixar Relatório em PDF",
                        data=f,
                        file_name=filename,
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Erro ao gerar relatório em PDF: {e}")