import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langgraph.checkpoint.sqlite import SqliteSaver

from sentinel.graph import build_graph

app = FastAPI(title="Sentinel Support Triage", version="0.1.0")

checkpointer = SqliteSaver.from_conn_string("sentinel.db")
graph = build_graph(checkpointer=checkpointer)


class TicketRequest(BaseModel):
    customer_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=2000)


class ApprovalRequest(BaseModel):
    approved: bool
    note: str = ""


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/tickets")
async def create_ticket(req: TicketRequest):
    ticket_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": ticket_id}}

    initial_state = {
        "ticket_id": ticket_id,
        "customer_id": req.customer_id,
        "message": req.message,
        "trace": [],
    }

    try:
        result = graph.invoke(initial_state, config)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if result.get("needs_human"):
        return {
            "status": "needs_human_review",
            "ticket_id": ticket_id,
            "summary": result.get("escalation_summary"),
            "trace": result.get("trace", []),
        }

    return {
        "status": "resolved",
        "ticket_id": ticket_id,
        "resolution": result.get("resolution"),
        "trace": result.get("trace", []),
    }


@app.post("/tickets/{ticket_id}/resume")
async def resume_ticket(ticket_id: str, req: ApprovalRequest):
    config = {"configurable": {"thread_id": ticket_id}}
    try:
        result = graph.invoke({"approved": req.approved}, config)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "status": "completed",
        "ticket_id": ticket_id,
        "approved": req.approved,
        "resolution": result.get("resolution"),
        "trace": result.get("trace", []),
    }


@app.get("/trace/{ticket_id}")
async def get_trace(ticket_id: str):
    config = {"configurable": {"thread_id": ticket_id}}
    state = graph.get_state(config)
    if not state or not state.values:
        raise HTTPException(status_code=404, detail="ticket not found")
    return {"ticket_id": ticket_id, "trace": state.values.get("trace", [])}
