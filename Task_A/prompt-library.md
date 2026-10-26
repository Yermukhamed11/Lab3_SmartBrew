# SmartBrew AI — reusable prompt library

**Retrospective prompt templates, composed after implementation; not messages actually sent by the student and not a historical transcript.** These templates demonstrate how to structure a future evidence-based development session. They contain no invented assistant responses or claims of student authorship. The readable interaction report is [prompt-log.md](prompt-log.md); the recorded messages are retained in the [conversation appendix](conversation-appendix.md).

## P01 — Elicit traceable requirements

```text
Act as a requirements analyst for SmartBrew AI, a self-service coffee machine.
Read the attached Lab 2 PDF before proposing requirements. Treat it as the human
baseline; do not invent a separately supplied System Description or stakeholder
answers. State that this is baseline-informed refinement, not blind elicitation.

Produce functional requirements using the original columns: ID, Description,
Inputs, Outputs, Precondition, Postcondition. Keep REQ-01–REQ-06 traceable and
separate original physical-system targets from prototype acceptance criteria.
Add measurable NFRs and ten actor/goal/benefit user stories. Preserve the Custom
Feature label for weather/time recommendations. For the product backlog, retain
SB-01–SB-10, original importance scores/story points, and all seven source columns.

Identify every added assumption, missing source and deferred physical interface.
Do not redefine hardware obligations as satisfied merely because a local fixture
passes. Include acceptance criteria that can fail when behavior is incorrect.
```

## P02 — Critically compare human and model artifacts

```text
Compare the proposed artifacts with the supplied Lab 2, using source page
references. Show all ten original human stories beside the refined wording and
explain each change. Compare all six requirements and all ten backlog items.

Distinguish preserved human decisions, useful additions, assumptions, omissions
and scope reductions. The below-15% inventory rule already exists in Lab 2;
credit only new boundary examples/testing to the refinement. Give an individual
reason for every rejected or deferred suggestion, including irrelevant cafe
pickup, loyalty and review features. Identify the limits of a comparison informed
by the baseline. Do not fabricate independent elicitation or instructor approval.
```

## P03 — Generate the ten-feature prototype

```text
Implement exactly SB-01–SB-10: menu/milk-sugar sliders, contactless payment
simulation, weather/time fixture provider, explained recommendations, inventory
alerts, administrator authentication, menu editing, technician PIN/service mode,
pump/heater diagnostics and CSV log export. Include brew progress and daily sales
as supporting original stories, without replacing any selected backlog item.

Use Python standard library, SQLite and a responsive browser UI. Validate inputs
on the server, protect admin/technician operations with separate sessions, and
make order creation plus inventory deductions atomic. Block brewing in service
mode and service entry while a drink is active. Label payments, sensors, weather
and diagnostics as simulations; identify recommendations as deterministic rules.
CSV download requires manual transfer to USB. Document function contracts and
explain architecture, operating assumptions and remaining physical-system gaps.
```

## P04 — Validate actual behavior

```text
Create meaningful HTTP integration tests with isolated temporary databases and
ephemeral ports. Exercise all ten features, wrong credentials/roles, declined
payments, insufficient-stock rollback, strict 15% boundary, offline fallback,
busy/service interlocks, CSV contents and restart persistence. Wait through the
real 12-second simulated brewing interval in a lifecycle test. Do not weaken
assertions or claim commands ran when they did not.

Run the suite and report actual counts, failures, skips, exit status and timing.
The existing project has 19 tests; preserve meaningful coverage rather than
forcing a number. Inspect startup and customer/admin/technician browser journeys
at desktop and mobile widths. Distinguish software evidence from hardware tests.
```

## P05 — Review documentation for independent execution

```text
Audit Task C against every source function/method: document purpose, input
parameters and return/output behavior, including side effects or errors where
useful. Correct inaccurate comments rather than adding decorative documentation.

Make README instructions sufficient for a new Linux machine: clone/cd steps,
Python 3.12.14 as the tested version, SQLite prerequisites, launch/stop commands,
test command and a guided demonstration of all ten features. Explain public demo
credentials, optional environment overrides, persistence and simulation limits.
Record that no third-party runtime packages or live API keys are required. Verify
paths and version files; do not claim untested operating systems or production
security guarantees.
```

## P06 — Package and review the submission

```text
Organize requirements, comparison, source PDF and AI records under Task_A/;
place the executable prototype, tests and execution guide under Task_B/. Keep a
clear root index and shared report. Update links, CI paths and archive packaging,
then verify startup and tests from the documented directories after relocation.

Build a Canvas ZIP containing source and report artifacts, excluding generated
databases, credentials, session data and Git metadata. Inspect its contents and
report actual repository publication status separately from local readiness.
Include model identity and honest prompt provenance. State that instructor access
and final Canvas upload remain separate submission actions. Never invent a push,
remote CI run, collaborator invitation or successful physical integration.
```

## Existing artifacts for reference

These are **existing project outputs**, linked for reference. They are not presented as newly generated responses to the retrospective templates above.

| Reference | Existing artifact |
| --- | --- |
| Human baseline | [Lab 2 PDF](reference/lab2.pdf) |
| Requirements and backlog | [requirements.md](requirements.md) |
| Critical comparison | [comparison.md](comparison.md) |
| Implementation | [app.py](../Task_B/app.py), [browser UI](../Task_B/static/index.html) |
| Tests and observed results | [HTTP tests](../Task_B/tests/test_app.py), [validation](../Task_B/validation.md) |
| Setup and demonstration | [Task B README](../Task_B/README.md) |
| Submission report | [Shared report](../docs/report.md) |
| Historical interaction | [Conversation appendix](conversation-appendix.md), [interaction report](prompt-log.md), [model disclosure](ai-usage.md) |
