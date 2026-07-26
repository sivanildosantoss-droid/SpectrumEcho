from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import json

class SpectrumEchoPDFGenerator:
    def __init__(self, json_data_str: str, filename: str = "relatorio_spectrumecho.pdf"):
        self.data = json.loads(json_data_str)
        self.filename = filename

    def generate(self):
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        
        styles = getSampleStyleSheet()
        
        # Estilos Customizados
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor('#1E293B'),
            spaceAfter=6
        )
        
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=15
        )

        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor('#0F172A'),
            spaceBefore=10,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#334155'),
            spaceAfter=6
        )

        story = []

        # Cabeçalho
        story.append(Paragraph("<b>SPECTRUMECHO</b> - Relatório de Governança Sensorial", title_style))
        story.append(Paragraph(f"<b>ID do Paciente:</b> {self.data['user_profile']['patient_id']} | <b>Nome:</b> {self.data['user_profile']['name']} | <b>Modo:</b> {self.data['user_profile']['mode'].upper()}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=15))

        # Logs de Criança / Ecolalia
        if self.data.get("sensory_and_emotional_logs"):
            story.append(Paragraph("1. Registros de Sobrecarga e Comunicação (Criança/Família)", section_style))
            for idx, log in enumerate(self.data["sensory_and_emotional_logs"], 1):
                triggers = ", ".join(log.get("triggers", []))
                echolalia = log.get("behavioral_manifestation", {}).get("echolalia_phrase", "Nenhuma registrada")
                media = log.get("behavioral_manifestation", {}).get("media_source", "Não informada")
                
                txt = f"<b>Evento #{idx}:</b> Nível de Estresse: <b>{log['stress_level_0_to_100']}/100</b><br/>" \
                      f"• <b>Gatilhos:</b> {triggers}<br/>" \
                      f"• <b>Frase Repetida (Ecolalia):</b> <i>\"{echolalia}\"</i><br/>" \
                      f"• <b>Origem da Mídia:</b> {media}"
                story.append(Paragraph(txt, body_style))
                story.append(Spacer(1, 6))

        # Logs de Adulto / Mascaramento
        if self.data.get("adult_masking_metrics"):
            story.append(Spacer(1, 10))
            story.append(Paragraph("2. Métricas de Drenagem Social e Mascaramento (Adulto)", section_style))
            masking = self.data["adult_masking_metrics"]
            txt_adult = f"• <b>Desgaste Social:</b> {masking.get('social_drain_score', 0)}/100<br/>" \
                        f"• <b>Pico de Reatividade:</b> {masking.get('reactivity_pico_0_100', 0)}/100<br/>" \
                        f"• <b>Tempo de Isolamento Necessário:</b> {masking.get('isolation_needed_minutes', 0)} minutos"
            story.append(Paragraph(txt_adult, body_style))

        # Rodapé / Nota do Sistema
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E2E8F0'), spaceAfter=10))
        story.append(Paragraph("<i>Relatório gerado automaticamente pela plataforma SpectrumEcho. Documento preparado para acompanhamento médico e terapêutico.</i>", subtitle_style))

        doc.build(story)
        print(f"📄 [PDF GERADO COM SUCESSO] Arquivo salvo em: {self.filename}")