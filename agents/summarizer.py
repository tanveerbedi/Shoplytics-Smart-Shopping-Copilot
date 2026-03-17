"""
Summary Agent V2 – produces a rich final report with chart data.
"""

from __future__ import annotations
import json
import logging
from typing import TYPE_CHECKING

from agents.base import BaseAgent
from models.schemas import FinalReport
from utils.llm import get_llm
from utils.helpers import extract_json_from_text

if TYPE_CHECKING:
    from orchestrator.state import AgentState

logger = logging.getLogger(__name__)

SUMMARY_PROMPT = """You are a helpful AI Shopping Copilot. Write a clear, professional synthesis.

User's question: {query}

Analysis results:
- Products compared: {num_products}
- Best pick: {best_pick}
- Reasoning: {reasoning}
- Comparison table:
{comparison_table}

Write a response that directly answers the user's question.

Respond with ONLY a JSON object:
{{
  "summary": "A 2-3 paragraph summary focusing on overall market landscape and price variance...",
  "recommendation": "Your final AI Copilot Recommendations formatted cleanly in markdown highlighting: 1) Best Value Product, 2) Cheapest Option, 3) Best Rated Option."
}}
"""


class SummaryAgent(BaseAgent):
    """Produces the final human-friendly report with chart data."""

    name = "summarizer"

    async def run(self, state: AgentState) -> AgentState:
        state["current_step"] = "summarizing"
        analysis = state.get("analysis")

        if not analysis:
            self._add_message(state, "❌ No analysis to summarize", level="error")
            state["final_report"] = FinalReport(
                summary="Unable to generate a report – no analysis data available.",
                recommendation="Please try again with a different query.",
            )
            return state

        self._add_message(state, "📝 Generating final report...")

        # Build report
        try:
            llm = get_llm(temperature=0.3)
            prompt = SUMMARY_PROMPT.format(
                query=state["query"],
                best_pick=analysis.best_pick,
                reasoning=analysis.reasoning,
                comparison_table=analysis.comparison_table,
                num_products=len(analysis.ranked_products),
            )

            response = await llm.ainvoke(prompt)
            raw = response.content if hasattr(response, "content") else str(response)
            json_str = extract_json_from_text(raw)
            data = json.loads(json_str)

            report = FinalReport(
                summary=data.get("summary", ""),
                products=analysis.ranked_products,
                comparison_table=analysis.comparison_table,
                recommendation=data.get("recommendation", analysis.reasoning),
                price_chart_data=analysis.price_chart_data,
            )

        except Exception as exc:
            self.logger.error("Summary generation failed: %s", exc)
            self._add_message(state, f"⚠️ LLM summary failed: {exc}", level="warn")

            # Fallback
            report = FinalReport(
                summary=(
                    f"Based on searching across multiple e-commerce sites for "
                    f"\"{state['query']}\", we found {len(analysis.ranked_products)} options. "
                    f"The top overall pick is **{analysis.best_pick}**."
                ),
                products=analysis.ranked_products,
                comparison_table=analysis.comparison_table,
                recommendation=f"**Best Value & Top Pick:** {analysis.best_pick}\n\n{analysis.reasoning}",
                price_chart_data=analysis.price_chart_data,
            )

        state["final_report"] = report
        self._add_message(state, "✅ Final report generated!")
        return state
