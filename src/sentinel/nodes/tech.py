"""Tech support agent: Vector RAG lookup + structured troubleshooting."""

from sentinel.state import TicketState
from sentinel.tools import search_kb
from sentinel.observability import setup_logger, log_event

logger = setup_logger("sentinel.tech")


def handle_tech(state: TicketState) -> dict:
    tools_used: list[str] = []
    message = state["message"]

    # Semantic vector search using the customer message
    articles = search_kb(message)
    tools_used.append("search_kb")

    if not articles:
        summary = (
            f"Tech issue requires human review.\n"
            f"Customer: {state['customer_id']}\n"
            f"Message: {message}\n"
            f"KB semantic search returned no high-confidence matches."
        )
        log_event(logger, "tech_escalate", reason="no_kb_match")
        return {
            "resolution": None,
            "tools_used": tools_used,
            "needs_human": True,
            "escalation_summary": summary,
            "trace": [{"node": "tech", "action": "escalate_no_kb_match"}],
        }

    top = articles[0]
    distance = top.get("distance", "N/A")
    similarity = top.get("similarity_score", "N/A")

    resolution = (
        f"Here is what I found for your issue:\n\n"
        f"**{top['title']}**\n{top['body']}\n\n"
        f"If this does not resolve your problem, reply and I will escalate to a human agent."
    )

    log_event(logger, "tech_resolved", article_id=top["id"], distance=distance, similarity=similarity)

    return {
        "resolution": resolution,
        "tools_used": tools_used,
        "needs_human": False,
        "trace": [{
            "node": "tech",
            "action": "kb_match",
            "article_id": top["id"],
            "distance": distance,
            "similarity": similarity,
        }],
    }
