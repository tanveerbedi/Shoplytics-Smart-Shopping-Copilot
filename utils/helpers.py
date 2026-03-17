"""
Shared utility functions: retry logic, text cleaning, truncation.
"""

import asyncio
import re
import logging
from typing import TypeVar, Callable, Any

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ── Retry ────────────────────────────────────────────────

async def retry_async(
    fn: Callable[..., Any],
    *args: Any,
    max_retries: int = 3,
    base_delay: float = 1.0,
    **kwargs: Any,
) -> Any:
    """
    Retry an async function with exponential backoff.
    
    Args:
        fn: Async callable to retry.
        max_retries: Maximum number of attempts.
        base_delay: Starting delay in seconds (doubles each retry).
    
    Returns:
        The result of a successful call.
    
    Raises:
        The last exception if all retries fail.
    """
    last_exception = None
    for attempt in range(max_retries):
        try:
            return await fn(*args, **kwargs)
        except Exception as exc:
            last_exception = exc
            delay = base_delay * (2 ** attempt)
            logger.warning(
                "Retry %d/%d for %s failed: %s – waiting %.1fs",
                attempt + 1,
                max_retries,
                fn.__name__,
                exc,
                delay,
            )
            await asyncio.sleep(delay)
    raise last_exception  # type: ignore[misc]


# ── Text Cleaning ────────────────────────────────────────

def clean_text(html: str) -> str:
    """
    Strip HTML tags, scripts, and styles; normalize whitespace.
    
    Args:
        html: Raw HTML string.
    
    Returns:
        Clean plain text.
    """
    soup = BeautifulSoup(html, "lxml")

    # Remove script and style elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def truncate(text: str, max_chars: int = 12000) -> str:
    """
    Truncate text to fit within an LLM context window.
    
    Args:
        text: Input string.
        max_chars: Maximum character count.
    
    Returns:
        Truncated string with ellipsis if shortened.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n... [truncated]"


def extract_json_from_text(text: str) -> str:
    """
    Extract the first JSON object or array from LLM output that may
    contain markdown code fences or other text.
    """
    # Try to find a JSON code block
    match = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?```", text)
    if match:
        return match.group(1).strip()

    # Try to find raw JSON (object or array)
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    if match:
        return match.group(1).strip()

    return text.strip()
