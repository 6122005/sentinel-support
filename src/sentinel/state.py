from typing import TypedDict, Annotated
import operator
from enum import Enum


class Route(str, Enum):
    BILLING = "billing"
    TECH = "tech"
    ESCALATE = "escalate"


class TicketState(TypedDict):
    # Input
    ticket_id: str
    customer_id: str
    message: str

    # Classification
    category: str | None
    confidence: float | None
    reasoning: str | None

    # Routing
    route: Route | None

    # Agent outputs
    resolution: str | None
    tools_used: list[str]
    needs_human: bool

    # Human escalation
    escalation_summary: str | None
    approved: bool | None

    # Audit trail
    trace: Annotated[list[dict], operator.add]
