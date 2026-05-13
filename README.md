# 🏥 Multi-Agent Infra for Hospital Chains

A multi-agent AI system that automates patient triage and critical case escalation in hospital chains using Google Gemini.

---

## Architecture

```
Patient comes in
      │
      ▼
┌─────────────────┐
│  Patient Agent  │  ← Collects symptoms, assesses severity
│  (Triage AI)    │    using LLM-based clinical reasoning
└────────┬────────┘
         │
         ▼
   Severity Check
  ┌───────┴────────┐
  │                │
normal/         critical/
borderline      borderline+
  │                │
  ▼                ▼
Case logged   ┌─────────────────┐
to memory     │  Orchestrator   │  ← Detects critical flag,
              │  (Coordinator)  │    triggers escalation
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Doctor Agent   │  ← Reads case from shared
              │  (Clinical AI)  │    memory, gives recommendation
              └─────────────────┘
                       │
                       ▼
              Case updated with
              doctor recommendation
              + audit trail logged
```

---

## Agents

### 1. Patient Agent (`patient_agent.py`)
- Collects and analyzes patient symptoms
- Uses Gemini LLM to assess clinical severity
- Classifies cases as `normal`, `borderline`, or `critical`
- Writes structured case data to shared memory

### 2. Doctor Agent (`doctor_agent.py`)
- Triggered only for critical/borderline cases
- Reads full case context from shared memory
- Generates clinical recommendations using Gemini
- Updates case status with treatment guidance

### 3. Orchestrator (`orchestrator.py`)
- Coordinates the flow between agents
- Monitors severity flags from Patient Agent
- Routes cases to Doctor Agent when needed
- Maintains full audit trail of all agent actions

### 4. Memory Store (`memory_store.py`)
- Shared memory layer between agents (JSON-based)
- Stores patient cases, severity, symptoms, and recommendations
- In production: replaceable with Supabase / Redis / Firestore

---

## Project Structure

```
multi-agent-infra/
├── patient_agent.py          # Triage agent
├── doctor_agent.py           # Doctor recommendation agent
├── orchestrator.py           # Agent coordinator
├── memory_store.py           # Shared memory layer
├── google_ai_studio_client.py # Gemini API wrapper
├── main.py                   # Demo runner (3 test cases)
├── requirements.txt          # Dependencies

```

---

## Demo Cases

The system runs 3 scenarios out of the box:

| Case | Symptoms | Severity | Escalated? |
|------|----------|----------|------------|
| Case 1 | Mild headache, low fever | Normal | ❌ No |
| Case 2 | Chest pain, breathlessness, high BP | Critical | ✅ Yes → Doctor Agent |
| Case 3 | High fever + confusion | Borderline | ⚠️ Yes → With warning |

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/bhavyamittal06/Multi-agent-infra.git
cd Multi-agent-infra
```

### 2. Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your API key
Create a `.env` file:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```
Get a free key at [aistudio.google.com](https://aistudio.google.com)

### 5. Run
```bash
python main.py
```

### 6. Run Web UI
```bash
uvicorn app:app --reload
```
Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Sample Output

```
============================================================
CASE 1: Mild Headache
============================================================
[Patient Agent] Assessing symptoms...
[Patient Agent] Severity: NORMAL
[Orchestrator] No escalation needed. Case logged.

============================================================
CASE 2: Chest Pain + Breathlessness
============================================================
[Patient Agent] Assessing symptoms...
[Patient Agent] Severity: CRITICAL 🚨
[Orchestrator] Critical case detected. Escalating to Doctor Agent...
[Doctor Agent] Reading case from memory...
[Doctor Agent] Recommendation: Immediate ECG, cardiac enzymes, O2 monitoring
[Orchestrator] Case updated. Audit trail saved.
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.13 |
| LLM | Google Gemini (via AI Studio) |
| Agent Memory | JSON (local) → Supabase in production |
| Agent Framework | Custom multi-agent orchestration |

---

## Production Roadmap

- [ ] Replace JSON memory with Supabase / Redis
- [ ] Add FastAPI endpoints (`POST /triage`, `POST /escalate`)
- [ ] Deploy on Railway.app for 24/7 availability
- [ ] Add more specialist agents (radiology, pharmacy)
- [ ] Real-time alerting via SMS/email on critical cases

---

## Author

**Bhavya Mittal** — [@bhavyamittal06](https://github.com/bhavyamittal06)
