# CareerChat — Agent Guide

## Purpose

US Army branch manager tool. Upload Resume PDF or ORB (Officer Record Brief) documents (PDF/DOCX), screen candidates, chat about qualifications, and compare/rank the best fits using AI.

## Stack

- **Frontend**: Streamlit (`streamlit run app.py`)
- **Language**: Python 3.10+
- **AI**: GPT-5.1 via Army Vantage (Palantir Foundry) OpenAI-compatible proxy, or direct OpenAI API for local dev
- **Data**: Army Vantage (Palantir Foundry) with SparkSQL
- **Parsing**: `pdfplumber` (PDF) + `python-docx` (DOCX) — previous Docling backend failed, do not reintroduce it
- **Validation**: `pydantic` for structured candidate data

## Project structure

```
CareerChat/
├── app.py                      # Streamlit entry point (Phase 2)
├── requirements.txt
├── src/
│   ├── config.py               # Env config: FOUNDRY_URL, FOUNDRY_TOKEN, OPENAI_API_KEY, MODEL_NAME
│   ├── models/
│   │   └── candidate.py        # Pydantic Candidate model
│   ├── parsers/
│   │   ├── pdf_parser.py       # pdfplumber text extraction
│   │   └── docx_parser.py      # python-docx text extraction
│   ├── ai/
│   │   ├── client.py           # OpenAI SDK → Foundry proxy or direct OpenAI
│   │   ├── prompts.py          # System prompts (extraction, Q&A, compare/rank)
│   │   └── extractor.py        # Raw text → structured Candidate via GPT
│   └── db/
│       └── vantage.py           # SparkSQL client for Vantage (stub until deployed)
├── tests/
│   └── test_parsers.py
├── test_backend.py              # CLI end-to-end test: parse → extract → print
├── VantageApp                   # Original prototype (reference only — uses palantir_models + pypdf)
├── BUILD_PLAN.md                # Full build plan and phases
├── AGENTS.md
└── README.md
```

## Commands

- `pip install -r requirements.txt` — install deps
- `streamlit run app.py` — run the app (once built)
- `python test_backend.py <path-to-pdf-or-docx>` — test parsing + extraction pipeline
- `pytest tests/` — run unit tests

## AI client — how it works

Two modes, auto-detected by `src/ai/client.py`:

| Mode | Trigger | Config |
|---|---|---|
| **Vantage/Foundry proxy** | `FOUNDRY_URL` env var set | `base_url={FOUNDRY_URL}/api/v2/llm/proxy/openai/v1`, `api_key=FOUNDRY_TOKEN` |
| **Direct OpenAI** (local dev) | `FOUNDRY_URL` not set | `api_key=OPENAI_API_KEY` |

Both use the standard `openai` Python SDK with identical request/response shapes. Foundry's proxy is OpenAI-compatible — same `chat.completions.create()` call.

Do NOT use `palantir_models` (`GenericCompletionLanguageModelInput`, etc.) in the Streamlit app — those are for Foundry Python transforms (batch pipelines), not interactive apps.

## Existing prototype: `VantageApp`

The repo contains `VantageApp` — an earlier prototype that uses `palantir_models.models.OpenAiGptChatLanguageModel` with `GPT_4_1_MINI` and `pypdf`. It reads PDFs from Foundry datasets (`orb_raw`) and has a basic chat interface. This file is kept as reference. The new `app.py` will:

- Upgrade from GPT-4.1-mini to GPT-5.1
- Switch from `pypdf` to `pdfplumber` (better text extraction)
- Add DOCX support via `python-docx`
- Add structured candidate extraction with Pydantic
- Add candidate comparison and ranking
- Use the OpenAI-compatible proxy (not `palantir_models` direct) for the Streamlit app
- Support local dev outside Vantage via direct OpenAI API

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `FOUNDRY_URL` | In Vantage | Base URL of the Foundry instance (e.g. `https://vantage.army.mil`) |
| `FOUNDRY_TOKEN` | In Vantage | Bearer token for Foundry API auth |
| `OPENAI_API_KEY` | Local dev | Direct OpenAI API key (fallback when not on Vantage) |
| `MODEL_NAME` | No | Model to use (default: `gpt-5.1`) |

## Vantage / Foundry specifics

- Streamlit apps in Foundry Code Workspaces have a **30-second startup timeout**
- Publish via JupyterLab Applications tab: `Publish application` → point to `app.py`
- Use `maestro env pip install <package>` to install libs in managed environments
- Environment tracked in `/home/user/repo/.envs/maestro/meta.yaml` and `hawk.lock`
- Docs: https://www.palantir.com/docs/foundry/code-workspaces/jupyterlab/

## Environment

- **Dev container**: `mcr.microsoft.com/devcontainers/universal:4.0.1-noble` (image only, no Dockerfile).
- **Container name** in devcontainer.json is `"Ona"`.
- **Recommended extension**: `sst-dev.opencode` (VS Code).
- **Git LFS** is enabled but has no tracked patterns yet (no `.gitattributes`).

## Git

- `.ona/review` and `.ona/artifacts` are in `.git/info/exclude` (never tracked).
- Remote: `origin` → `https://github.com/limynet/CareerChat.git`.
- Vantage doc: https://vantage.army.mil/docs/foundry/code-workspaces/jupyterlab#jupyterlab
- Foundry doc: https://www.palantir.com/docs/foundry/code-workspaces/jupyterlab

## Dataset

User will provide a dataset media link to be added to README when available.
