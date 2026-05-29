#!/usr/bin/env python3
"""CareerChat — US Army Branch Manager Tool.

Upload Resume PDFs or ORB (Officer Record Brief) documents (PDF/DOCX),
screen candidates, chat about qualifications, and compare/rank the best fits.
"""
import streamlit as st

from src.parsers.pdf_parser import extract_text_from_pdf
from src.parsers.docx_parser import extract_text_from_docx
from src.ai.extractor import extract_candidate, chat_about_candidate, compare_candidates
from src.models.candidate import Candidate


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="CareerChat",
    page_icon="🎖️",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------

if "candidates" not in st.session_state:
    st.session_state.candidates: list[Candidate] = []

if "chat_histories" not in st.session_state:
    st.session_state.chat_histories: dict[str, list[dict]] = {}


# ---------------------------------------------------------------------------
# Sidebar — Upload
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("📄 Upload Documents")

    uploaded_files = st.file_uploader(
        "Upload PDF or DOCX",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help="Upload Officer Record Briefs (ORBs) or resumes",
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Check if already processed
            existing_names = [c.source_file for c in st.session_state.candidates]
            if uploaded_file.name in existing_names:
                continue

            with st.spinner(f"Processing {uploaded_file.name}..."):
                try:
                    file_bytes = uploaded_file.read()
                    suffix = uploaded_file.name.lower().split(".")[-1]

                    if suffix == "pdf":
                        raw_text = extract_text_from_pdf(file_bytes)
                    elif suffix == "docx":
                        raw_text = extract_text_from_docx(file_bytes)
                    else:
                        st.error(f"Unsupported file type: {uploaded_file.name}")
                        continue

                    candidate = extract_candidate(raw_text, uploaded_file.name)
                    st.session_state.candidates.append(candidate)
                    st.success(f"✅ {candidate.name} ({candidate.rank or 'N/A'})")

                except ValueError as e:
                    st.error(f"Extraction error for {uploaded_file.name}: {e}")
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {e}")

    st.divider()

    # Show loaded candidates
    st.subheader("📋 Candidates")
    if st.session_state.candidates:
        for i, c in enumerate(st.session_state.candidates):
            st.markdown(f"**{i+1}. {c.name}** — {c.rank or '?'} {c.branch or ''}")
        if st.button("🗑️ Clear All", type="secondary"):
            st.session_state.candidates = []
            st.session_state.chat_histories = {}
            st.rerun()
    else:
        st.info("No candidates loaded yet. Upload documents above.")

    st.divider()
    st.caption("CareerChat — Powered by GPT-5.1")


# ---------------------------------------------------------------------------
# Main area — Tabs
# ---------------------------------------------------------------------------

tab_overview, tab_chat, tab_compare = st.tabs(
    ["📊 Overview", "💬 Chat", "⚖️ Compare & Rank"]
)


# ---------------------------------------------------------------------------
# Tab 1: Overview
# ---------------------------------------------------------------------------

with tab_overview:
    st.header("Candidate Overview")

    if not st.session_state.candidates:
        st.info("Upload documents in the sidebar to get started.")
    else:
        for i, c in enumerate(st.session_state.candidates):
            with st.expander(f"**{i+1}. {c.name}** — {c.rank or 'N/A'}", expanded=(i == 0)):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Branch:** {c.branch or 'N/A'}")
                    st.markdown(f"**MOS:** {c.mos or 'N/A'}")
                    st.markdown(f"**Years of Service:** {c.years_of_service or 'N/A'}")
                    if c.education:
                        st.markdown("**Education:**")
                        for edu in c.education:
                            st.markdown(f"  - {edu}")
                with col2:
                    if c.assignments:
                        st.markdown("**Assignments:**")
                        for a in c.assignments[:5]:
                            st.markdown(f"  - {a}")
                    if c.skills:
                        st.markdown("**Skills:**")
                        for s in c.skills[:8]:
                            st.markdown(f"  - {s}")
                    if c.awards:
                        st.markdown(f"**Awards:** {', '.join(c.awards[:5])}")
                    if c.deployments:
                        st.markdown(f"**Deployments:** {', '.join(c.deployments[:3])}")


# ---------------------------------------------------------------------------
# Tab 2: Chat about a candidate
# ---------------------------------------------------------------------------

with tab_chat:
    st.header("Chat About a Candidate")

    if not st.session_state.candidates:
        st.info("Upload documents first to start chatting.")
    else:
        candidate_names = [f"{i+1}. {c.name}" for i, c in enumerate(st.session_state.candidates)]
        selected_idx = st.selectbox(
            "Select a candidate:",
            range(len(candidate_names)),
            format_func=lambda i: candidate_names[i],
        )

        selected_candidate = st.session_state.candidates[selected_idx]
        candidate_key = selected_candidate.source_file

        # Initialize chat history for this candidate
        if candidate_key not in st.session_state.chat_histories:
            st.session_state.chat_histories[candidate_key] = []

        history = st.session_state.chat_histories[candidate_key]

        # Display chat history
        for msg in history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat input
        if prompt := st.chat_input(f"Ask about {selected_candidate.name}..."):
            history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = chat_about_candidate(
                            selected_candidate, prompt, history=history[:-1]
                        )
                        st.markdown(response)
                        history.append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error: {e}")


# ---------------------------------------------------------------------------
# Tab 3: Compare & Rank
# ---------------------------------------------------------------------------

with tab_compare:
    st.header("Compare & Rank Candidates")

    if len(st.session_state.candidates) < 2:
        st.info("Upload at least 2 candidate documents to compare.")
    else:
        # Multi-select candidates
        candidate_options = [
            f"{i+1}. {c.name} ({c.rank or 'N/A'}, {c.branch or '?'})"
            for i, c in enumerate(st.session_state.candidates)
        ]
        selected_indices = st.multiselect(
            "Select candidates to compare (min 2):",
            range(len(candidate_options)),
            format_func=lambda i: candidate_options[i],
        )

        criteria = st.text_input(
            "Role requirements or ranking criteria (optional):",
            placeholder="e.g., Battalion S3 position requiring deployment experience",
        )

        if st.button("⚖️ Compare Selected", type="primary", disabled=len(selected_indices) < 2):
            selected_candidates = [st.session_state.candidates[i] for i in selected_indices]

            with st.spinner("Analyzing candidates..."):
                try:
                    result = compare_candidates(selected_candidates, criteria=criteria)
                    st.markdown(result)
                except Exception as e:
                    st.error(f"Error: {e}")
