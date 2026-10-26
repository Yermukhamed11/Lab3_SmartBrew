# Validation evidence — 26 October 2026

## Environment

The current managed Linux instance ran Python 3.12.14 with standard-library SQLite. There are no third-party application packages. Node.js v24.19.0 was used only for JavaScript syntax checking. Chromium and Playwright available in the development instance were used for browser QA; these are optional QA tools, not required to run the application or the unittest suite.

## Automated HTTP integration suite

Command, run from the `Task_B` directory (the suite was rerun after relocation):

```sh
python3 -m unittest discover -s tests -v
```

**Result: 19 tests passed in 22.585 seconds, exit status 0.** Tests use temporary SQLite databases, ephemeral HTTP ports and independent cookie-aware clients. They exercise actual HTTP handlers and persistence, rather than mock the API. The lifecycle test waits for the real 12-second simulated brewing interval.

Coverage includes public catalog, milk/sugar bounds, approved and declined payments, no stock deduction on decline, atomic rejection of insufficient stock, inventory's strict below-15% boundary, weather/time fixtures and fallback recommendations, incorrect credentials, role separation and logout, menu additions/edits/hiding, service interlocks, pass/fail diagnostics, CSV contents, daily completed sales and persistence across server restart. See [test_app.py](tests/test_app.py) for executable assertions.

There were no skipped, disabled or expected-failure cases. These tests validate the software simulation, not physical NFC payments or machinery.

## Browser functional check

An isolated server used a disposable database at `/tmp/smartbrew-browser-qa.db` rather than changing the retained development database. A real headless Chromium session exercised:

1. Five seeded catalog entries and the hot-weather recommendation of Iced Latte.
2. Milk set to 20% and sugar to 5 g, with recipe preview updates.
3. A declined payment error followed by an approved payment.
4. Reloading the page during brewing and restoring the opaque order ID.
5. Progress reaching ready after approximately 12 seconds and collecting the drink.
6. Incorrect and correct administrator passwords.
7. Creating a drink through the menu editor.
8. Setting beans to 100 g and observing a low-stock alert.
9. Seeing the collected Iced Latte represented as $4.20 in daily revenue.
10. Technician login, enabling service mode, a simulated pump fault, downloading the CSV and verifying `milk_pump` / `FAIL` in its contents, then returning to normal mode.
11. A 390 × 844 mobile viewport with no page-level horizontal overflow.

**Result: all assertions passed; no uncaught JavaScript exceptions.** A second check against the clean retained development database verified populated stock-bar widths under the strict Content Security Policy and no browser console errors. Browser QA initially found a missing favicon (404), which was added and rechecked. Review also corrected HTML inline progress widths to CSSOM updates compatible with the policy, corrected UTC hour initialization, and aligned revenue captions with completed-order accounting.

Screenshots: [desktop](screenshots/desktop.png), [mobile](screenshots/mobile.png). The screenshots show the clean seeded customer view, captured separately from the disposable functional-test data.

## Additional checks and scope

- `node --check static/app.js`: passed after the frontend changes.
- Python compilation and a source AST check found no named Python function/method lacking a docstring. All 49 named JavaScript functions have adjacent documentation comments.
- Application startup from the documented working directory passed. Local HTML, JavaScript and menu requests returned usable results; the retained application database started with the five default drinks.
- Cloud `start_skill` was saved successfully for review. No installation script was necessary because the runtime and all standard-library dependencies are already available. Saving does not publish or verify restoration in a future task.
- GitHub Actions is configured to run the integration suite; a remote workflow run is not claimed here.
- Browser QA was run as a development check. The reusable, dependency-free acceptance suite is `unittest`; Playwright is not an undeclared runtime prerequisite.
- No physical card, bank charge, weather API, sensor, pump, heater or USB write was tested. No live recommendation model is used.

## Task C review after the user's explicit recheck request

Reviewed all named functions/methods across application, browser client, integration tests and packaging script. Existing comments were present, but the review found underspecified parameter contracts and a few inaccurate descriptions. Expanded the 28 backend function/method docstrings with explicit Inputs/Returns, clarified HTTP-test helper and ZIP-script contracts, and corrected `heading()` to identify trusted HTML input and `recipeText()` to identify plain text output. AST comparisons against the initial commit confirmed the Python edits changed documentation only.

Added fresh-clone/extracted-ZIP working-directory instructions; aligned all ten README demo steps with real UI labels; explained that signing out does not exit service mode. `.python-version` and GitHub Actions now pin the actually tested Python 3.12.14. No third-party packages are needed.

The review also found a real preview/documentation mismatch: the UI displayed milk percentage while the requirements/demo expected millilitres too. It now displays both, e.g. `20% milk (40 ml of 200 ml)`. A targeted Chromium assertion passed for that example. JavaScript syntax and Python compilation passed after the review. No Python behavior changed, so the already-passed HTTP integration suite did not need a redundant rerun.

## Separate-task folder validation

After relocating the prototype to `Task_B/`, `python3 -m unittest discover -s tests -v` executed **19 tests in 22.564 seconds: all passed, exit 0**, with no skipped or disabled tests. The working directory is `Task_B/`, matching the updated CI workflow and execution guide. The development server was restarted there, and existing runtime data was preserved in `Task_B/data/`. Local document links and the new archive layout are checked separately; historical quoted paths in the conversation log are retained as evidence of their original messages.
