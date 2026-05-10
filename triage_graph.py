"""LangGraph StateGraph for hospital triage (Gemini + JSON memory)."""

from __future__ import annotations

import operator
import warnings

# LangGraph pulls a serde that emits PendingDeprecationWarning until defaults change upstream.
warnings.filterwarnings(
    "ignore",
    message="The default value of `allowed_objects`",
)

from typing import Annotated, Any, Literal, NotRequired, TypedDict, cast

from langgraph.graph import END, START, StateGraph

import doctor_agent
import memory_store
import patient_agent


class TriageState(TypedDict):
    """Graph state: required keys are always set on invoke; rest filled by nodes."""

    patient_id: str
    symptoms: str
    audit_log: Annotated[list[str], operator.add]
    severity: NotRequired[str]
    recommendation: NotRequired[str]
    patient_assessment: NotRequired[dict[str, Any]]
    doctor_consult: NotRequired[dict[str, Any] | None]


def patient_node(state: TriageState) -> dict[str, Any]:
    symptoms = state["symptoms"]
    assessment = patient_agent.assess(symptoms)
    sev = str(assessment.get("severity", "borderline")).lower()
    if sev not in ("normal", "borderline", "critical"):
        sev = "borderline"
        assessment["severity"] = sev
    summary = assessment.get("summary", "")
    route = assessment.get("suggested_route", "")
    rec = f"{summary} Suggested route: {route}".strip()
    return {
        "severity": sev,
        "patient_assessment": assessment,
        "recommendation": rec,
        "audit_log": [f"patient_node: severity={sev}"],
    }


def doctor_node(state: TriageState) -> dict[str, Any]:
    assessment = state.get("patient_assessment")
    if assessment is None:
        raise RuntimeError("patient_assessment missing before doctor_node")
    consult = doctor_agent.consult(state["symptoms"], assessment)
    rec = str(consult.get("recommendation", "")).strip()
    return {
        "doctor_consult": consult,
        "recommendation": rec or state.get("recommendation", ""),
        "audit_log": ["doctor_node: consult completed"],
    }


def memory_node(state: TriageState) -> dict[str, Any]:
    audit = list(state.get("audit_log", []))
    audit.append("memory_node: case appended to triage_memory.json")
    record = {
        "case_id": state["patient_id"],
        "patient_id": state["patient_id"],
        "severity": state.get("severity"),
        "symptoms": state["symptoms"],
        "recommendation": state.get("recommendation"),
        "patient_assessment": state.get("patient_assessment"),
        "doctor_consult": state.get("doctor_consult"),
        "audit_log": audit,
    }
    memory_store.append_run(record)
    return {"audit_log": ["memory_node: case appended to triage_memory.json"]}


def route_after_patient(state: TriageState) -> Literal["doctor", "memory"]:
    sev = str(state.get("severity", "borderline")).lower()
    if sev in ("critical", "borderline"):
        return "doctor"
    return "memory"


def _build_graph():
    g = StateGraph(TriageState)
    g.add_node("patient", patient_node)
    g.add_node("doctor", doctor_node)
    g.add_node("memory", memory_node)
    g.add_edge(START, "patient")
    g.add_conditional_edges(
        "patient",
        route_after_patient,
        {"doctor": "doctor", "memory": "memory"},
    )
    g.add_edge("doctor", "memory")
    g.add_edge("memory", END)
    return g.compile()


COMPILED = _build_graph()


def _outcome_from_final(state: TriageState) -> dict[str, Any]:
    sev = str(state.get("severity", "")).lower()
    doctor = state.get("doctor_consult")
    if doctor is not None:
        routing = "Physician agent consulted for borderline or critical presentation."
    else:
        routing = "No physician agent consult required; patient assessment used for routine guidance."
    return {
        "case_id": state["patient_id"],
        "severity": state.get("severity"),
        "symptoms": state["symptoms"],
        "recommendation": state.get("recommendation"),
        "patient_assessment": state.get("patient_assessment"),
        "doctor_consult": doctor,
        "routing_note": routing,
        "audit_log": list(state.get("audit_log", [])),
    }


def run_triage(symptoms: str, patient_id: str) -> dict[str, Any]:
    initial: TriageState = {
        "patient_id": patient_id,
        "symptoms": symptoms,
        "audit_log": [],
    }
    final = cast(TriageState, COMPILED.invoke(initial))
    return _outcome_from_final(final)
