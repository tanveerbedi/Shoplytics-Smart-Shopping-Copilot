"""
Universal AI Web Agent V3 – Streamlit Premium Dashboard

Premium UI with:
• Glassmorphism dark theme
• 3-pane layout (Control, Console, Analytics)
• Agent progress visualization
• Interactive Plotly charts
• Browser Screenshots gallery
"""

import time
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Shoplytics – AI-Powered Product Intelligence & Smart Shopping Copilot",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-main: #06080F;
        --bg-panel: rgba(16, 20, 28, 0.7);
        --bg-card: rgba(22, 28, 40, 0.8);
        --accent-primary: #8a2be2;
        --accent-secondary: #00FF9D;
        --accent-glow: rgba(138, 43, 226, 0.4);
        --text-main: #F1F5F9;
        --text-muted: #94A3B8;
        --border-color: rgba(255, 255, 255, 0.08);
    }
    
    html, body, [class*="st-"] { 
        font-family: 'Inter', sans-serif; 
    }
    
    /* Background Override for App */
    .stApp {
        background-color: var(--bg-main);
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(138, 43, 226, 0.05), transparent 25%),
            radial-gradient(circle at 85% 30%, rgba(0, 255, 157, 0.03), transparent 25%);
    }

    /* Top Nav Bar */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background: var(--bg-panel);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-bottom: 1px solid var(--border-color);
        margin-top: -3rem;
        margin-bottom: 2rem;
        border-radius: 0 0 24px 24px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    .logo-container {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .logo-text {
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #FFFFFF 0%, var(--accent-secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .status-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(0, 255, 157, 0.1);
        border: 1px solid rgba(0, 255, 157, 0.2);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        color: var(--accent-secondary);
        font-weight: 500;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: var(--accent-secondary);
        border-radius: 50%;
        box-shadow: 0 0 10px var(--accent-secondary);
        animation: pulse-dot 2s infinite;
    }
    
    @keyframes pulse-dot {
        0% { box-shadow: 0 0 0 0 rgba(0, 255, 157, 0.6); }
        70% { box-shadow: 0 0 0 8px rgba(0, 255, 157, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 255, 157, 0); }
    }

    /* Agent Log Console */
    .agent-console {
        background: #090B10;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.2rem;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.8rem;
        line-height: 1.7;
        height: 400px;
        overflow-y: auto;
        color: var(--text-muted);
        box-shadow: inset 0 2px 20px rgba(0,0,0,0.5);
    }
    .agent-console .agent-name { color: var(--accent-primary); font-weight: 600; text-shadow: 0 0 8px rgba(138,43,226,0.3); }
    .agent-console .info { color: #58a6ff; }
    .agent-console .warn { color: #d29922; }
    .agent-console .error { color: #ff4444; }

    /* Pipeline Nodes */
    .pipeline-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 1.5rem;
        padding: 1rem;
        background: var(--bg-card);
        border-radius: 16px;
        border: 1px solid var(--border-color);
    }
    .pipeline-node {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 12px 18px;
        background: rgba(10, 12, 18, 0.6);
        border: 1px solid transparent;
        border-radius: 12px;
        color: var(--text-muted);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-weight: 500;
        font-size: 0.95rem;
    }
    .pipeline-node.active {
        background: rgba(138, 43, 226, 0.15);
        border-color: var(--accent-primary);
        color: white;
        box-shadow: 0 0 20px rgba(138,43,226,0.2);
        transform: translateX(5px);
    }
    .pipeline-node.done {
        border-left: 3px solid var(--accent-secondary);
        color: var(--text-main);
    }
    .node-icon {
        font-size: 1.3rem;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
    }
    
    /* Stats Row Container */
    .stats-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Best Value Card */
    .deal-card {
        background: linear-gradient(135deg, rgba(30,36,44,0.8) 0%, rgba(18,22,28,0.9) 100%);
        border: 1px solid rgba(0, 255, 157, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
        flex: 1;
        box-shadow: 0 8px 32px rgba(0, 255, 157, 0.05);
    }
    .deal-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 100%; height: 3px;
        background: linear-gradient(90deg, var(--accent-secondary), #00A3FF);
    }
    
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        flex: 1;
        text-align: center;
    }
    
    .metric-value { font-size: 2.2rem; font-weight: 700; color: white; letter-spacing: -1px; margin-bottom: 0.2rem;}
    .metric-label { font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; font-weight: 600;}
    
    .deal-title { font-size: 0.85rem; color: var(--accent-secondary); text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 0.8rem;}
    .deal-productName { font-size: 1.2rem; font-weight: 600; color: white; margin-bottom: 0.5rem; line-height: 1.3;}
    .deal-price { font-size: 1.8rem; font-weight: 700; color: var(--accent-secondary); }
    .deal-store { font-size: 0.9rem; color: var(--text-muted); }

    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Inputs Overrides */
    div[data-baseweb="input"] {
        background-color: #0D1117 !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 1px var(--accent-primary) !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Configuration ────────────────────────────────────────
API_BASE = "http://localhost:8000"

PIPELINE_STEPS = [
    ("📋", "Planner", "planning"),
    ("🔍", "Search", "searching"),
    ("🔗", "Filter", "filtering"),
    ("🌐", "Browser", "browsing"),
    ("🔬", "Extractor", "extracting"),
    ("🧬", "Deduplicate", "deduplicating"),
    ("🤖", "Sentiment", "sentiment"),
    ("⚖️", "Deal Match", "deal_detection"),
    ("📈", "Ranking", "ranking"),
    ("📝", "Summary", "summarizing"),
]

# ── Top Navigation ───────────────────────────────────────
st.markdown("""
<div class="top-nav">
    <div class="logo-container">
        <span style="font-size: 1.8rem;">⚡</span>
        <span class="logo-text" style="display:flex; flex-direction:column; line-height: 1;">
            Shoplytics
            <span style="font-size: 0.75rem; font-weight: 500; color: #94A3B8; margin-top:2px;">AI-Powered Product Intelligence & Smart Shopping Copilot</span>
        </span>
    </div>
    <div class="status-badge">
        <div class="status-dot"></div>
        System Online
    </div>
</div>
""", unsafe_allow_html=True)

# ── State ────────────────────────────────────────────────
for key, default in [
    ("task_id", None), ("task_status", None),
    ("task_messages", []), ("task_result", None),
    ("query_input", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── API Polling ──────────────────────────────────────────
if st.session_state.task_id:
    try:
        resp = requests.get(f"{API_BASE}/api/task/{st.session_state.task_id}", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.task_status = data["status"]
            st.session_state.task_messages = data.get("messages", [])
            st.session_state.task_result = data.get("result")
    except Exception:
        pass

# ── Actions ──────────────────────────────────────────────
def run_query(q):
    if not q.strip(): return
    try:
        resp = requests.post(f"{API_BASE}/api/task", json={"query": q.strip()}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        st.session_state.task_id = data["task_id"]
        st.session_state.task_status = "pending"
        st.session_state.task_messages = []
        st.session_state.task_result = None
    except Exception as e:
        st.error(f"Failed to start task: {e}")

# ── Helper to find current step ───────────────────────────
status = st.session_state.task_status
current_step_id = None

for msg in reversed(st.session_state.task_messages):
    agent = msg.get("agent", "").lower() if isinstance(msg, dict) else ""
    content = msg.get("content", "").lower() if isinstance(msg, dict) else ""
    for _, _, step_id in PIPELINE_STEPS:
        if step_id in content or step_id in agent:
            current_step_id = step_id
            break
    if current_step_id:
        break

# Map steps to index
step_idx = -1
for i, (_, _, sid) in enumerate(PIPELINE_STEPS):
    if sid == current_step_id:
        step_idx = i
        break
if status == "completed":
    step_idx = len(PIPELINE_STEPS)

# ── Layout: 3 Columns ────────────────────────────────────
# Left: Controls & Pipeline (20%)
# Center: Log & Browser (30%)
# Right: Analytics & Data (50%)
col_left, col_center, col_right = st.columns([1, 1.3, 2.2], gap="large")

with col_left:
    st.markdown("### 🎯 Command Input")
    
    with st.form(key="search_form", clear_on_submit=False):
        q = st.text_input(
            "Query",
            placeholder="E.g. Find best 4K TVs under ₹40000",
            label_visibility="collapsed",
            value=st.session_state.query_input
        )
        submitted = st.form_submit_button("🚀 Launch Scraper Agents", use_container_width=True)
        if submitted and q:
            run_query(q)
            st.rerun()
            
    # Sample Suggestions
    st.markdown("<p style='font-size: 0.8rem; color: #94A3B8; margin-top: 10px; margin-bottom: 5px;'>SUGGESTED</p>", unsafe_allow_html=True)
    if st.button("Compare iPhone 15 prices"):
        st.session_state.query_input = "Compare iPhone 15 prices across stores"
        st.rerun()
    if st.button("Sony Noise Cancelling Headphones"):
        st.session_state.query_input = "Best Sony noise cancelling headphones deals"
        st.rerun()

    st.markdown("<br>### ⚡ Execution Pipeline", unsafe_allow_html=True)
    
    # Render Pipeline Nodes
    nodes_html = '<div class="pipeline-container">'
    for i, (emoji, name, sid) in enumerate(PIPELINE_STEPS):
        cls = ""
        if status == "completed" or i < step_idx:
            cls = "done"
        elif i == step_idx:
            cls = "active"
        nodes_html += f'''
        <div class="pipeline-node {cls}">
            <div class="node-icon">{emoji}</div>
            {name}
        </div>
        '''
    nodes_html += '</div>'
    st.html(nodes_html)

with col_center:
    st.markdown("### 🖥️ Agent Terminal")
    
    messages = st.session_state.task_messages
    if messages:
        lines = []
        for msg in messages:
            agent = msg.get("agent", "system") if isinstance(msg, dict) else "system"
            content = msg.get("content", "") if isinstance(msg, dict) else ""
            level = msg.get("level", "info") if isinstance(msg, dict) else "info"
            lines.append(
                f'<span class="agent-name">[{agent.upper()}]</span> '
                f'<span class="{level}">{content}</span>'
            )
        st.markdown(f'<div class="agent-console">{"<br>".join(lines)}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="agent-console" style="display:flex;align-items:center;justify-content:center;">Awaiting orders...</div>', unsafe_allow_html=True)

    st.markdown("<br>### 🧠 AI Decision Intelligence", unsafe_allow_html=True)
    
    if status in ("pending", "running"):
        st.info("AI is gathering and analyzing market data to formulate a recommendation...")
        
    elif status == "completed" and st.session_state.task_result:
        res = st.session_state.task_result
        
        # Safely handle both dict and object types
        if isinstance(res, dict):
            prods = res.get("products", [])
            chart_data = res.get("price_chart_data", [])
            summary = res.get("summary", "")
            recommendation = res.get("recommendation", "")
            metrics = res.get("best_deal_metrics", {})
            reasons = res.get("best_deal_reasons", [])
        else:
            prods = getattr(res, "products", [])
            chart_data = getattr(res, "price_chart_data", [])
            summary = getattr(res, "summary", "")
            recommendation = getattr(res, "recommendation", "")
            
            # Extract metrics safely from Pydantic model
            if hasattr(res, "model_dump"):
                dump = res.model_dump()
                metrics = dump.get("best_deal_metrics", {})
                reasons = dump.get("best_deal_reasons", [])
            else:
                metrics = getattr(res, "best_deal_metrics", {})
                reasons = getattr(res, "best_deal_reasons", [])
                
        if prods and chart_data:
             # AI Reason Block
             st.markdown("#### 💡 Why this recommendation?")
             if recommendation:
                 st.write(recommendation)
             elif summary:
                 st.write(summary)
                 
             if reasons:
                 for r in reasons:
                     st.markdown(f"✅ **{r}**")
             
             # Metric breakdown chart
             if metrics and sum(metrics.values()) > 0:
                 st.markdown("#### ⚖️ Decision Factors")
                 # Convert metrics dict to dataframe for plotting
                 m_df = pd.DataFrame([
                     {"Factor": "Price", "Score": metrics.get("price_score", 0)},
                     {"Factor": "Rating", "Score": metrics.get("rating_score", 0)},
                     {"Factor": "Brand", "Score": metrics.get("brand_score", 0)},
                     {"Factor": "Store Trust", "Score": metrics.get("trust_score", 0)}
                 ])
                 
                 fig_metrics = px.bar(
                     m_df,
                     x="Score", y="Factor",
                     orientation="h",
                     color="Factor",
                     title="Weighted Scoring Breakdown",
                     template="plotly_dark",
                     height=250
                 )
                 fig_metrics.update_layout(
                     margin=dict(l=0, r=0, t=30, b=0), 
                     paper_bgcolor='rgba(0,0,0,0)', 
                     plot_bgcolor='rgba(0,0,0,0)',
                     showlegend=False
                 )
                 st.plotly_chart(fig_metrics, use_container_width=True)
        else:
            st.warning("Analysis completed, but no products met the criteria.")
    else:
        st.info("AI Reasoning will appear here after analysis completes.")

with col_right:
    st.markdown("### 📊 Market Intelligence")
    
    result = st.session_state.task_result
    
    if status == "running" or status == "pending":
        st.info("Gathering and analyzing data... Please wait.")
        
    elif status == "failed":
        st.error("Task failed to execute.")
        
    elif status == "completed" and result:
        # Prepare Data
        if isinstance(result, dict):
            products = result.get("products", [])
            chart_data = result.get("price_chart_data", [])
        else:
            products = result.products
            chart_data = result.price_chart_data
            
        df = pd.DataFrame(chart_data)
        
        # Display Top KPI Cards
        total_products = len(products)
        avg_price = df["price"].mean() if not df.empty and "price" in df.columns else 0
        best_deal = df.loc[df["score"].idxmax()] if not df.empty and "score" in df.columns else None

        if not df.empty and "source" in df.columns:
            # Clean source names
            def n_source(s):
                p = [x.strip().lower() for x in str(s).split(",")]
                out = []
                for x in p:
                    if "amazon" in x: out.append("Amazon")
                    elif "flipkart" in x: out.append("Flipkart")
                    elif "croma" in x: out.append("Croma")
                    elif "reliance" in x: out.append("Reliance Digital")
                    elif "vijay" in x: out.append("Vijay Sales")
                    else: out.append(x.title())
                return ", ".join(list(dict.fromkeys(out)))
            df["source_clean"] = df["source"].apply(n_source)
        
        # Build Stats HTML
        if best_deal is not None:
            stats_html = f'''
            <div class="stats-row">
                <div class="deal-card">
                    <div class="deal-title">🏆 Top Recommendation</div>
                    <div class="deal-productName">{best_deal["name"][:50]}...</div>
                    <div class="deal-price">₹{best_deal["price"]:,.0f}</div>
                    <div class="deal-store">Found at {best_deal.get("source_clean", "Store")} • Score: {best_deal["score"]}/100</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{total_products}</div>
                    <div class="metric-label">Items Analyzed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">₹{avg_price:,.0f}</div>
                    <div class="metric-label">Market Average</div>
                </div>
            </div>
            '''
            st.markdown(stats_html, unsafe_allow_html=True)
            
        # Plotly Charts
        if not df.empty and "price" in df.columns:
            c1, c2 = st.columns(2)
            with c1:
                # Scatter or Bar Chart for Price spread
                fig = px.bar(
                    df.head(8),
                    x="price", y="source_clean",
                    color="score",
                    orientation="h",
                    title="Price vs Store (Top 8)",
                    color_continuous_scale="Viridis",
                    template="plotly_dark",
                    height=300
                )
                fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                # Store Comparison Box plot or Bar
                store_avg = df.groupby("source_clean")["price"].mean().reset_index()
                fig2 = px.pie(
                    store_avg,
                    values="price",
                    names="source_clean",
                    title="Average Price per Store",
                    hole=0.4,
                    template="plotly_dark",
                    height=300
                )
                fig2.update_traces(textposition='inside', textinfo='percent+label')
                fig2.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### 📋 Product Database")
        
        # Stylized Dataframe
        if not df.empty:
            display_cols = ["image_url", "name", "price", "source_clean", "score", "deal_tag", "rating", "sentiment_indicator", "positive_percentage", "link"]
            existing_cols = []
            
            # Add explicit HTML links to names instead of markdown
            if "name" in df.columns and "product_url" in df.columns:
                df["link"] = df["product_url"].apply(
                    lambda url: f'<a href="{url}" target="_blank" style="padding: 4px 8px; background: rgba(0, 255, 157, 0.2); border-radius: 4px; color: #00FF9D; text-decoration: none; font-weight: 500; font-size: 12px;">View</a>' 
                    if pd.notnull(url) and str(url).strip() != "" else ""
                )
                  
                df["name"] = df.apply(
                    lambda row: f'<a href="{row["product_url"]}" target="_blank" style="color: #58a6ff; text-decoration: none; font-weight: 500;">{row["name"]}</a>' 
                    if pd.notnull(row["product_url"]) and str(row["product_url"]).strip() != "" else row["name"], 
                    axis=1
                )
                
            # Convert image_url to an actual HTML img tag
            if "image_url" in df.columns:
                df["image_url"] = df["image_url"].apply(
                    lambda url: f'<img src="{url}" height="50" style="border-radius:4px; object-fit: cover;">' 
                    if pd.notnull(url) and str(url).strip() not in ["", "None"] else ""
                )
                
            existing_cols = [c for c in display_cols if c in df.columns]

            ddf = df[existing_cols].copy()
            ddf = ddf.rename(columns={
                "image_url": "Image",
                "name": "Product Name",
                "price": "Price (₹)",
                "source_clean": "Store",
                "score": "Score",
                "deal_tag": "Deal",
                "rating": "Rating",
                "sentiment_indicator": "Sentiment",
                "positive_percentage": "Positivity",
                "link": "Link"
            })
            
            st.write(
                ddf.to_html(escape=False, index=False),
                unsafe_allow_html=True
            )
                        
    else:
        st.info("Results and charts will populate here after the Agent completes its execution.")

# Autorefresh when running
if status in ("pending", "running"):
    time.sleep(1.5)
    st.rerun()
