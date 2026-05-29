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

### Secret mapping (devcontainer)

Gitpod secrets are mapped to standard variable names at container startup via `.devcontainer/secrets.sh` and `remoteEnv` in `devcontainer.json`:

| Gitpod secret name | Maps to |
|---|---|
| `z_ai` | `OPENAI_API_KEY` |
| `z_api` | `OPENAI_API_KEY` (fallback) |
| `gemini_api` | `GEMINI_API_KEY` |
| `poe_api` | `POE_API_KEY` |

If `gemini_api`, `z_api`, or `poe_api` are not reaching the container, check that they are scoped to this repository in Gitpod Settings → Variables.

## Vantage / Foundry specifics

- Streamlit apps in Foundry Code Workspaces have a **30-second startup timeout**
- Publish via JupyterLab Applications tab: `Publish application` → point to `app.py`
- Use `maestro env pip install <package>` to install libs in managed environments
- Environment tracked in `/home/user/repo/.envs/maestro/meta.yaml` and `hawk.lock`
- Docs: https://www.palantir.com/docs/foundry/code-workspaces/jupyterlab/

## OpenCode setup

- **Project config**: `opencode.json` at repo root — loads `AGENTS.md` as instructions, pre-configures bash permissions for git/pip/python/pytest
- **Custom agents**: `.opencode/agent/` — includes `test-runner` subagent for running tests
- **Devcontainer**: `postStartCommand` auto-installs opencode CLI via `curl -fsSL https://opencode.ai/install | bash` if not present
- **VS Code extension**: `sst-dev.opencode` (auto-installed by devcontainer)
- After changing `opencode.json`, `.opencode/agent/*.md`, or `.opencode/skill/*/SKILL.md`, **restart opencode** for changes to take effect

## Environment

- **Dev container**: `mcr.microsoft.com/devcontainers/universal:4.0.1-noble` with Python 3.10 feature.
- **Container name** in devcontainer.json is `"Ona"`.
- **Git LFS** is enabled but has no tracked patterns yet (no `.gitattributes`).

## Git

- `.ona/review` and `.ona/artifacts` are in `.git/info/exclude` (never tracked).
- Remote: `origin` → `https://github.com/limynet/CareerChat.git`.
- Vantage doc: https://vantage.army.mil/docs/foundry/code-workspaces/jupyterlab#jupyterlab
- Foundry doc: https://www.palantir.com/docs/foundry/code-workspaces/jupyterlab

## Dataset

User will provide a dataset media link to be added to README when available.
