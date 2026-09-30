# GL-003 Architecture

## Working Model

```text
                    HUMAN / AUTHORITY OWNER
                              |
                       grant / revoke
                              |
                              v
                    AUTHORIZATION STATE
                   ACTIVE / REVOKED /
                        EXPIRED
                              |
                              |
                +-------------+-------------+
                |                           |
                v                           v
             AI AGENT                POLICY CHECKPOINT
                |                           ^
                | proposes                  |
                v                           |
          ACTION PROPOSAL ------------------+
                                            |
                                      ALLOW / DENY
                                            |
                               +------------+------------+
                               |                         |
                               v                         v
                            EXECUTE                     STOP
                               |                         |
                               +------------+------------+
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

## Architectural Principle

The agent may propose an action.

The agent does not decide whether its own authority remains valid.

That decision belongs to an independent policy boundary using current authorization state.
