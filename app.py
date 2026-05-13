"""FastAPI web app for the multi-agent triage system."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.requests import Request

from orchestrator import triage

app = FastAPI(title="Multi-Agent Triage UI", version="1.0.0")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TriageRequest(BaseModel):
    symptoms: str = Field(..., min_length=10, description="Patient symptom description")
    case_id: str | None = Field(None, description="Optional custom case id")


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> Any:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/triage")
def run_triage(payload: TriageRequest) -> dict[str, Any]:
    symptoms = payload.symptoms.strip()
    if not symptoms:
        raise HTTPException(status_code=400, detail="Symptoms are required.")

    case_id = (payload.case_id or "").strip() or f"case-{uuid.uuid4().hex[:8]}"
    try:
        return triage(symptoms=symptoms, case_id=case_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
