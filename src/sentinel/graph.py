import sqlite3
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.sqlite import SqliteSaver

# Ensure SqliteSaver works seamlessly both directly and as context manager
if not hasattr(SqliteSaver, "_sentinel_patched"):
    SqliteSaver.__enter__ = lambda self: self
    SqliteSaver.__exit__ = lambda self, exc_type, exc_val, exc_tb: None

    @classmethod
    def _robust_from_conn_string(cls, conn_string: str):
        conn = sqlite3.connect(conn_string, check_same_thread=False)
        return cls(conn)

    SqliteSaver.from_conn_string = _robust_from_conn_string
    SqliteSaver._sentinel_patched = True

from sentinel.state import TicketState
from sentinel.nodes import (
    normalize_ticket,
    classify_ticket,
    handle_billing,
    handle_tech,
    escalate_to_human,
)


def route_ticket(state: TicketState) -> str:
    return state["route"].value


def build_graph(checkpointer=None):
    builder = StateGraph(TicketState)

    builder.add_node("intake", normalize_ticket)
    builder.add_node("classify", classify_ticket)
    builder.add_node("billing", handle_billing)
    builder.add_node("tech", handle_tech)
    builder.add_node("escalate", escalate_to_human)

    builder.add_edge(START, "intake")
    builder.add_edge("intake", "classify")

    builder.add_conditional_edges(
        "classify",
        route_ticket,
        {
            "billing": "billing",
            "tech": "tech",
            "escalate": "escalate",
        },
    )

    builder.add_edge("billing", END)
    builder.add_edge("tech", END)
    builder.add_edge("escalate", END)

    return builder.compile(checkpointer=checkpointer)
