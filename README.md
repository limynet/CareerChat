*Thinking...*

> The user wants me to draft the README in markdown format for them to copy. They want a clean, copyable markdown file. Let me write the README based on the build plan context provided, without repeating the conversation context.
> 
> The user said "drat" which I think means "draft" - a typo.
> 
> Let me write a clean, well-structured README.md based on the CareerChat build plan that was discussed, incorporating the Palantir documentation context.

```markdown
# CareerChat: AI-Powered ORB/CRB Screening Assistant

**CareerChat** is an enterprise-grade screening and comparison tool designed for US Army Branch Managers and the S1 Talent Branch Chief. Powered by GPT-5.1 via Palantir's Artificial Intelligence Platform (AIP), it ingests Officer Record Briefs (ORB), Civilian Record Briefs (CRB), and standard resumes to extract structured qualifications, enable interactive Q&A, and rank candidates against specific operational criteria.

---

## 🔄 Evolution from `VantageApp`

This repository supersedes the legacy `VantageApp` prototype.

| Capability | `VantageApp` (Legacy) | `CareerChat` (Current) |
| :--- | :--- | :--- |
| **LLM** | GPT-4.1-mini | GPT-5.1 |
| **Document Parsing** | `pypdf` (text-layer only) | `pdfplumber` + `python-docx` |
| **Data Extraction** | Raw context stuffing | Structured Pydantic models via LLM |
| **Analysis** | Single-document chat | Multi-candidate comparison & ranking |
| **AI Integration** | `palantir_models` SDK | OpenAI-compatible SDK via AIP Proxy |
| **Data Sources** | Foundry Datasets only | File Upload + Foundry Datasets + SparkSQL |

---

## 🏗️ Architecture & AIP Integration

```text
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

### Dual-Mode AI Client

CareerChat leverages **Palantir's LLM-provider compatible APIs**, which proxy requests to underlying
models while enforcing AIP data governance, zero data retention (ZDR), and rate limiting.

| Environment | Condition | Client Configuration |
| :--- | :--- | :--- |
| **Army Vantage / Foundry** | `FOUNDRY_URL` is set | `openai.OpenAI(base_url=f"{FOUNDRY_URL}/api/v2/llm/proxy/openai/v1", api_key=FOUNDRY_TOKEN)` |
| **Local Development** | `FOUNDRY_URL` is absent | `openai.OpenAI(api_key=OPENAI_API_KEY)` |

> **Note:** The `palantir_models` SDK is reserved for batch Python transforms only.
> Interactive Streamlit applications must use the OpenAI-compatible REST proxy.

---

## 📁 Project Structure

```
careerchat/
├── app.py                    # Main Streamlit application
├── requirements.txt
├── test_backend.py           # CLI end-to-end test
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── config.py             # Env vars, auto-detect Vantage vs local
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── client.py         # Dual-mode OpenAI client
│   │   ├── extractor.py      # LLM extraction → Pydantic
│   │   └── prompts.py        # System prompts
│   ├── models/
│   │   ├── __init__.py
│   │   └── candidate.py      # Pydantic Candidate schema
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── pdf_parser.py     # pdfplumber text extraction
│   │   └── docx_parser.py    # python-docx text extraction
│   └── db/
│       ├── __init__.py
│       └── vantage.py        # SparkSQL / Foundry dataset interface
└── tests/
    └── test_parsers.py
```

---

## 📊 Candidate Data Model

Documents are parsed and passed to the LLM to extract a structured Pydantic model, ensuring
consistent downstream analysis and comparison.

```python
# src/models/candidate.py
from pydantic import BaseModel

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
    raw_text: str                       # Full extracted text from document
    source_file: str                    # Original filename
```

---

## 🔑 Environment Variables

| Variable | Required | Purpose |
| :--- | :--- | :--- |
| `FOUNDRY_URL` | In Vantage | Base URL of the Foundry instance (e.g. `https://vantage.army.mil`) |
| `FOUNDRY_TOKEN` | In Vantage | Bearer token for Foundry API auth |
| `OPENAI_API_KEY` | Local dev | Direct OpenAI API key (fallback when not on Vantage) |
| `MODEL_NAME` | Optional | Model override (default: `gpt-5.1`) |

---

## 🛠️ Local Development

### 1. Clone and set up environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root (already listed in `.gitignore`):

```env
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-5.1
```

### 3. Test the backend (CLI)

```bash
python test_backend.py path/to/resume.pdf
# → parses → extracts → prints structured Candidate JSON
```

### 4. Run the application

```bash
streamlit run app.py
```

---

## 🏛️ Army Vantage / Foundry Deployment

Deploying CareerChat in Palantir Foundry requires adherence to Code Workspace constraints and
AIP security governance.

### 1. Managed Environments (Maestro)

Do **not** use raw `pip install` in the terminal. Use Maestro to ensure the environment is
consistently restored across workspace restarts, published apps, and notebook transforms.

```bash
maestro env pip install streamlit openai pdfplumber python-docx pydantic
```

This updates `/home/user/repo/.envs/maestro/meta.yaml` and regenerates the `hawk.lock` file.
Both files should be committed to version control.

To sync your environment after pulling new changes or switching branches:

```bash
maestro env install
```

### 2. Publishing the Streamlit App

1. Open the **Applications** tab in your JupyterLab® Code Workspace.
2. Select **Publish application**.
3. Point the file path to `app.py`.
4. Select **Publish and sync** to trigger CI checks and deploy.

> ⚠️ **Critical Constraint:** Published Streamlit apps have a strict **30-second startup timeout**.
> The server must fully initialize within this window or the deployment will fail.
> Keep top-level imports lean. Defer heavy processing (model loading, DB queries) until
> after first user interaction.

### 3. LLM Authentication on Vantage

On Vantage, the `FOUNDRY_TOKEN` environment variable is automatically available. The app routes
all LLM requests through the AIP-governed proxy:

```
POST /api/v2/llm/proxy/openai/v1/chat/completions
Authorization: Bearer {FOUNDRY_TOKEN}
```

Only models enabled on your enrollment are accessible through this endpoint. Usage is visible
in the Foundry Resource Management application and is subject to rate limiting.

---

## 🚀 Build Roadmap

### Phase 1 — Backend & Extraction Pipeline
*Goal: Working parsing and AI extraction testable from the CLI.*

- [ ] `requirements.txt` — `streamlit`, `openai`, `pdfplumber`, `python-docx`, `pydantic`
- [ ] `.gitignore` — `__pycache__/`, `.env`, `.streamlit/secrets.toml`, uploaded files
- [ ] `src/config.py` — load env vars, auto-detect Vantage vs local
- [ ] `src/models/candidate.py` — Pydantic `Candidate` schema
- [ ] `src/parsers/pdf_parser.py` — `extract_text(file_bytes) -> str` via `pdfplumber`
- [ ] `src/parsers/docx_parser.py` — `extract_text(file_bytes) -> str` via `python-docx`
- [ ] `src/ai/client.py` — `get_client() -> OpenAI` dual-mode factory
- [ ] `src/ai/prompts.py` — `EXTRACTION_PROMPT`, `CANDIDATE_QA_PROMPT`, `COMPARE_RANK_PROMPT`
- [ ] `src/ai/extractor.py` — `extract_candidate(raw_text, filename) -> Candidate`
- [ ] `src/db/vantage.py` — stub `save_candidate()`, `get_candidates()`, `compare_candidates()`
- [ ] `tests/test_parsers.py` — unit tests for PDF and DOCX extractors
- [ ] `test_backend.py` — CLI end-to-end: parse → extract → print JSON

### Phase 2 — Streamlit Application
*Goal: Interactive UI for upload, chat, and comparison.*

- [ ] `app.py` — main app with sidebar navigation
- [ ] Upload UI — PDF/DOCX upload, parse, display structured `Candidate` result
- [ ] Single-candidate chat — pick a candidate, ask qualifications questions
- [ ] Compare & rank — multi-select candidates, AI side-by-side evaluation
- [ ] Session state — `st.session_state` for candidates list and chat history

### Phase 3 — Vantage Integration & Persistence
*Goal: Persistent storage and production deployment on Army Vantage.*

- [ ] Implement SparkSQL client in `src/db/vantage.py`
- [ ] Store parsed candidates persistently to Foundry dataset
- [ ] Query historical candidate data in the UI
- [ ] Publish Streamlit app via JupyterLab Applications tab
- [ ] Configure managed environment via `maestro env pip install`

### Phase 4 — Documentation & Polish

- [ ] Finalize `README.md` with dataset media link (TBD)
- [ ] Update `AGENTS.md` with conventions discovered during build

---

## ⚙️ Key Design Decisions

1. **`pdfplumber` + `python-docx`** for text extraction — not Docling (failed in prior attempts).
2. **OpenAI-compatible proxy** for Foundry AI — standard `openai` SDK, not `palantir_models` transforms SDK.
3. **Pydantic** for structured candidate data validation and LLM output parsing.
4. **Streamlit session state** for ephemeral in-session data; **Vantage/SparkSQL** for persistence.
5. **30-second startup timeout** — app must stay lean for Foundry Code Workspace deployment.
6. **Dual-mode AI client** — identical code path works on Vantage and locally without modification.

---

## 📚 References

- [Palantir AIP — LLM-Provider Compatible APIs](https://www.palantir.com/docs/foundry/aip/llm-provider-compatible-apis/)
- [Palantir AIP — Overview](https://www.palantir.com/docs/foundry/aip/overview/)
- [Code Workspaces — JupyterLab® Deployment](https://www.palantir.com/docs/foundry/code-workspaces/jupyterlab/)
- [Model Integration — Overview](https://www.palantir.com/docs/foundry/model-integration/overview/)
- [Army Vantage JupyterLab Docs](https://vantage.army.mil/docs/foundry/code-workspaces/jupyterlab#jupyterlab)
```