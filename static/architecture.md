# Architecture Deep-Dive

## Agent Interaction Flow

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI
    participant P as Planner
    participant S as Search Agent
    participant B as Browser Agent
    participant E as Extractor
    participant A as Analyst
    participant SM as Summarizer

    U->>API: POST /api/task {"query": "..."}
    API-->>U: {"task_id": "abc123"}
    
    API->>P: Analyze query
    P->>P: LLM: decompose into subtasks
    P-->>API: TaskPlan (3-5 steps)
    
    API->>S: Execute search subtasks
    S->>S: Serper API calls
    S-->>API: SearchResult[] (URLs + snippets)
    
    API->>B: Visit top URLs
    B->>B: Playwright/httpx fetch
    B-->>API: Raw page content[]
    
    API->>E: Extract structured data
    E->>E: LLM: parse products from text
    E-->>API: ExtractedProduct[]
    
    alt No products found
        API->>B: Retry with more URLs
        B-->>API: More page content
        API->>E: Re-extract
        E-->>API: ExtractedProduct[]
    end
    
    API->>A: Compare & rank
    A->>A: LLM: analysis + comparison table
    A-->>API: AnalysisResult
    
    API->>SM: Generate report
    SM->>SM: LLM: natural-language summary
    SM-->>API: FinalReport
    
    API-->>U: GET /api/task/{id} → results
```

---

## Prompt Templates

### Planner Prompt
```
You are a planning agent for an autonomous web research system.
Given a user's task, create a step-by-step execution plan.

Available tools: search, browse, extract, analyze

Rules:
1. Limit to 3-5 steps maximum
2. Start with search steps
3. End with an analyze step
4. Be specific about what data to extract

User's task: {query}
→ Outputs JSON: TaskPlan
```

### Extraction Prompt
```
Extract ALL relevant products/items from this webpage text.
Provide: name, price (numeric + display), currency, rating, specs, source.

Rules:
1. Only extract EXPLICITLY stated data (no guessing)
2. Null for unavailable fields
3. Return empty list if no products found

Webpage text: {content}
→ Outputs JSON: ExtractedProduct[]
```

### Analysis Prompt
```
Rank products by value-for-money, features, and ratings.
Create a Markdown comparison table.
Select best pick with reasoning.

Products: {products_json}
Original query: {query}
→ Outputs JSON: AnalysisResult
```

---

## Monitoring Dashboard Design

The Streamlit dashboard provides:

| Panel | Content |
|-------|---------|
| **Agent Activity Log** | Real-time stream of emoji-tagged messages from each agent |
| **Status Badge** | Visual pending → running → completed/failed status |
| **Comparison Table** | Markdown table of ranked products |
| **Recommendation Card** | Highlighted best-pick with reasoning |
| **Raw Data Expander** | Collapsible view of all extracted products |

### WebSocket Protocol

Messages sent over `ws://localhost:8000/ws/task/{id}`:

```json
{"type": "message", "agent": "search", "content": "🔍 Searching...", "level": "info"}
{"type": "status", "status": "running"}
{"type": "result", "data": {"summary": "...", "comparison_table": "...", ...}}
```

---

## Error Handling Philosophy

```mermaid
graph LR
    A[Operation] --> B{Success?}
    B -->|Yes| C[Continue Pipeline]
    B -->|No| D{Retries Left?}
    D -->|Yes| E[Exponential Backoff]
    E --> A
    D -->|No| F{Has Fallback?}
    F -->|Yes| G[Use Fallback]
    G --> C
    F -->|No| H[Partial Result + Error Note]
    H --> C
```

**Key principle:** Never completely fail. Always return *something* useful, even if partial.

---

## Performance Considerations

| Area | Optimization |
|------|-------------|
| **Search** | Parallel Serper calls for multiple subtasks |
| **Browsing** | Configurable `MAX_BROWSER_PAGES` to limit concurrent Playwright instances |
| **Extraction** | Text truncation to 10K chars prevents context overflow |
| **LLM Calls** | Temperature 0.0–0.1 for extraction (factual) and 0.3 for summarization (creative) |
| **Anti-Bot** | Random user-agents + delays between page visits |
