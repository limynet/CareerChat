# Fix LLM Documentation: palantir_models as Primary

## TL;DR
> **Summary**: Correct BUILD_PLAN.md and AGENTS.md to reflect that `palantir_models` + `language_model_service_api` is the primary LLM client on Vantage, and `OPENAI_API_KEY` is a placeholder for optional local dev only.
> **Deliverables**: Updated BUILD_PLAN.md, Updated AGENTS.md
> **Effort**: Quick
> **Parallel**: YES - 2 waves
> **Critical Path**: Task 1 → Task 2 (both can run in parallel)

## Context

### Original Request
The current BUILD_PLAN.md and AGENTS.md incorrectly describe the OpenAI SDK proxy as the primary LLM approach and say "Do NOT use `palantir_models` in the Streamlit app." The actual working prototype (`VantageApp`) uses `palantir_models.models.OpenAiGptChatLanguageModel` + `language_model_service_api`. The docs need to be corrected to match reality.

### Interview Summary
- Confirmed: `palantir_models` is the primary/correct way to load LLMs on Vantage
- Confirmed: `OPENAI_API_KEY` is a placeholder for potential local deployment only
- Confirmed: Redesign `src/ai/client.py` around `palantir_models` as primary, OpenAI SDK as local-dev fallback

### Key Findings from Exploration
- `VantageApp` (working prototype) uses: `palantir_models.models.OpenAiGptChatLanguageModel.get("GPT_4_1_MINI")` + `language_model_service_api`
- `src/` directory does not exist yet — all code is planned, not built
- BUILD_PLAN.md has two conflicting sections: lines 52-63 (OpenAI proxy) vs lines 144-151 (palantir_models code sample)
- AGENTS.md line 62 explicitly says "Do NOT use palantir_models" — directly contradicts user intent

## Work Objectives

### Core Objective
Correct both documentation files so the architecture description matches the actual `palantir_models` approach used in production.

### Deliverables
1. Updated `BUILD_PLAN.md` with corrected LLM architecture
2. Updated `AGENTS.md` with corrected AI client section

### Definition of Done
- `OPENAI_API_KEY` described as "placeholder for optional local dev" everywhere it appears
- `palantir_models` described as primary LLM mechanism on Vantage
- No conflicting sections remain (OpenAI proxy vs palantir_models)
- Build plan steps (1.4 config.py, 1.11 client.py) reflect palantir_models architecture
- Key Design Decisions section updated

### Must Have
- All references to LLM loading corrected
- Environment variable table corrected
- Architecture comparison table corrected
- Code samples showing correct `palantir_models` pattern

### Must NOT Have
- No removal of local dev / OpenAI SDK as fallback option (just reposition it as secondary)
- No changes to files other than BUILD_PLAN.md and AGENTS.md
- No changes to parsing, DB, or UI sections

## Verification Strategy
- Agent re-reads both files after edits and confirms zero contradictions
- Grep for "Do NOT use palantir_models" — must return 0 results
- Grep for "OpenAI-compatible proxy" — must not appear as primary description

## Execution Strategy

### Parallel Execution Waves

**Wave 1** (2 tasks, parallel):
- Task 1: Fix BUILD_PLAN.md
- Task 2: Fix AGENTS.md

### Dependency Matrix
| Task | Depends On | Blocks |
|------|-----------|--------|
| 1 | — | 3 |
| 2 | — | 3 |
| 3 (verify) | 1, 2 | — |

### Agent Dispatch Summary
Wave 1: 2 tasks × `quick` category
Wave 2: 1 verification task × `quick` category

## TODOs

- [ ] 1. Fix BUILD_PLAN.md — Correct LLM architecture documentation

  **What to do**: Edit BUILD_PLAN.md with the following changes. Each change is identified by line range in the current file:

  **Change 1 — Comparison table (lines 26-27)**:
  Current: `| AI client | palantir_models direct | OpenAI-compatible proxy (works in Vantage AND locally) |`
  New: `| AI client | palantir_models direct | palantir_models (primary) + OpenAI SDK (local dev fallback) |`

  **Change 2 — "AI Client — Two Modes" section (lines 52-65)**:
  Replace entirely with a section titled "AI Client — Two Modes" that:
  - Mode 1 (Primary/Vantage): `palantir_models.models.OpenAiGptChatLanguageModel` + `language_model_service_api`. Show code sample:
    ```python
    from palantir_models.models import OpenAiGptChatLanguageModel
    from language_model_service_api.languagemodelservice_api_completion_v3 import GptChatCompletionRequest
    from language_model_service_api.languagemodelservice_api import ChatMessage, ChatMessageRole

    model = OpenAiGptChatLanguageModel.get("GPT_4_1")
    response = model.create_chat_completion(GptChatCompletionRequest([ChatMessage(ChatMessageRole.USER, "prompt")]))
    ```
  - Mode 2 (Local dev fallback): When not on Vantage (`palantir_models` unavailable), falls back to `openai` SDK with `OPENAI_API_KEY`. Mark this as "placeholder — for local development testing only".
  - Remove the line "The `palantir_models` SDK is for Foundry Python transforms only. Do NOT use it in the Streamlit app."

  **Change 3 — Remove duplicate section (lines 144-151)**:
  Remove the standalone "## LLM should be load like this" section at the bottom. Its content is now integrated into the corrected "AI Client" section above.

  **Change 4 — Key Design Decisions (lines 154-158)**:
  Current item 2: `**OpenAI-compatible proxy** for Foundry AI — standard openai SDK, not palantir_models transforms`
  New item 2: `**palantir_models + language_model_service_api** for Foundry AI — native Palantir LLM bridge (OpenAI SDK as optional local dev fallback)`

  **Change 5 — config.py step 1.4 (line 78)**:
  Current: `Load FOUNDRY_URL, FOUNDRY_TOKEN, OPENAI_API_KEY, MODEL_NAME from env. Auto-detect Vantage vs local`
  New: `Load FOUNDRY_URL, FOUNDRY_TOKEN, MODEL_NAME from env. OPENAI_API_KEY optional (local dev placeholder only). Auto-detect Vantage vs local`

  **Change 6 — client.py step 1.11 (line 85)**:
  Current: `get_client() -> OpenAI — returns configured client for Foundry proxy or direct OpenAI`
  New: `get_client() — returns palantir_models LLM on Vantage, OpenAI SDK fallback for local dev`

  **Change 7 — Environment Variables table (lines 164-168)**:
  Change `OPENAI_API_KEY` row: Purpose from "Direct OpenAI API key (fallback when not on Vantage)" to "Placeholder for local development only (not used on Vantage)"

  **Must NOT do**: Do not change parsing steps, DB steps, UI steps, or Phase structure.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: Single file text edits, well-defined changes
  - Skills: [] — Reason: No specialized skills needed
  - Omitted: [] — none needed

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: Task 3 | Blocked By: none

  **References**:
  - Pattern: `VantageApp:1-21` — Working prototype showing correct palantir_models usage
  - Current file: `BUILD_PLAN.md` — the file being edited

  **Acceptance Criteria**:
  - [ ] No mention of "OpenAI-compatible proxy" as primary approach
  - [ ] "Do NOT use palantir_models" text removed
  - [ ] `palantir_models` described as primary Vantage LLM mechanism
  - [ ] `OPENAI_API_KEY` described as "placeholder" or "local dev only"
  - [ ] Duplicate "LLM should be load like this" section removed
  - [ ] Code sample shows `palantir_models` pattern matching VantageApp

  **QA Scenarios**:
  ```
  Scenario: No contradictions
    Tool: Bash (grep)
    Steps: grep -c "Do NOT use.*palantir_models" BUILD_PLAN.md
    Expected: Returns 0
    Evidence: .omo/evidence/task-1-no-contradictions.txt

  Scenario: palantir_models is primary
    Tool: Bash (grep)
    Steps: grep -c "palantir_models" BUILD_PLAN.md
    Expected: Returns >= 3 (multiple references to palantir_models as primary)
    Evidence: .omo/evidence/task-1-primary-check.txt
  ```

  **Commit**: YES | Message: `docs: correct LLM architecture to palantir_models primary` | Files: BUILD_PLAN.md

- [ ] 2. Fix AGENTS.md — Correct AI client and environment documentation

  **What to do**: Edit AGENTS.md with the following changes:

  **Change 1 — Stack line (line 11)**:
  Current: `- **AI**: GPT-5.1 via Army Vantage (Palantir Foundry) OpenAI-compatible proxy, or direct OpenAI API for local dev`
  New: `- **AI**: GPT-5.1 via `palantir_models` on Army Vantage (Palantir Foundry), or OpenAI API for local dev (placeholder)`

  **Change 2 — Project structure config.py comment (line 23)**:
  Current: `Env config: FOUNDRY_URL, FOUNDRY_TOKEN, OPENAI_API_KEY, MODEL_NAME`
  New: `Env config: FOUNDRY_URL, FOUNDRY_TOKEN, MODEL_NAME (OPENAI_API_KEY for local dev placeholder only)`

  **Change 3 — Project structure client.py comment (line 30)**:
  Current: `OpenAI SDK → Foundry proxy or direct OpenAI`
  New: `palantir_models LLM client (OpenAI SDK fallback for local dev)`

  **Change 4 — "AI client — how it works" section (lines 52-62)**:
  Replace the entire section with:
  - **Primary mode (Vantage)**: Uses `palantir_models.models.OpenAiGptChatLanguageModel` with `language_model_service_api`. Show code pattern matching VantageApp. This is the production approach on Army Vantage.
  - **Fallback mode (local dev)**: When `palantir_models` is unavailable (not on Vantage), falls back to `openai` Python SDK with `OPENAI_API_KEY`. This is a placeholder for local development testing only — not used in production.
  - Remove: "Do NOT use `palantir_models` (`GenericCompletionLanguageModelInput`, etc.) in the Streamlit app — those are for Foundry Python transforms (batch pipelines), not interactive apps."
  - Add note: The VantageApp prototype already demonstrates this pattern. The new app (`app.py` + `src/`) will follow the same `palantir_models` approach, upgraded to GPT-5.1 and with structured extraction.

  **Change 5 — "Existing prototype: VantageApp" section (lines 64-74)**:
  Update bullet list. Remove: "Use the OpenAI-compatible proxy (not `palantir_models` direct) for the Streamlit app"
  Replace with: "Continue using `palantir_models` (same as VantageApp) upgraded from GPT-4.1-mini to GPT-5.1"

  **Change 6 — Environment variables table (lines 79-83)**:
  Change `OPENAI_API_KEY` row: Required from "Local dev" to "Optional (local dev only)", Purpose from "Direct OpenAI API key (fallback when not on Vantage)" to "Placeholder for local development only (not used on Vantage)"

  **Change 7 — Secret mapping section (lines 87-96)**:
  Add note after the table: "Note: `OPENAI_API_KEY` (mapped from `z_ai`/`z_api`) is used only for local development when `palantir_models` is unavailable. On Vantage, the app uses `FOUNDRY_TOKEN` with `palantir_models`."

  **Must NOT do**: Do not change OpenCode setup, Git, Environment, Dataset, Vantage/Foundry specifics, or Commands sections.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: Single file text edits, well-defined changes
  - Skills: [] — Reason: No specialized skills needed
  - Omitted: [] — none needed

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: Task 3 | Blocked By: none

  **References**:
  - Pattern: `VantageApp:1-21` — Working prototype showing correct palantir_models usage
  - Current file: `AGENTS.md` — the file being edited

  **Acceptance Criteria**:
  - [ ] No mention of "Do NOT use palantir_models" or "OpenAI-compatible proxy" as primary
  - [ ] `palantir_models` described as primary Vantage LLM mechanism
  - [ ] `OPENAI_API_KEY` described as "placeholder" or "local dev only"
  - [ ] Code sample or reference shows `palantir_models` pattern
  - [ ] "Existing prototype" section does not say "not palantir_models direct"

  **QA Scenarios**:
  ```
  Scenario: No contradictions
    Tool: Bash (grep)
    Steps: grep -c "Do NOT use.*palantir_models" AGENTS.md
    Expected: Returns 0
    Evidence: .omo/evidence/task-2-no-contradictions.txt

  Scenario: palantir_models is primary
    Tool: Bash (grep)
    Steps: grep -c "palantir_models" AGENTS.md
    Expected: Returns >= 3
    Evidence: .omo/evidence/task-2-primary-check.txt

  Scenario: OPENAI_API_KEY marked as placeholder
    Tool: Bash (grep)
    Steps: grep "OPENAI_API_KEY" AGENTS.md | grep -c -i "placeholder\|local dev only\|optional"
    Expected: Returns >= 1
    Evidence: .omo/evidence/task-2-placeholder-check.txt
  ```

  **Commit**: YES | Message: `docs: correct AI client docs to palantir_models primary` | Files: AGENTS.md

- [ ] 3. Verify no contradictions remain across both files

  **What to do**: After Tasks 1 and 2 are complete, verify consistency:

  1. `grep -n "Do NOT use.*palantir" BUILD_PLAN.md AGENTS.md` — must return 0 results
  2. `grep -n "OpenAI-compatible proxy" BUILD_PLAN.md AGENTS.md` — must return 0 results
  3. `grep -c "palantir_models" BUILD_PLAN.md` — must be >= 3
  4. `grep -c "palantir_models" AGENTS.md` — must be >= 3
  5. `grep "OPENAI_API_KEY" BUILD_PLAN.md AGENTS.md` — every line must include "placeholder" or "local dev" or "optional"
  6. Re-read both files to confirm narrative consistency

  **Must NOT do**: Do not make any edits in this task — verification only.

  **Recommended Agent Profile**:
  - Category: `quick` — Reason: Simple grep verification
  - Skills: [] — Reason: No specialized skills needed
  - Omitted: [] — none needed

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: none | Blocked By: Tasks 1, 2

  **References**:
  - Both edited files

  **Acceptance Criteria**:
  - [ ] All 6 grep checks pass
  - [ ] No contradictions found in full file read

  **QA Scenarios**:
  ```
  Scenario: Consistency check
    Tool: Bash (grep chain)
    Steps: Run all 6 grep commands above
    Expected: All pass (0 forbidden patterns, >= 3 required references, all OPENAI_API_KEY lines marked)
    Evidence: .omo/evidence/task-3-consistency.txt
  ```

  **Commit**: NO — verification only

## Commit Strategy
- Task 1: `docs: correct LLM architecture to palantir_models primary` (BUILD_PLAN.md)
- Task 2: `docs: correct AI client docs to palantir_models primary` (AGENTS.md)
- Task 3: No commit (verification)

## Success Criteria
- Both docs describe `palantir_models` as the primary LLM mechanism on Vantage
- `OPENAI_API_KEY` is consistently described as placeholder/optional for local dev
- Zero contradictions between sections within each file
- Code samples show the `palantir_models` + `language_model_service_api` pattern from VantageApp
