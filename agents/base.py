"""
Base agent abstract class.
Every agent implements `run(state) -> state`.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from orchestrator.state import AgentState


class BaseAgent(ABC):
    """Abstract base for all agents in the pipeline."""

    name: str = "base"

    def __init__(self) -> None:
        self.logger = logging.getLogger(f"agent.{self.name}")

    @abstractmethod
    async def run(self, state: AgentState) -> AgentState:
        """
        Execute the agent's logic.

        Args:
            state: Current pipeline state.

        Returns:
            Updated pipeline state.
        """
        ...

    def _add_message(
        self, state: AgentState, content: str, level: str = "info"
    ) -> None:
        """Append a log message to the state's message list."""
        from models.schemas import AgentMessage

        state["messages"].append(
            AgentMessage(agent=self.name, content=content, level=level)
        )
