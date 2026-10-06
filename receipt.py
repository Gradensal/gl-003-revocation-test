import json
from dataclasses import dataclass
from pathlib import Path

from authorization import Authorization
from policy import ActionProposal, PolicyResult


@dataclass(frozen=True)
class DecisionReceipt:
    receipt_id: str
    authorization_id: str | None
    agent_id: str
    proposal_id: str
    action: str
    resource: str
    decision: str
    reason_code: str
    authorization_state: str | None
    proposed_at: str
    checked_at: str

    @classmethod
    def from_evaluation(
        cls,
        authorization: Authorization | None,
        proposal: ActionProposal,
        result: PolicyResult,
    ) -> "DecisionReceipt":
        timestamp = int(result.checked_at.timestamp())

        authorization_id = (
            authorization.authorization_id
            if authorization is not None
            else None
        )

        authorization_state = (
            result.authorization_state.value
            if result.authorization_state is not None
            else None
        )

        return cls(
            receipt_id=(
                f"RR-{proposal.proposal_id}-{timestamp}"
            ),
            authorization_id=authorization_id,
            agent_id=proposal.agent_id,
            proposal_id=proposal.proposal_id,
            action=proposal.action,
            resource=proposal.resource,
            decision=result.decision.value,
            reason_code=result.reason_code,
            authorization_state=authorization_state,
            proposed_at=proposal.proposed_at.isoformat(),
            checked_at=result.checked_at.isoformat(),
        )

    def to_dict(self) -> dict[str, str | None]:
        return {
            "receipt_id": self.receipt_id,
            "authorization_id": self.authorization_id,
            "agent_id": self.agent_id,
            "proposal_id": self.proposal_id,
            "action": self.action,
            "resource": self.resource,
            "decision": self.decision,
            "reason_code": self.reason_code,
            "authorization_state": self.authorization_state,
            "proposed_at": self.proposed_at,
            "checked_at": self.checked_at,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            indent=2,
        )

    def write_json(
        self,
        path: str | Path,
    ) -> None:
        destination = Path(path)

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination.write_text(
            self.to_json() + "\n",
            encoding="utf-8",
        )