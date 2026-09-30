# GL-003 — Revocation Test

## Project Type

Gradensal Lab research prototype.

## Research Question

What happens when an AI agent's delegated authority changes after the agent has already started working?

## Hypothesis

Authorization should not be assumed to remain valid for the lifetime of an agent session.

For consequential actions, current authority should be evaluated as close as possible to the action boundary.

## Core Architecture

```text
Human / Authority Owner
        |
        v
Authorization State
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
 Execute  Stop
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

## Acceptance Criteria

Scenario 1:

```text
ACTIVE authorization
valid proposal
current policy check
=> ALLOW
```

Scenario 2:

```text
authorization revoked before proposal
current policy check
=> DENY / AUTHORIZATION_REVOKED
```

Scenario 3:

```text
authorization expired
current policy check
=> DENY / AUTHORIZATION_EXPIRED
```

Scenario 4:

```text
proposal created while ACTIVE
authority revoked before execution
current policy check
=> DENY / AUTHORIZATION_REVOKED
```

Scenario 4 is the central research test.

## Design Principles

The agent does not determine its own authority.

Authorization state exists independently of the action proposal.

Policy evaluation uses current authorization state.

Revocation is explicit and timestamped.

Expiration is evaluated at the requested action boundary.

Decision evidence is preserved as JSON.

The experiment fails closed for revoked, expired, or mismatched-agent cases.

## Non-Goals

GL-003 does not attempt to implement:

```text
production IAM
OAuth infrastructure
cryptographic delegation
distributed policy propagation
payment execution
credential vaulting
agent sandboxing
hardware isolation
distributed consensus
production-grade security
```

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
Question: What happens when authority changes?
Layer: Revocation / Runtime Authorization
```

## Portfolio Claim

The defensible claim for GL-003 is:

> I built a deterministic experiment demonstrating why delegated authority should be re-evaluated at a consequential action boundary rather than assumed to remain valid throughout an agent session.
