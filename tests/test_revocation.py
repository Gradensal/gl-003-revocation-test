from datetime import UTC, datetime, timedelta

import pytest

from authorization import Authorization, AuthorizationState
from policy import (
    ActionProposal,
    PolicyDecision,
    evaluate_action,
)
from receipt import DecisionReceipt

BASE = datetime(
    2026,
    9,
    29,
    10,
    0,
    tzinfo=UTC,
)


def make_authorization() -> Authorization:
    return Authorization(
        authorization_id="AUTH-TEST",
        agent_id="agent-001",
        objective="Perform approved test actions",
        created_at=BASE,
        expires_at=BASE + timedelta(hours=2),
    )


def make_proposal(
    proposed_at: datetime | None = None,
    agent_id: str = "agent-001",
) -> ActionProposal:
    return ActionProposal(
        proposal_id="P-TEST",
        agent_id=agent_id,
        action="write_record",
        resource="test-resource",
        proposed_at=(
            proposed_at
            or BASE + timedelta(minutes=5)
        ),
    )


def test_active_authorization_allows_action() -> None:
    auth = make_authorization()

    result = evaluate_action(
        auth,
        make_proposal(),
        BASE + timedelta(minutes=6),
    )

    assert result.decision is PolicyDecision.ALLOW
    assert result.reason_code == "AUTHORIZED"
    assert (
        result.authorization_state
        is AuthorizationState.ACTIVE
    )


def test_revoked_authorization_denies_action() -> None:
    auth = make_authorization()

    auth.revoke(
        BASE + timedelta(minutes=10)
    )

    result = evaluate_action(
        auth,
        make_proposal(
            BASE + timedelta(minutes=11)
        ),
        BASE + timedelta(minutes=12),
    )

    assert result.decision is PolicyDecision.DENY

    assert (
        result.reason_code
        == "AUTHORIZATION_REVOKED"
    )

    assert (
        result.authorization_state
        is AuthorizationState.REVOKED
    )


def test_expired_authorization_denies_action() -> None:
    auth = make_authorization()

    result = evaluate_action(
        auth,
        make_proposal(
            BASE + timedelta(
                hours=2,
                minutes=1,
            )
        ),
        BASE + timedelta(
            hours=2,
            minutes=1,
        ),
    )

    assert result.decision is PolicyDecision.DENY

    assert (
        result.reason_code
        == "AUTHORIZATION_EXPIRED"
    )

    assert (
        result.authorization_state
        is AuthorizationState.EXPIRED
    )


def test_midrun_revocation_denies_previously_valid_proposal() -> None:
    auth = make_authorization()

    proposal = make_proposal(
        BASE + timedelta(minutes=20)
    )

    assert (
        auth.effective_state(
            BASE + timedelta(minutes=20)
        )
        is AuthorizationState.ACTIVE
    )

    auth.revoke(
        BASE + timedelta(minutes=21)
    )

    result = evaluate_action(
        auth,
        proposal,
        BASE + timedelta(minutes=22),
    )

    assert result.decision is PolicyDecision.DENY

    assert (
        result.reason_code
        == "AUTHORIZATION_REVOKED"
    )


def test_agent_mismatch_denies_action() -> None:
    auth = make_authorization()

    result = evaluate_action(
        auth,
        make_proposal(
            agent_id="different-agent"
        ),
        BASE + timedelta(minutes=6),
    )

    assert result.decision is PolicyDecision.DENY
    assert result.reason_code == "AGENT_MISMATCH"


def test_exact_expiration_time_is_expired() -> None:
    auth = make_authorization()

    assert (
        auth.effective_state(auth.expires_at)
        is AuthorizationState.EXPIRED
    )


def test_double_revocation_is_rejected() -> None:
    auth = make_authorization()

    auth.revoke(
        BASE + timedelta(minutes=10)
    )

    with pytest.raises(
        ValueError,
        match="already revoked",
    ):
        auth.revoke(
            BASE + timedelta(minutes=11)
        )


def test_revocation_after_expiration_is_rejected() -> None:
    auth = make_authorization()

    with pytest.raises(
        ValueError,
        match="expired authorization cannot be revoked",
    ):
        auth.revoke(
            BASE + timedelta(hours=2)
        )


def test_receipt_serializes_decision_evidence(
    tmp_path,
) -> None:
    auth = make_authorization()
    proposal = make_proposal()

    result = evaluate_action(
        auth,
        proposal,
        BASE + timedelta(minutes=6),
    )

    receipt = DecisionReceipt.from_evaluation(
        auth,
        proposal,
        result,
    )

    output = tmp_path / "receipt.json"

    receipt.write_json(output)

    content = output.read_text(
        encoding="utf-8"
    )

    assert '"decision": "allow"' in content

    assert (
        '"reason_code": "AUTHORIZED"'
        in content
    )

    assert (
        '"authorization_state": "active"'
        in content
    )


def test_missing_authorization_fails_closed() -> None:
    result = evaluate_action(
        None,
        make_proposal(),
        BASE + timedelta(minutes=6),
    )

    assert result.decision is PolicyDecision.DENY

    assert (
        result.reason_code
        == "AUTHORIZATION_UNAVAILABLE"
    )

    assert result.authorization_state is None


def test_missing_authorization_receipt_preserves_denial_evidence(
    tmp_path,
) -> None:
    proposal = make_proposal()

    result = evaluate_action(
        None,
        proposal,
        BASE + timedelta(minutes=6),
    )

    receipt = DecisionReceipt.from_evaluation(
        None,
        proposal,
        result,
    )

    output = tmp_path / "missing-authorization-receipt.json"

    receipt.write_json(output)

    content = output.read_text(
        encoding="utf-8"
    )

    assert '"decision": "deny"' in content

    assert (
        '"reason_code": "AUTHORIZATION_UNAVAILABLE"'
        in content
    )

    assert '"authorization_id": null' in content
    assert '"authorization_state": null' in content