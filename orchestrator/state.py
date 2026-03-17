"""
Agent State V2 – shared state for the 8-node pipeline.
"""

from __future__ import annotations
from typing import Optional, TypedDict

from models.schemas import (
    TaskPlan,
    SearchResult,
    ExtractedProduct,
    AnalysisResult,
    FinalReport,
    AgentMessage,
)


class AgentState(TypedDict, total=False):
    """Shared state flowing through the agent pipeline."""

    # Input
    query: str

    # Planner output
    plan: Optional[TaskPlan]

    # Search output
    search_results: list[SearchResult]

    # Domain Filter output
    filtered_results: list[SearchResult]

    # Browser output
    raw_pages: list[dict]                  # [{url, title, content, html, domain}]
    screenshots: list[dict]                # [{url, path}]

    # Extractor output
    extracted_products: list[ExtractedProduct]

    # Deduplicator output
    deduplicated_products: list[ExtractedProduct]

    # Ranking output
    analysis: Optional[AnalysisResult]

    # Summarizer output
    final_report: Optional[FinalReport]

    # Monitoring / logging
    messages: list[AgentMessage]
    current_step: str
    error: Optional[str]
