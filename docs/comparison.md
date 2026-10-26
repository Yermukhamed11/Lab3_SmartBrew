# Task A — Comparison with human-authored Assignment 2

## Evidence and method

The baseline is the user's three-page **Lab Assignment 2 — Task 2b: Requirements and Planning — SmartBrew AI** PDF, supplied during this conversation. Its original file is retained as [reference/lab2.pdf](reference/lab2.pdf); a `pdftotext -layout` extraction is [reference/lab2.txt](reference/lab2.txt). The separate original System Description was not supplied. The baseline contains ten user stories, six system requirements (REQ-01–REQ-06), and ten backlog items (SB-01–SB-10); it does not contain a distinct NFR section.

The LLM first proposed an ungrounded cafe-ordering interpretation from the repository name. **That interpretation was superseded when the PDF arrived.** It is not attributed to Assignment 2 and is not the implemented final scope. The reviewed final artifacts preserve the PDF's actors, identifiers, story wording and table formats. This is a real annotated comparison against the supplied PDF, not a reconstructed human submission.

The differences below distinguish requirements clarification from prototype simplification. Physical interfaces remain unimplemented even where a corresponding UI simulation is executable.

## System requirements: side-by-side review

| Baseline | LLM refinement / final implementation | Assessment |
| --- | --- | --- |
| REQ-01 displays digital menu/customization after touchscreen interaction. Inputs/outputs and pre/postconditions are specified, but slider units/ranges are not. | Preserves menu/sliders; specifies milk 0–100% of 200 ml and sugar 0–20 g, immediate preview and server validation. | **Improvement:** testable units/bounds. **Assumption:** the milk allowance and sugar maximum need stakeholder approval; they are not in the PDF. |
| REQ-02 uses an NFC card/phone tap; payment success/failure; approval begins brewing. | Approved/declined card/phone fixture, atomic inventory/order creation, decline has no stock side effects, busy-machine rejection. | **Improvement:** failure/consistency criteria. **Scope gap:** no NFC reader or payment gateway is integrated; physical payment requirement remains deferred. |
| REQ-03 uses weather API/time, requires internet and displays an AI suggestion. | Explicit weather/time fixtures, explained threshold rules, available-drink fallback and time-only offline behavior. | **Improvement:** defined decisions/failure mode. **Scope gap:** no background weather API or runtime AI model. Offline fallback changes the original internet precondition and is labeled as a prototype refinement. |
| REQ-04 reads physical ingredient sensors and alerts below 15%. | Preserves strict threshold with capacities and exact boundary checks; admin sets simulated stock and purchases deduct recipes transactionally. | **Improvement:** 15% is no longer ambiguous at equality. **Scope gap:** no physical sensors/polling. |
| REQ-05 admin credentials and new-item data update the menu. | Separate admin session, protected endpoints, price/milk validation, edit/hide workflow; customer visibility tested. | **Improvement:** role checks, negative tests and edit semantics. **Limitation:** public demo credentials and no production identity management. |
| REQ-06 technician PIN/component, locked service mode, results/logs saved to USB. | Distinct technician role; service/brewing interlock; pump/heater pass/fail fixtures; protected CSV browser download. | **Improvement:** enforce mode and roles. **Scope gap:** no actuation, direct USB save or certified safety controller; nominal two-second duration is fixture metadata. |
| US progress bar has no dedicated requirement row. | Added REQ-07: 12-second simulated progress, ready/collect state and reload recovery. | **Improvement:** makes a baseline story testable. **Assumption:** 12 seconds is a demonstration duration. |
| US daily sales report has no dedicated requirement/backlog item. | Added REQ-08: current UTC day, completed sales, counts, average and popular drinks. | **Improvement:** closes story-to-requirement gap. **Assumption:** completed/collected revenue policy and UTC day boundary. |
| USB export is bundled into REQ-06. | Added REQ-09 for independent authorization, CSV fields and manual USB-copy limitation. | **Improvement:** separates export acceptance from diagnostics; does not claim physical compliance. |

## User-story comparison

All ten original actor/goal/benefit statements are retained in [requirements.md](requirements.md) as US-01–US-10; the IDs are added for traceability. The final table adds acceptance criteria and requirement/backlog links. No original story is silently dropped.

The main improvement is translating “fast and easy”, “find broken parts” and “know which drinks sell best” into observable software behavior without claiming those phrases establish measured usability, physical fault detection or business value. The original stories do not define milk units, decline side effects, authorization failures, report accounting, offline recommendation behavior or service/brewing exclusion. These are explicit new decisions rather than facts inferred from the human author.

## Backlog comparison

| Item(s) | Preserved | Change / consequence |
| --- | --- | --- |
| SB-01 | Menu/sliders, importance 100, estimate 5 | Recipe-preview bounds and units are explicit. |
| SB-02 | Contactless success/failure journey, 95 / 5 | Hardware “tap registered test card” is replaced by a labeled approval/decline simulator. |
| SB-03 | Weather/time context and offline demonstration, 80 / 3 | Scenario selector replaces background external fetching; offline event and fallback are observable. |
| SB-04 | 30°C → iced demonstration, 75 / 5 | Explainable rules replace an unspecified AI implementation; available-stock fallback added. |
| SB-05 | Strict below-15% and 10%-beans demo, 90 / 3 | Simulated stock override replaces physical sensor API. |
| SB-06 | Wrong/correct admin login, 85 / 3 | Session/role checks added; “secure” narrowed to actual demo controls. |
| SB-07 | Add/edit drink, 85 / 5 | Hide action and bounded integer-cent prices added; arbitrary physical recipes are not inferred from names. |
| SB-08 | Technician PIN and maintenance access, 70 / 2 | Explicit service navigation replaces hidden screen-corner triple tap. |
| SB-09 | Milk pump test UI, 70 / 5 | Fixture pass/fault output replaces physical two-second activation. |
| SB-10 | CSV log export, 60 / 3 | Browser download replaces direct USB filesystem write. |

Importance and story points are **unchanged baseline estimates**, not post hoc effort measurements. The final dependency order clarifies that authentication precedes protected operations, even when a dependent item has higher business importance.

## New NFRs and critical assessment

The PDF has no separately enumerated NFRs. NFR-01–NFR-10 add reproducible Linux execution, atomic updates, role isolation, input bounds, restart persistence, sampled responsive usability, failure transparency, function documentation, isolated tests and auditability. These help make the independent-machine evaluation concrete. They are limited to demonstrated behavior: no performance SLA, accessibility certification, production security compliance or physical-machine safety claim is invented.

The model initially **missed the system's actual coffee-machine context** because it had only the repository name. It also could not obtain real hardware protocols, payment-provider requirements or the original full System Description from the PDF alone. The final artifacts correct the context and list those gaps rather than fill them with fabricated integrations. Human review remains necessary for real-machine safety, operating constraints, accessibility and whether the instructor accepts simulated hardware as the prototype scope.

## Rejected or deferred LLM suggestions

These are documented design decisions from this interaction, not claims that the human Lab 2 contained the suggestions.

| Suggestion | Decision and justification |
| --- | --- |
| Cafe pickup scheduling and a multi-order barista queue | **Rejected.** The PDF describes a self-service coffee machine, not a cafe pickup service. One active drink and direct collection fit the supplied scope. |
| Customer loyalty balances and reward redemption | **Rejected.** No supporting requirement/story exists in the PDF; it would displace required machine functions and require invented financial policy. |
| Customer ratings/reviews | **Rejected.** Not in the baseline and unnecessary for demonstrating the selected ten features. |
| A shopping cart with multi-item checkout | **Rejected.** Baseline interaction selects and prepares a drink; a cart adds unrelated ordering semantics. |
| Unauthenticated role switching as an administration demo | **Rejected.** SB-06 and SB-08 explicitly require credentials/PIN; actual role-protected sessions are implemented. |
| Calling the weather/time recommender a live AI model | **Rejected.** No model integration exists. The UI and documentation identify deterministic rules. |
| Live NFC charges, sensor polling, actuator control and direct USB writing | **Deferred, not falsely completed.** Hardware/protocol/provider access was unavailable; simulations allow reproducible software evaluation but do not satisfy physical acceptance tests. |
| Hidden triple-tap technician entry | **Replaced for prototype.** Explicit navigation makes independent evaluation discoverable; PIN and service authorization remain mandatory. The original gesture remains an unimplemented UI detail. |
| Real weather API/key setup | **Deferred.** Deterministic scenarios support the required hot/offline demonstrations without undeclared network dependencies; no claim of actual API integration. |
| Invented latency/security guarantees or a complete portability claim | **Rejected.** Measurements and certification were not available; only the verified Linux runtime and concrete controls are reported. |

## Student review before submission

Review the actual PDF/source comparison and the added assumptions. Supply the separate System Description if it imposes constraints not in the PDF. Confirm whether the instructor accepts the explicit hardware/payment/weather substitutions; physical acceptance cannot be inferred from passing software tests. Do not describe the AI's critical review as an independently conducted human usability study or stakeholder interview.
