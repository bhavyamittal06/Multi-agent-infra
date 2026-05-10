"""Coordinates patient and doctor agents and persists outcomes to JSON."""

from __future__ import annotations

from typing import Any

import doctor_agent
import memory_store
import patient_agent


def triage(symptoms: str, case_id: str) -> dict[str, Any]:
    patient_view = patient_agent.assess(symptoms)
    severity = patient_view.get("severity", "borderline")

    if severity == "normal":
        outcome = {
            "case_id": case_id,
            "severity": severity,
            "patient_assessment": patient_view,
            "doctor_consult": None,
            "routing_note": "No physician agent consult required; use patient assessment for routine guidance.",
        }
    else:
        doctor_view = doctor_agent.consult(symptoms, patient_view)
        outcome = {
            "case_id": case_id,
            "severity": severity,
            "patient_assessment": patient_view,
            "doctor_consult": doctor_view,
            "routing_note": "Physician agent consulted for borderline or critical presentation.",
        }

    memory_store.append_run(outcome)
    return outcome
