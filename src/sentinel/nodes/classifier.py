"""Classifier node: structured-output ticket classification with confidence gate."""

import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from sentinel.state import TicketState, Route
from sentinel.observability import setup_logger, log_event

logger = setup_logger("sentinel.classifier")

CLASSIFIER_PROMPT = ChatPromptTemplate.from_template(
    """You are a support ticket classifier for a digital wallet app.

Classify this ticket into EXACTLY ONE category:
- billing (refunds, invoices, charges, payment issues)
- tech (app crashes, login failures, sync errors)
- general (anything else)

Return confidence 0-1. If confidence < 0.6, return category 'general'.

Respond ONLY as JSON:
{{"category": "billing|tech|general", "confidence": 0.0, "reasoning": "one sentence"}}

Ticket: {message}"""
)


def _mock_classify(message: str) -> tuple[str, float, str]:
    msg = message.lower()
    if any(k in msg for k in ["refund", "invoice", "charge", "charged", "billing", "payment", "ord_"]):
        return "billing", 0.95, "Mock rule: billing keywords detected"
    if any(k in msg for k in ["crash", "login", "sync", "error", "bug", "app"]):
        return "tech", 0.95, "Mock rule: tech keywords detected"
    return "general", 0.4, "Mock rule: general / unclear issue"


def classify_ticket(state: TicketState) -> dict:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    is_dummy_key = not api_key or "your-key" in api_key or "dummy" in api_key
    use_mock = os.getenv("MOCK_LLM", "false").lower() in ("true", "1") or is_dummy_key

    if use_mock:
        category, confidence, reasoning = _mock_classify(state["message"])
        log_event(logger, "classify_mock_mode", category=category, confidence=confidence)
    else:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        chain = CLASSIFIER_PROMPT | llm

        try:
            response = chain.invoke({"message": state["message"]})
            result = json.loads(response.content)
            category = result["category"]
            confidence = float(result["confidence"])
            reasoning = result.get("reasoning", "")
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            log_event(logger, "classify_parse_failure", error=str(exc))
            category, confidence, reasoning = "general", 0.0, "parse_failure"
        except Exception as exc:
            log_event(logger, "classify_llm_failure", error=str(exc))
            category, confidence, reasoning = "general", 0.0, f"llm_failure: {str(exc)}"

    if confidence < 0.6:
        route = Route.ESCALATE
    elif category == "billing":
        route = Route.BILLING
    elif category == "tech":
        route = Route.TECH
    else:
        route = Route.ESCALATE

    log_event(
        logger,
        "classify",
        ticket_id=state["ticket_id"],
        category=category,
        confidence=confidence,
        route=route.value,
    )

    return {
        "category": category,
        "confidence": confidence,
        "reasoning": reasoning,
        "route": route,
        "trace": [{
            "node": "classify",
            "category": category,
            "confidence": confidence,
            "route": route.value,
        }],
    }
