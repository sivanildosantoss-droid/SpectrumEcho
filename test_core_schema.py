from spectrumecho_schema import SpectrumEchoEngine
from report_generator import SpectrumEchoPDFGenerator
from echolalia_translator import EcholaliaTranslator
import os

def run_tests():
    print("--- INICIANDO TESTES DO SPECTRUMECHO CORE + PDF + TRADUTOR (v0.3.0-alpha) ---")
    
    # 1. Teste de Perfil Criança (Ex: Murilo)
    engine_child = SpectrumEchoEngine(patient_id="MURI-2026", mode="child_and_parent", name="Murilo", age=8)
    
    # Testando o Tradutor de Ecolalia
    translator = EcholaliaTranslator()
    phrase_to_test = "O trem esta fora dos trilhos"
    translation_result = translator.translate_phrase(phrase_to_test)
    
    assert translation_result["matched"] == True
    assert "Sobrecarga" in translation_result["translation"]["inferred_emotion"]
    print("✅ [TESTE 1/4 APROVADO] Tradutor de Ecolalia identificou a emoção corretamente!")

    # Adicionando o log traduzido ao motor
    engine_child.add_child_log(
        stress_level=85,
        triggers=["som_agudo", "mudanca_rotina"],
        echolalia_phrase=phrase_to_test,
        media_source=translation_result["translation"]["media_source"]
    )
    json_out = engine_child.export_json()
    assert "MURI-2026" in json_out
    print("✅ [TESTE 2/4 APROVADO] Schema de Criança atualizado com dados da tradução!")

    # 2. Teste de Perfil Adulto (Ex: Sivanildo)
    engine_adult = SpectrumEchoEngine(patient_id="SIVA-2026", mode="adult", name="Sivanildo", age=35)
    engine_adult.set_adult_masking(social_drain=90, reactivity_pico=75, isolation_minutes=45)
    json_adult_out = engine_adult.export_json()
    assert "social_drain_score" in json_adult_out
    print("✅ [TESTE 3/4 APROVADO] Schema de Adulto e Mascaramento validado!")

    # 3. Teste de Geração do PDF Final
    pdf_filename = "relatorio_teste_spectrumecho_v030.pdf"
    pdf_gen = SpectrumEchoPDFGenerator(json_data_str=json_out, filename=pdf_filename)
    pdf_gen.generate()
    assert os.path.exists(pdf_filename)
    print(f"✅ [TESTE 4/4 APROVADO] PDF com relatório completo gerado em '{pdf_filename}'!")

    print("\n--- TODOS OS TESTES PASSARAM COM SUCESSO! HEAD v0.3.0 PRONTA. ---")

if __name__ == "__main__":
    run_tests()