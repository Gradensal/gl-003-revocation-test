# GL-003 — Build Ledger

**Project:** Revocation Test
**Lab:** Gradensal Lab
**Project type:** Deterministic runtime-authorization research prototype
**Document purpose:** Historical engineering record and release handoff

> **Evidence convention:** Historical verification statements below describe the checkpoints recorded during development. They are not a claim that tests, CI, or the demo have been rerun on the final release commit.

---

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

**Design decision:** The proposal does not preserve the authority that existed when it was created. The policy evaluates authorization when the consequential action is considered for execution.

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

These receipts provide inspectable evaluation evidence. The prototype does not claim cryptographic integrity or tamper-proof logging.

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

This JSON is an illustrative excerpt of the relevant receipt fields, not a claim that the complete generated receipt contains only these four fields.

`UNAVAILABLE` is deliberately **not** modeled as a fourth authorization lifecycle state.

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

Demonstration summary recorded at the October 6 checkpoint:

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

Engineering state **recorded at the October 6 checkpoint**:

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

The public demonstration screenshot was cropped to avoid exposing the local development directory.

### Git Checkpoints

Implementation:

```text
0a0e6cb Add fail-closed authorization handling
```

Documentation and evidence:

```text
2ec08b8 Document fail-closed authorization evidence
```

These are historical commit references. The final release commit, remote publication and tag must be verified separately.

### Research Finding

The experiment supports a runtime-authorization principle:

> Authority must be both valid and verifiable at the consequential action boundary.

A previously valid proposal does not preserve authority.

If authority has been revoked or expired, execution is denied.

If current authority cannot be established, GL-003 fails closed rather than guessing, and preserves an auditable reason for the denial.

### Important Design Distinction

```text
AUTHORIZATION STATE
ACTIVE / REVOKED / EXPIRED

is different from

AUTHORIZATION AVAILABILITY
AVAILABLE / UNAVAILABLE
```

`UNAVAILABLE` does not describe the lifecycle state of an authorization. It means the policy layer cannot establish a verifiable authorization record at decision time.

### Historical Project Status

**As recorded on October 6:**

```text
Milestone status: VERIFIED
Local tests: GREEN
Ruff: GREEN
GitHub Actions CI: GREEN
Working tree at checkpoint: CLEAN
```

This historical checkpoint must not be substituted for verification of the final documentation and release commit.

### Next Possible Research Direction

Future work could investigate:

```text
malformed authorization records
authorization-service lookup failure
distributed or stale authorization data
explicit comparison of fail-open vs fail-closed behavior
```

These are future extensions, not requirements for the current GL-003 milestone.

---

## 2026-10-08 — Final Documentation and Release Preparation

### Milestone 11 — Public Documentation Reconciliation

A revised `README.md` was prepared to preserve the existing implementation description while improving formatting, technical clarity, and consistency between the five-scenario output, receipt inventory, test information, and limitations.

This Build Ledger consolidates the milestone history above without changing the meaning of prior engineering decisions or rewriting the original checkpoint results.

**Documentation preparation is not, by itself, evidence of release completion.** The updated files still need to be saved to the repository, inspected, and verified against the checked-out source.

### Final Demonstration Acceptance Matrix

| Scenario | State or verification condition at action boundary | Expected decision | Expected reason code |
|---|---|---|---|
| Active authority | `ACTIVE` | `ALLOW` | `AUTHORIZED` |
| Revoked authority | `REVOKED` | `DENY` | `AUTHORIZATION_REVOKED` |
| Expired authority | `EXPIRED` | `DENY` | `AUTHORIZATION_EXPIRED` |
| Mid-run revocation | `REVOKED` after proposal creation | `DENY` | `AUTHORIZATION_REVOKED` |
| Authorization unavailable | No verifiable authorization record | `DENY` | `AUTHORIZATION_UNAVAILABLE` |

**Acceptance criterion:** The final demo run matches all five expected decisions and produces five inspectable receipts. Record its actual output under `evidence/test-results/` only after running it.

### Release Verification Commands

From the existing repository root, in the project's configured Python environment:

```bash
git status --short
git log -1 --oneline
python --version
python -m pytest -q
ruff check .
python run_demo.py
```

Expected behavior based on the last recorded checkpoint:

```text
pytest: 11 tests pass
Ruff: no violations
Demo: 1 ALLOW, 4 DENY
```

**These are expectations to recheck, not newly observed October 8 results.** If a command fails, preserve the failure evidence and fix the smallest cause before publishing a release.

To inspect the generated evidence:

```bash
find evidence/receipts -maxdepth 1 -type f | sort
ls -l evidence/test-results/
```

Confirm that the current demo output, saved text results, screenshots, and README accurately describe the same revision of the project.

### Verification and Security Boundaries

Check the following before release:

- No `.env` secrets, access tokens, credentials, or private data are included in tracked files.
- Synthetic receipts do not expose sensitive environment or local machine information.
- The README's dependency installation and run commands work from the actual repository.
- `README.md`, `docs/architecture.md`, `PROJECT.md`, and this ledger agree on implemented behavior.
- The 11-test badge and GitHub Actions badge reflect the intended release commit.
- The project's `LICENSE` file exists and reflects the intended public license.
- No assertion of production-grade authorization, cryptographic guarantees, or distributed revocation is made without evidence.

### Known Technical Limitations

1. **Synthetic authorization data:** No production identity service or connected enterprise application is exercised.
2. **Local deterministic policy:** The experiment isolates rule behavior; it is not a complete identity and access management system.
3. **Time-of-check/time-of-use risk:** Action-boundary checking does not by itself prove that a real external action and an authorization check are atomic.
4. **No distributed revocation guarantee:** Propagation delays, stale caches, network partitions, and concurrency have not been evaluated.
5. **Availability trade-off:** Failing closed can block otherwise legitimate operations during authorization outages.
6. **No benchmark claims:** The scenario results do not establish latency, throughput, operating cost, or real-world security effectiveness.
7. **Receipt limits:** JSON receipts are inspectable decision records, not proven tamper-evident audit logs.

### Portfolio Evidence and Publication

Recommended durable evidence:

```text
README.md
BUILD_LEDGER.md
PROJECT.md
docs/architecture.md
tests/test_revocation.py
evidence/receipts/
evidence/test-results/
evidence/screenshots/05-fail-closed-authorization-demo.png
```

A short case study can describe the user problem, research hypothesis, architecture, five scenarios, measured outcomes, failure boundaries, and business implications. It must clearly identify GL-003 as a research prototype.

**Portfolio thesis:** A delegated agent action can be valid when proposed and denied later if its authority changes or cannot be verified before execution.

### Release Readiness Checklist

- [ ] Updated README saved and links/diagrams render correctly
- [ ] Original Build Ledger history preserved and final section saved
- [ ] Source tree and README commands checked against actual files
- [ ] All automated tests pass on the release commit
- [ ] Ruff passes on the release commit
- [ ] All five demo outcomes reproduced
- [ ] All five receipts present and inspected
- [ ] Test and demo evidence saved from the final revision
- [ ] No secrets or sensitive paths in tracked files or screenshots
- [ ] Git working tree reviewed and intended changes committed
- [ ] GitHub Actions green on the final commit
- [ ] Existing tags checked before creating `v0.1.0`
- [ ] Versioned GitHub release published if appropriate
- [ ] Portfolio entry linked to verified repository/release

### Proposed Release Summary

**Release title:** `GL-003 — Revocation Test v0.1.0`

**Release scope:** A deterministic research prototype showing active, revoked, expired, mid-run-revoked, and unavailable-authorization scenarios at an action boundary, accompanied by tests and inspectable decision receipts.

The tag and release must not be described as published until they exist on GitHub.

### Completion Rule

GL-003 may be marked **released** when all relevant release-readiness checks are satisfied on an identifiable commit.

Until then, its appropriate status is:

```text
Implementation and historical evaluation: recorded
Documentation update: prepared for repository reconciliation
Final test/demo reproduction: pending confirmation
Tagged GitHub release: pending confirmation
```

---

## Closing Engineering Insight

The central insight is **temporal authority**: permission is not necessarily valid forever because it was valid at proposal creation.

GL-003 makes three distinct denial conditions visible: revoked authority, expired authority, and unverifiable authority. The fourth denial demonstration shows that revocation during a running workflow must be considered at the action boundary.

The experiment establishes those behaviors in a controlled prototype and leaves production-grade distributed enforcement as a separate engineering problem.


---

## 2026-10-08 — Final Local Verification

Reproduced the GL-003 authorization experiment using the
existing Python 3.12.6 virtual environment.

### Automated Verification

Command: `python -m pytest -q`

Result: 11 tests passed.

Command: `ruff check .`

Result: All checks passed.

### Controlled Demonstration

Command: `python run_demo.py`

Verified five scenarios:

| Scenario | Decision | Reason |
|---|---|---|
| Active authority | ALLOW | AUTHORIZED |
| Revoked authority | DENY | AUTHORIZATION_REVOKED |
| Expired authority | DENY | AUTHORIZATION_EXPIRED |
| Mid-run revocation | DENY | AUTHORIZATION_REVOKED |
| Authorization unavailable | DENY | AUTHORIZATION_UNAVAILABLE |

Summary: **1 ALLOW, 4 DENY**.

All five expected JSON receipts were generated in
`evidence/receipts/`.

### Repository Inspection

- MIT license present.
- Python 3.12 configured for Ruff and CI.
- No environment-variable references found in Python files.
- No tracked secret-like filenames found by the inspection command.
- Existing CI workflow identified at `.github/workflows/ci.yml`.
- Existing Git tag `v0.1.0` identified.

### Remaining Release Actions

- Commit final documentation.
- Push to GitHub.
- Verify GitHub Actions on the final commit.
- Compare the existing `v0.1.0` tag with the final commit.
- Publish a new patch release only if needed.
- Link the verified release from the portfolio.

### Conclusion

The local prototype passes its documented automated checks
and reproduces all five synthetic authorization decisions.

Production authorization and distributed revocation guarantees
remain outside the project's tested scope.
