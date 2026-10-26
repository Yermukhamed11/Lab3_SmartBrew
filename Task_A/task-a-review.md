# Task A review against the assignment

This review uses the actual Assignment 2 PDF and the assignment prompt in [prompt-log.md](prompt-log.md). It checks the submission artifacts, not instructor acceptance or unavailable original source material.

| Task A condition | Evidence after review | Result / limitation |
| --- | --- | --- |
| Functional and non-functional requirements | [requirements.md](requirements.md): nine prototype FR rows, ten NFR rows, six source-target mappings | Present; original hardware objectives are not replaced by simulation claims |
| Format matching Assignment 2 | Same six FR columns; actor/goal/benefit stories; same seven backlog columns and scales | Preserved structure; acceptance/traceability annotations are explicitly added |
| User Stories | Ten LLM-refined US-01–US-10; all ten original human sentences in [comparison.md](comparison.md) | Full side-by-side wording and change assessments; Custom Feature marker retained |
| Product Backlog | SB-01–SB-10 with original importance and Fibonacci estimates | All ten pairs match the PDF; updated descriptions/demos are marked adaptations |
| Prompt strategy and main prompts/key responses | [ai-usage.md](ai-usage.md), [prompt-log.md](prompt-log.md) | Original English messages, labeled English translations and labeled summaries; exact hidden model build is unavailable and not invented |
| Clearly highlighted comparison | Requirement-by-requirement, story-by-story and backlog comparisons | Preserved, added, narrowed and deferred aspects distinguished |
| Improvements, omissions and incorrect/unneeded suggestions | Critical assessment and rejection/deferment table in [comparison.md](comparison.md) | Each rejected/deferred suggestion has a reason; original 15% rule credited to the human |
| Model/version disclosure | GPT-6 through Codex for Task A, with exact-build limitation | Available identity documented; no fabricated version/date |

## Corrections made

- Corrected the unsupported claim that the LLM resolved an ambiguous inventory threshold: the human already specified **below 15%**. The contribution is explicit boundary examples/testing.
- Added a full original-versus-refined table for every user story rather than describing all stories in one paragraph. Retained the human Custom Feature label.
- Separated six original physical-system commitments from prototype acceptance requirements and their remaining physical gaps.
- Made the method explicit: baseline-informed refinement, not independent/blind elicitation. The final model output was informed by Assignment 2.
- Added an assumption register: slider quantities, pricing, concurrency, simulated duration, fallback behavior, accounting/day boundary, hardware substitutions and access defaults.
- Clarified that a hot-weather recommendation can use an explained available fallback if the seeded iced drink is unavailable; clarified read-driven readiness and default-recipe availability.

The separate original System Description is still unavailable. Therefore the artifacts can be checked against the supplied Lab 2 but cannot establish coverage of unknown requirements from another document. Physical interfaces and runtime AI remain deferred as described in the report; this review does not certify the project meets those original physical acceptance tests.

Document checks passed after these edits: all ten original story sentences match the normalized PDF extraction exactly; all ten refined sentences differ explicitly from their originals; nine prototype FR rows, ten NFR rows and ten backlog rows are present; all ten importance/effort pairs match Lab 2; the original PDF hash is unchanged; all local Markdown links resolve. A second read-only review found no remaining material contradictions. Only documentation changed, so application tests were not rerun for this review.

The submission language was subsequently reviewed: requests, prompts and responses are presented in English, with translation provenance retained in the prompt record and model disclosure. This is an English edition of the actual interaction, not a claim that Russian-language messages were originally written in English.
