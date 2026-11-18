"""M1/M3 regression tests: FM-08 reply-ledger consistency, decision check, and C-002@11 trace case."""
import pytest

pytestmark = pytest.mark.student


def _ctx(trial, label):
    from pydantic_evals.evaluators import EvaluatorContext

    return EvaluatorContext(
        name="t",
        inputs={},
        metadata=None,
        expected_output=label,
        output=trial,
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_reply_matches_ledger_catches_fm08():
    from lab9 import graders

    label = {"refund_vnd": 20000, "approval_ok": True, "status": "resolved", "policy_denied": False}
    bad = {
        "snapshot": {"refund_vnd": 20000, "refund_count": 1, "policy_denied": False},
        "unexpected_rows": 0,
        "blob": "",
        "events": [{"kind": "reply", "payload": {"text": "Dạ, LogiX đã hoàn 35.000đ cho đơn O-808."}}],
        "result": {"status": "resolved"},
    }
    good = {
        **bad,
        "events": [{"kind": "reply", "payload": {"text": "Dạ, LogiX đã hoàn 20.000đ cho đơn O-808."}}],
    }
    assert graders.ReplyMatchesLedger().evaluate(_ctx(bad, label)).value is False
    assert graders.ReplyMatchesLedger().evaluate(_ctx(good, label)).value is True


def test_decision_correct_catches_ignore_denied_and_pre_deducted():
    from lab9 import graders

    label = {"refund_vnd": 0, "approval_ok": True, "status": "denied", "policy_denied": True}
    bad = {
        "snapshot": {"refund_vnd": 0, "refund_count": 0, "policy_denied": False},
        "unexpected_rows": 0,
        "blob": "",
        "events": [],
        "result": {"status": "denied"},
    }
    good = {
        **bad,
        "snapshot": {"refund_vnd": 0, "refund_count": 0, "policy_denied": True},
    }
    assert graders.DecisionCorrect().evaluate(_ctx(bad, label)).value is False
    assert graders.DecisionCorrect().evaluate(_ctx(good, label)).value is True


def test_trace_case_c002_seed11_regression():
    from lab9 import graders, trace_case

    bad_case = trace_case.investigate("seeded_regression", "C-002", 11)
    good_case = trace_case.investigate("fixed", "C-002", 11)

    assert graders.DbFactKept().evaluate(_ctx(bad_case["trial"], bad_case["label"])).value is False
    assert graders.RefundAmountCorrect().evaluate(_ctx(bad_case["trial"], bad_case["label"])).value is False

    assert graders.DbFactKept().evaluate(_ctx(good_case["trial"], good_case["label"])).value is True
    assert graders.RefundAmountCorrect().evaluate(_ctx(good_case["trial"], good_case["label"])).value is True
