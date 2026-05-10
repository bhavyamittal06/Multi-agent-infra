"""Entry point for triage; delegates to the LangGraph workflow."""

from __future__ import annotations

from typing import Any

from triage_graph import run_triage


def triage(symptoms: str, case_id: str) -> dict[str, Any]:
    """Backward-compatible name: ``case_id`` is stored as ``patient_id`` in graph state."""
    return run_triage(symptoms, patient_id=case_id)
