# Task A — LLM-assisted requirements elicitation

System: **SmartBrew AI**, a coffee-machine touchscreen application. This revision uses the supplied [Assignment 2 PDF](reference/lab2.pdf), not an independently supplied full System Description. The PDF is the human-authored baseline; refinements below were generated with OpenAI GPT-6 through Codex and critically reviewed against that baseline. Exact model build identifiers are not exposed.

## Scope, actors and explicit decisions

Actors are Customer, System Administrator and Maintenance Technician. The customer selects a drink, adjusts milk/sugar, pays and follows preparation. The administrator manages menu entries, monitors ingredients and reviews sales. The technician enters service mode, tests components and exports logs.

The executable deliverable is a **software simulation** of one machine serving one drink at a time. NFC approval, weather, ingredient sensors and hardware tests are local fixtures. CSV export is a browser download; a person may copy it to USB. The suggestion engine is deterministic weather/time logic, not a deployed LLM. These choices allow repeatable Linux evaluation without hardware, accounts or internet. They narrow the prototype relative to the physical-system requirements and are not claims of completed physical integration.

Prototype decisions: milk ranges from 0–100% of a 200 ml allowance; sugar ranges from 0–20 g; customization has no surcharge. Brewing takes 12 simulated seconds. A ready drink must be collected before another order or service mode. Daily reporting uses UTC and completed/collected orders. These values were not specified by Assignment 2.

## Functional requirements

The table preserves Assignment 2's columns. Existing IDs remain traceable; REQ-07–REQ-09 make its additional user stories and export behavior explicit.

| ID | Description | Inputs | Outputs | Precondition | Postcondition |
| --- | --- | --- | --- | --- | --- |
| REQ-01 | Display active drinks/prices and customize the selected recipe | Drink selection; milk integer 0–100%; sugar integer 0–20 g | Menu, recipe preview, validation errors | Application reachable; active menu exists | Selected recipe is displayed; invalid bounds rejected server-side |
| REQ-02 | Process contactless-payment outcome and start brewing atomically | Selected drink/recipe; card or phone; approved/declined fixture | Approval/order ID or decline/error; progress | Machine normal and idle; sufficient recipe stock for approval | Approval creates one order and deducts full recipe once; decline creates no paid order or stock mutation |
| REQ-03 | Suggest an available drink using weather and time | Hot/cold/mild/offline scenario; UTC hour 0–23 | Drink and plain-language reason, source provenance | At least one drink available | Hot 30°C prefers iced; cold 4°C prefers latte; mild/offline use time rules; unavailable preference falls back to available drink |
| REQ-04 | Monitor ingredient percentages and alert strictly below 15% | Simulated ingredient level; positive capacity | Per-ingredient percentage and low-stock alert | Administrator session for stock changes; fixture data available | 149/1000 is low; 150/1000 is not; invalid/negative stock rejected |
| REQ-05 | Authenticate administrators and add/edit/hide menu entries | Password; name, description, price, category, default milk, active state | Authenticated session; saved menu or error | Correct administrator credential for protected operations | Active edits appear in customer menu; hidden drinks disappear; unauthorized writes rejected |
| REQ-06 | Authenticate technicians and run safe service-mode diagnostics | Technician PIN; service mode; component; pass/fault fixture | Component result, nominal test duration and audit event | Technician session; no brewing/uncollected drink; service mode for diagnostics | Customer purchase blocked in service mode; test logged; no physical equipment activated |
| REQ-07 | Show brew progress and collect completed drink | Opaque order ID; polling; collect action | Brewing progress, ready/completed state | Approved order exists | At approximately 12 seconds the order becomes ready; collection marks completed once |
| REQ-08 | Report daily sales and drink popularity | Administrator session; current UTC day | Order counts, completed revenue/average and popular drinks | Application has zero or more orders | Empty day displays zeros; only completed orders contribute completed revenue; repeated reads do not double-count |
| REQ-09 | Export service/error logs as CSV | Technician session; export request | Downloadable UTF-8 CSV with event/severity/time | Logged events may exist; technician authenticated | Header and current event rows are exported; physical USB copy remains manual |

Weather/time rule order is explicit: online temperature ≥25°C → Iced Latte; online temperature ≤10°C → Caffè Latte; otherwise hour <12 → Espresso; otherwise Cappuccino. If the preferred seeded drink is hidden or unavailable, choose the first available menu entry. Offline mode clearly announces a time-only fallback. The names and boundaries are prototype choices.

## Non-functional requirements

These measurable NFRs refine omissions in the PDF. “Acceptance” means the target/check, not a blanket production guarantee. Actual observed results are in [validation.md](validation.md).

| ID | Requirement and acceptance criterion | Rationale/status |
| --- | --- | --- |
| NFR-01 Reproducibility | On Linux with Python ≥3.11 and SQLite, `python3 app.py` starts with no third-party package install or external service | Verified on Python 3.12.14; other OS versions not independently tested |
| NFR-02 Data integrity | An insufficient-stock purchase leaves every stock value and order count unchanged; a decline consumes nothing | HTTP integration assertions cover atomic rollback and decline |
| NFR-03 Authorization | Every admin mutation/report requires admin role; diagnostics/log export require technician role; wrong role and unauthenticated calls fail | Tests cover rejected and valid requests; public demo credentials limit security |
| NFR-04 Input safety | Server rejects malformed JSON, non-finite/out-of-range numbers and unsupported menu fields; SQL uses bound values | Bounded request body: 64 KiB; tests cover representative invalid inputs |
| NFR-05 Persistence | Menu edits, inventory, orders and logs survive process restart with same SQLite path | Restart integration test; browser sessions deliberately do not survive |
| NFR-06 Usability | At 390 × 844 and desktop widths, principal controls remain usable without page-level horizontal scrolling; status and errors use text | Browser QA passed at sampled viewports; no formal WCAG certification claimed |
| NFR-07 Failure transparency | UI/API identify weather, payment and hardware as simulations; offline weather yields explained fallback rather than silent success | Weather, recommendation and error paths tested |
| NFR-08 Maintainability | Every named Python/JavaScript function has purpose and input/output documentation; tests cover the ten feature IDs | Python AST/docstring check and source review; no code-coverage percentage claim |
| NFR-09 Isolation and safe evaluation | Automated tests use temporary databases and ephemeral ports, do not reset the user's database, and need no physical machine | Reusable HTTP suite has 19 passing tests |
| NFR-10 Auditability | Payment declines, low inventory and diagnostics generate inspectable events; CSV includes a failed diagnostic when one is generated | CSV and event assertions passed; logs do not store credentials |

The baseline did not set performance targets. This report avoids inventing a response-time guarantee from a single development machine. The 12-second interval is the simulated brew duration, not network latency.

## User stories and acceptance criteria

The story wording preserves the ten Assignment 2 actor/goal/benefit statements; acceptance criteria are LLM refinements.

| ID | User story | Acceptance criteria | Requirements / backlog |
| --- | --- | --- | --- |
| US-01 | As a Customer, I want to look at the digital menu so that I can see the coffee choices and prices. | Active drinks and prices shown; hidden drinks absent; seeded five drinks load. | REQ-01 / SB-01 |
| US-02 | As a Customer, I want to use sliders to change the amount of sugar and milk so that the drink tastes the way I like. | Milk 20% changes recipe to 40 ml; sugar display tracks slider; invalid API values rejected. | REQ-01 / SB-01 |
| US-03 | As a Customer, I want to pay with a contactless card or phone so that paying is fast and easy. | Both method choices work in simulation; decline reports failure without stock/order side effects; approval starts brewing. | REQ-02 / SB-02 |
| US-04 | As a Customer, I want the AI to suggest a drink based on the weather and time so that I can try something new. | Hot scenario recommends an available iced drink; offline mode explains time fallback; UI exposes rule-based engine. | REQ-03 / SB-03, SB-04 |
| US-05 | As a Customer, I want to see a progress bar so that I know when my coffee is ready. | Approved order progresses to ready after 12 seconds; reload resumes stored ID; collection closes the order. | REQ-07 / supporting workflow |
| US-06 | As a System Admin, I want to edit the menu so that I can add new drinks and keep it updated. | Valid admin adds/edits/hides a drink; customer menu reflects it; wrong role cannot edit. | REQ-05 / SB-06, SB-07 |
| US-07 | As a System Admin, I want to get an alert when ingredients are low (below 15%) so that I can refill the machine in time. | Beans 100/1000 triggers alert; 150/1000 does not; adequate refill removes it. | REQ-04 / SB-05 |
| US-08 | As a System Admin, I want to see daily sales reports so that I know which drinks sell best. | Authorized daily report includes completed counts, integer-cent revenue and popular drinks; no double-count on refresh. | REQ-08 / supporting workflow |
| US-09 | As a Maintenance Technician, I want to run hardware tests on pumps and heaters so that I can find broken parts easily. | Service mode required; test gives a labeled simulated pass/fail result and logged component; brewing is interlocked. | REQ-06 / SB-08, SB-09 |
| US-10 | As a Maintenance Technician, I want to save error logs to a USB drive so that I can check them on my computer. | Technician downloads CSV containing a generated fault; manual copy to USB documented; no direct USB-write claim. | REQ-09 / SB-10 |

## Product backlog

This preserves the baseline's **ID, Name, Imp., Est., Description, How to demo, Notes** format and its 1–100 importance scale and Fibonacci story-point estimates. The ten IDs, importance values and estimates are retained for comparable scope. Estimates were not retrospectively replaced with measured effort.

| ID | Name | Imp. | Est. | Description | How to demo | Notes |
| --- | --- | ---: | ---: | --- | --- | --- |
| SB-01 | UI Menu & Customization | 100 | 5 | Menu, prices and milk/sugar recipe sliders | Select Latte, set milk 20%, verify 40 ml preview | Core feature; software implementation |
| SB-02 | NFC Payment Integration | 95 | 5 | Card/phone success and decline with atomic order/stock handling | Decline, verify no consumption; approve and watch brew | Physical NFC adapter deferred; explicit simulation |
| SB-03 | Weather Data Fetcher | 80 | 3 | Local weather/time provider with offline behavior | Switch offline → hot and inspect weather provenance | Real background/API fetching deferred |
| SB-04 | AI Suggestion Widget | 75 | 5 | Weather/time suggestion with visible explanation | Set 30°C, press Surprise me, receive available iced drink | Deterministic rules, no live AI model |
| SB-05 | Inventory Alerts | 90 | 3 | Capacity-based strict below-15% checks | Set beans to 100/1000; inspect admin alert | Simulated sensor values; no hardware polling |
| SB-06 | Admin Authentication | 85 | 3 | Password-based admin session and protected operations | Incorrect then correct password; verify role separation | Demo defaults; production hardening deferred |
| SB-07 | Menu Editor Dashboard | 85 | 5 | Add/edit/hide menu entries | Add drink at $4, edit price and inspect menu | New drinks use documented standard base recipe |
| SB-08 | Service Mode Login | 70 | 2 | Separate technician PIN and service interlock | Enter PIN, enable service mode; purchase is blocked | Explicit navigation replaces hidden triple-tap gesture |
| SB-09 | Hardware Diagnostic UI | 70 | 5 | Pump/heater component fixtures and fault logging | Test milk pump, then simulate a fault | Nominal 2-second result returned immediately; no actuation |
| SB-10 | USB Error Log Exporter | 60 | 3 | Protected CSV download of service/error events | Generate fault, download CSV and inspect row | User copies downloaded file to USB manually |

Dependency order: SB-01 before SB-02; SB-03 before SB-04; SB-06 before SB-05/SB-07; SB-08 before SB-09/SB-10. High importance does not override these prerequisites. US-05 progress and US-08 reporting are included as supporting requirements, not substituted for any of the ten selected items.

## Open questions and deferred physical-system work

The original full System Description, real machine interfaces, payment provider, weather API/location, hardware safety rules, deployment security policy and precise UI accessibility standard were not supplied. A production version needs stakeholder validation and real adapters/certification. The concrete original-format comparison and explicit acceptance/rejection decisions are in [comparison.md](comparison.md).
