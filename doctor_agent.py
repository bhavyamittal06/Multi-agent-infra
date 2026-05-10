"""Doctor agent: recommendations for higher-acuity cases (LLM)."""

from __future__ import annotations

import json
from typing import Any

from google_ai_studio_client import chat_json

DOCTOR_SYSTEM = """You are an emergency physician giving brief triage guidance for clinicians and staff.
This is not a substitute for in-person evaluation. Respond with one JSON object only, no markdown.

Schema:
{
  "recommendation": "2-4 sentences: immediate actions, monitoring, what to rule out",
  "escalation": "e.g. EMS, ED now, urgent same-day clinic",
  "disclaimers": "one short line that this is triage support only"
}
"""


def consult(symptoms: str, patient_assessment: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "symptoms": symptoms.strip(),
        "patient_agent_assessment": patient_assessment,
    }
    user = json.dumps(payload, ensure_ascii=False)
    return chat_json(DOCTOR_SYSTEM, user)
