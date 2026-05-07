import streamlit as st
import time
from langchain_core.messages import HumanMessage
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Purdue Research Intelligence",
    page_icon="🚂",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Purdue CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=Source+Sans+3:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Variables ── */
:root {
    --gold:        #CFB991;
    --gold-light:  #E8D5A3;
    --gold-dark:   #9E8049;
    --black:       #1C1C1C;
    --surface:     #222222;
    --surface2:    #2A2A2A;
    --border:      rgba(207,185,145,0.18);
    --border-h:    rgba(207,185,145,0.45);
    --text:        #F0EBE0;
    --muted:       #8A8070;
    --green:       #7EC8A4;
    --red:         #E07070;
}

/* ── Reset ── */
html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    color: var(--text);
}

.stApp {
    background-color: var(--black);
    background-image:
        radial-gradient(ellipse 100% 60% at 50% -20%, rgba(207,185,145,0.07) 0%, transparent 65%),
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 79px,
            rgba(207,185,145,0.03) 80px
        ),
        repeating-linear-gradient(
            90deg,
            transparent,
            transparent 79px,
            rgba(207,185,145,0.03) 80px
        );
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2.5rem 4rem; max-width: 1280px; }

/* ── Top institutional bar ── */
.inst-bar {
    background: var(--gold);
    padding: 0.45rem 2.5rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin: 0 -2.5rem 0;
}
.inst-bar-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    font-weight: 900;
    color: var(--black);
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.inst-bar-divider {
    width: 1px;
    height: 18px;
    background: rgba(0,0,0,0.25);
}
.inst-bar-sub {
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.75rem;
    font-weight: 500;
    color: rgba(0,0,0,0.6);
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

/* ── Hero ── */
.hero {
    padding: 3.5rem 0 2.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2.5rem;
}
.hero-kicker {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.hero-kicker::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--gold-dark), transparent);
    max-width: 180px;
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.6rem, 5.5vw, 4.8rem);
    font-weight: 900;
    line-height: 1.0;
    letter-spacing: -0.02em;
    color: var(--text);
    margin: 0 0 0.5rem;
}
.hero h1 em {
    font-style: italic;
    color: var(--gold);
}
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: var(--muted);
    max-width: 560px;
    line-height: 1.7;
    margin-top: 1rem;
}

/* ── Input section label ── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-label::before {
    content: '//';
    opacity: 0.5;
}

/* ── Form / inputs ── */
.stTextInput > div > div > input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.8rem 1.1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    letter-spacing: 0.01em !important;
}
.stTextInput > div > div > input::placeholder { color: var(--muted) !important; }
.stTextInput > div > div > input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(207,185,145,0.1) !important;
    outline: none !important;
}
.stTextInput > label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: var(--gold) !important;
    font-weight: 500 !important;
}

/* ── Button ── */
.stButton > button,
.stFormSubmitButton > button {
    background: var(--gold) !important;
    color: var(--black) !important;
    font-family: 'Playfair Display', serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.05em !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.75rem 2rem !important;
    cursor: pointer !important;
    transition: background 0.2s, transform 0.15s, box-shadow 0.2s !important;
    box-shadow: 0 2px 16px rgba(207,185,145,0.2), inset 0 1px 0 rgba(255,255,255,0.15) !important;
    width: 100% !important;
    text-transform: uppercase !important;
}
.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: var(--gold-light) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(207,185,145,0.3) !important;
}
.stButton > button:active,
.stFormSubmitButton > button:active {
    transform: translateY(0) !important;
    background: var(--gold-dark) !important;
}

/* ── Pipeline cards ── */
.pipeline-grid {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
}
.pipe-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.1rem 1.4rem;
    display: flex;
    align-items: flex-start;
    gap: 1.1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, background 0.3s;
}
.pipe-card.active {
    border-color: var(--gold);
    background: rgba(207,185,145,0.05);
}
.pipe-card.done {
    border-color: rgba(126,200,164,0.35);
    background: rgba(126,200,164,0.04);
}
.pipe-card-accent {
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: rgba(255,255,255,0.04);
    border-radius: 8px 0 0 8px;
    transition: background 0.3s;
}
.pipe-card.active .pipe-card-accent { background: var(--gold); }
.pipe-card.done   .pipe-card-accent { background: var(--green); }
.pipe-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 400;
    color: rgba(207,185,145,0.2);
    line-height: 1;
    min-width: 2rem;
    transition: color 0.3s;
}
.pipe-card.active .pipe-num { color: rgba(207,185,145,0.6); }
.pipe-card.done   .pipe-num { color: rgba(126,200,164,0.5); }
.pipe-body { flex: 1; }
.pipe-title {
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.15rem;
    letter-spacing: 0.01em;
}
.pipe-desc {
    font-size: 0.78rem;
    color: var(--muted);
    font-weight: 300;
}
.pipe-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.2rem 0.55rem;
    border-radius: 3px;
    margin-top: 0.2rem;
    width: fit-content;
}
.ps-waiting { color: var(--muted); background: rgba(255,255,255,0.04); }
.ps-running { color: var(--black); background: var(--gold); animation: pulse-badge 1.2s ease-in-out infinite; }
.ps-done    { color: var(--black); background: var(--green); }

@keyframes pulse-badge {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.7; }
}

/* ── Results ── */
.results-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--text);
    margin: 2.5rem 0 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.results-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

.raw-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}
.raw-panel-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 0.8rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border);
}
.raw-content {
    font-size: 0.85rem;
    line-height: 1.75;
    color: #B0A898;
    white-space: pre-wrap;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 400;
}

.report-panel {
    background: var(--surface);
    border: 1px solid rgba(207,185,145,0.25);
    border-top: 3px solid var(--gold);
    border-radius: 0 0 8px 8px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
}
.report-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid var(--border);
}

.critic-panel {
    background: var(--surface);
    border: 1px solid rgba(126,200,164,0.25);
    border-top: 3px solid var(--green);
    border-radius: 0 0 8px 8px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
}
.critic-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--green);
    margin-bottom: 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(126,200,164,0.15);
}

/* ── Download button ── */
.stDownloadButton > button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--gold) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 0.55rem 1.4rem !important;
    transition: border-color 0.2s, background 0.2s !important;
    width: auto !important;
}
.stDownloadButton > button:hover {
    background: rgba(207,185,145,0.08) !important;
    border-color: var(--gold) !important;
}

/* ── Expander ── */
details > summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    color: var(--muted) !important;
    text-transform: uppercase;
    cursor: pointer;
}
details > summary:hover { color: var(--gold) !important; }

/* ── Spinner ── */
.stSpinner > div { color: var(--gold) !important; }

/* ── Footer ── */
.footer {
    margin-top: 4rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.footer-left {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.footer-right {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: rgba(207,185,145,0.3);
    letter-spacing: 0.06em;
}

/* ── Markdown content styling ── */
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Playfair Display', serif !important;
    color: var(--text) !important;
}
.stMarkdown h2 { color: var(--gold-light) !important; }
.stMarkdown p  { color: #C8C0B4 !important; line-height: 1.8 !important; }
.stMarkdown li { color: #C8C0B4 !important; }
.stMarkdown strong { color: var(--gold-light) !important; }
.stMarkdown code {
    background: rgba(207,185,145,0.08) !important;
    color: var(--gold) !important;
    border-radius: 3px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Pill tags ── */
.pill {
    display: inline-block;
    background: rgba(207,185,145,0.08);
    border: 1px solid rgba(207,185,145,0.2);
    border-radius: 4px;
    padding: 0.2rem 0.65rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: var(--muted);
    letter-spacing: 0.05em;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
    cursor: default;
}
.pill:hover {
    background: rgba(207,185,145,0.13);
    color: var(--gold);
    border-color: rgba(207,185,145,0.35);
}
</style>
""", unsafe_allow_html=True)


# ── Helper: step state ────────────────────────────────────────────────────────
def get_step_state(step: str, results: dict, running: bool) -> str:
    steps = ["search", "reader", "writer", "critic"]
    if step in results:
        return "done"
    if running:
        for k in steps:
            if k not in results:
                return "running" if k == step else "waiting"
    return "waiting"


def render_pipe_card(num: str, title: str, desc: str, state: str):
    status_map = {
        "waiting": ("Waiting",  "ps-waiting"),
        "running": ("Running",  "ps-running"),
        "done":    ("Complete", "ps-done"),
    }
    label, badge_cls = status_map.get(state, ("Waiting", "ps-waiting"))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="pipe-card {card_cls}">
        <div class="pipe-card-accent"></div>
        <div class="pipe-num">{num}</div>
        <div class="pipe-body">
            <div class="pipe-title">{title}</div>
            <div class="pipe-desc">{desc}</div>
            <div class="pipe-status {badge_cls}">{label}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [("results", {}), ("running", False), ("done", False)]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── Institutional bar ─────────────────────────────────────────────────────────
st.markdown("""
<div class="inst-bar">
    <span class="inst-bar-logo">Purdue University</span>
    <div class="inst-bar-divider"></div>
    <span class="inst-bar-sub">Research Intelligence Platform</span>
</div>
""", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-kicker">Multi-Agent AI System &nbsp;·&nbsp; NorthWest, IN</div>
    <h1>Research<br><em>Intelligence</em></h1>
    <p class="hero-sub">
        Four specialized AI agents working in sequence — searching the web,
        scraping sources, drafting reports, and applying critical review —
        to deliver polished research on any subject.
    </p>
</div>
""", unsafe_allow_html=True)


# ── Layout ────────────────────────────────────────────────────────────────────
col_left, col_gap, col_right = st.columns([5, 0.4, 4])

with col_left:
    st.markdown('<div class="section-label">Research Query</div>', unsafe_allow_html=True)

    with st.form("research_form", clear_on_submit=False):
        topic = st.text_input(
            "Topic",
            placeholder="e.g. Advances in solid-state battery technology 2025",
            key="topic_input",
            label_visibility="collapsed",
        )
        run_btn = st.form_submit_button("Run Research Pipeline →", use_container_width=True)

    # Example topics
    st.markdown('<div style="margin-top:0.8rem;margin-bottom:0.4rem;font-family:\'JetBrains Mono\',monospace;font-size:0.6rem;color:#5A5248;letter-spacing:0.18em;text-transform:uppercase;">Example topics</div>', unsafe_allow_html=True)
    examples = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress", "Quantum computing breakthroughs"]
    pills_html = "".join(f'<span class="pill">{e}</span>' for e in examples)
    st.markdown(f'<div>{pills_html}</div>', unsafe_allow_html=True)

    # Brief about section
    st.markdown("""
    <div style="margin-top:2rem;padding:1.2rem 1.5rem;background:rgba(207,185,145,0.04);border:1px solid rgba(207,185,145,0.1);border-radius:8px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;letter-spacing:0.2em;text-transform:uppercase;color:rgba(207,185,145,0.5);margin-bottom:0.6rem;">About this system</div>
        <p style="font-size:0.82rem;color:#7A7268;line-height:1.7;margin:0;">
            Built on LangChain's multi-agent framework. Each pipeline stage is an independent
            agent with specialized tools — web search, content scraping, structured writing,
            and analytical critique.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="section-label">Pipeline Status</div>', unsafe_allow_html=True)

    r = st.session_state.results
    running = st.session_state.running

    render_pipe_card("01", "Search Agent",  "Gathers recent web information",        get_step_state("search", r, running))
    render_pipe_card("02", "Reader Agent",  "Scrapes & extracts deep content",       get_step_state("reader", r, running))
    render_pipe_card("03", "Writer Chain",  "Drafts the full research report",       get_step_state("writer", r, running))
    render_pipe_card("04", "Critic Chain",  "Reviews, scores & refines the report",  get_step_state("critic", r, running))


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False

        results = {}
        topic_val = topic.strip()

        with st.spinner("Search Agent — gathering web intelligence…"):
            try:
                search_agent = build_search_agent()
                sr = search_agent.invoke({
                    "messages": [HumanMessage(content=f"Find recent, reliable and detailed information about: {topic_val}")]
                })
                results["search"] = sr["messages"][-1].content
                st.session_state.results = dict(results)
            except RuntimeError as e:
                st.session_state.running = False
                st.error(str(e))
                st.stop()

        with st.spinner("Reader Agent — scraping top resources…"):
            reader_agent = build_reader_agent()
            rr = reader_agent.invoke({
                "messages": [HumanMessage(content=(
                    f"Based on the following search results about '{topic_val}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{results['search'][:800]}"
                ))]
            })
            results["reader"] = rr["messages"][-1].content
            st.session_state.results = dict(results)

        with st.spinner("Writer Chain — drafting the research report…"):
            research_combined = (
                f"SEARCH RESULTS:\n{results['search']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
            )
            results["writer"] = writer_chain.invoke({
                "topic": topic_val,
                "research": research_combined
            })
            st.session_state.results = dict(results)

        with st.spinner("Critic Chain — reviewing and scoring the report…"):
            results["critic"] = critic_chain.invoke({
                "report": results["writer"]
            })
            st.session_state.results = dict(results)

        st.session_state.running = False
        st.session_state.done = True
        st.rerun()


# ── Results ───────────────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="results-header">Output</div>', unsafe_allow_html=True)

    # Raw outputs — collapsed by default
    if "search" in r:
        with st.expander("01 · Search Agent — raw output"):
            st.markdown(
                f'<div class="raw-panel"><div class="raw-panel-label">Search Agent Output</div>'
                f'<div class="raw-content">{r["search"]}</div></div>',
                unsafe_allow_html=True,
            )

    if "reader" in r:
        with st.expander("02 · Reader Agent — scraped content"):
            st.markdown(
                f'<div class="raw-panel"><div class="raw-panel-label">Reader Agent Output</div>'
                f'<div class="raw-content">{r["reader"]}</div></div>',
                unsafe_allow_html=True,
            )

    # Final report
    if "writer" in r:
        st.markdown('<div class="report-panel"><div class="report-label">03 · Final Research Report</div>', unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        col_dl, col_spacer = st.columns([2, 5])
        with col_dl:
            st.download_button(
                label="↓  Download Report (.md)",
                data=r["writer"],
                file_name=f"purdue_research_{int(time.time())}.md",
                mime="text/markdown",
            )

    # Critic feedback
    if "critic" in r:
        st.markdown('<div class="critic-panel"><div class="critic-label">04 · Critic Review & Score</div>', unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <div class="footer-left">Purdue University · Research Intelligence Platform · LangChain Multi-Agent</div>
    <div class="footer-right">Boiler Up 🚂</div>
</div>
""", unsafe_allow_html=True)