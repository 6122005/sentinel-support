"""Billing agent: handles refunds, invoices, charge disputes."""

from sentinel.state import TicketState
from sentinel.tools import get_order, issue_refund
from sentinel.observability import setup_logger, log_event

logger = setup_logger("sentinel.billing")

REFUND_APPROVAL_THRESHOLD = 50.0


def handle_billing(state: TicketState) -> dict:
    message = state["message"].lower()
    tools_used: list[str] = []

    # Naive order-id extraction (production: use LLM tool-calling)
    order_id = None
    for token in message.split():
        if token.startswith("ord_"):
            order_id = token.strip(".,!?")
            break

    if not order_id:
        return {
            "resolution": "I could not find an order ID in your message. "
                          "Please reply with your order ID (e.g., ord_901).",
            "tools_used": tools_used,
            "needs_human": False,
            "trace": [{"node": "billing", "action": "missing_order_id"}],
        }

    order = get_order(order_id)
    tools_used.append("get_order")

    if not order:
        return {
            "resolution": f"Order {order_id} was not found. Escalating to a human agent.",
            "tools_used": tools_used,
            "needs_human": True,
            "escalation_summary": f"Order lookup failed for {order_id}.",
            "trace": [{"node": "billing", "action": "order_not_found", "order_id": order_id}],
        }

    if order["amount"] >= REFUND_APPROVAL_THRESHOLD:
        summary = (
            f"Refund approval required.\n"
            f"Order: {order_id}\n"
            f"Amount: ${order['amount']:.2f}\n"
            f"Customer: {state['customer_id']}\n"
            f"Reason: {state['message']}"
        )
        log_event(logger, "billing_escalate", order_id=order_id, amount=order["amount"])
        return {
            "resolution": None,
            "tools_used": tools_used,
            "needs_human": True,
            "escalation_summary": summary,
            "trace": [{
                "node": "billing",
                "action": "escalate_for_approval",
                "order_id": order_id,
                "amount": order["amount"],
            }],
        }

    result = issue_refund(order_id, order["amount"])
    tools_used.append("issue_refund")

    if result.get("success"):
        resolution = f"Refund of ${order['amount']:.2f} for {order_id} processed successfully."
    else:
        resolution = f"Refund failed: {result.get('reason', 'unknown')}. A human will follow up."

    log_event(logger, "billing_resolved", order_id=order_id, success=result.get("success"))

    return {
        "resolution": resolution,
        "tools_used": tools_used,
        "needs_human": not result.get("success", False),
        "trace": [{
            "node": "billing",
            "action": "refund_processed",
            "order_id": order_id,
            "success": result.get("success"),
        }],
    }
