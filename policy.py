from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from authorization import Authorization, AuthorizationState


class PolicyDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class ActionProposal:
    proposal_id: str
    agent_id: str
    action: str
    resource: str
    proposed_at: datetime


@dataclass(frozen=True)
class PolicyResult:
    decision: PolicyDecision
    reason_code: str
    checked_at: datetime
    authorization_state: AuthorizationState | None


def evaluate_action(
    authorization: Authorization | None,
    proposal: ActionProposal,
    checked_at: datetime,
) -> PolicyResult:
    if checked_at.tzinfo is None or checked_at.utcoffset() is None:
        raise ValueError("checked_at must be timezone-aware")

    if (
        proposal.proposed_at.tzinfo is None
        or proposal.proposed_at.utcoffset() is None
    ):
        raise ValueError(
            "proposal.proposed_at must be timezone-aware"
        )

    if authorization is None:
        return PolicyResult(
            decision=PolicyDecision.DENY,
            reason_code="AUTHORIZATION_UNAVAILABLE",
            checked_at=checked_at,
            authorization_state=None,
        )

    if proposal.agent_id != authorization.agent_id:
        return PolicyResult(
            decision=PolicyDecision.DENY,
            reason_code="AGENT_MISMATCH",
            checked_at=checked_at,
            authorization_state=authorization.effective_state(
                checked_at
            ),
        )

    if checked_at < authorization.created_at:
        return PolicyResult(
            decision=PolicyDecision.DENY,
            reason_code="AUTHORIZATION_NOT_YET_VALID",
            checked_at=checked_at,
            authorization_state=AuthorizationState.ACTIVE,
        )

    if proposal.proposed_at < authorization.created_at:
        return PolicyResult(
            decision=PolicyDecision.DENY,
            reason_code="PROPOSAL_PREDATES_AUTHORIZATION",
            checked_at=checked_at,
            authorization_state=authorization.effective_state(
                checked_at
            ),
        )

    if proposal.proposed_at > checked_at:
        return PolicyResult(
            decision=PolicyDecision.DENY,
            reason_code="PROPOSAL_FROM_FUTURE",
            checked_at=checked_at,
            authorization_state=authorization.effective_state(
                checked_at
            ),
        )

    effective_state = authorization.effective_state(
        checked_at
    )

    if effective_state is AuthorizationState.REVOKED:
        return PolicyResult(
            decision=PolicyDecision.DENY,
            reason_code="AUTHORIZATION_REVOKED",
            checked_at=checked_at,
            authorization_state=effective_state,
        )

    if effective_state is AuthorizationState.EXPIRED:
        return PolicyResult(
            decision=PolicyDecision.DENY,
            reason_code="AUTHORIZATION_EXPIRED",
            checked_at=checked_at,
            authorization_state=effective_state,
        )

    return PolicyResult(
        decision=PolicyDecision.ALLOW,
        reason_code="AUTHORIZED",
        checked_at=checked_at,
        authorization_state=effective_state,
    )