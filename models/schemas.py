"""
Pydantic data models for the Universal AI Web Agent V2.
All inter-agent data flows through these schemas.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Planner Models ───────────────────────────────────────

class SubTask(BaseModel):
    """A single step produced by the Planner Agent."""
    id: int = Field(description="Step number")
    description: str = Field(description="What this step should accomplish")
    tool_hint: str = Field(
        default="search",
        description="Suggested tool: search | browse | extract | analyze",
    )
    status: str = Field(default="pending", description="pending | running | done | failed")


class TaskPlan(BaseModel):
    """Execution plan for a user query."""
    goal: str = Field(description="High-level goal extracted from the user query")
    subtasks: list[SubTask] = Field(default_factory=list, description="Ordered steps")


# ── Search Models ────────────────────────────────────────

class SearchResult(BaseModel):
    """A single search-engine hit."""
    title: str = ""
    url: str = ""
    snippet: str = ""
    domain: str = Field(default="", description="Extracted domain name (e.g. amazon.in)")


# ── Extraction Models ───────────────────────────────────

class ExtractedProduct(BaseModel):
    """Structured product / item extracted from a webpage."""
    name: str = Field(default="", description="Product or item name")
    price: Optional[str] = Field(default=None, description="Price as displayed (incl. currency)")
    price_numeric: Optional[float] = Field(default=None, description="Numeric price for comparison")
    currency: str = Field(default="INR", description="Currency code")
    rating: Optional[float] = Field(default=None, description="Rating out of 5")
    review_count: Optional[str] = Field(default=None, description="Number of reviews")
    brand: Optional[str] = Field(default=None, description="Brand name extracted from title or specs")
    storage: Optional[str] = Field(default=None, description="Storage variant (e.g. 128GB)")
    color: Optional[str] = Field(default=None, description="Color variant")
    seller: Optional[str] = Field(default=None, description="Seller name")
    specs: dict = Field(default_factory=dict, description="Key specifications")
    deal_score: Optional[float] = Field(default=None, description="Mathematically computed deal score relative to market")
    deal_tag: Optional[str] = Field(default=None, description="Premium | Average | Best Value | Overpriced")
    sentiment_summary: Optional[str] = Field(default=None, description="LLM-generated one-liner sentiment")
    positive_percentage: Optional[int] = Field(default=None, description="Percentage of positive sentiment")
    negative_percentage: Optional[int] = Field(default=None, description="Percentage of negative sentiment")
    sentiment_indicator: Optional[str] = Field(default=None, description="Sentiment Badge (e.g. Highly Positive)")
    product_url: Optional[str] = Field(default=None, description="Direct link to the product")
    image_url: Optional[str] = Field(default=None, description="Image URL of the product")
    source_url: str = Field(default="", description="URL the data came from")
    source_site: str = Field(default="", description="Website name (e.g. Amazon, Flipkart)")
    screenshot_path: Optional[str] = Field(default=None, description="Path to page screenshot")
    extraction_method: str = Field(default="llm", description="css | llm")


# ── Analysis Models ─────────────────────────────────────

class AnalysisResult(BaseModel):
    """Output of the Ranking Agent."""
    ranked_products: list[ExtractedProduct] = Field(default_factory=list)
    comparison_table: str = Field(default="", description="Markdown table")
    best_pick: str = Field(default="", description="Recommended product name")
    reasoning: str = Field(default="", description="Why the best pick was chosen")
    best_deal_reasons: list[str] = Field(default_factory=list, description="Bullet points explaining why it's the best pick")
    best_deal_metrics: dict = Field(default_factory=dict, description="Scoring breakdown of the best pick")
    price_chart_data: list[dict] = Field(
        default_factory=list,
        description="[{name, price, source}] for chart rendering",
    )


# ── Agent Communication ─────────────────────────────────

class AgentMessage(BaseModel):
    """A log message emitted by any agent for monitoring."""
    agent: str = Field(description="Agent name")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: str = Field(default="info", description="info | warn | error")


# ── Final Output ────────────────────────────────────────

class FinalReport(BaseModel):
    """The final deliverable sent back to the user."""
    summary: str = Field(default="", description="Natural-language summary")
    products: list[ExtractedProduct] = Field(default_factory=list)
    comparison_table: str = Field(default="", description="Markdown comparison table")
    recommendation: str = Field(default="", description="Final recommendation text")
    price_chart_data: list[dict] = Field(default_factory=list, description="Chart data")


# ── API Models ──────────────────────────────────────────

class TaskRequest(BaseModel):
    """Incoming task from the user."""
    query: str = Field(description="User's natural-language task")


class TaskStatus(BaseModel):
    """Status of a running task."""
    task_id: str
    status: str = Field(default="pending", description="pending | running | completed | failed")
    messages: list[AgentMessage] = Field(default_factory=list)
    result: Optional[FinalReport] = None
    error: Optional[str] = None
