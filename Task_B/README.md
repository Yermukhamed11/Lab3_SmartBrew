# Task B — SmartBrew AI implementation

A working browser-based coffee-machine prototype for **Lab Assignment 3: Software Engineering with LLMs**. Customers select and customize a drink, try weather/time suggestions, simulate contactless payment, and follow brewing progress. Administrators manage the menu, stock and daily sales; technicians use a separate service interface for simulated diagnostics and CSV log export.

The ten selected functionalities preserve the **SB-01–SB-10** identifiers from the supplied Assignment 2 PDF. Physical NFC terminals, weather providers, ingredient sensors, pumps, heaters and USB devices are represented by explicit local simulations. The recommendation engine uses transparent deterministic rules; “AI” is the system name, not a claim that an LLM runs inside the application.

## Requirements and setup

- Python **3.11 or newer**, with the standard-library `sqlite3` module. Developed and tested in Linux with Python **3.12.14**; `.python-version` pins the recommended reproducible version to **3.12.14**.
- A modern browser with JavaScript enabled.
- Git, if cloning the repository; a downloaded and extracted source ZIP is also supported.
- No third-party Python packages, database server, API key, payment account, internet connection or hardware is needed after obtaining the repository. `requirements.txt` records that there are no external Python dependencies.
- The supported evaluation environment is Linux. Other operating systems have not been independently validated.

Obtain the source and enter its directory:

```bash
git clone https://github.com/Yermukhamed11/Lab3_SmartBrew.git
cd Lab3_SmartBrew/Task_B
```

If using the submission ZIP, extract it and enter its `Lab3_SmartBrew/Task_B` directory instead. Install Python 3.11+ through your operating system if the version check below fails. There is no compilation or dependency-installation step: Python serves the static browser assets and initializes SQLite directly.

From the `Task_B` directory:

```bash
python3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
python3 app.py --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000` in your own browser. Stop the server with **Ctrl+C**. This is a local execution address, not a hosted cloud preview or deployed website.

The server creates and seeds `data/smartbrew.db` on first launch. Subsequent launches preserve menu edits, inventory, orders, logs and service mode. Browser sessions expire after one hour and do not survive a server restart. The customer browser remembers the most recent order ID so that progress can be resumed.

For a separate clean demonstration database without deleting existing work:

```bash
python3 app.py --port 8001 --db /tmp/smartbrew-demo.db
```

Choose a new filename if that path already contains data you wish to retain. Never delete the existing database merely to restart the application.

## Demonstrate all ten functionalities

The interface has **Brew coffee**, **Administration**, **Machine service** and **Sales insights** navigation entries. Follow the sequence below; finish collecting an active drink before entering service mode.

| Feature | Steps | Expected result |
| --- | --- | --- |
| **SB-01 — Menu and customization** | In **Brew coffee**, select **Caffè Latte**. Move the **Milk** slider to **20%** and change **Sugar**. | The recipe preview changes. Milk ranges from 0–100% of a 200 ml allowance; sugar ranges from 0–20 g. Prices are stored in integer cents; customization does not add a surcharge. |
| **SB-02 — Contactless payment simulation** | Choose **Card** and **Declined · simulation** under **Demo payment response**, then click **Pay & brew**. Retry with **Approved · simulation**; **Phone** is also available. | A decline shows an error and consumes no ingredients. Approval starts one brewing order. Wait approximately **12 seconds**, then click **Collect my coffee** for the ready drink. This never charges real money. |
| **SB-03 — Weather context simulation** | Under **Weather simulation**, switch between **Hot · 30°C**, **Cold day**, **Mild day** and **Offline**; adjust **UTC hour**. | The local weather fixture displays its source. Offline mode shows an unavailable source and permits a time-only recommendation. No live weather API request occurs. |
| **SB-04 — Suggestion widget** | Set hot weather (**30°C**) and select **Surprise me**. Then try offline weather. | An available iced drink is suggested in hot weather; offline mode explains its time-only fallback. Suggestions include a reason and can be customized before payment. |
| **SB-05 — Inventory alerts** | Sign in to **Administration**, open **Ingredients & alerts**, and choose **Set level** on **Coffee beans**. Set **100 g** out of the **1000 g** capacity, click **Save simulated reading**, then restore an adequate level. | A low-stock alert appears at 10%. The threshold is strictly **below 15%**: 150 g is not low, 149 g is. Stock controls are simulated sensor overrides. |
| **SB-06 — Administrator authentication** | Open **Administration**, enter an incorrect **Admin password** and click **Sign in to administration**; then repeat with `smartbrew-admin`. | Wrong credentials are rejected; a valid session unlocks administrator operations. Technician credentials cannot authorize administrator endpoints. |
| **SB-07 — Menu editor** | In **Administration → Menu editor**, choose **Add drink**. Supply **Drink name**, **Description**, **Price (USD)**, **Temperature** and **Default milk (%)**, then **Add to the collection**. Use **Edit → Save changes** to change its price or clear **Active on customer menu**; return to **Brew coffee**. | Active additions and edits appear in the customer menu; hidden drinks disappear. New drinks use the prototype's standard coffee recipe, not a recipe inferred from their name. |
| **SB-08 — Technician access and service mode** | Collect any active drink. Open **Machine service**, enter **Maintenance PIN** `2468`, click **Access service workspace**, then **Enable service mode**. | A separate technician session opens. Service mode blocks customer brewing. Entry is rejected while an uncollected order is active. |
| **SB-09 — Diagnostic interface** | In service mode, click **Simulate 2 s test** on **Milk pump**, **Water pump** or **Heating element**. Repeat with **Simulate component fault** checked. | Deterministic pass/fail readings and audit events appear. The nominal two-second fixture is returned immediately; no physical component is activated. |
| **SB-10 — CSV error log export** | As technician, click **Export CSV** in **Machine event log** after generating a diagnostic fault. | The browser downloads `smartbrew-logs.csv`, including the failed diagnostic. Save or copy that file to a USB drive manually if desired; the application does not mount or write a physical USB device. |

Additional baseline user stories are also demonstrated: the customer sees brewing progress; **Sales insights** shows today's UTC order counts, revenue from completed/collected drinks, average completed order value and popular drinks. Sales insights requires administrator sign-in. A browser holds one role at a time, so sign in again when switching between administrator and technician work. Use **Finish maintenance** to return the machine to normal mode before resuming customer purchases; signing out alone leaves service mode enabled.

The machine serves one drink at a time. Ingredients are checked and deducted atomically with order creation, so insufficient stock cannot partially consume a recipe. A ready drink must be collected before the next order. Do not close an active order and expect a second purchase to bypass this interlock.

## Test

From the `Task_B` directory:

```bash
python3 -m unittest discover -s tests -v
```

The suite starts real HTTP servers on ephemeral local ports and creates isolated temporary SQLite databases. It checks menu/customization validation, successful and declined payments, atomic inventory deductions, strict 15% alerts, weather/recommendation scenarios, administrator and technician authorization, menu editing, service interlocks, diagnostic outcomes, CSV downloads, daily sales, brewing progress and persistence across a server restart. One lifecycle test waits for the actual twelve-second brewing interval; allow approximately half a minute for the suite. It does not consume or reset your development database.

GitHub Actions runs the same suite with Python **3.12.14**, matching the recommended local version. JavaScript can also be syntax-checked with Node.js when available:

```bash
node --check static/app.js
```

Node.js is optional developer tooling, not an application runtime dependency. Test execution evidence is recorded separately in the report; these instructions do not imply that every platform or physical integration has been tested.

## Configuration

| Variable | Purpose | Default |
| --- | --- | --- |
| `SMARTBREW_DB` | SQLite path, unless `--db` is supplied | `Task_B/data/smartbrew.db` from the repository root |
| `SMARTBREW_ADMIN_PASSWORD` | Administrator password | `smartbrew-admin` (public demo credential) |
| `SMARTBREW_TECH_PIN` | Technician PIN | `2468` (public demo credential) |

`--host` and `--port` select the listening address and port. Use `--help` for command-line details. Set credential overrides through your environment rather than committing values. The disclosed defaults are intentional demonstration credentials, not production secrets.

This prototype uses HTTP on loopback, opaque in-memory session cookies, role checks, same-origin mutation checks, bounded validation and parameterized SQL. It is not a production payment or machine-control system: it has no TLS termination, account-management workflow, login rate limiting, certified payment integration, real hardware safety controller or live external-service adapter. Keep it on a trusted local machine.

## Assignment artifacts

- [Task A — Requirements, user stories and backlog](../Task_A/requirements.md)
- [Task A — Annotated comparison with Assignment 2](../Task_A/comparison.md)
- [Task A — Assignment checklist and review corrections](../Task_A/task-a-review.md)
- [AI model disclosure and prompting strategy](../Task_A/ai-usage.md)
- [Prompt log and key responses](../Task_A/prompt-log.md)
- [Lab report and feature traceability](../docs/report.md)

The supplied Assignment 2 PDF is the human-authored comparison baseline. The original full System Description was not supplied separately; additions beyond the PDF are explicitly identified as prototype decisions rather than historical facts. See the comparison for retained requirements, refinements, rejected suggestions and hardware-related scope differences. AI assistance is disclosed for Tasks A, B and C; exact model build identifiers unavailable to the assistant are not invented.

## Repository and submission

Repository: <https://github.com/Yermukhamed11/Lab3_SmartBrew>

The implementation lives in `Task_B/`; requirements and comparison artifacts live in `Task_A/`. Shared report and repository tooling remain at the root. Do not commit the generated SQLite database, credentials, browser-session data or local test outputs. The repository layout is intentionally small:

```text
Task_A/                Requirements, comparison, prompts and Lab 2 reference
Task_B/
  app.py               HTTP API, SQLite and simulations
  static/              Browser UI and styles
  tests/               HTTP integration tests
  requirements.txt     No third-party dependencies
  validation.md        Execution evidence
  screenshots/         Browser evidence
  README.md            This execution guide
docs/report.md         Combined lab report
scripts/               Submission archive generator
.github/workflows/     CI configuration
```

Create a submission archive from the `Task_B` directory:

```bash
python3 ../scripts/package_submission.py
```

The default output is `SmartBrew_Lab3_Submission.zip` one directory above the checkout (`/workspace/SmartBrew_Lab3_Submission.zip` in this cloud environment); inspect the printed output or use the script's `--help` for an alternate destination. The archive excludes generated databases and Git metadata. For Canvas, upload the ZIP containing the report/artifacts and source, or reference the repository as permitted by the assignment. If the repository is private, invite instructor **riccardoRubei** as a collaborator using GitHub settings. The student must perform the final review and submission; repository visibility, collaborator access, remote publication and Canvas upload are separate actions and are not implied by a local successful run.
