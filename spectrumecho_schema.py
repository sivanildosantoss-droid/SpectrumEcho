import json
from datetime import datetime

class SpectrumEchoEngine:
    def __init__(self, patient_id: str, mode: str, name: str, age: int):
        self.data = {
            "spectrumecho_version": "v0.1.0-alpha",
            "created_at": datetime.utcnow().isoformat(),
            "user_profile": {
                "patient_id": patient_id,
                "mode": mode,  # "child", "adult", ou "child_and_parent"
                "name": name,
                "age": age
            },
            "sensory_and_emotional_logs": [],
            "adult_masking_metrics": {},
            "therapist_summary": {}
        }

    def add_child_log(self, stress_level: int, triggers: list, echolalia_phrase: str = None, media_source: str = None):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "stress_level_0_to_100": stress_level,
            "triggers": triggers,
            "behavioral_manifestation": {
                "echolalia_detected": True if echolalia_phrase else False,
                "echolalia_phrase": echolalia_phrase,
                "media_source": media_source
            }
        }
        self.data["sensory_and_emotional_logs"].append(log_entry)

    def set_adult_masking(self, social_drain: int, reactivity_pico: int, isolation_minutes: int):
        self.data["adult_masking_metrics"] = {
            "social_drain_score": social_drain,
            "reactivity_pico_0_100": reactivity_pico,
            "isolation_needed_minutes": isolation_minutes
        }

    def export_json(self) -> str:
        return json.dumps(self.data, indent=2, ensure_ascii=False)