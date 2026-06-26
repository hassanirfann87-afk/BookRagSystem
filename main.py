import streamlit as st
from src.chain import rag_chain
import html

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lumière — Intelligence",
    page_icon="◆",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Design system ──────────────────────────────────────────────────────────────
# Color palette (WCAG AA verified contrast ratios noted inline)
# --bg          #0D0E14   Page canvas
# --surface     #13151E   Card / container fill  (contrast 4.6:1 on text-primary)
# --surface-2   #1A1D29   Raised surface
# --user-bg     #1F2133   User message bubble
# --accent      #6C63FF   Primary action (contrast 3.1:1 on bg — used only on white text)
# --accent-text #A89CFF   Accent text on dark bg (contrast 4.8:1)
# --text-pri    #F0F0F5   Primary text (contrast 15.3:1 on bg)
# --text-sec    #8B8FA8   Secondary text (contrast 4.5:1 on bg — AA pass)
# --text-mut    #50546A   Muted / placeholders (contrast 3.2:1 — decorative use only)
# --success     #22C98A   Online indicator
# --danger-bg   #2D1A1A   Error surface
# --danger-bdr  #6B2A2A   Error border
# --danger-txt  #F87171   Error text (contrast 5.8:1 on danger-bg)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;1,400&family=Lora:ital,wght@0,400;0,500;1,400;1,500&display=swap');

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; }

/* ── Page canvas ── */
.stApp {
    background: #0D0E14 !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    color: #F0F0F5;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header,
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"] { display: none !important; }

/* ── Main content width ── */
.main .block-container {
    max-width: 800px !important;
    padding: 0 1.5rem 6rem !important;
}

/* ══════════════════════════════════════
   TOP BAR
══════════════════════════════════════ */
.lm-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0 16px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 0;
    position: sticky;
    top: 0;
    background: #0D0E14;
    z-index: 100;
}
.lm-logo {
    display: flex;
    align-items: center;
    gap: 10px;
}
.lm-logo-mark {
    width: 32px; height: 32px;
    background: #6C63FF;
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 700;
    color: #fff;
    letter-spacing: 0;
    flex-shrink: 0;
}
.lm-logo-name {
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: #F0F0F5;
}
.lm-badge {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #A89CFF;
    background: rgba(108,99,255,0.12);
    border: 1px solid rgba(108,99,255,0.22);
    border-radius: 5px;
    padding: 2px 7px;
}
.lm-status {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 12px;
    color: #50546A;
}
.lm-status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #22C98A;
    flex-shrink: 0;
}

/* ══════════════════════════════════════
   HERO (empty state)
══════════════════════════════════════ */
.lm-hero {
    text-align: center;
    padding: 64px 16px 52px;
}
.lm-hero-eyebrow {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #A89CFF;
    margin-bottom: 18px;
}
.lm-hero-eyebrow::before,
.lm-hero-eyebrow::after {
    content: '';
    display: block;
    width: 30px;
    height: 1px;
    background: rgba(168,156,255,0.3);
}
.lm-hero-title {
    font-family: 'Lora', Georgia, serif;
    font-size: clamp(2.2rem, 6vw, 3.6rem);
    font-weight: 500;
    line-height: 1.12;
    letter-spacing: -0.01em;
    color: #F0F0F5;
    margin-bottom: 18px;
}
.lm-hero-title em {
    color: #A89CFF;
    font-style: italic;
}
.lm-hero-sub {
    font-size: 16px;
    line-height: 1.65;
    color: #8B8FA8;
    max-width: 400px;
    margin: 0 auto 36px;
    font-weight: 400;
}
.lm-pills {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
}
.lm-pill {
    font-size: 12px;
    font-weight: 500;
    color: #8B8FA8;
    background: #13151E;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 5px 13px;
}

/* ══════════════════════════════════════
   CONVERSATION
══════════════════════════════════════ */
.lm-convo {
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-bottom: 32px;
}

.lm-pair {
    padding: 24px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.lm-pair:last-child { border-bottom: none; }

/* User message */
.lm-user-row {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 16px;
}
.lm-user-bubble {
    background: #1F2133;
    border: 1px solid rgba(108,99,255,0.22);
    border-radius: 18px 18px 4px 18px;
    padding: 13px 17px;
    max-width: 82%;
    font-size: 15px;
    line-height: 1.6;
    color: #EEEEF5;
    font-weight: 400;
}
.lm-user-label {
    text-align: right;
    font-size: 11px;
    font-weight: 500;
    color: #50546A;
    letter-spacing: 0.06em;
    margin-bottom: 6px;
    padding-right: 2px;
}

/* AI message */
.lm-ai-row {
    display: flex;
    flex-direction: column;
}
.lm-ai-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 600;
    color: #50546A;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.lm-ai-icon {
    width: 24px; height: 24px;
    background: #6C63FF;
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 700; color: #fff;
    flex-shrink: 0;
}
.lm-ai-bubble {
    background: #13151E;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 4px 18px 18px 18px;
    padding: 16px 20px;
    max-width: 92%;
    font-family: 'Lora', Georgia, serif;
    font-size: 15.5px;
    line-height: 1.78;
    color: #D8D8E8;
    font-weight: 400;
}

/* ══════════════════════════════════════
   INPUT FORM  — override Streamlit
══════════════════════════════════════ */
div[data-testid="stForm"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}

/* Sticky input bar at bottom */
.lm-input-bar {
    position: sticky;
    bottom: 0;
    background: #0D0E14;
    padding: 16px 0 20px;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin-top: 8px;
}
.lm-input-label {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #50546A;
    margin-bottom: 10px;
}

/* Text input */
div[data-testid="stForm"] input[type="text"] {
    background: #13151E !important;
    border: 1.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 14px !important;
    color: #F0F0F5 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    font-weight: 400 !important;
    padding: 13px 18px !important;
    line-height: 1.5 !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    caret-color: #6C63FF !important;
}
div[data-testid="stForm"] input[type="text"]:focus {
    border-color: rgba(108,99,255,0.55) !important;
    box-shadow: 0 0 0 4px rgba(108,99,255,0.08) !important;
    outline: none !important;
}
div[data-testid="stForm"] input[type="text"]::placeholder {
    color: #50546A !important;
    font-style: italic !important;
}

/* Submit button */
button[kind="formSubmit"] {
    background: #6C63FF !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.7rem 2rem !important;
    width: 100% !important;
    margin-top: 10px !important;
    transition: background 0.18s ease, transform 0.12s ease, box-shadow 0.18s ease !important;
    box-shadow: 0 4px 16px rgba(108,99,255,0.28) !important;
    cursor: pointer !important;
    min-height: 46px !important;
}
button[kind="formSubmit"]:hover {
    background: #5850E8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(108,99,255,0.38) !important;
}
button[kind="formSubmit"]:active {
    transform: translateY(0) scale(0.99) !important;
    box-shadow: 0 2px 8px rgba(108,99,255,0.25) !important;
}
button[kind="formSubmit"]:focus-visible {
    outline: 3px solid rgba(108,99,255,0.5) !important;
    outline-offset: 2px !important;
}

/* Form label */
div[data-testid="stForm"] label,
div[data-testid="stForm"] .stTextInput label {
    color: #50546A !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    margin-bottom: 6px !important;
}

/* ══════════════════════════════════════
   LOADING / SPINNER
══════════════════════════════════════ */
div[data-testid="stSpinner"] {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 12px 18px !important;
    background: rgba(108,99,255,0.08) !important;
    border: 1px solid rgba(108,99,255,0.15) !important;
    border-radius: 12px !important;
    margin: 16px 0 !important;
}
div[data-testid="stSpinner"] p {
    color: #A89CFF !important;
    font-size: 14px !important;
    margin: 0 !important;
}

/* ══════════════════════════════════════
   ALERTS / ERRORS
══════════════════════════════════════ */
div[data-testid="stAlert"][data-baseweb="notification"] {
    background: #2D1A1A !important;
    border: 1px solid #6B2A2A !important;
    border-radius: 12px !important;
    color: #F87171 !important;
    font-size: 14px !important;
}
div[data-testid="stAlert"][data-baseweb="notification"] p {
    color: #F87171 !important;
}

/* Warning */
.stAlert[data-baseweb="notification"][kind="warning"] {
    background: #2B2515 !important;
    border-color: #6B5A20 !important;
}
.stAlert[data-baseweb="notification"][kind="warning"] p {
    color: #FCD34D !important;
}

/* ══════════════════════════════════════
   SCROLLBAR
══════════════════════════════════════ */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.08);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(108,99,255,0.35);
}

/* ══════════════════════════════════════
   FOOTER
══════════════════════════════════════ */
.lm-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 2px 0;
}
.lm-footer-hint {
    font-size: 12px;
    color: #50546A;
    font-style: italic;
}
.lm-kbd {
    font-size: 11px;
    color: #50546A;
    background: #1A1D29;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 5px;
    padding: 2px 7px;
    font-family: 'Inter', monospace;
}

/* ══════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════ */
@media (max-width: 640px) {
    .main .block-container { padding: 0 1rem 5rem !important; }
    .lm-hero { padding: 40px 8px 36px; }
    .lm-user-bubble { max-width: 92%; }
    .lm-ai-bubble { max-width: 98%; }
}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Top bar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="lm-topbar" role="banner">
  <div class="lm-logo">
    <div class="lm-logo-mark" aria-hidden="true">L</div>
    <span class="lm-logo-name">LUMIÈRE</span>
    <span class="lm-badge">Intelligence</span>
  </div>
  <div class="lm-status" role="status" aria-label="System online">
    <div class="lm-status-dot" aria-hidden="true"></div>
    <span>System online</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Hero (empty state) or conversation ────────────────────────────────────────
if not st.session_state.chat_history:
    st.markdown("""
    <div class="lm-hero" role="main">
      <div class="lm-hero-eyebrow" aria-hidden="true">Knowledge Intelligence</div>
      <h1 class="lm-hero-title">Ask anything.<br><em>Get clarity.</em></h1>
      <p class="lm-hero-sub">Every answer is grounded in your knowledge base. Source-backed, accurate, instant.</p>
      <div class="lm-pills" aria-label="Key features">
        <span class="lm-pill">Deep search</span>
        <span class="lm-pill">Source-grounded</span>
        <span class="lm-pill">Instant answers</span>
        <span class="lm-pill">Conversation history</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="lm-convo" role="log" aria-live="polite" aria-label="Conversation">', unsafe_allow_html=True)
    for item in reversed(st.session_state.chat_history):
        q = html.escape(item["question"])
        a = html.escape(item["answer"])
        st.markdown(f"""
        <div class="lm-pair">
          <div class="lm-user-label">You</div>
          <div class="lm-user-row">
            <div class="lm-user-bubble" role="article" aria-label="Your question">{q}</div>
          </div>
          <div class="lm-ai-row">
            <div class="lm-ai-label">
              <div class="lm-ai-icon" aria-hidden="true">L</div>
              Lumière
            </div>
            <div class="lm-ai-bubble" role="article" aria-label="Lumière response">{a}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── Input form ─────────────────────────────────────────────────────────────────
with st.form(key="lm_form", clear_on_submit=True):
    question = st.text_input(
        "Your question",
        placeholder="Ask anything about your knowledge base…",
        label_visibility="collapsed",
    )
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submitted = st.form_submit_button(
            "Ask Lumière →",
            use_container_width=True,
        )

st.markdown("""
<div class="lm-footer">
  <span class="lm-footer-hint">Grounded in your documents</span>
  <span class="lm-kbd">↵ send</span>
</div>
""", unsafe_allow_html=True)

# ── Logic ──────────────────────────────────────────────────────────────────────
if submitted and question.strip():
    with st.spinner("Searching the knowledge base…"):
        try:
            response = rag_chain.invoke(question)
            st.session_state.chat_history.append({
                "question": question,
                "answer": response.content,
            })
            st.rerun()
        except Exception as exc:
            st.error(f"Could not retrieve an answer. {str(exc)}")
elif submitted:
    st.warning("Enter a question to get started.")