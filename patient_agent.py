"""Patient-facing agent: symptom intake and severity triage (LLM)."""

from __future__ import annotations

from typing import Any

from google_ai_studio_client import chat_json

PATIENT_SYSTEM = """You are a clinical triage assistant for a hospital. You do NOT diagnose;
you estimate urgency for routing only. Always respond with a single JSON object, no markdown.

Schema:
{
  "severity": "normal" | "borderline" | "critical",
  "summary": "one short sentence",
  "red_flags": ["optional short strings"],
  "suggested_route": "e.g. primary care, urgent care, emergency"
}

Rules:
- "critical": life-threatening or time-sensitive (chest pain with cardiac features, stroke signs, sepsis, severe SOB, etc.)
- "borderline": needs clinician soon; could worsen; ambiguous serious symptoms (fever + meningitis features, moderate dyspnea, etc.)
- "normal": mild, self-limited, or clearly primary-care appropriate
"""


def assess(symptoms: str) -> dict[str, Any]:
    user = f"Patient reports the following (verbatim or paraphrased):\n{symptoms.strip()}"
    data = chat_json(PATIENT_SYSTEM, user)
    sev = str(data.get("severity", "")).lower()
    if sev not in ("normal", "borderline", "critical"):
        data["severity"] = "borderline"
    return data
