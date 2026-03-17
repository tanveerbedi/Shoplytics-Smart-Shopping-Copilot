"""
Planner Agent – breaks a user query into an actionable execution plan.

Uses an LLM to analyze the query and produce a structured TaskPlan
containing ordered subtasks with tool hints.
"""

from __future__ import annotations
import json
import logging
from typing import TYPE_CHECKING

from agents.base import BaseAgent
from models.schemas import TaskPlan, SubTask
from utils.llm import get_llm
from utils.helpers import extract_json_from_text

if TYPE_CHECKING:
    from orchestrator.state import AgentState

logger = logging.getLogger(__name__)

PLANNER_PROMPT = """You are a planning agent for an autonomous web research system.

Given a user's task, create a step-by-step execution plan. Each step should be a concrete action.

Available tools for steps:
- "search": Search the internet for information
- "browse": Visit a specific website to extract data
- "extract": Extract structured data from page content
- "analyze": Compare and rank collected results

Rules:
1. Limit the plan to 3-5 steps maximum.
2. Start with search steps to find relevant URLs.
3. Follow with browse/extract steps for the most promising results.
4. End with an analyze step to compare findings.
5. Be specific about what to search for and what data to extract.

Respond with ONLY a JSON object matching this schema:
{{
  "goal": "High-level description of what the user wants",
  "subtasks": [
    {{
      "id": 1,
      "description": "Specific action description",
      "tool_hint": "search|browse|extract|analyze",
      "status": "pending"
    }}
  ]
}}

User's task: {query}
"""


class PlannerAgent(BaseAgent):
    """Decomposes a user query into subtasks for the pipeline."""

    name = "planner"

    async def run(self, state: AgentState) -> AgentState:
        state["current_step"] = "planning"
        self._add_message(state, f"📋 Planning task: {state['query']}")

        llm = get_llm(temperature=0.1)
        prompt = PLANNER_PROMPT.format(query=state["query"])

        try:
            response = await llm.ainvoke(prompt)
            raw_text = response.content if hasattr(response, "content") else str(response)
            json_str = extract_json_from_text(raw_text)
            plan_data = json.loads(json_str)
            plan = TaskPlan(**plan_data)

            # Cap subtasks at 5
            if len(plan.subtasks) > 5:
                plan.subtasks = plan.subtasks[:5]

            state["plan"] = plan
            self._add_message(
                state,
                f"✅ Plan created with {len(plan.subtasks)} steps: {plan.goal}",
            )
            self.logger.info("Plan: %s", plan.model_dump_json(indent=2))

        except Exception as exc:
            self.logger.error("Planning failed: %s", exc)
            self._add_message(state, f"❌ Planning failed: {exc}", level="error")

            # Fallback: create a generic plan
            state["plan"] = TaskPlan(
                goal=state["query"],
                subtasks=[
                    SubTask(id=1, description=f"Search for: {state['query']}", tool_hint="search"),
                    SubTask(id=2, description="Browse top results", tool_hint="browse"),
                    SubTask(id=3, description="Extract key information", tool_hint="extract"),
                    SubTask(id=4, description="Analyze and compare findings", tool_hint="analyze"),
                ],
            )
            self._add_message(state, "⚠️ Using fallback generic plan", level="warn")

        return state
