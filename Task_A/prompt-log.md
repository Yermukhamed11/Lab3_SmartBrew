# SmartBrew AI — Interaction report

**Lab Assignment 3 · Tasks A–C · OpenAI GPT-6 through Codex**

This report presents the development conversation as a sequence of decisions: establish the source, refine requirements, implement a bounded prototype, review evidence, and prepare the submission. It summarizes the actual interaction; it does not replace the original requests with more elaborate prompts that were never sent.

| Read this for… | Document |
| --- | --- |
| The development story and key decisions | This interaction report |
| The original assignment prompt, translated conversation excerpts and actual process prompts | [Conversation appendix](conversation-appendix.md) |
| Well-structured prompts for repeating or extending the work | [Retrospective prompt library](prompt-library.md) |
| Model identity, translation policy and method limits | [AI usage disclosure](ai-usage.md) |

**Reading note.** Student quotations below are English translations of actual short requests. Assistant findings are labeled summaries of the work performed. The prompt library was composed after implementation; it is a reusable guide, not a record of prompts previously written by the student. The original assignment text is retained in the appendix instead of repeated at the beginning of this report.

## 1. Establish the source and correct the scope

**Objective:** determine what SmartBrew actually represents before treating proposed features as requirements.

**Student input:** the lab assignment, authorization to proceed and the Assignment 2 PDF. One source-related message was: “I sent it as a PDF.”

**Assistant finding — summary:** the repository name alone led to a provisional cafe interpretation. The supplied PDF instead described a self-service coffee machine. The implementation was corrected to preserve SB-01–SB-10, and unrelated cart, pickup, loyalty and review features were dropped. The separate original System Description was unavailable.

**Decision:** use the supplied PDF as the comparison baseline and identify additional assumptions explicitly. Treat weather, NFC, sensors, component tests and USB transfer as limited prototype interfaces rather than completed physical integrations.

**Evidence:** [original Lab 2 PDF](reference/lab2.pdf), [source comparison](comparison.md), [assumption register](requirements.md#assumption-and-decision-register).

## 2. Turn the source into reviewable requirements

**Objective:** produce requirements, user stories and a backlog that can be compared with the human baseline.

**Student review request:** “Check Task A too.”

**Assistant finding — summary:** simply repeating the original stories did not make the LLM's contribution clear. The review produced ten distinct refined stories and compared each with its full human original. It also found that the inventory threshold had incorrectly been presented as an LLM clarification: the human source already specified strictly below 15%.

**Decisions:**

- Credit the original threshold, feature IDs, importance scores and estimates to the human source.
- Distinguish six original target-system concerns from nine prototype acceptance requirements.
- Record ten NFRs and eight explicit assumptions without inventing stakeholder approval.
- Identify accepted refinements, rejected off-scope suggestions and deferred source obligations separately.

**Evidence:** [requirements and backlog](requirements.md), [story-by-story comparison](comparison.md#user-story-comparison), [Task A review](task-a-review.md).

**Method limit:** this was refinement informed by Lab 2. It was not blind elicitation from an independently supplied System Description.

## 3. Implement and verify the ten-feature prototype

**Objective:** make the selected features observable in a runnable user experience.

**Context:** implementation followed the user's authorization to complete Lab 3. The assistant coordinated backend, frontend, tests and documentation through shared feature/API contracts. Those process prompts are attributed to the assistant in the [appendix](conversation-appendix.md); they are not presented as student-authored prompts.

**Assistant result — summary:** a Python-standard-library/SQLite application with customer, administrator and technician workflows. Purchases check stock atomically; failed payments do not consume ingredients; service mode blocks customer purchases; diagnostics and recommendations disclose their simulated/rule-based nature.

**Evidence:** [application source](../Task_B/app.py), [browser client](../Task_B/static/app.js), [HTTP integration tests](../Task_B/tests/test_app.py).

**Observed verification:** the initial suite executed 19 tests successfully. After the folder reorganization, the same 19 tests passed again in 22.564 seconds. Browser checks exercised payment failure/success, brewing, reload recovery, administration, service faults and CSV download. These results validate software behavior, not physical hardware or real charges.

**Evidence:** [validation record](../Task_B/validation.md), [ten-feature execution guide](../Task_B/README.md#demonstrate-all-ten-functionalities).

## 4. Review documentation against the rubric

**Objective:** make the project understandable and executable on another machine.

**Student review request:** “Check the requirements again, and fix anything that is incorrect.”

**Assistant finding — summary:** function comments existed but some input/output contracts were underspecified. The review expanded backend docstrings, clarified trusted HTML versus plain text, added fresh-clone working-directory instructions and matched demo steps to the actual UI. Python 3.12.14 was pinned as the tested version. A recipe-preview mismatch was corrected so 20% milk explicitly displays 40 ml of a 200 ml allowance.

**Decision:** document the actual implementation and verified environment, retaining the simulation limits and explicit setup commands.

**Evidence:** [Task B README](../Task_B/README.md), [documented backend](../Task_B/app.py), [CI configuration](../.github/workflows/ci.yml).

## 5. Organize and prepare the submission

**Objective:** make the deliverables easy to navigate and consistent with the requested submission language.

**Student requests:** “Task A and Task B need to be separated into folders” and “Make all requests, prompts and responses English for submission.”

**Assistant result — summary:** analysis and prompting artifacts were moved to `Task_A/`; the prototype and its execution evidence were moved to `Task_B/`. Links, CI and archive generation were updated. Historical Russian messages were translated into English with their translation status retained. The presentation was then reorganized into this report, an evidence appendix and a retrospective prompt library.

**Evidence:** [Task A index](README.md), [Task B index](../Task_B/README.md), [combined report](../docs/report.md), [archive generator](../scripts/package_submission.py).

## Reflection

The useful prompting pattern demonstrated by the work is to provide source material, constrain the output format, demand explicit assumptions, request a comparison, execute the result and review failures against evidence. The initial cafe assumption shows why source grounding matters. The later reviews show why passing code alone does not make requirement attribution or documentation accurate.

The [prompt library](prompt-library.md) expresses these lessons as reusable English prompts. It is a retrospective aid for future work; the actual conversation evidence remains in the [appendix](conversation-appendix.md).
