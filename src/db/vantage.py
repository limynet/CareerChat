"""Vantage/SparkSQL database client for persistent candidate storage.

Phase 3 will replace these stubs with real SparkSQL queries against
Army Vantage (Palantir Foundry) datasets.

Currently implements in-memory storage for local development and testing.
"""
import logging
from typing import Optional

from src.models.candidate import Candidate

logger = logging.getLogger(__name__)

_candidates_store: list[Candidate] = []


def save_candidate(candidate: Candidate) -> str:
    """Save a candidate to the in-memory store.

    Args:
        candidate: Candidate to save.

    Returns:
        Confirmation message with candidate name.
    """
    _candidates_store.append(candidate)
    logger.info("Saved candidate: %s (total: %d)", candidate.name, len(_candidates_store))
    return f"Saved: {candidate.name}"


def get_candidates(
    name: Optional[str] = None, branch: Optional[str] = None
) -> list[Candidate]:
    """Retrieve candidates, optionally filtered by name or branch.

    Args:
        name: Optional name filter (case-insensitive substring match).
        branch: Optional branch filter (case-insensitive exact match).

    Returns:
        List of matching candidates.
    """
    results = _candidates_store
    if name:
        results = [c for c in results if name.lower() in c.name.lower()]
    if branch:
        results = [c for c in results if c.branch and c.branch.lower() == branch.lower()]
    return results


def clear_candidates() -> int:
    """Clear all stored candidates.

    Returns:
        Count of cleared candidates.
    """
    count = len(_candidates_store)
    _candidates_store.clear()
    logger.info("Cleared %d candidates", count)
    return count
