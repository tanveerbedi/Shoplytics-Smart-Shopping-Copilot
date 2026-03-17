"""
Domain Filter Agent – filters search results to trusted e-commerce domains.

Ensures the pipeline focuses on reliable, structured e-commerce sites
rather than random blogs or forums.
"""

from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from agents.base import BaseAgent
from extractors import TRUSTED_DOMAINS, is_trusted_domain

if TYPE_CHECKING:
    from orchestrator.state import AgentState

logger = logging.getLogger(__name__)

MIN_TRUSTED_RESULTS = 10


class DomainFilterAgent(BaseAgent):
    """Filters search results to keep only trusted e-commerce domains."""

    name = "domain_filter"

    async def run(self, state: AgentState) -> AgentState:
        state["current_step"] = "filtering"
        results = state.get("search_results", [])

        if not results:
            self._add_message(state, "❌ No search results to filter", level="error")
            state["filtered_results"] = []
            return state

        self._add_message(
            state,
            f"🔍 Filtering {len(results)} results through trusted domains: "
            + ", ".join(TRUSTED_DOMAINS),
        )

        # Separate trusted and untrusted
        trusted = []
        untrusted = []
        seen_domains = set()

        for r in results:
            if is_trusted_domain(r.domain):
                # Allow up to 4 results per domain to ensure diversity
                domain_count = sum(1 for t in trusted if t.domain == r.domain)
                if domain_count < 4:
                    trusted.append(r)
                    seen_domains.add(r.domain)
                    self._add_message(
                        state,
                        f"✅ Trusted [{r.domain}]: {r.title[:45]}",
                    )
            else:
                untrusted.append(r)

        # If too few trusted results, include top untrusted as fallback
        if len(trusted) < MIN_TRUSTED_RESULTS:
            fallback_count = MIN_TRUSTED_RESULTS - len(trusted)
            fallback = untrusted[:fallback_count]
            trusted.extend(fallback)
            if fallback:
                self._add_message(
                    state,
                    f"⚠️ Only {len(trusted) - len(fallback)} trusted results found, "
                    f"adding {len(fallback)} backup results",
                    level="warn",
                )

        state["filtered_results"] = trusted
        self._add_message(
            state,
            f"📊 Kept {len(trusted)} results from "
            f"{len(set(r.domain for r in trusted))} domains",
        )
        return state
