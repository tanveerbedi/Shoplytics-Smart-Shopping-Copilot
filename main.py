"""
Universal AI Web Agent – FastAPI Application Entry Point.

Run with: uvicorn main:app --reload --port 8000
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api.routes import router

# ── Logging ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)-20s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("web_agent")


# ── Lifespan (startup / shutdown) ────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("🚀 Universal AI Web Agent starting up...")
    logger.info("   LLM Provider : %s", settings.llm_provider)
    logger.info("   LLM Model    : %s", 
                settings.gemini_model if settings.llm_provider == "gemini" 
                else settings.ollama_model)
    logger.info("   Headless      : %s", settings.playwright_headless)

    # Install Playwright browsers if needed
    try:
        import subprocess
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True,
        )
        logger.info("   Playwright   : ✅ Chromium ready")
    except Exception as exc:
        logger.warning("   Playwright   : ⚠️ Browser install skipped (%s)", exc)

    yield  # App is running

    logger.info("👋 Shutting down...")


# ── FastAPI App ──────────────────────────────────────────

app = FastAPI(
    title="Universal AI Web Agent",
    description="Autonomous multi-agent system for internet research tasks",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS – allow Streamlit and other frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(router)


# ── Direct run ───────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
