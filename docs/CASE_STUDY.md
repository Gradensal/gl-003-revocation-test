
# GL-003 — Revocation Test

## When an AI Agent's Permission Changes Mid-Task

**Gradensal Lab | Reliable Agent Systems**

**Author:** Lissette Gorrin Rodriguez  
**Project type:** Independent engineering research prototype  
**Language:** Python 3.12  
**Focus:** Runtime authorization, revocation, fail-closed controls, decision evidence

---

## Executive Summary

GL-003 — Revocation Test examines a problem in long-running AI agent workflows:

**An action may have been authorized when proposed, but that authorization may no longer be valid when execution occurs.**

I built a deterministic Python prototype to test whether a policy layer can reevaluate delegated authority at the action boundary.

The controlled demonstration covers five authorization conditions: active, revoked, expired, mid-run revoked, and unavailable.

The recorded demonstration produces **1 ALLOW and 4 DENY** decisions, including a fail-closed denial when current authorization cannot be established.

The prototype illustrates authorization lifecycle enforcement and decision traceability. It is not a production identity or authorization system.

---

## 1. The Problem

Enterprise agents increasingly operate through multi-step workflows.

Between receiving permission and attempting an action:

- A user may revoke authorization.
- An authorization may expire.
- The agent's permitted scope may change.
- An authorization record may become unavailable.

If an agent treats its original approval as permanent, it can attempt an action after the authority required for that action has ceased to exist.

The system must distinguish between:

**Authority that existed when a proposal was created** and **authority that is valid when an action is evaluated**.

---

## 2. Research Question

What happens when an agent creates an action proposal while its delegated authority is valid, but that authority is revoked before execution?

A related question is:

What should happen when the system cannot establish the authorization state at the action boundary?

### Hypothesis

A deterministic policy layer that checks current authority before execution can deny actions based on revoked, expired, or unverifiable authorization rather than trusting earlier approval.

---

## 3. My Contribution

I developed the GL-003 prototype and organized its evaluation around authorization lifecycle transitions.

The work includes:

- Modeling active, revoked, and expired authorization states
- Implementing runtime policy decisions
- Separating authorization lifecycle state from authorization availability
- Evaluating proposals against current authority
- Handling unavailable authorization without a policy crash
- Producing machine-readable decision receipts
- Testing policy behavior and edge conditions
- Creating reproducible demonstration scenarios
- Documenting results, engineering decisions, and limitations

This is an independent laboratory project, not a client deployment or a claim of production security ownership.

---

## 4. Architecture

The agent proposes an action.

The policy layer evaluates whether the agent currently has valid authority for that action.

The action boundary then enforces the policy decision and produces evidence explaining the result.

```text
AGENT
  |
  v
ACTION PROPOSAL
  |
  v
CURRENT AUTHORIZATION EVALUATION
  |
  +-- ACTIVE and valid ----------> ALLOW
  |
  +-- REVOKED -------------------> DENY
  |
  +-- EXPIRED -------------------> DENY
  |
  +-- UNAVAILABLE --------------> DENY
                                     
          |
          v
    DECISION RECEIPT
          |
          v
    EVALUATION EVIDENCE
```

### Implementation components

**authorization.py**

Models delegated authorization and lifecycle behavior.

**policy.py**

Evaluates the current authorization state and produces an ALLOW or DENY decision with a reason code.

**receipt.py**

Produces machine-readable decision evidence.

**run_demo.py**

Executes the five controlled scenarios and writes decision receipts.

**tests/test_revocation.py**

Provides automated coverage of lifecycle behavior, policy decisions, edge cases, identity matching, and receipt handling.

---

## 5. The Five-Scenario Experiment

| Scenario | Expected result | Recorded result | Reason |
|---|---|---|---|
| Active authority | ALLOW | ALLOW | AUTHORIZED |
| Revoked authority | DENY | DENY | AUTHORIZATION_REVOKED |
| Expired authority | DENY | DENY | AUTHORIZATION_EXPIRED |
| Mid-run revocation | DENY | DENY | AUTHORIZATION_REVOKED |
| Authorization unavailable | DENY | DENY | AUTHORIZATION_UNAVAILABLE |

### Recorded demonstration summary

**5 scenarios: 1 ALLOW, 4 DENY**

The mid-run revocation scenario is the central experiment.

1. The agent has active authorization.
2. It creates an action proposal.
3. Authorization is revoked before execution.
4. The action boundary reevaluates current authority.
5. The policy denies the action.

The proposal does not preserve the original authorization.

### Fail-closed extension

The authorization-unavailable scenario was introduced after testing the assumption that a valid authorization object would always exist.

Previously, evaluating a missing authorization could raise an `AttributeError` when policy code accessed an attribute on `None`.

The policy contract was extended to accept `Authorization | None`.

When authority cannot be established, the policy returns:

```text
DENY
AUTHORIZATION_UNAVAILABLE
```

The decision receipt preserves the missing authorization fields as null values rather than falsely recording a valid authorization state.

---

## 6. Testing and Evidence

The recorded project checkpoint includes:

- Python 3.12
- 11 passing automated tests
- Passing Ruff checks
- Passing GitHub Actions CI
- Five demonstration scenarios
- Five JSON decision receipts

These results belong to the previously documented checkpoint and should be reconfirmed against the final release commit.

### Reproduction

```bash
python -m pip install -r requirements-dev.txt
ruff check .
python -m pytest -q
python run_demo.py
```

The demonstration writes evidence into:

```text
evidence/receipts/
```

Stored evaluation results are available under:

```text
evidence/test-results/
```

### Selected failure cases

Automated verification includes tests for authorization revocation, expiration boundaries, agent identity mismatches, repeated revocation, and unavailable authority.

These cases investigate the negative paths of the policy, not just successful authorization.

---

## 7. Key Engineering Decisions

### Evaluate current authority

Authorization is checked for the proposed action rather than relying exclusively on a prior session-level approval.

### Keep policy deterministic

The authorization decision is expressed through explicit conditions and reason codes. A language model is not asked to invent whether permission exists.

### Fail closed

Unavailable or unverifiable authority results in denial.

This is a conservative policy with a real availability trade-off.

### Distinguish lifecycle from availability

The authorization lifecycle has three states:

ACTIVE, REVOKED, and EXPIRED.

UNAVAILABLE is not a fourth lifecycle state. It represents the inability to establish an authorization record.

### Preserve decision receipts

Each controlled scenario produces structured evidence describing the resulting decision.

Receipts support debugging and review, but do not independently establish tamper resistance or non-repudiation.

---

## 8. What I Learned

### A proposal is not permanent permission

The agent's planned action and its authorization to execute are different concerns.

### Negative-path tests reveal architectural assumptions

Testing `authorization = None` exposed a failure mode that successful authorization scenarios did not reveal.

### Fail-closed behavior must be deliberate

Failing closed prevents uncertainty from silently becoming permission, but can also interrupt legitimate work.

### Auditable decisions are easier to explain

A decision is more useful when the reason is explicit and associated with an inspectable receipt.

These lessons apply beyond AI agents to other software systems involving time-limited or revocable permissions.

---

## 9. Limitations

GL-003 is a synthetic deterministic prototype.

It does not demonstrate:

- Production identity-provider integration
- Cryptographically signed authorization
- Distributed revocation propagation
- Race-free execution across systems
- Network-partition recovery
- Real payment or email tool execution
- Enterprise deployment
- Measured production throughput or latency
- Compliance certification
- Universal agent security

A production implementation would need additional work on authenticated state changes, concurrency, least privilege, revocation consistency, logging, privacy, and operational recovery.

---

## 10. Business Relevance

As agents begin executing business operations, organizations need controls that remain meaningful throughout the task lifecycle.

Approving an agent at the beginning of a workflow may not be enough if the underlying authority changes before a consequential action.

GL-003 makes that concern testable in a controlled environment.

A practical question for an executive or AI implementation team is:

**Can we demonstrate that an agent stops when its required authority has been withdrawn or cannot be verified?**

This question connects AI system architecture with governance, accountability, risk management, and business process design.

---

## 11. Portfolio Relevance

GL-003 provides evidence relevant to roles involving:

- AI solutions and implementation
- Technical content and developer education
- AI product communication
- Enterprise AI architecture
- AI governance and evaluation
- Technical narrative strategy

It demonstrates the ability to investigate a technical failure mode, implement a controlled test, document evidence, and translate the finding into a business-relevant explanation.

It does not substitute for production engineering, client implementation, team leadership, or real organizational deployment experience.

---

## 12. Future Research

Potential extensions include:

1. Malformed authorization records
2. Authorization-service lookup failures
3. Distributed and stale authorization state
4. Revocation during concurrent execution
5. Time-of-check/time-of-use testing
6. Fail-open versus fail-closed comparison
7. Authorization caching and expiry
8. Tamper-evident decision receipts

These are future directions, not features claimed in the present prototype.

---

## 13. Related Work

GL-003 is part of Gradensal Lab's broader research into reliable AI systems.

**GL-001 — Agent Flight Recorder**

Investigates agent observability and execution evidence.

**GL-002 — Agent Intent Receipt**

Investigates intent and authorization evidence.

**GL-003 — Revocation Test**

Investigates whether previously granted authority remains valid at the execution boundary.

These experiments explore complementary concerns without claiming a production-ready integrated agent-governance platform.

---

## Conclusion

The principal finding of GL-003 is architectural:

**Authority must be valid and verifiable when the consequential action is evaluated.**

An agent may have been legitimately authorized earlier and still be denied later.

The prototype demonstrates this distinction through reproducible synthetic scenarios, deterministic policy decisions, and machine-readable evidence.

---

**About**

Lissette Gorrin Rodriguez — AI Builder × Storyteller

Gradensal Lab: https://github.com/Gradensal

Portfolio: https://lissettegorrin.com/

LinkedIn: https://www.linkedin.com/in/lissettegorrin/
