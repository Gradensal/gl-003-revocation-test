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

### Research Finding

The experiment demonstrates that a previously valid proposal should not be treated as proof of continuing authority.

Current authorization state must be evaluated near the consequential action boundary.
