# SmartBrew AI · Lab Assignment 3

An LLM-assisted software engineering project for a smart coffee machine. The repository separates requirements analysis from the executable prototype while preserving the **SB-01–SB-10** feature identifiers from Assignment 2.

| Folder | Contents | Start here |
| --- | --- | --- |
| **Task_A/** | Functional and non-functional requirements, user stories, product backlog, comparison with the supplied Assignment 2 PDF, AI model disclosure and prompt records | [Task A guide](Task_A/README.md) |
| **Task_B/** | Runnable Python/SQLite web prototype, documented source code, browser UI, automated tests and validation evidence | [Task B execution guide](Task_B/README.md) |
| **docs/** | Cross-task lab report and traceability | [Lab report](docs/report.md) |

Task C documentation and repository-management deliverables are included in the README files, source comments, configuration files and CI workflow.

## Run the prototype

Use **Python 3.12.14** (the pinned and tested version), a Python installation with standard-library SQLite support, and a modern browser. The application uses only Python's standard library; there are no third-party package dependencies or separate build step. Python 3.11+ is supported by the source, while Linux with Python 3.12.14 is the verified environment.

```bash
git clone https://github.com/Yermukhamed11/Lab3_SmartBrew.git
cd Lab3_SmartBrew/Task_B
python3 app.py --host 127.0.0.1 --port 8000
```

If you downloaded the submission ZIP, extract it and enter its `Lab3_SmartBrew/Task_B` directory instead. Open the local address printed by the server in your browser. Stop the server with **Ctrl+C**.

From the same `Task_B` directory, run the isolated HTTP integration tests:

```bash
python3 -m unittest discover -s tests -v
```

The [Task B guide](Task_B/README.md) includes prerequisites, configuration, demonstration credentials, database behavior and step-by-step instructions for all ten features. Physical payments, weather, sensors and machine components are explicitly simulated; drink recommendations use deterministic rules rather than a live AI model.

## Read the assignment artifacts

- [Requirements, user stories and backlog](Task_A/requirements.md)
- [Annotated comparison with Assignment 2](Task_A/comparison.md)
- [AI models and prompting strategy](Task_A/ai-usage.md)
- [English prompt log and key responses](Task_A/prompt-log.md)
- [Cross-task report and feature traceability](docs/report.md)

The supplied Assignment 2 PDF is the comparison baseline. The original full System Description was not supplied separately; prototype decisions and deviations are documented explicitly.

## Prepare the submission

From the **repository root**, create the Canvas archive:

```bash
python3 scripts/package_submission.py
```

The script reports the generated ZIP path and excludes runtime databases and Git metadata. Review the archive and [lab report](docs/report.md) before submission. Repository: <https://github.com/Yermukhamed11/Lab3_SmartBrew>. If private, invite instructor **riccardoRubei** as a collaborator. GitHub publication, collaborator access and Canvas upload require their respective final submission actions.
