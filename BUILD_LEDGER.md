# GL-003 — Build Ledger

## 2026-09-29 / 2026-09-30

### Milestone 1 — Project Initialization

Created the GL-003 repository scaffold.

Established:

```text
Python virtual environment
Git repository
pytest test environment
Gradensal Lab project structure
```

### Milestone 2 — Authorization Lifecycle

Implemented:

```text
ACTIVE
REVOKED
EXPIRED
```

Added explicit revocation timestamp handling and expiration-boundary evaluation.

### Milestone 3 — Runtime Policy Evaluation

Implemented deterministic policy evaluation at the action boundary.

Decision outcomes:

```text
ALLOW
DENY
```

Primary reason codes:

```text
AUTHORIZED
AUTHORIZATION_REVOKED
AUTHORIZATION_EXPIRED
AGENT_MISMATCH
AUTHORIZATION_NOT_YET_VALID
PROPOSAL_PREDATES_AUTHORIZATION
PROPOSAL_FROM_FUTURE
```

### Milestone 4 — Decision Evidence

Implemented JSON decision receipts containing:

```text
authorization ID
agent ID
proposal ID
action
resource
decision
reason code
authorization state
proposal timestamp
policy-check timestamp
```

### Milestone 5 — Controlled Demonstration

Implemented four primary scenarios:

```text
active authority
revoked authority
expired authority
mid-run revocation
```

The mid-run scenario creates a proposal while authority is active, revokes authority before execution, and re-evaluates authorization at the action boundary.

Expected result:

```text
DENY
AUTHORIZATION_REVOKED
```

### Milestone 6 — Automated Verification

Created automated tests covering authorization lifecycle, policy decisions, edge cases, agent mismatch, revocation rules, and receipt serialization.

Verification artifacts are stored under:

```text
evidence/test-results/
```

---

## 2026-10-06

### Milestone 7 — Fail-Closed Authorization Verification

Extended GL-003 beyond known authorization states to test what happens when current authority cannot be established at the action boundary.

Previously, `evaluate_action()` assumed that an `Authorization` object would always be available.

A new test exposed the resulting failure:

```text
authorization = None
        ↓
policy attempts authorization.agent_id
        ↓
AttributeError
```

The policy contract was updated to accept:

```python
Authorization | None
```

When no verifiable authorization is available, the policy now returns:

```text
DENY
AUTHORIZATION_UNAVAILABLE
authorization_state = None
```

rather than crashing or assuming that previously granted authority remains valid.

### Milestone 8 — Auditable Fail-Closed Decisions

Extended `DecisionReceipt` so a denied action can still produce audit evidence when no authorization record is available.

The receipt preserves missing authorization information as:

```json
{
  "authorization_id": null,
  "decision": "deny",
  "reason_code": "AUTHORIZATION_UNAVAILABLE",
  "authorization_state": null
}
```

`UNAVAILABLE` is deliberately not modeled as a fourth authorization lifecycle state.

The lifecycle remains:

```text
ACTIVE
REVOKED
EXPIRED
```

Authorization availability is treated as a separate verification concern.

### Milestone 9 — Controlled Demonstration Expansion

Expanded the executable demonstration from four to five scenarios:

```text
1. Active authority          -> ALLOW
2. Revoked authority         -> DENY
3. Expired authority         -> DENY
4. Mid-run revocation        -> DENY
5. Authorization unavailable -> DENY
```

Current demonstration summary:

```text
1 ALLOW, 4 DENY
```

The fifth scenario produces:

```text
AUTHORIZATION_UNAVAILABLE
```

and generates:

```text
evidence/receipts/05-authorization-unavailable.json
```

### Milestone 10 — Verification and Documentation

Current verified engineering state:

```text
Python 3.12
11 automated tests passing
Ruff checks passing
5 controlled scenarios
5 machine-readable decision receipts
GitHub Actions CI passing
```

Updated:

```text
policy.py
receipt.py
run_demo.py
tests/test_revocation.py
README.md
docs/architecture.md
evidence/test-results/
```

Added or refreshed evidence:

```text
evidence/receipts/05-authorization-unavailable.json
evidence/screenshots/05-fail-closed-authorization-demo.png
evidence/test-results/demo.txt
evidence/test-results/pytest.txt
```

The public demonstration screenshot was also cropped to avoid exposing the local development directory.

### Git Checkpoints

Implementation:

```text
0a0e6cb Add fail-closed authorization handling
```

Documentation and evidence:

```text
2ec08b8 Document fail-closed authorization evidence
```

### Research Finding

The experiment now supports a broader runtime-authorization principle:

> Authority must be both valid and verifiable at the consequential action boundary.

A previously valid proposal does not preserve authority.

If authority has been revoked or expired, execution is denied.

If current authority cannot be established, GL-003 fails closed rather than guessing, and it preserves an auditable reason for the denial.

### Important Design Distinction

```text
AUTHORIZATION STATE
ACTIVE / REVOKED / EXPIRED

is different from

AUTHORIZATION AVAILABILITY
AVAILABLE / UNAVAILABLE
```

`UNAVAILABLE` does not describe the lifecycle state of an authorization.

It means the policy layer cannot establish a verifiable authorization record at decision time.

### Current Project Status

```text
Milestone status: VERIFIED
Local tests: GREEN
Ruff: GREEN
GitHub Actions CI: GREEN
Working tree at checkpoint: CLEAN
```

### Next Possible Research Direction

Future work could investigate one of the following without changing the conclusions already demonstrated:

```text
malformed authorization records
authorization-service lookup failure
distributed or stale authorization data
explicit comparison of fail-open vs fail-closed behavior
```

These are future extensions, not requirements for the current GL-003 milestone.