"""Routing edge tests."""

from sentinel.graph import route_ticket
from sentinel.state import Route


def test_route_billing():
    assert route_ticket({"route": Route.BILLING}) == "billing"


def test_route_tech():
    assert route_ticket({"route": Route.TECH}) == "tech"


def test_route_escalate():
    assert route_ticket({"route": Route.ESCALATE}) == "escalate"
