"""Escalation node: build a human-review package. Does NOT resolve."""

from sentinel.state import TicketState
from sentinel.observability import setup_logger, log_event

logger = setup_logger("sentinel.escalation")


def escalate_to_human(state: TicketState) -> dict:
    summary = (
        f"ESCALATION REQUIRED\n"
        f"Ticket: {state['ticket_id']}\n"
        f"Customer: {state['customer_id']}\n"
        f"Message: {state['message']}\n"
        f"Classifier category: {state.get('category', 'unknown')}\n"
        f"Confidence: {state.get('confidence') or 0.0:.2f}\n"
        f"Reason: {state.get('reasoning', 'N/A')}\n"
        f"Action: review and approve/deny via POST /tickets/{state['ticket_id']}/resume"
    )

    log_event(logger, "escalate", ticket_id=state["ticket_id"])

    return {
        "needs_human": True,
        "escalation_summary": summary,
        "route": None,
        "trace": [{
            "node": "escalate",
            "action": "human_review_requested",
            "confidence": state.get("confidence"),
        }],
    }
