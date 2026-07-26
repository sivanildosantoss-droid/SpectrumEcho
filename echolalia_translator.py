class EcholaliaTranslator:
    def __init__(self):
        # Mapeamento inicial de frases e contextos de mídia
        self.knowledge_base = {
            "O trem esta fora dos trilhos": {
                "media_source": "Thomas e Seus Amigos",
                "scene_context": "O trem perdeu o controle ou a rota foi alterada bruscamente.",
                "inferred_emotion": "Sobrecarga, perda de previsibilidade ou ansiedade por mudança de rotina.",
                "action_recommendation": "Reduzir estímulos, validar a quebra de expectativa e antecipar o próximo passo de forma clara."
            },
            "Perigo a vista": {
                "media_source": "Patrulha Canina",
                "scene_context": "Situação de emergência ou alerta eminente.",
                "inferred_emotion": "Sensação de ameaça sensorial (barulho muito alto, ambiente desconhecido) ou medo direto.",
                "action_recommendation": "Oferecer ambiente seguro, abafador de ruído e espaço de descompressão sem cobranças."
            },
            "Eu preciso de um tempo": {
                "media_source": "Desenhos Diversos / Diálogo Comum",
                "scene_context": "Personagem se afasta para recuperar energias.",
                "inferred_emotion": "Bateria social/sensorial no limite.",
                "action_recommendation": "Permitir o isolamento sem julgamento. Não forçar contato físico ou conversa."
            }
        }

    def translate_phrase(self, phrase: str) -> dict:
        # Busca exata ou por palavra-chave no banco
        for key, value in self.knowledge_base.items():
            if key.lower() in phrase.lower():
                return {
                    "matched": True,
                    "phrase": phrase,
                    "translation": value
                }
        
        # Caso a frase ainda não esteja cadastrada na base
        return {
            "matched": False,
            "phrase": phrase,
            "translation": {
                "media_source": "Desconhecida/Personalizada",
                "scene_context": "Frase específica do repertório individual.",
                "inferred_emotion": "Necessita de observação de contexto pelos pais/terapeuta.",
                "action_recommendation": "Registrar o horário e os estímulos do ambiente no momento em que a frase foi dita."
            }
        }