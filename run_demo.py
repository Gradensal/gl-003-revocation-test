from datetime import UTC, datetime, timedelta

from authorization import Authorization
from policy import ActionProposal, evaluate_action
from receipt import DecisionReceipt

BASE = datetime(
    2026,
    9,
    29,
    10,
    0,
    tzinfo=UTC,
)


def make_authorization(
    suffix: str,
) -> Authorization:
    return Authorization(
        authorization_id=f"AUTH-{suffix}",
        agent_id="procurement-agent",
        objective="Create approved procurement actions",
        created_at=BASE,
        expires_at=BASE + timedelta(hours=2),
    )


def run_scenario(
    number: int,
    name: str,
    authorization: Authorization,
    proposal: ActionProposal,
    checked_at: datetime,
) -> DecisionReceipt:
    result = evaluate_action(
        authorization,
        proposal,
        checked_at,
    )

    receipt = DecisionReceipt.from_evaluation(
        authorization,
        proposal,
        result,
    )

    print(f"\n[{number}] {name}")
    print(
        "Authorization state: "
        f"{result.authorization_state.value.upper()}"
    )
    print(
        f"Decision: {result.decision.value.upper()}"
    )
    print(f"Reason: {result.reason_code}")

    filename = (
        "evidence/receipts/"
        f"{number:02d}-"
        f"{name.lower().replace(' ', '-')}.json"
    )

    receipt.write_json(filename)

    print(f"Receipt: {filename}")

    return receipt


def main() -> None:
    print("GL-003 — Revocation Test")
    print(
        "Action-boundary authorization experiment"
    )

    active_auth = make_authorization("001")

    active_proposal = ActionProposal(
        proposal_id="P-001",
        agent_id="procurement-agent",
        action="create_purchase_order",
        resource="office-chair",
        proposed_at=BASE + timedelta(minutes=5),
    )

    run_scenario(
        1,
        "Active Authority",
        active_auth,
        active_proposal,
        BASE + timedelta(minutes=6),
    )

    revoked_auth = make_authorization("002")

    revoked_auth.revoke(
        BASE + timedelta(minutes=10)
    )

    revoked_proposal = ActionProposal(
        proposal_id="P-002",
        agent_id="procurement-agent",
        action="create_purchase_order",
        resource="monitor",
        proposed_at=BASE + timedelta(minutes=11),
    )

    run_scenario(
        2,
        "Revoked Authority",
        revoked_auth,
        revoked_proposal,
        BASE + timedelta(minutes=12),
    )

    expired_auth = make_authorization("003")

    expired_proposal = ActionProposal(
        proposal_id="P-003",
        agent_id="procurement-agent",
        action="create_purchase_order",
        resource="keyboard",
        proposed_at=(
            BASE + timedelta(hours=2, minutes=1)
        ),
    )

    run_scenario(
        3,
        "Expired Authority",
        expired_auth,
        expired_proposal,
        BASE + timedelta(hours=2, minutes=1),
    )

    midrun_auth = make_authorization("004")

    midrun_proposal = ActionProposal(
        proposal_id="P-004",
        agent_id="procurement-agent",
        action="create_purchase_order",
        resource="laptop-dock",
        proposed_at=BASE + timedelta(minutes=20),
    )

    midrun_auth.revoke(
        BASE + timedelta(minutes=21)
    )

    run_scenario(
        4,
        "Midrun Revocation",
        midrun_auth,
        midrun_proposal,
        BASE + timedelta(minutes=22),
    )

    print("\nSUMMARY")
    print("1 ALLOW, 3 DENY")

    print(
        "Core finding: a proposal valid when created "
        "can still be denied at execution"
    )

    print(
        "if delegated authority is revoked before "
        "the action boundary."
    )


if __name__ == "__main__":
    main()
