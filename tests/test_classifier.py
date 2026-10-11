"""Classifier tests: structured output + confidence gate."""

from unittest.mock import patch, MagicMock

from sentinel.nodes.classifier import classify_ticket
from sentinel.state import Route


def _mock_llm_response(content: str):
    mock = MagicMock()
    mock.content = content
    return mock


@patch("sentinel.nodes.classifier.ChatOpenAI")
def test_billing_high_confidence(mock_llm):
    chain_mock = MagicMock()
    chain_mock.invoke.return_value = _mock_llm_response(
        '{"category": "billing", "confidence": 0.9, "reasoning": "refund request"}'
    )
    mock_llm.return_value.__or__ = MagicMock(return_value=chain_mock)

    state = {"ticket_id": "t1", "message": "refund please", "trace": []}
    with patch("sentinel.nodes.classifier.CLASSIFIER_PROMPT") as prompt:
        prompt.__or__ = MagicMock(return_value=chain_mock)
        result = classify_ticket(state)

    assert result["route"] == Route.BILLING
    assert result["confidence"] == 0.9


def test_low_confidence_escalates():
    from sentinel.nodes.classifier import classify_ticket
    from unittest.mock import patch, MagicMock

    chain_mock = MagicMock()
    chain_mock.invoke.return_value = _mock_llm_response(
        '{"category": "general", "confidence": 0.3, "reasoning": "unclear"}'
    )

    state = {"ticket_id": "t2", "message": "something weird", "trace": []}
    with patch("sentinel.nodes.classifier.ChatOpenAI") as mock_llm, \
         patch("sentinel.nodes.classifier.CLASSIFIER_PROMPT") as prompt:
        mock_llm.return_value.__or__ = MagicMock(return_value=chain_mock)
        prompt.__or__ = MagicMock(return_value=chain_mock)
        result = classify_ticket(state)

    assert result["route"] == Route.ESCALATE
