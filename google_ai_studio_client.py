"""Google AI Studio (Gemini API) JSON helper — loads .env from project root."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from dotenv import dotenv_values, find_dotenv
from google import genai
from google.genai import errors, types

# Default model: often has separate free-tier pool from gemini-2.0-flash (which can show limit: 0).
_DEFAULT_MODEL = "gemini-2.5-flash-lite"

_ROOT = Path(__file__).resolve().parent


def _load_env_files() -> None:
    """Load .env files; ignore empty values so GOOGLE_API_KEY= does not block other sources."""
    paths: list[Path] = []
    found = find_dotenv(usecwd=True)
    project_env = _ROOT / ".env"
    if found:
        fp = Path(found).resolve()
        if fp != project_env.resolve():
            paths.append(Path(found))
    paths.append(project_env)

    merged: dict[str, str] = {}
    for path in paths:
        if not path.is_file():
            continue
        for key, raw in dotenv_values(path).items():
            if raw is None:
                continue
            val = str(raw).strip().strip("'\"")
            if val:
                merged[key] = val

    for key, val in merged.items():
        cur = os.environ.get(key)
        if cur is None or not str(cur).strip():
            os.environ[key] = val


_load_env_files()


def _api_key() -> str | None:
    for name in ("GOOGLE_API_KEY", "GEMINI_API_KEY"):
        raw = os.environ.get(name)
        if raw is None:
            continue
        s = raw.strip().strip("'\"")
        if s:
            return s
    return None


def chat_json(system: str, user: str) -> dict[str, Any]:
    key = _api_key()
    if not key:
        env_path = _ROOT / ".env"
        hint = (
            f"The value after GOOGLE_API_KEY= in {env_path} is empty. "
            "Paste your key from https://aistudio.google.com/apikey (no spaces), save, and retry. "
            "Or run: export GOOGLE_API_KEY=your_key"
        )
        if env_path.is_file():
            raise RuntimeError(
                "No API key found. " + hint
            )
        raise RuntimeError(
            "No API key found. Create a .env in the project folder with GOOGLE_API_KEY=... "
            "from https://aistudio.google.com/apikey or export GOOGLE_API_KEY."
        )
    model_name = (os.environ.get("GEMINI_MODEL") or _DEFAULT_MODEL).strip() or _DEFAULT_MODEL

    client = genai.Client(api_key=key)
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.2,
                response_mime_type="application/json",
            ),
        )
    except errors.ClientError as exc:
        if exc.code == 429:
            raise RuntimeError(
                "Gemini API quota or rate limit (429). Try in .env: GEMINI_MODEL="
                f"{_DEFAULT_MODEL!r} or gemini-2.5-flash, wait for the reset window, "
                "or enable billing / check limits at "
                "https://ai.google.dev/gemini-api/docs/rate-limits — "
                f"current model was {model_name!r}."
            ) from exc
        if exc.code == 403:
            msg = str(exc.message or exc).lower()
            if "leaked" in msg or "permission_denied" in msg:
                raise RuntimeError(
                    "Gemini returned 403: this API key was disabled as leaked or is not allowed. "
                    "Create a new key at https://aistudio.google.com/apikey , put it in .env as "
                    "GOOGLE_API_KEY=... (do not share or commit it), and delete any old key that was exposed."
                ) from exc
            raise RuntimeError(
                "Gemini returned 403 PERMISSION_DENIED. Check that GOOGLE_API_KEY is correct, "
                "the Generative Language API is enabled for your project, and billing/API restrictions "
                "allow this key."
            ) from exc
        raise
    raw = (response.text or "").strip() or "{}"
    return json.loads(raw)
