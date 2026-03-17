"""
Search Agent V2 – site-targeted searches for comprehensive coverage.

Generates per-domain searches (site:amazon.in, site:flipkart.com, etc.)
to ensure results from multiple e-commerce sites.
"""

from __future__ import annotations
import logging
from urllib.parse import urlparse
from typing import TYPE_CHECKING

import httpx

from agents.base import BaseAgent
from models.schemas import SearchResult
from utils.helpers import retry_async
from config import settings

if TYPE_CHECKING:
    from orchestrator.state import AgentState

logger = logging.getLogger(__name__)

SERPER_URL = "https://google.serper.dev/search"
MAX_RESULTS_PER_QUERY = 10

# Targeted e-commerce domains for site-specific searches
TARGET_SITES = [
    "amazon.in",
    "flipkart.com",
    "croma.com",
    "reliancedigital.in",
    "vijaysales.com",
    "tatacliq.com",
]


class SearchAgent(BaseAgent):
    """Searches the web with site-targeted queries for broad e-commerce coverage."""

    name = "search"

    async def _search_serper(self, query: str) -> list[SearchResult]:
        """Execute a single Serper API search."""
        headers = {
            "X-API-KEY": settings.serper_api_key,
            "Content-Type": "application/json",
        }
        payload = {"q": query, "num": MAX_RESULTS_PER_QUERY, "gl": "in"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(SERPER_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("organic", [])[:MAX_RESULTS_PER_QUERY]:
            url = item.get("link", "")
            domain = ""
            try:
                domain = urlparse(url).netloc.replace("www.", "")
            except Exception:
                pass

            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=url,
                    snippet=item.get("snippet", ""),
                    domain=domain,
                )
            )
        return results

    async def run(self, state: AgentState) -> AgentState:
        state["current_step"] = "searching"
        plan = state.get("plan")

        if not plan:
            self._add_message(state, "❌ No plan available for search", level="error")
            return state

        # Build search queries: general + site-targeted
        base_query = plan.goal
        queries = [base_query]

        # Add site-specific searches for comprehensive coverage
        for site in TARGET_SITES:
            queries.append(f"{base_query} site:{site}")

        all_results: list[SearchResult] = []

        for i, query_text in enumerate(queries):
            is_site_search = "site:" in query_text
            label = query_text if not is_site_search else query_text.split("site:")[1]
            self._add_message(
                state,
                f"🔍 {'🎯 ' if is_site_search else ''}Searching: {label[:60]}",
            )
            try:
                results = await retry_async(
                    self._search_serper, query_text, max_retries=2
                )
                all_results.extend(results)
                self._add_message(
                    state,
                    f"✅ Found {len(results)} results"
                    + (f" from {label}" if is_site_search else ""),
                )
            except Exception as exc:
                self.logger.error("Search failed for '%s': %s", query_text, exc)
                self._add_message(
                    state,
                    f"⚠️ Search failed: {label[:40]} – {exc}",
                    level="warn",
                )

        # Deduplicate by URL
        seen_urls: set[str] = set()
        unique: list[SearchResult] = []
        for r in all_results:
            if r.url and r.url not in seen_urls:
                seen_urls.add(r.url)
                unique.append(r)

        state["search_results"] = unique
        self._add_message(
            state,
            f"📊 Total unique results: {len(unique)} across {len(set(r.domain for r in unique))} domains",
        )
        return state
