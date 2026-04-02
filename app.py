

import streamlit as st
from agent import LabAgent

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CSE Lab AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS  —  dark purple / neon theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #0d0b1e 0%, #1a0533 50%, #0d1a33 100%);
    min-height: 100vh;
}

/* ── Header banner ── */
.header-box {
    background: linear-gradient(90deg, #6a00f4, #bc00dd, #ff0090);
    border-radius: 18px;
    padding: 26px 32px;
    margin-bottom: 28px;
    text-align: center;
    box-shadow: 0 8px 40px rgba(188,0,221,0.45);
}
.header-box h1 { color: #fff; margin: 0; font-size: 1.9rem; font-weight: 700; letter-spacing: -0.5px; }
.header-box p  { color: rgba(255,255,255,0.82); margin: 6px 0 0; font-size: 0.92rem; }

/* ── Chat bubbles ── */
.user-bubble {
    background: linear-gradient(135deg, #6a00f4, #bc00dd);
    color: #fff;
    border-radius: 18px 18px 4px 18px;
    padding: 14px 18px;
    margin: 10px 0 10px auto;
    max-width: 78%;
    box-shadow: 0 4px 18px rgba(106,0,244,0.35);
    font-size: 0.94rem;
    line-height: 1.55;
    word-wrap: break-word;
}
.bot-bubble {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.13);
    color: #e4e4f0;
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    margin: 10px auto 10px 0;
    max-width: 84%;
    box-shadow: 0 4px 18px rgba(0,0,0,0.35);
    font-size: 0.94rem;
    line-height: 1.65;
    word-wrap: break-word;
}
.blocked-bubble {
    background: rgba(220, 38, 38, 0.12);
    border: 1px solid rgba(220, 38, 38, 0.38);
    color: #fca5a5;
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    margin: 10px auto 10px 0;
    max-width: 84%;
    font-size: 0.94rem;
    line-height: 1.6;
}

/* ── Text input ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid rgba(255,255,255,0.16) !important;
    border-radius: 12px !important;
    color: #f0f0ff !important;
    padding: 13px 17px !important;
    font-size: 0.94rem !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input::placeholder { color: rgba(255,255,255,0.38) !important; }
.stTextInput > div > div > input:focus {
    border-color: #bc00dd !important;
    box-shadow: 0 0 0 3px rgba(188,0,221,0.22) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6a00f4, #bc00dd) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 11px 24px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 22px rgba(188,0,221,0.55) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(10, 7, 30, 0.97) !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}
[data-testid="stSidebar"] * { color: #c8c0e0 !important; }

.sb-card {
    background: rgba(106,0,244,0.14);
    border: 1px solid rgba(106,0,244,0.35);
    border-radius: 10px;
    padding: 9px 13px;
    margin: 5px 0;
    font-size: 0.82rem;
    color: #c8aeff !important;
}
.sb-block {
    background: rgba(220,38,38,0.12);
    border: 1px solid rgba(220,38,38,0.3);
    border-radius: 10px;
    padding: 7px 12px;
    margin: 4px 0;
    font-size: 0.8rem;
    color: #fca5a5 !important;
}

/* ── Gradient divider ── */
.g-hr {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(188,0,221,0.55), transparent);
    border: none;
    margin: 18px 0;
}

/* ── Status badge ── */
.badge-green {
    display: inline-block;
    background: #14532d;
    border: 1px solid #166534;
    color: #86efac;
    border-radius: 20px;
    padding: 3px 11px;
    font-size: 0.76rem;
    font-weight: 600;
}
.badge-red {
    display: inline-block;
    background: #450a0a;
    border: 1px solid #7f1d1d;
    color: #fca5a5;
    border-radius: 20px;
    padding: 3px 11px;
    font-size: 0.76rem;
    font-weight: 600;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    color: rgba(255,255,255,0.28);
    padding: 50px 0 30px;
}
.empty-state .icon { font-size: 3.2rem; }
.empty-state p { margin-top: 10px; font-size: 0.98rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Load agent  (cached — runs only once per session)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="🔧 Loading models and building FAISS index…")
def load_agent():
    return LabAgent()

try:
    agent = load_agent()
    agent_ok = True
except Exception as e:
    agent_ok = False
    agent_error = str(e)

# ─────────────────────────────────────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "prefill" not in st.session_state:
    st.session_state.prefill = ""

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧪 Lab Info")
    for item in [
        "📍 Room 304, Block B",
        "🕘 Mon–Fri  |  9 AM – 4 PM",
        "👨‍🏫 Asst. Prof. Arun",
        "🖥️ 10× RTX 3090  ·  2× RTX 4090",
        "🐧 Ubuntu 22.04  ·  Python 3.10+",
    ]:
        st.markdown(f'<div class="sb-card">{item}</div>', unsafe_allow_html=True)

    st.markdown('<div class="g-hr"></div>', unsafe_allow_html=True)
    st.markdown("## 🛡️ Blocked Topics")
    for item in [
        "🔒 Passwords & Wi-Fi keys",
        "🔒 API keys & Tokens",
        "🔒 SSH credentials",
        "🔒 IP addresses & Ports",
        "🔒 Proxy & Firewall info",
    ]:
        st.markdown(f'<div class="sb-block">{item}</div>', unsafe_allow_html=True)

    st.markdown('<div class="g-hr"></div>', unsafe_allow_html=True)

    # Agent status
    if agent_ok:
        st.markdown('<span class="badge-green">✅ Agent Ready</span>', unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:0.78rem;color:#888;margin-top:6px;">'
            f'{agent.index.ntotal} vectors · FAISS IndexFlatL2</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<span class="badge-red">❌ Agent Error</span>', unsafe_allow_html=True)

    st.markdown('<div class="g-hr"></div>', unsafe_allow_html=True)
    st.markdown("## 💡 Try Asking")
    sample_questions = [
        "What are the lab timings?",
        "How do I fix a kernel crash?",
        "What is the GPU compute quota?",
        "What is the attendance policy?",
        "What ML labs are covered?",
        "How do I get extra GPU hours?",
        "What deep learning frameworks are installed?",
        "How are lab submissions graded?",
    ]
    for q in sample_questions:
        if st.button(q, key=f"sq_{q}"):
            st.session_state.prefill = q
            st.rerun()

    st.markdown('<div class="g-hr"></div>', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat History"):
        st.session_state.history = []
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <h1>🤖 CSE Lab AI Assistant</h1>
    <p>Advanced AI &amp; Deep Learning Lab · Powered by Groq LLaMA · FAISS · CrossEncoder</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Agent error banner
# ─────────────────────────────────────────────────────────────────────────────
if not agent_ok:
    st.error(f"**Agent failed to load:** {agent_error}")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Chat history display
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.history:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">💬</div>
        <p>Ask me anything about the lab — timings, policies, GPU quotas, troubleshooting…</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="user-bubble">🧑‍💻&nbsp; {msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        elif msg.get("blocked"):
            st.markdown(
                f'<div class="blocked-bubble">🔒&nbsp; {msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            # Render markdown inside the bubble properly
            with st.container():
                st.markdown(
                    '<div class="bot-bubble">🤖&nbsp; <strong>Lab Assistant</strong><br><br>'
                    + msg["content"].replace("\n", "<br>")
                    + "</div>",
                    unsafe_allow_html=True,
                )

st.markdown('<div class="g-hr"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Input form
# ─────────────────────────────────────────────────────────────────────────────
prefill_value = st.session_state.pop("prefill", "")

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            label="",
            value=prefill_value,
            placeholder="Ask about labs, policies, GPU usage, troubleshooting…",
            label_visibility="collapsed",
        )
    with col2:
        submitted = st.form_submit_button("Send ➤")

# ─────────────────────────────────────────────────────────────────────────────
# Handle submission
# ─────────────────────────────────────────────────────────────────────────────
if submitted and user_input.strip():
    query = user_input.strip()

    # Add user message
    st.session_state.history.append({"role": "user", "content": query})

    # Get answer
    with st.spinner("🔍 Searching knowledge base and generating answer…"):
        answer, is_blocked = agent.ask(query)

    # Add assistant message
    st.session_state.history.append({
        "role": "assistant",
        "content": answer,
        "blocked": is_blocked,
    })

    st.rerun()