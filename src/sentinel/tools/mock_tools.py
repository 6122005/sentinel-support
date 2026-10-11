"""Mock internal tools. Replace with real API calls in production."""

import json
from pathlib import Path
from typing import Any

from sentinel.rag.vector_store import get_kb_vector_store

_ORDERS: dict[str, dict[str, Any]] = {
    "ord_901": {"id": "ord_901", "customer_id": "cust_101", "amount": 490.0, "status": "charged"},
    "ord_902": {"id": "ord_902", "customer_id": "cust_102", "amount": 29.0, "status": "charged"},
    "ord_903": {"id": "ord_903", "customer_id": "cust_103", "amount": 1500.0, "status": "refunded"},
}

_KB_PATH = Path(__file__).resolve().parents[3] / "data" / "kb_articles.json"


def get_order(order_id: str) -> dict[str, Any]:
    """Look up an order by ID. Returns empty dict if not found."""
    return _ORDERS.get(order_id, {})


def issue_refund(order_id: str, amount: float) -> dict[str, Any]:
    """Issue a refund. Returns confirmation payload."""
    order = _ORDERS.get(order_id)
    if not order:
        return {"success": False, "reason": "order_not_found"}
    if amount > order["amount"]:
        return {"success": False, "reason": "amount_exceeds_order"}
    order["status"] = "refunded"
    return {"success": True, "order_id": order_id, "refunded": amount}


def search_kb(query: str) -> list[dict[str, Any]]:
    """Search internal knowledge base using semantic vector search (ChromaDB RAG).

    Falls back to keyword matching if vector store encounters an issue.
    """
    try:
        store = get_kb_vector_store()
        matches = store.search(query=query, top_k=2)
        if matches:
            return matches
    except Exception:
        pass

    # Resilient keyword fallback
    if not _KB_PATH.exists():
        return []
    articles = json.loads(_KB_PATH.read_text(encoding="utf-8"))
    q = query.lower()
    keywords = [w for w in q.split() if len(w) > 2]
    matches = []
    for a in articles:
        text = f"{a['title']} {a['body']}".lower()
        if q in text or (keywords and any(k in text for k in keywords)):
            matches.append(a)
    return matches
