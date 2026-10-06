# GL-003 — Revocation Test

## Project Type

Gradensal Lab research prototype.

## Research Question

What happens when an AI agent's delegated authority changes, expires, or cannot be verified after the agent has already started working?

## Hypothesis

Authorization should not be assumed to remain valid for the lifetime of an agent session.

For consequential actions, current authority should be evaluated as close as possible to the action boundary.

If current authority cannot be established, the system should fail closed rather than infer permission from earlier authorization.

## Core Architecture

```text
Human / Authority Owner
        |
        v
Authorization Record
        |
   +----+----+
   |         |
AVAILABLE  UNAVAILABLE
   |         |
   v         v
Authorization   FAIL CLOSED
State              |
   |               |
   +-------+-------+
           |
           v
         Agent
           |
           v
   Action Proposal
           |
           v
 Runtime Policy Check
           |
       +---+---+
       |       |
     ALLOW    DENY
       |       |
       v       v
    Execute   Stop
        \       /
         \     /
          v   v
     Decision Evidence
```

## Authorization States

```text
ACTIVE
REVOKED
EXPIRED
```

These are lifecycle states of an authorization that can be evaluated.

`UNAVAILABLE` is not a fourth authorization state.

It means that no verifiable authorization can be established at the action boundary.

## Acceptance Criteria

### Scenario 1 — Active Authority

```text
ACTIVE authorization
valid proposal
current policy check
=> ALLOW / AUTHORIZED
```

### Scenario 2 — Revoked Authority

```text
authorization revoked before proposal
current policy check
=> DENY / AUTHORIZATION_REVOKED
```

### Scenario 3 — Expired Authority

```text
authorization expired
current policy check
=> DENY / AUTHORIZATION_EXPIRED
```

### Scenario 4 — Mid-Run Revocation

```text
proposal created while ACTIVE
authority revoked before execution
current policy check
=> DENY / AUTHORIZATION_REVOKED
```

This remains the central revocation experiment.

### Scenario 5 — Authorization Unavailable

```text
proposal reaches action boundary
no verifiable authorization is available
current policy check
=> DENY / AUTHORIZATION_UNAVAILABLE
```

The resulting decision receipt must preserve the missing information accurately:

```text
authorization_id = null
authorization_state = null
```

The system must not fabricate an authorization state or infer permission from earlier context.

## Design Principles

The agent does not determine its own authority.

Authorization exists independently of the action proposal.

Policy evaluation uses current authorization at the action boundary.

Revocation is explicit and timestamped.

Expiration is evaluated at the requested action boundary.

A previously valid proposal does not preserve authority.

Known revoked authority fails closed.

Known expired authority fails closed.

Unavailable authorization also fails closed.

Authorization availability is separate from authorization lifecycle state.

Missing authorization information is represented as missing data rather than invented values.

Decision evidence is preserved as JSON.

Policy failures should be deterministic and auditable rather than depending on accidental software crashes.

## Current Verified State

```text
Python 3.12
11 automated tests passing
Ruff checks passing
GitHub Actions CI passing
5 controlled scenarios
5 machine-readable decision receipts
```

Demonstration result:

```text
1 ALLOW
4 DENY
```

## Non-Goals

GL-003 does not attempt to implement:

```text
production IAM
OAuth infrastructure
cryptographic delegation
distributed policy propagation
remote authorization-service reliability
payment execution
credential vaulting
agent sandboxing
hardware isolation
distributed consensus
production-grade security
```

The current implementation is a deterministic research prototype designed to isolate runtime authorization behavior.

## Relationship to Gradensal Lab

GL-001:

```text
Question: What did the agent do?
Layer: Observability
```

GL-002:

```text
Question: What was the agent allowed to do?
Layer: Delegated Authority
```

GL-003:

```text
Question: Does that authority still exist and can it be verified at action time?
Layer: Revocation / Runtime Authorization
```

## Portfolio Claim

The defensible claim for GL-003 is:

> I built a deterministic runtime-authorization experiment showing that an AI agent's earlier permission should not automatically authorize a later consequential action. The system re-evaluates authority at the action boundary, denies revoked or expired authority, and fails closed with an auditable reason when current authorization cannot be established.

## Key Technical Insight

```text
PREVIOUS AUTHORIZATION
does not guarantee
CURRENT AUTHORIZATION
```

and:

```text
UNKNOWN AUTHORITY
does not equal
PERMISSION
```

The resulting principle is:

> **Authority must be valid and verifiable at the moment of action.**