"""
LLM client factory – returns a LangChain chat model based on config.
Supports Groq (free, fast), Google Gemini (cloud), and Ollama (local).
"""

from langchain_core.language_models.chat_models import BaseChatModel
from config import settings


def get_llm(temperature: float = 0.2) -> BaseChatModel:
    """
    Instantiate and return the configured LLM.
    
    Priority: groq (default, free) → gemini → ollama
    
    Returns:
        A LangChain-compatible chat model.
    """
    if settings.llm_provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=temperature,
        )

    elif settings.llm_provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=temperature,
            convert_system_message_to_human=True,
        )

    elif settings.llm_provider == "ollama":
        from langchain_community.chat_models import ChatOllama

        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=temperature,
        )

    else:
        raise ValueError(
            f"Unknown LLM provider: {settings.llm_provider!r}. "
            "Set LLM_PROVIDER to 'groq', 'gemini', or 'ollama'."
        )
