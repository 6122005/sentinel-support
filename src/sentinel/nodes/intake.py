"""Intake node: normalize and validate the incoming ticket."""

import uuid
from sentinel.state import TicketState
from sentinel.observability import setup_logger, log_event

logger = setup_logger("sentinel.intake")


def normalize_ticket(state: TicketState) -> dict:
    ticket_id = state.get("ticket_id") or str(uuid.uuid4())
    message = (state.get("message") or "").strip()

    if not message:
        raise ValueError("Ticket message cannot be empty")

    if len(message) > 2000:
        message = message[:2000]

    log_event(logger, "intake", ticket_id=ticket_id, length=len(message))

    return {
        "ticket_id": ticket_id,
        "message": message,
        "trace": [{"node": "intake", "ticket_id": ticket_id}],
    }
