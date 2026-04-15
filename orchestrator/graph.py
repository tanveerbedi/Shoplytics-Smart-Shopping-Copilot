"""
LangGraph V2 workflow – 8-node pipeline with domain filtering.

Flow: Planner → Search → Domain Filter → Browser → Extractor → Ranking → Summarizer → END
"""

from __future__ import annotations
import logging
from typing import Literal

from langgraph.graph import StateGraph, END

from orchestrator.state import AgentState
from agents.planner import PlannerAgent
from agents.search import SearchAgent
from agents.domain_filter import DomainFilterAgent
from agents.browser import BrowserAgent
from agents.extractor import ExtractionAgent
from agents.deduplicator import DeduplicationAgent
from agents.sentiment import SentimentAgent
from agents.deal import DealAgent
from agents.analyst import AnalysisAgent
from agents.summarizer import SummaryAgent

logger = logging.getLogger(__name__)

# ── Agent singletons ─────────────────────────────────────
_planner = PlannerAgent()
_searcher = SearchAgent()
_domain_filter = DomainFilterAgent()
_browser = BrowserAgent()
_extractor = ExtractionAgent()
_deduplicator = DeduplicationAgent()
_sentiment = SentimentAgent()
_deal = DealAgent()
_ranker = AnalysisAgent()
_summarizer = SummaryAgent()


# ── Node functions ───────────────────────────────────────

async def plan_node(state: AgentState) -> AgentState:
    return await _planner.run(state)

async def search_node(state: AgentState) -> AgentState:
    return await _searcher.run(state)

async def domain_filter_node(state: AgentState) -> AgentState:
    return await _domain_filter.run(state)

async def browse_node(state: AgentState) -> AgentState:
    return await _browser.run(state)

async def extract_node(state: AgentState) -> AgentState:
    return await _extractor.run(state)

async def deduplicate_node(state: AgentState) -> AgentState:
    return await _deduplicator.run(state)

async def sentiment_node(state: AgentState) -> AgentState:
    return await _sentiment.run(state)

async def deal_node(state: AgentState) -> AgentState:
    return await _deal.run(state)

async def rank_node(state: AgentState) -> AgentState:
    return await _ranker.run(state)

async def summarize_node(state: AgentState) -> AgentState:
    return await _summarizer.run(state)


# ── Conditional edges ────────────────────────────────────

def should_retry_or_deduplicate(state: AgentState) -> Literal["deduplicator", "browser"]:
    """
    After extraction, proceed to deduplicate.
    Removing the browser retry logic to prevent infinite loops when scraping fails.
    """
    return "deduplicator"


# ── Graph builder ────────────────────────────────────────

def build_graph():
    """
    Construct and compile the 10-node LangGraph workflow.

    Pipeline:
    Planner → Search → Domain Filter → Browser → Extractor
        → (conditional) → Deduplicator → Sentiment → Deal → Ranker → Summarizer → END
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", plan_node)
    workflow.add_node("searcher", search_node)
    workflow.add_node("domain_filter", domain_filter_node)
    workflow.add_node("browser", browse_node)
    workflow.add_node("extractor", extract_node)
    workflow.add_node("deduplicator", deduplicate_node)
    workflow.add_node("sentiment", sentiment_node)
    workflow.add_node("deal", deal_node)
    workflow.add_node("ranker", rank_node)
    workflow.add_node("summarizer", summarize_node)

    # Entry point
    workflow.set_entry_point("planner")

    # Linear edges
    workflow.add_edge("planner", "searcher")
    workflow.add_edge("searcher", "domain_filter")
    workflow.add_edge("domain_filter", "browser")
    workflow.add_edge("browser", "extractor")

    # Conditional: after extraction, deduplicate or retry
    workflow.add_conditional_edges(
        "extractor",
        should_retry_or_deduplicate,
        {"deduplicator": "deduplicator", "browser": "browser"},
    )

    workflow.add_edge("deduplicator", "sentiment")
    workflow.add_edge("sentiment", "deal")
    workflow.add_edge("deal", "ranker")
    workflow.add_edge("ranker", "summarizer")
    workflow.add_edge("summarizer", END)

    return workflow.compile()


# Pre-built graph instance
agent_graph = build_graph()
