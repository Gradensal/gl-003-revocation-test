# GL-003 Architecture

## Working Model

```text
                    HUMAN / AUTHORITY OWNER
                              |
                       grant / revoke
                              |
                              v
                    AUTHORIZATION RECORD
                              |
                   +----------+----------+
                   |                     |
                AVAILABLE             UNAVAILABLE
                   |                     |
                   v                     v
           AUTHORIZATION STATE       FAIL CLOSED
        ACTIVE / REVOKED / EXPIRED       |
                   |                     |
                   +----------+----------+
                              |
                              v
                      POLICY CHECKPOINT
                              ^
                              |
                         AI AGENT
                              |
                           proposes
                              |
                              v
                       ACTION PROPOSAL
                              |
                              v
                         ALLOW / DENY
                              |
                    +---------+---------+
                    |                   |
                    v                   v
                 EXECUTE               STOP
                    |                   |
                    +---------+---------+
                              |
                              v
                       DECISION RECEIPT
```

## Key Separation

```text
AGENT CAPABILITY
does not equal
CURRENT AUTHORITY
```

and:

```text
AUTHORITY AT SESSION START
does not equal
AUTHORITY AT ACTION TIME
```

GL-003 also distinguishes:

```text
AUTHORIZATION STATE
from
AUTHORIZATION AVAILABILITY
```

`ACTIVE`, `REVOKED`, and `EXPIRED` are lifecycle states of an authorization that can be evaluated.

`UNAVAILABLE` is not a fourth lifecycle state. It means the policy layer cannot establish a verifiable authorization record at the action boundary.

In that condition, the policy fails closed.

## Mid-Run Revocation Sequence

```text
10:00
Authorization ACTIVE

10:20
Agent creates proposal

10:21
Human revokes authorization

10:22
Policy checkpoint evaluates current authority

10:22
DENY
AUTHORIZATION_REVOKED
```

## Authorization-Unavailable Sequence

```text
10:30
Agent creates proposal

10:31
Action reaches policy checkpoint

10:31
No verifiable authorization is available

10:31
DENY
AUTHORIZATION_UNAVAILABLE

10:31
Decision receipt records:
authorization_id = null
authorization_state = null
```

## Policy Boundary

The agent may propose an action.

The agent does not decide whether its own authority remains valid.

That decision belongs to an independent policy boundary evaluated at action time.

The policy distinguishes between:

```text
KNOWN AUTHORIZATION
        |
        +-- ACTIVE  -> ALLOW when other policy checks pass
        +-- REVOKED -> DENY
        +-- EXPIRED -> DENY

NO VERIFIABLE AUTHORIZATION
        |
        +-- DENY
            AUTHORIZATION_UNAVAILABLE
```

## Audit Behavior

A fail-closed decision should still leave evidence.

When authorization is unavailable, GL-003 does not fabricate an authorization identifier or lifecycle state.

Instead, the receipt records:

```json
{
  "authorization_id": null,
  "decision": "deny",
  "reason_code": "AUTHORIZATION_UNAVAILABLE",
  "authorization_state": null
}
```

This preserves the distinction between:

- a known revoked authorization;
- a known expired authorization;
- and an authorization whose current validity cannot be established.

## Architectural Principle

**Authority must be valid and verifiable at the consequential action boundary.**

A previously valid proposal does not preserve authority.

If authority has been revoked or expired, the action is denied.

If current authority cannot be established, the system fails closed and preserves an auditable denial reason.