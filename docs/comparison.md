# Task A — Comparison with human-authored Assignment 2

## Evidence and method

The baseline is the user's three-page **Lab Assignment 2 — Task 2b: Requirements and Planning — SmartBrew AI** PDF, supplied during this conversation. Its original file is retained as [reference/lab2.pdf](reference/lab2.pdf); a `pdftotext -layout` extraction is [reference/lab2.txt](reference/lab2.txt). The separate original System Description was not supplied. The baseline contains ten user stories, six system requirements (REQ-01–REQ-06), and ten backlog items (SB-01–SB-10); it does not contain a distinct NFR section.

The LLM first proposed an ungrounded cafe-ordering interpretation from the repository name. **That interpretation was superseded when the PDF arrived.** It is not attributed to Assignment 2 and is not the implemented final scope. The reviewed final artifacts preserve the PDF's actors, identifiers and requirement/backlog table columns; the revised story wording is explicitly compared below. This is a real annotated comparison against the supplied PDF, not a reconstructed human submission.

**Methodological limitation:** this is a comparison of the human baseline with a **baseline-informed LLM refinement**, not an independently elicited blind model output. The model had already read Lab 2; retaining its features is therefore not evidence that it independently discovered them. A separate original System Description was unavailable. Preserved material is credited to the human source; only the concrete additions/changes below are credited to this LLM interaction.

The differences below distinguish requirements clarification from prototype simplification. Physical interfaces remain unimplemented even where a corresponding UI simulation is executable.

## System requirements: side-by-side review

| Baseline | LLM refinement / final implementation | Assessment |
| --- | --- | --- |
| REQ-01 displays digital menu/customization after touchscreen interaction. Inputs/outputs and pre/postconditions are specified, but slider units/ranges are not. | Preserves menu/sliders; specifies milk 0–100% of 200 ml and sugar 0–20 g, immediate preview and server validation. | **Improvement:** testable units/bounds. **Assumption:** the milk allowance and sugar maximum need stakeholder approval; they are not in the PDF. |
| REQ-02 uses an NFC card/phone tap; payment success/failure; approval begins brewing. | Approved/declined card/phone fixture, atomic inventory/order creation, decline has no stock side effects, busy-machine rejection. | **Improvement:** failure/consistency criteria. **Scope gap:** no NFC reader or payment gateway is integrated; physical payment requirement remains deferred. |
| REQ-03 uses weather API/time, requires internet and displays an AI suggestion. | Explicit weather/time fixtures, explained threshold rules, available-drink fallback and time-only offline behavior. | **Improvement:** defined decisions/failure mode. **Scope gap:** no background weather API or runtime AI model. Offline fallback changes the original internet precondition and is labeled as a prototype refinement. |
| REQ-04 reads physical ingredient sensors and alerts below 15%. | Preserves strict threshold with capacities and exact boundary checks; admin sets simulated stock and purchases deduct recipes transactionally. | **Preserved human rule:** the PDF already says strictly below 15%. **Added verification:** explicit 149/1000 and 150/1000 boundary examples; no new threshold is credited to the LLM. **Scope gap:** no physical sensors/polling. |
| REQ-05 admin credentials and new-item data update the menu. | Separate admin session, protected endpoints, price/milk validation, edit/hide workflow; customer visibility tested. | **Improvement:** role checks, negative tests and edit semantics. **Limitation:** public demo credentials and no production identity management. |
| REQ-06 technician PIN/component, locked service mode, results/logs saved to USB. | Distinct technician role; service/brewing interlock; pump/heater pass/fail fixtures; protected CSV browser download. | **Improvement:** enforce mode and roles. **Scope gap:** no actuation, direct USB save or certified safety controller; nominal two-second duration is fixture metadata. |
| US progress bar has no dedicated requirement row. | Added REQ-07: 12-second simulated progress, ready/collect state and reload recovery. | **Improvement:** makes a baseline story testable. **Assumption:** 12 seconds is a demonstration duration. |
| US daily sales report has no dedicated requirement/backlog item. | Added REQ-08: current UTC day, completed sales, counts, average and popular drinks. | **Improvement:** closes story-to-requirement gap. **Assumption:** completed/collected revenue policy and UTC day boundary. |
| USB export is bundled into REQ-06. | Added REQ-09 for independent authorization, CSV fields and manual USB-copy limitation. | **Improvement:** separates export acceptance from diagnostics; does not claim physical compliance. |

## User-story comparison

All human story sentences below are transcribed from PDF p. 1 with line-wrap whitespace normalized; the original **(Custom Feature)** marker is retained. The second column records the LLM-refined versions from the current review. Numeric acceptance criteria and simulation substitutions are separate proposals, not human baseline statements.

| ID | Human Lab 2 | LLM-refined story | Difference / critical assessment |
| --- | --- | --- | --- |
| US-01 | As a Customer, I want to look at the digital menu so that I can see the coffee choices and prices. | As a Customer, I want to view active drinks with their current prices and availability so that I can choose a drink the machine can prepare. | Adds availability and active-state criteria; these are proposed refinements, not wording from Lab 2. |
| US-02 | As a Customer, I want to use sliders to change the amount of sugar and milk so that the drink tastes the way I like. | As a Customer, I want to adjust milk and sugar with sliders and preview the quantities before payment so that I can confirm my preferred recipe. | Retains sliders; adds observable quantities/confirmation. Numeric limits remain prototype assumptions. |
| US-03 | As a Customer, I want to pay with a contactless card or phone so that paying is fast and easy. | As a Customer, I want to see approval or failure for my contactless card or phone payment before brewing so that an unsuccessful payment does not start a drink. | Adds a failure case and ordering constraint; does not prove faster payment or implement real NFC. |
| US-04 | As a Customer, I want the AI to suggest a drink based on the weather and time so that I can try something new. (Custom Feature) | As a Customer, I want a weather-and-time-based drink suggestion with an explanation so that I can decide whether to try something new. (Custom Feature) | Preserves the custom recommendation goal; explanation is new. Rule-based simulation is a scoped substitute for the original AI/API ambition, not proof of its implementation. |
| US-05 | As a Customer, I want to see a progress bar so that I know when my coffee is ready. | As a Customer, I want to see brewing progress and a distinct ready state so that I know when to collect my drink. | Makes ready/collection states explicit; the 12-second duration and reload recovery are new prototype decisions. |
| US-06 | As a System Admin, I want to edit the menu so that I can add new drinks and keep it updated. | As a System Admin, I want to add, edit or hide menu entries after signing in so that customers see the current drink selection. | Adds hide semantics and links existing authentication concerns to menu editing. |
| US-07 | As a System Admin, I want to get an alert when ingredients are low (below 15%) so that I can refill the machine in time. | As a System Admin, I want to see the ingredient and remaining percentage whenever its level is below 15% so that I can identify what needs refilling. | The strict threshold already exists in Lab 2. Adds displayed detail and concrete boundary checks; no physical sensor integration is claimed. |
| US-08 | As a System Admin, I want to see daily sales reports so that I know which drinks sell best. | As a System Admin, I want a daily report of order counts, collected-drink revenue and drink popularity so that I can identify the best-selling drinks. | Defines report fields; completed-order accounting and UTC day are proposed assumptions requiring business review. |
| US-09 | As a Maintenance Technician, I want to run hardware tests on pumps and heaters so that I can find broken parts easily. | As a Maintenance Technician, I want to select a pump or heater in service mode and inspect a recorded test result so that I can investigate a suspected component fault. | Connects existing service mode to diagnostics and recorded outcomes. Simulated pass/fail does not detect a physical fault. |
| US-10 | As a Maintenance Technician, I want to save error logs to a USB drive so that I can check them on my computer. | As a Maintenance Technician, I want to export timestamped error logs in a readable file for transfer to USB so that I can investigate failures on another computer. | Adds a portable format and timestamp fields. Browser download/manual USB copying does not satisfy the original direct-USB objective. |

The model did not establish improved usability merely by rewriting “fast and easy” or “find broken parts”. The additional acceptance criteria are testable software decisions, not results of a human usability study. Every original capability remains traceable; the physical gaps are called out rather than removed from the comparison.

## Backlog comparison

Source: SB-01–SB-05 on PDF p. 2; SB-06 spans pp. 2–3; SB-07–SB-10 on p. 3. Columns/IDs and importance/estimates are preserved, but descriptions and demo procedures below are prototype adaptations rather than verbatim baseline copies.

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

**Missing-source versus model limitations:** the absent standalone System Description prevents checking requirements beyond the supplied PDF. That is an evidence gap, not proof those requirements never existed. The model's initial cafe/rewards/reviews direction was an actual interpretation failure. Real weather fetching, hardware actuation, direct USB export and hidden triple-tap access were identified but deferred/substituted; they must not be described as silently overlooked or completed. The strict below-15% rule was already correctly specified by the human. The final review additionally corrected the missing Custom Feature marker and made all ten story changes visible.

The PDF has no separately enumerated NFRs. NFR-01–NFR-10 add reproducible Linux execution, atomic updates, role isolation, input bounds, restart persistence, sampled responsive usability, failure transparency, function documentation, isolated tests and auditability. These help make the independent-machine evaluation concrete. They are limited to demonstrated behavior: no performance SLA, accessibility certification, production security compliance or physical-machine safety claim is invented.

The model initially **missed the system's actual coffee-machine context** because it had only the repository name. It also could not obtain real hardware protocols, payment-provider requirements or the original full System Description from the PDF alone. The final artifacts correct the context and list those gaps rather than fill them with fabricated integrations. Human review remains necessary for real-machine safety, operating constraints, accessibility and whether the instructor accepts simulated hardware as the prototype scope.

## Rejected LLM suggestions and deferred source obligations

The first five rows are actual off-scope suggestions from the provisional LLM direction. Later rows separately identify source obligations or review constraints; they are not presented as additional requirements invented by the LLM.

| Suggestion / obligation | Origin | Decision and justification |
| --- | --- | --- |
| Cafe pickup scheduling and a multi-order barista queue | Provisional LLM scope | **Rejected.** The PDF describes a self-service coffee machine, not a cafe pickup service. One active drink and direct collection fit the supplied scope. |
| Customer loyalty balances and reward redemption | Provisional LLM scope | **Rejected.** No supporting requirement/story exists in the PDF; it would displace required machine functions and require invented financial policy. |
| Customer ratings/reviews | Provisional LLM scope | **Rejected.** Not in the baseline and unnecessary for demonstrating the selected ten features. |
| A shopping cart with multi-item checkout | Provisional LLM scope | **Rejected.** Baseline interaction selects and prepares a drink; a cart adds unrelated ordering semantics. |
| Unauthenticated role switching as an administration demo | Provisional LLM interface direction | **Rejected.** SB-06 and SB-08 explicitly require credentials/PIN; actual role-protected sessions are implemented. |
| Calling the weather/time recommender a live AI model | Unsupported implementation claim, rejected during review; not a separately proposed requirement | **Rejected.** No model integration exists. The UI and documentation identify deterministic rules. |
| Live NFC charges, sensor polling, actuator control and direct USB writing | Physical goals in the human baseline | **Deferred, not falsely completed.** Hardware/protocol/provider access was unavailable; simulations allow reproducible software evaluation but do not satisfy physical acceptance tests. |
| Hidden triple-tap technician entry | Human backlog SB-08 demonstration | **Replaced for prototype.** Explicit navigation makes independent evaluation discoverable; PIN and service authorization remain mandatory. The original gesture remains an unimplemented UI detail. |
| Real weather API/key setup | Human REQ-03 / SB-03 API goal; provider/key details unspecified | **Deferred.** Deterministic scenarios support the required hot/offline demonstrations without undeclared network dependencies; no claim of actual API integration. |
| Invented latency/security guarantees or a complete portability claim | Review constraint; no earlier measured SLA or certification was supplied | **Rejected.** Measurements and certification were not available; only the verified Linux runtime and concrete controls are reported. |

## Student review before submission

Review the actual PDF/source comparison and the added assumptions. Supply the separate System Description if it imposes constraints not in the PDF. Confirm whether the instructor accepts the explicit hardware/payment/weather substitutions; physical acceptance cannot be inferred from passing software tests. Do not describe the AI's critical review as an independently conducted human usability study or stakeholder interview.
