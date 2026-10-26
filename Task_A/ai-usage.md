# AI assistance and model disclosure

| Task | Model used in this session | Contribution | Human/student responsibility |
| --- | --- | --- | --- |
| A — Requirements and comparison | OpenAI GPT-6 through Codex | Read supplied Lab 2 PDF, retain its formats/IDs, refine requirements, acceptance criteria and NFRs, annotate differences and reject off-scope ideas | Check interpretation, added assumptions and whether physical integrations may be simulated |
| B — Code generation and execution | OpenAI GPT-6 through Codex | Generated Python/SQLite API, HTML/CSS/JavaScript UI, HTTP tests and setup instructions; ran actual tests/browser checks | Review code/results, demonstrate features, confirm submission scope |
| C — Documentation and repository | OpenAI GPT-6 through Codex | README, function documentation, Task A report, model/prompt record and packaging/CI configuration | Review artifacts and perform final course submission/access checks |

**Version disclosure:** the assistant identity exposed in this environment is GPT-6 via Codex. An exact dated model build, internal snapshot identifier, temperature and routing configuration are not exposed and are not invented. Parallel Codex agents inherited the same model configuration; they are not independently identified as different models. No external model runs inside the SmartBrew application.

## Task A method and comparison limits

The final Task A artifacts were generated **after seeing the human Lab 2**, so the process is baseline-informed elicitation/refinement. It is not a controlled independent comparison, and retained human features/priority values are not credited as new LLM discoveries. No separate original System Description was available. During the later Task A review, the model generated distinct refined stories and an explicit source-to-prototype mapping; every original sentence remains visible alongside its refinement in [comparison.md](comparison.md). The current prompts and key responses are recorded in [prompt-log.md](prompt-log.md), including that review.

## Prompt strategy actually used

1. **Establish evidence before implementation.** Inspect the repository and ask for System Description/Lab 2. Initially the repository was empty. The user authorized proceeding, so a provisional cafe interpretation was stated explicitly rather than represented as a known requirement.
2. **Ground and correct.** When the supplied PDF became available, extract and read its real stories, REQ-01–REQ-06 and SB-01–SB-10. Replace the cafe/rewards/reviews direction with the coffee-machine scope. Preserve original importance values, estimates and table columns for comparison.
3. **Constrain generation.** Select exactly the baseline's ten backlog items. Separate software simulation from physical acceptance. Use Python standard library/SQLite and a same-origin browser UI to minimize independent-machine dependency issues. Require function input/output documentation and meaningful HTTP tests.
4. **Divide outputs while preserving contracts.** Code, frontend, tests and documentation were assigned as parallel agent tasks. The parent supplied shared feature/API contracts and corrected scope when the PDF arrived. These are process prompts, not invented interviews with stakeholders.
5. **Critically review and execute.** Check negative as well as positive behavior: declines, insufficient stock, wrong-role requests, 15% boundary, busy/service interlocks and offline weather. Compare claims against source and actual results; retain limitations rather than changing the criteria to call simulations physical integrations.
6. **Preserve evidence.** Keep original PDF/text, annotated comparison, visible conversation excerpts and executable source/test outputs. See [prompt-log.md](prompt-log.md) and [validation.md](../Task_B/validation.md).

## Limits of the interaction record

[prompt-log.md](prompt-log.md) records the actual main task prompt, known user steering, visible assistant responses and selected process prompts. It is a structured conversational record, **not a raw API export or a claim that internal tool telemetry has been reproduced in full**. Code-generation outputs are retained verbatim as repository source files and linked from the record instead of duplicated as thousands of lines inside the report. Originally English quotations are identified as verbatim. Messages originally written in Russian are presented as faithful English translations and labeled accordingly; the submission does not claim they were originally exchanged in English. Summaries are labeled as summaries. No dialogue is backdated or invented to resemble an earlier Lab 2 elicitation session.

The comparison is against the supplied human PDF. The student did not independently author the LLM artifacts in this session; AI assistance applies to all three tasks. The student should export the original platform conversation too if a course reviewer requires the complete raw chat history rather than this structured record and generated files.

## English submission edition

At the user's request, the submission presents every request, prompt and response in English. Russian-language source messages were translated with OpenAI GPT-6 through Codex; translated passages are explicitly labeled, while original English prompts retain their verbatim status. The mixed-language process prompt is labeled as an English version with its embedded user quotation translated. The original conversation is not rewritten historically; earlier repository revisions retain the earlier text, and the current submission contains the English edition. This translation changes presentation, not the requirements, test results, model disclosure or implementation.

## Critical evaluation

The largest model failure was the initial unsupported assumption that SmartBrew was a cafe-ordering application. Requiring source evidence and applying the PDF corrected it. The useful contributions were testable bounds, atomic stock/payment behavior, explicit role separation, offline recommendation behavior and cross-artifact traceability. The model could not establish real hardware safety, NFC payment compliance or external API behavior; passing local tests does not address those gaps.
