# Lab Assignment 3 — SmartBrew AI

Prepared 26 October 2026. Repository: <https://github.com/Yermukhamed11/Lab3_SmartBrew>. AI assistance: OpenAI GPT-6 through Codex for Tasks A, B and C; exact model build not exposed. See [AI usage](../Task_A/ai-usage.md).

## Task A — Requirements and critical comparison

The human baseline is the supplied three-page Assignment 2 PDF: [original](../Task_A/reference/lab2.pdf), [layout-preserving extraction](../Task_A/reference/lab2.txt). [requirements.md](../Task_A/requirements.md) contains functional and non-functional requirements, all ten user stories with acceptance criteria, and a prioritized product backlog in the baseline's format. [comparison.md](../Task_A/comparison.md) provides row-by-row differences, improvements, missing/unsupported assumptions and individual rejection/deferment reasons. [prompt-log.md](../Task_A/prompt-log.md) records the conversational evidence and code-output references.

The model initially inferred a cafe from the repository name; that provisional scope was rejected after reading the PDF. The final system is a coffee-machine interface. The separate full System Description was not supplied, so the PDF is the available source of truth. Additional numeric bounds, accounting policies and simulation choices are identified explicitly. This is baseline-informed LLM refinement, not blind independent elicitation. The comparison now pairs all ten original human stories with their LLM-refined wording; the requirements separate original target commitments from prototype acceptance and register unresolved assumptions.

The later [Task A checklist/review](../Task_A/task-a-review.md) records the rubric checks and corrections, including full story-to-story comparisons, the already-human-defined 15% threshold, and unresolved source/physical-scope limits.

## Task B — Ten implemented software functionalities

| Selected feature | Implementation / main behavior | Verification |
| --- | --- | --- |
| SB-01 UI Menu & Customization | Customer catalog, active availability, milk/sugar sliders and live recipe preview | HTTP validation, browser slider check |
| SB-02 NFC Payment Integration | Explicit card/phone approval/decline simulation; atomic purchase and stock deduction | Success/decline, rollback and 12-second lifecycle tests; browser approval/decline |
| SB-03 Weather Data Fetcher | Local named weather/time provider, offline condition and provenance | Scenario/hour and offline HTTP checks |
| SB-04 AI Suggestion Widget | Explainable deterministic weather/time rules with available-drink fallback | Hot/cold/time/offline tests; browser 30°C iced suggestion |
| SB-05 Inventory Alerts | Capacity percentages, strict below-15% alert and simulated stock override | Exact 15% boundary tests; browser 100/1000 beans alert |
| SB-06 Admin Authentication | Password session, rejected credentials and role-protected endpoints | Wrong credentials/role/logout tests; browser login |
| SB-07 Menu Editor Dashboard | Administrator adds/edits/hides drinks and customer menu updates | HTTP CRUD visibility tests; browser drink creation |
| SB-08 Service Mode Login | Separate technician PIN session and persisted service mode; brewing/service exclusion | Role and busy/service interlock tests; browser technician workflow |
| SB-09 Hardware Diagnostic UI | Pump/heater pass/fault fixtures with event logging | Diagnostic HTTP tests; browser failed milk-pump fixture |
| SB-10 USB Error Log Exporter | Technician CSV download; documented manual USB copy | CSV authorization/content tests; browser download with FAIL/milk_pump |

Supporting original user stories include brew progress/collection and administrator daily sales/popular drinks. These support the chosen ten items rather than replace them. There is no customer loyalty program, review system, cafe pickup scheduler or multi-item cart in the final scope.

### Architecture and important behavior

- `Task_B/app.py`: Python 3.11+ standard-library HTTP server, validation, session authorization, SQLite transactions and simulation providers.
- `Task_B/static/`: accessible HTML controls, responsive CSS and vanilla JavaScript with same-origin API calls. The browser remembers an opaque current-order ID for progress restoration.
- `Task_B/tests/test_app.py`: actual HTTP integration tests using temporary databases, ephemeral ports and independent cookie-aware clients.
- SQLite retains menu, inventory, orders, logs and service mode. Session tokens are in memory and expire; they are not persisted across server restart.

The software serves one drink at a time, rejects insufficient stock without partial changes and blocks purchases while in service mode. Money is represented as integer cents. Sales use completed/collected orders on the current UTC day. These policies are documented prototype decisions, not unquoted historical requirements.

### Execution evidence

On Linux with Python 3.12.14, `python3 -m unittest discover -s tests -v` from `Task_B/` executed **19 tests; all passed in 22.585 seconds, exit status 0**. No cases were skipped or disabled. A real Chromium functional check exercised the principal customer/admin/technician journeys and CSV output; desktop and 390 × 844 mobile checks passed without page-level horizontal overflow or uncaught JavaScript errors. JavaScript syntax and Python function-documentation checks also passed. Full evidence and limits are recorded in [validation.md](../Task_B/validation.md), with [desktop](../Task_B/screenshots/desktop.png) and [mobile](../Task_B/screenshots/mobile.png) screenshots.

These results demonstrate the runnable software simulation. No physical NFC terminal, real payment, sensor, pump, heater, weather API or physical USB write was validated. Nominal two-second diagnostics return fixtures immediately. Recommendations use rules rather than an embedded AI model. Physical acceptance criteria remain outside this prototype's completed scope.

## Task C — Documentation and repository

[README.md](../Task_B/README.md) provides overview, supported Python/Linux environment, dependency-free setup, execution instructions, a ten-feature demonstration guide, test commands, public demo credentials, configuration and constraints. Source functions/methods carry purpose/input/output documentation. CI records the reusable test command; a remote CI run is not claimed solely from local success.

The source repository includes an archive generator at `scripts/package_submission.py`. The Canvas ZIP contains the report, Task A artifacts, original comparison source, application, tests and execution instructions while excluding generated databases and Git metadata. Remote publication and instructor access are distinct actions; use the final delivery message for the actual push status. If the repository is private, instructor **riccardoRubei** must be invited. Canvas upload remains the student's action.

## Source provenance and unresolved scope

The original PDF bytes are preserved with SHA-256 (paths below are relative to the repository root):

```text
7888c6078825fb98e68beaa570d3146a31be18a6f5d43f83c53df4d41fb7ce17  Task_A/reference/lab2.pdf
f2091fe9ae7caefac09102c0556e761501689dc4dbe27045a62c4bd5105f1432  Task_A/reference/lab2.txt
```

Before submission, the student should review assumptions and verify that the instructor accepts simulated interfaces for the executable prototype. The original physical-machine objectives have not been silently redefined as satisfied. This report is an AI-assisted development artifact, not evidence of an independently conducted stakeholder interview or physical-device certification.
