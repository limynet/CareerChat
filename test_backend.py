#!/usr/bin/env python3
"""CLI end-to-end test: parse document -> extract candidate -> print JSON.

Usage:
    python test_backend.py <path-to-pdf-or-docx>

Requires OPENAI_API_KEY or FOUNDRY_URL+FOUNDRY_TOKEN to be set.
"""
import json
import pathlib
import sys

from src.parsers.pdf_parser import extract_text_from_pdf
from src.parsers.docx_parser import extract_text_from_docx
from src.ai.extractor import extract_candidate


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-pdf-or-docx>", file=sys.stderr)
        sys.exit(1)

    file_path = pathlib.Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: file not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    suffix = file_path.suffix.lower()

    # Step 1: Parse document
    print(f"Parsing {suffix.upper()} file: {file_path.name}")
    file_bytes = file_path.read_bytes()

    if suffix == ".pdf":
        raw_text = extract_text_from_pdf(file_bytes)
    elif suffix in (".docx", ".doc"):
        raw_text = extract_text_from_docx(file_bytes)
    else:
        print(f"Error: unsupported file type: {suffix}", file=sys.stderr)
        sys.exit(1)

    print(f"Extracted {len(raw_text)} characters of text")
    print(f"First 500 chars:\n{'-'*40}\n{raw_text[:500]}\n{'-'*40}\n")

    # Step 2: Extract structured candidate data via GPT
    print("Extracting candidate data via GPT...")
    try:
        candidate = extract_candidate(raw_text, file_path.name)
    except Exception as e:
        print(f"Error during extraction: {e}", file=sys.stderr)
        sys.exit(1)

    # Step 3: Print structured result
    print("\n" + "=" * 60)
    print("EXTRACTED CANDIDATE")
    print("=" * 60)

    result = candidate.model_dump()
    raw_text_len = len(result.pop("raw_text", ""))
    print(json.dumps(result, indent=2, default=str))
    print(f"\n[raw_text: {raw_text_len} chars omitted from display]")

    print("\n" + "=" * 60)
    print("SUCCESS")
    print("=" * 60)


if __name__ == "__main__":
    main()
