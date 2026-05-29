# CareerChat — Build Plan

## Overview

US Army branch manager tool powered by GPT-5.1. Upload Resume PDFs or ORB (Officer Record Brief) documents (PDF/DOCX), screen candidates, chat about qualifications, and compare/rank the best fits.

## Existing prototype: `VantageApp`

The repo contains `VantageApp` — a working earlier prototype with:

- `palantir_models.models.OpenAiGptChatLanguageModel` with `GPT_4_1_MINI`
- `pypdf.PdfReader` for PDF parsing
- Reads from Foundry datasets (`Dataset.get("orb_raw")`)
- Basic chat interface with context stuffing (first 5 resumes, 2000 chars each)
- `language_model_service_api` for chat completion requests

The new app (`app.py` + `src/`) supersedes this. Key upgrades:

| Aspect | `VantageApp` (old) | `app.py` (new) |
|---|---|---|
| Model | GPT-4.1-mini | GPT-5.1 |
| PDF parsing | `pypdf` | `pdfplumber` (better extraction) |
| DOCX support | None | `python-docx` |
| Candidate extraction | None (raw text stuffing) | Structured via Pydantic + GPT |
| Comparison/ranking | None | Multi-candidate compare and rank |
| AI client | `palantir_models` direct | OpenAI-compatible proxy (works in Vantage AND locally) |
| Data source | Foundry dataset only | Upload + Foundry dataset + SparkSQL |

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Streamlit UI                    │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Upload   │  │ Chat     │  │ Compare/Rank  │  │
│  │ PDF/DOCX │  │ about    │  │ candidates    │  │
│  └────┬─────┘  │ candidate│  │ side-by-side  │  │
│       │        └────┬─────┘  └───────┬───────┘  │
└───────┼─────────────┼────────────────┼──────────┘
        │             │                │
        ▼             ▼                ▼
┌─────────────────────────────────────────────────┐
│                  src/ backend                    │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Parsers  │  │ AI       │  │ DB            │  │
│  │ pdfplumb │  │ OpenAI   │  │ Vantage       │  │
│  │ docx     │  │ SDK      │  │ SparkSQL      │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
└─────────────────────────────────────────────────┘
```

## AI Client — Two Modes

The app auto-detects its environment:

| Mode | When | How |
|---|---|---|
| **Vantage/Foundry proxy** | `FOUNDRY_URL` env var is set | `openai.OpenAI(base_url={FOUNDRY_URL}/api/v2/llm/proxy/openai/v1, api_key=FOUNDRY_TOKEN)` |
| **Direct OpenAI** | `FOUNDRY_URL` not set | `openai.OpenAI(api_key=OPENAI_API_KEY)` |

Both modes use the identical `openai` Python SDK with the same `chat.completions.create()` calls. Foundry's LLM proxy is fully OpenAI-compatible.

The `palantir_models` SDK (`GenericCompletionLanguageModelInput`, etc.) is for Foundry Python transforms (batch pipelines) only. Do NOT use it in the Streamlit app.

Reference: https://www.palantir.com/docs/foundry/aip/llm-provider-compatible-apis/

## Phases

### Phase 1 — Backend (build and test first)

Goal: Working parsing + AI extraction pipeline testable from CLI.

| Step | File | What | Status |
|------|------|------|--------|
| 1.1 | `requirements.txt` | Dependencies: `streamlit`, `openai`, `pdfplumber`, `python-docx`, `pydantic` | ☐ |
| 1.2 | `.gitignore` | Ignore `__pycache__/`, `.env`, `.streamlit/secrets.toml`, uploaded files | ☐ |
| 1.3 | `src/__init__.py` | Package init | ☐ |
| 1.4 | `src/config.py` | Load `FOUNDRY_URL`, `FOUNDRY_TOKEN`, `OPENAI_API_KEY`, `MODEL_NAME` from env. Auto-detect Vantage vs local | ☐ |
| 1.5 | `src/models/__init__.py` | Package init | ☐ |
| 1.6 | `src/models/candidate.py` | Pydantic model: `name`, `rank`, `branch`, `mos`, `education`, `assignments`, `skills`, `raw_text`, `source_file` | ☐ |
| 1.7 | `src/parsers/__init__.py` | Package init | ☐ |
| 1.8 | `src/parsers/pdf_parser.py` | `extract_text(file_bytes) -> str` using `pdfplumber` | ☐ |
| 1.9 | `src/parsers/docx_parser.py` | `extract_text(file_bytes) -> str` using `python-docx` | ☐ |
| 1.10 | `src/ai/__init__.py` | Package init | ☐ |
| 1.11 | `src/ai/client.py` | `get_client() -> OpenAI` — returns configured client for Foundry proxy or direct OpenAI | ☐ |
| 1.12 | `src/ai/prompts.py` | System prompts: `EXTRACTION_PROMPT`, `CANDIDATE_QA_PROMPT`, `COMPARE_RANK_PROMPT` | ☐ |
| 1.13 | `src/ai/extractor.py` | `extract_candidate(raw_text, filename) -> Candidate` — sends to GPT with extraction prompt | ☐ |
| 1.14 | `src/db/__init__.py` | Package init | ☐ |
| 1.15 | `src/db/vantage.py` | Stub interface: `save_candidate()`, `get_candidates()`, `compare_candidates()` via SparkSQL | ☐ |
| 1.16 | `tests/test_parsers.py` | Unit tests for PDF and DOCX text extraction | ☐ |
| 1.17 | `test_backend.py` | CLI end-to-end test: `python test_backend.py <path-to-pdf-or-docx>` → parse → extract → print JSON | ☐ |

### Phase 2 — Streamlit UI

Goal: Interactive app with upload, chat, and comparison.

| Step | File | What | Status |
|------|------|------|--------|
| 2.1 | `app.py` | Main Streamlit app with sidebar navigation | ☐ |
| 2.2 | Upload UI | Sidebar: upload PDF/DOCX, parse, extract candidate data, display structured result | ☐ |
| 2.3 | Single-candidate chat | Chat interface: pick a candidate, ask questions about qualifications, get AI-powered answers | ☐ |
| 2.4 | Compare and rank | Multi-select candidates, ask AI to compare strengths/weaknesses, rank for a given role/criteria | ☐ |
| 2.5 | Session state | Streamlit session state for candidates and chat history | ☐ |

### Phase 3 — Vantage Integration

Goal: Persistent storage and deployment on Army Vantage.

| Step | What | Status |
|------|------|--------|
| 3.1 | Implement SparkSQL client in `src/db/vantage.py` | ☐ |
| 3.2 | Store parsed candidates persistently | ☐ |
| 3.3 | Query historical candidate data | ☐ |
| 3.4 | Publish Streamlit app via JupyterLab Applications tab | ☐ |
| 3.5 | Configure managed environment via `maestro env pip install` | ☐ |

### Phase 4 — Documentation and Polish

| Step | What | Status |
|------|------|--------|
| 4.1 | Update `README.md` with purpose, setup, deployment instructions | ☐ |
| 4.2 | Add dataset media link to README (user will provide) | ☐ |
| 4.3 | Update `AGENTS.md` with any new conventions discovered during build | ☐ |

## Candidate Data Model

```python
# src/models/candidate.py — Pydantic model
class Candidate(BaseModel):
    name: str
    rank: str | None = None
    branch: str | None = None
    mos: str | None = None              # Military Occupational Specialty
    education: list[str] | None = None
    assignments: list[str] | None = None
    skills: list[str] | None = None
    certifications: list[str] | None = None
    years_of_service: int | None = None
    deployments: list[str] | None = None
    awards: list[str] | None = None
    raw_text: str                        # Full extracted text from document
    source_file: str                     # Original filename
```
## LLM should be load like this
in .py
from language_model_service_api.languagemodelservice_api_completion_v3 import GptChatCompletionRequest
from language_model_service_api.languagemodelservice_api import ChatMessage, ChatMessageRole
from palantir_models.models import OpenAiGptChatLanguageModel

model = OpenAiGptChatLanguageModel.get("GPT_4_1")
response = model.create_chat_completion(GptChatCompletionRequest([ChatMessage(ChatMessageRole.USER, "why is the sky blue?")]))
## Key Design Decisions

1. **`pdfplumber` + `python-docx`** for text extraction — not Docling (failed previously)
2. **OpenAI-compatible proxy** for Foundry AI — standard `openai` SDK, not `palantir_models` transforms
3. **Pydantic** for structured candidate data validation
4. **Streamlit session state** for ephemeral data during a session; **Vantage/SparkSQL** for persistent storage
5. **30-second startup timeout** — app must be lean for Foundry Code Workspace deployment
6. **Dual-mode AI client** — works on Vantage (Foundry proxy) and locally (direct OpenAI) without code changes

## Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `FOUNDRY_URL` | In Vantage | Base URL of the Foundry instance (e.g. `https://vantage.army.mil`) |
| `FOUNDRY_TOKEN` | In Vantage | Bearer token for Foundry API auth |
| `OPENAI_API_KEY` | Local dev | Direct OpenAI API key (fallback when not on Vantage) |
| `MODEL_NAME` | No | Model to use (default: `gpt-5.1`) |

## Vantage / Foundry Constraints

- Published Streamlit apps have a **30-second startup timeout**
- Publish via JupyterLab Applications tab → `Publish application` → point to `app.py`
- Install libs with `maestro env pip install <package>` in managed environments
- Environment tracked in `/home/user/repo/.envs/maestro/meta.yaml` and `hawk.lock`
- Docs: https://www.palantir.com/docs/foundry/code-workspaces/jupyterlab/

## References

- Foundry LLM proxy API: https://www.palantir.com/docs/foundry/aip/llm-provider-compatible-apis/
- Foundry OpenAI proxy endpoint: `/api/v2/llm/proxy/openai/v1/chat/completions`
- Army Vantage docs: https://vantage.army.mil/docs/foundry/code-workspaces/jupyterlab#jupyterlab
- Palantir model integration: https://www.palantir.com/docs/foundry/model-integration/overview/
- AIP overview: https://www.palantir.com/docs/foundry/aip/overview/
