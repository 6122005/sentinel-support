"""End-to-end graph test with mocked LLM."""

from unittest.mock import patch, MagicMock

from langgraph.checkpoint.sqlite import SqliteSaver
from sentinel.graph import build_graph


def _mock_chain(content: str):
    chain = MagicMock()
    chain.invoke.return_value = MagicMock(content=content)
    return chain


def test_small_refund_resolved():
    chain = _mock_chain('{"category": "billing", "confidence": 0.9, "reasoning": "refund"}')
    with patch("sentinel.nodes.classifier.ChatOpenAI") as mock_llm, \
         patch("sentinel.nodes.classifier.CLASSIFIER_PROMPT") as prompt:
        mock_llm.return_value.__or__ = MagicMock(return_value=chain)
        prompt.__or__ = MagicMock(return_value=chain)

        checkpointer = SqliteSaver.from_conn_string(":memory:")
        graph = build_graph(checkpointer=checkpointer)

        result = graph.invoke(
            {
                "ticket_id": "t1",
                "customer_id": "cust_102",
                "message": "refund for ord_902",
                "trace": [],
            },
            {"configurable": {"thread_id": "t1"}},
        )

    assert result["needs_human"] is False
    assert "Refund" in result["resolution"]


def test_large_refund_escalates():
    chain = _mock_chain('{"category": "billing", "confidence": 0.9, "reasoning": "refund"}')
    with patch("sentinel.nodes.classifier.ChatOpenAI") as mock_llm, \
         patch("sentinel.nodes.classifier.CLASSIFIER_PROMPT") as prompt:
        mock_llm.return_value.__or__ = MagicMock(return_value=chain)
        prompt.__or__ = MagicMock(return_value=chain)

        checkpointer = SqliteSaver.from_conn_string(":memory:")
        graph = build_graph(checkpointer=checkpointer)

        result = graph.invoke(
            {
                "ticket_id": "t2",
                "customer_id": "cust_101",
                "message": "refund for ord_901",
                "trace": [],
            },
            {"configurable": {"thread_id": "t2"}},
        )

    assert result["needs_human"] is True
    assert "Refund approval required" in result["escalation_summary"]
