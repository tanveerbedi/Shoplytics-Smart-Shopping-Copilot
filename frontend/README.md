# Shoplytics — React Frontend

AI-Powered Product Intelligence & Smart Shopping Copilot.

Cyberpunk terminal dashboard built with React 18, Vite, TailwindCSS, Zustand, and Framer Motion.

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Start the dev server (proxies API to FastAPI on :8000)
npm run dev

# 3. Open http://localhost:5173
```

## Prerequisites

- **Node.js** 18+
- **FastAPI backend** running on `http://localhost:8000`

Start the backend first:
```bash
cd ..
python main.py
# or: uvicorn main:app --port 8000
```

## Architecture

```
src/
├── api/client.js              # Axios + WebSocket URL builder
├── store/useShoplyticsStore.js # Zustand global state
├── hooks/
│   ├── useLogStream.js        # WebSocket → live agent logs
│   └── usePipeline.js         # Task creation + polling fallback
├── components/
│   ├── shared/                # StatusDot, GlowButton, Header
│   ├── CommandPanel/          # QueryInput, SuggestedQueries, ExecutionPipeline
│   ├── AgentTerminal/         # LogStream, LogLine, AIDecisionBox
│   └── MarketIntelligence/    # PriceTable, ProductRow, RecommendationCard
├── App.jsx                    # 3-panel layout shell
├── main.jsx                   # React entry point
└── index.css                  # Tailwind + custom terminal CSS
```

## API Endpoints (FastAPI Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/task` | Create a new scraping task |
| GET | `/api/task/{id}` | Get task status + results |
| WS | `/ws/task/{id}` | Stream live agent logs |
| GET | `/health` | Health check |

## Design Tokens

- **Background**: `#0a0a0f` (main), `#0f0f17` (panel), `#1a1a2e` (border)
- **Accent**: `#00f5ff` (cyan), `#39ff14` (green), `#ffb800` (amber), `#ff3131` (red)
- **Fonts**: JetBrains Mono (terminal), Syne (headings)

## Build for Production

```bash
npm run build
npm run preview
```
