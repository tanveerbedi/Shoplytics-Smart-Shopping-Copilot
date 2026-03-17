"""
Central configuration for the Universal AI Web Agent.
Reads from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── LLM ──────────────────────────────────────────
    llm_provider: Literal["groq", "gemini", "ollama"] = Field(
        default="groq", description="Which LLM backend to use"
    )

    # Groq (free, fast inference)
    groq_api_key: str = Field(default="", description="Groq API key")
    groq_model: str = Field(default="llama-3.3-70b-versatile", description="Groq model name")

    # Gemini (backup)
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-2.0-flash", description="Gemini model name")

    # Ollama
    ollama_base_url: str = Field(
        default="http://localhost:11434", description="Ollama server URL"
    )
    ollama_model: str = Field(default="llama3", description="Ollama model name")

    # ── Search ───────────────────────────────────────
    serper_api_key: str = Field(default="", description="Serper.dev API key")

    # ── Browser ──────────────────────────────────────
    playwright_headless: bool = Field(
        default=True, description="Run Playwright in headless mode"
    )
    max_browser_pages: int = Field(
        default=3, description="Max concurrent browser pages"
    )

    # ── Server ───────────────────────────────────────
    api_host: str = Field(default="0.0.0.0", description="API listen host")
    api_port: int = Field(default=8000, description="API listen port")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# Singleton settings instance
settings = Settings()
