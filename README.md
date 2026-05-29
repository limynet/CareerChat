# a read me file for opencode
The Goal: Build a Streamlit RAG app inside Palantir Foundry (Maestro) to ingest military resumes (ORB/CRB) from the orb_raw dataset, parse them using Docling, and query them using Foundry's native LLM bridge (palantir-models).
Obstacle 1 (Dependency Hell): Maestro’s base image ships with a conda-managed opencv-python that violently clashed with pip when installing Docling. We bypassed this by forcing Maestro to rebuild the pip environment from scratch.
Obstacle 2 (The Airgap): Docling’s default StandardPdfPipeline attempts to download RapidOCR weights from modelscope.cn at runtime. Foundry’s network sandbox blocks this, causing silent failures on scanned PDFs.
Obstacle 3 (Plugin Collisions): To bypass the airgap, you attempted to install internal Vantage OCR plugins (docling-google-ocr and docling-glm-ocr). While docling-glm-ocr installed, it aggressively upgraded your environment to docling 2.96.0 and pandas 3.0.3.
The Breaking Point: The upgrade to pandas 3.0.3 fundamentally broke palantir-models (which strictly requires pandas<3.0.0), and docling-google-ocr was rendered incompatible with the new Docling 2.96 ecosystem.
🚦 Current Environment Status
Docling Core: 🟢 Upgraded to v2.96.0 (via docling-glm-ocr).
GLM OCR Plugin: 🟡 Installed (v0.5.0), but untested due to environment instability.
Google OCR Plugin: 🔴 Broken (incompatible with Docling 2.96).
Palantir Models (LLM Bridge): 🔴 Critical Failure Risk (broken by Pandas 3.0.3).
Streamlit UI: 🟡 Functional, but throwing deprecation warnings for use_container_width.
🗺️ The New Building Plan
To move forward, we need to shift from reactive troubleshooting to a structured build plan. Here are the three phases to finalize your application.

Phase 1: Environment Triage & Stabilization (Immediate)
Before writing any more app code, we must rescue palantir-models and clean up the dead Google OCR package.

Run these commands in your Maestro terminal:

bash
# 1. Rip out the incompatible Google OCR package
maestro env pip uninstall docling-google-ocr

# 2. Downgrade pandas to save the Palantir LLM bridge 
# (Docling-core supports pandas 2.x, so this is safe)
maestro env pip install "pandas>=2.1.4,<3.0.0"

Phase 2: The OCR Strategy (Choose Your Path)
With the environment stabilized, you have two viable paths for handling the scanned/image-based ORB/CRB PDFs.

Path A: The GLM Plugin Route (If it survives the Pandas downgrade)
If docling-glm-ocr doesn't break when we downgrade Pandas, use the diagnostic script we discussed to find its Options class, and inject it into PdfPipelineOptions. This keeps everything inside the Docling pipeline.

Path B: The Vision-LLM Route (Highly Recommended for Foundry)
If the GLM plugin breaks due to the Pandas downgrade, abandon local OCR entirely. Foundry natively supports multimodal models. Instead of fighting Docling's OCR dependencies, use pymupdf to convert scanned PDF pages to images, and pass those images directly to Foundry's GPT-4o Vision model via palantir-models.

Why this is better: It completely sidesteps the modelscope.cn airgap issue, requires zero heavy OCR dependencies (no rapidocr, no easyocr), and leverages Foundry's secure, enterprise-grade vision APIs.
Phase 3: App Architecture & Polish
Once the parsing pipeline is locked, upgrade the application logic:

Fix Streamlit Deprecations: Do a global find-and-replace in your code. Change use_container_width=True to width="stretch" to eliminate the console warnings.
Smarter Context Retrieval: Right now, your RAG logic uses df.head(5). This means the LLM only ever sees the first 5 resumes in the dataframe. Upgrade this to a basic keyword-matching filter or implement a lightweight vector store (like FAISS or ChromaDB, if permitted in Vantage) to retrieve the most relevant resumes based on the user's prompt.
Asynchronous Parsing: Docling parsing is CPU-intensive. Move the load_raw_data() execution to a background task or cache it aggressively so the Streamlit UI doesn't lock up for 5 minutes every time the app boots.
🎯 Your Next Immediate Action
Execute the two maestro env pip commands from Phase 1. Once the lockfile is written successfully, try importing palantir_models and docling_glm_ocr in a Python shell to verify both survived the Pandas downgrade. Let me know the result, and we will execute either Path A or Path B for the OCR strategy.