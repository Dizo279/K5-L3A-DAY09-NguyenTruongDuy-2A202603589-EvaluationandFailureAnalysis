"""Reproduce the ticket-trust failure and its fixed control."""
import pytest

pytestmark = pytest.mark.student


def test_ticket_trust_trace_is_regression_and_fixed_control_passes():
    from lab9.trace_case import investigate

    broken = investigate("seeded_regression", "C-002", 55)
    broken_trial, broken_label = broken["trial"], broken["label"]
    assert any(event.get("kind") == "model_override" for event in broken_trial["events"])
    assert broken_trial["snapshot"]["refund_vnd"] != broken_label["refund_vnd"]
    assert broken_trial["result"]["status"] != broken_label["status"]

    fixed = investigate("fixed", "C-002", 55)
    fixed_trial, fixed_label = fixed["trial"], fixed["label"]
    assert not any(event.get("kind") == "model_override" for event in fixed_trial["events"])
    assert fixed_trial["snapshot"]["refund_vnd"] == fixed_label["refund_vnd"]
    assert fixed_trial["result"]["status"] == fixed_label["status"]
