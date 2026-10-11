"""CLI entry point for local testing without FastAPI."""

import uuid
from langgraph.checkpoint.sqlite import SqliteSaver

from sentinel.graph import build_graph


def run(message: str, customer_id: str = "cust_101") -> None:
    checkpointer = SqliteSaver.from_conn_string(":memory:")
    graph = build_graph(checkpointer=checkpointer)

    ticket_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": ticket_id}}

    state = {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "message": message,
        "trace": [],
    }

    result = graph.invoke(state, config)

    print("=" * 60)
    print(f"Ticket: {ticket_id}")
    print(f"Status: {'NEEDS HUMAN' if result.get('needs_human') else 'RESOLVED'}")
    print("-" * 60)
    if result.get("needs_human"):
        print(result.get("escalation_summary"))
    else:
        print(result.get("resolution"))
    print("-" * 60)
    print("Trace:")
    for entry in result.get("trace", []):
        print(f"  {entry}")


if __name__ == "__main__":
    import sys
    msg = " ".join(sys.argv[1:]) or "I was charged twice for ord_901, need a refund"
    run(msg)
