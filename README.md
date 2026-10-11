# Sentinel Support Triage 🛡️

A production-grade, stateful Multi-Agent Support Orchestrator with Human-in-the-Loop safeguards and Semantic RAG.

## 🚀 Key Highlights (Enterprise 10+ LPA Architecture)

- **LangGraph State Machine:** Dynamic routing across specialized agents (`intake` ➔ `classifier` ➔ `billing` / `tech` / `escalate`).
- **Confidence Gating:** Prevents hallucinations by routing queries with confidence `< 0.6` directly to human escalation.
- **Deterministic Guardrails (HITL):** Financial refunds $\ge \$50$ pause execution for Human Manager approval via REST endpoint `/resume`.
- **Fault-Tolerant Checkpointing:** SQLite checkpointer (`sentinel.db`) persists agent state across server restarts.
- **Vector Database RAG:** Integrated with **ChromaDB** for semantic knowledge base search with distance metrics.
- **Full Observability & Audit Trail:** Structured JSON logging and `/trace/{ticket_id}` audit retrieval.
- **Operations Control Plane:** Modern interactive **Streamlit Dashboard** for live ticket simulation, manager approvals, and trace exploration.

---

## 🏗️ Architecture

```text
POST /tickets ──> [Intake Node]
                         │
                         ▼
                 [Classifier Node] ──(Confidence < 0.6)──> [Escalate to Human]
                         │                                       │
            ┌────────────┴────────────┐                          ▼
            ▼                         ▼                   (Paused in SQLite)
     [Billing Agent]            [Tech Agent]                     │
     (Checks $50 limit)     (ChromaDB Vector RAG)                ▼
            │                         │                    POST /resume
            └────────────┬────────────┘                          │
                         ▼                                       ▼
                       [END] <───────────────────────────────────┘
```

---

## ⚡ Quick Start

```powershell
# 1. Activate environment
.\.venv\Scripts\Activate.ps1

# 2. Run tests (9/9 passing)
pytest -v

# 3. Start the FastAPI backend
uvicorn sentinel.api:app --reload

# 4. In a second terminal, launch the Streamlit Operations Dashboard
streamlit run src/sentinel/dashboard/app.py
```

Dashboard will open at: `http://localhost:8501`  
FastAPI Swagger Docs at: `http://localhost:8000/docs`

---

## 📂 Project Structure

```text
sentinel-support/
├── data/
│   └── kb_articles.json           # Knowledge Base data
├── src/
│   └── sentinel/
│       ├── api.py                 # FastAPI endpoints (/tickets, /resume, /trace)
│       ├── graph.py               # LangGraph StateGraph definition
│       ├── state.py               # TicketState TypedDict schema
│       ├── observability.py       # Structured JSON telemetry
│       ├── dashboard/
│       │   └── app.py             # Streamlit Operations Dashboard
│       ├── rag/
│       │   └── vector_store.py    # ChromaDB Vector Store & Semantic Search
│       ├── nodes/
│       │   ├── intake.py          # Ticket validation & normalization
│       │   ├── classifier.py      # Confidence-gated LLM classifier
│       │   ├── billing.py         # Refund processing & $50 threshold guardrail
│       │   ├── tech.py            # Tech troubleshooting via Vector RAG
│       │   └── escalation.py      # Human escalation packaging
│       └── tools/
│           └── mock_tools.py      # Order lookup, refunds, and RAG search
└── tests/
    ├── test_classifier.py
    ├── test_routing.py
    ├── test_e2e.py
    └── test_rag.py                # ChromaDB vector search tests
```
