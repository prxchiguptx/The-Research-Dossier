import sys
import asyncio

# Place this at the absolute top of app.py before importing streamlit
if sys.platform == 'win32':
    # Silences the noisy Proactor connection reset logs in Windows asyncio
    from asyncio.proactor_events import _ProactorBasePipeTransport
    
    def silence_connection_lost(self, exc):
        if isinstance(exc, ConnectionResetError):
            return
        self._orig_call_connection_lost(exc)
        
    if not hasattr(_ProactorBasePipeTransport, '_orig_call_connection_lost'):
        _ProactorBasePipeTransport._orig_call_connection_lost = _ProactorBasePipeTransport._call_connection_lost
        _ProactorBasePipeTransport._call_connection_lost = silence_connection_lost
import streamlit as st
from datetime import datetime
from pipeline import run_research_pipeline

st.set_page_config(
    page_title="The Research Dossier",
    page_icon="🗂️",
    layout="wide",
)

# ----------------------------------------------------------------------------
# STYLE — "Research Dossier" theme
# ----------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root{
    --ink:        #0F1720;
    --panel:      #182233;
    --panel-2:    #1E2A3D;
    --parchment:  #F3ECDD;
    --parchment-2:#EAE1CC;
    --gold:       #D9A441;
    --teal:       #3FA796;
    --rose:       #C1666B;
    --violet:     #8C7AE6;
    --text:       #ECE6D6;
    --text-dim:   #9AA5B1;
}

/* base canvas */
[data-testid="stAppViewContainer"]{
    background:
        radial-gradient(1200px 600px at 15% -10%, #1a2740 0%, transparent 60%),
        var(--ink);
    color: var(--text);
}
[data-testid="stHeader"]{ background: transparent; }
[data-testid="stSidebar"]{
    background: var(--panel);
    border-right: 1px solid rgba(217,164,65,0.15);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Fraunces', serif !important; }

/* ---- Masthead ---- */
.dossier-header{
    display:flex; justify-content:space-between; align-items:flex-end;
    border-bottom: 2px solid var(--gold);
    padding-bottom: 18px; margin-bottom: 6px;
    animation: fadeSlide 0.6s ease-out;
}
.dossier-eyebrow{
    font-family:'IBM Plex Mono', monospace;
    letter-spacing: 3px; font-size: 12px; color: var(--gold);
    text-transform: uppercase; margin-bottom: 6px;
}
.dossier-title{
    font-family:'Fraunces', serif; font-weight:700; font-size: 42px;
    color: var(--text); margin:0; line-height:1.05;
}
.dossier-sub{
    font-family:'IBM Plex Mono', monospace; font-size: 12px;
    color: var(--text-dim); text-align:right; line-height:1.6;
}
@keyframes fadeSlide { from {opacity:0; transform: translateY(-8px);} to {opacity:1; transform: translateY(0);} }

/* ---- form field ---- */
.stTextInput input{
    background: var(--panel-2) !important;
    color: var(--text) !important;
    border: 1px solid rgba(217,164,65,0.35) !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    padding: 12px 14px !important;
}
.stTextInput input:focus{
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 1px var(--gold) !important;
}
.stTextInput label { font-family:'IBM Plex Mono', monospace; color: var(--text-dim) !important; letter-spacing:1px; font-size:12px !important; text-transform:uppercase;}

/* ---- primary button as a wax-stamp action ---- */
.stButton>button, .stFormSubmitButton>button{
    background: var(--gold) !important;
    color: #17110a !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    font-size: 13px !important;
    padding: 12px 20px !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton>button:hover, .stFormSubmitButton>button:hover{
    transform: translateY(-2px);
    box-shadow: 0 6px 14px rgba(217,164,65,0.25);
}

/* ---- exhibit cards (the 4 pipeline stages) ---- */
.exhibit-row{ display:flex; gap:14px; margin: 18px 0 26px 0; flex-wrap: wrap; }
.exhibit-card{
    flex:1; min-width: 200px;
    background: var(--panel);
    border: 1px solid rgba(255,255,255,0.06);
    border-left: 4px solid var(--accent, var(--gold));
    border-radius: 6px;
    padding: 16px 16px 14px 16px;
    position: relative;
    animation: fadeSlide 0.5s ease-out;
}
.exhibit-tag{
    font-family:'IBM Plex Mono', monospace; font-size: 11px;
    color: var(--accent, var(--gold)); letter-spacing:2px; text-transform:uppercase;
    margin-bottom: 6px; display:block;
}
.exhibit-title{ font-family:'Fraunces', serif; font-weight:600; font-size:17px; margin:0 0 4px 0; color: var(--text);}
.exhibit-desc{ font-size:12.5px; color: var(--text-dim); margin:0; }
.stamp-corner{
    position:absolute; top:10px; right:12px;
    font-family:'IBM Plex Mono', monospace; font-size:10px;
    color: var(--text-dim); opacity:0.6;
}

/* ---- processing pulse ---- */
.pulse-dot{
    display:inline-block; width:9px; height:9px; border-radius:50%;
    background: var(--gold); margin-right:8px;
    animation: pulse 1.2s infinite ease-in-out;
    vertical-align:middle;
}
@keyframes pulse{
    0%   { box-shadow: 0 0 0 0 rgba(217,164,65,0.55); }
    70%  { box-shadow: 0 0 0 9px rgba(217,164,65,0); }
    100% { box-shadow: 0 0 0 0 rgba(217,164,65,0); }
}

/* ---- status box override ---- */
[data-testid="stStatusWidget"], [data-testid="stExpander"]{
    background: var(--panel) !important;
    border: 1px solid rgba(217,164,65,0.2) !important;
    border-radius: 6px !important;
}

/* ---- tabs as folder tabs ---- */
.stTabs [data-baseweb="tab-list"]{ gap: 4px; border-bottom: 2px solid rgba(217,164,65,0.25); }
.stTabs [data-baseweb="tab"]{
    background: var(--panel) !important;
    border-radius: 6px 6px 0 0 !important;
    font-family:'IBM Plex Mono', monospace !important;
    font-size: 12.5px !important;
    letter-spacing: 0.5px;
    color: var(--text-dim) !important;
    padding: 10px 16px !important;
}
.stTabs [aria-selected="true"]{
    background: var(--gold) !important;
    color: #17110a !important;
    font-weight: 600 !important;
}

/* ---- report parchment card ---- */
.parchment{
    background: linear-gradient(180deg, var(--parchment) 0%, var(--parchment-2) 100%);
    color: #221c12;
    border-radius: 6px;
    padding: 30px 34px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    font-family: 'Fraunces', serif;
    font-size: 16px;
    line-height: 1.65;
}
.parchment h1, .parchment h2, .parchment h3{ color:#221c12 !important; }
.parchment * { color:#221c12; }

/* plain text areas -> case-note look */
.stTextArea textarea{
    background: var(--panel-2) !important;
    color: var(--text) !important;
    font-family:'IBM Plex Mono', monospace !important;
    font-size: 12.5px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 6px !important;
}

/* download button */
.stDownloadButton>button{
    background: transparent !important;
    color: var(--gold) !important;
    border: 1px solid var(--gold) !important;
    font-family:'IBM Plex Mono', monospace !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    font-size: 12px !important;
    border-radius: 3px !important;
}
.stDownloadButton>button:hover{ background: rgba(217,164,65,0.12) !important; }

hr{ border-color: rgba(217,164,65,0.2) !important; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# STATE
# ----------------------------------------------------------------------------
if "state" not in st.session_state:
    st.session_state.state = None
if "topic" not in st.session_state:
    st.session_state.topic = ""
if "running" not in st.session_state:
    st.session_state.running = False
if "case_no" not in st.session_state:
    st.session_state.case_no = datetime.now().strftime("%Y%m%d-%H%M")

# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🗂️ The Dossier")
    st.markdown(
        "<span style='font-family:IBM Plex Mono; font-size:12px; color:#9AA5B1;'>"
        "A four-stage investigation, run by four specialist agents."
        "</span>", unsafe_allow_html=True
    )
    st.divider()
    st.markdown(
        "**EXHIBIT 01** — Search Agent  \n"
        "**EXHIBIT 02** — Reader Agent  \n"
        "**EXHIBIT 03** — Writer  \n"
        "**EXHIBIT 04** — Critic  \n"
    )
    st.divider()
    if st.session_state.state:
        st.success("Case closed — results below.")
        if st.button("🗑️ Open a new case", use_container_width=True):
            st.session_state.state = None
            st.session_state.topic = ""
            st.session_state.case_no = datetime.now().strftime("%Y%m%d-%H%M")
            st.rerun()

# ----------------------------------------------------------------------------
# MASTHEAD
# ----------------------------------------------------------------------------
st.markdown(f"""
<div class="dossier-header">
    <div>
        <div class="dossier-eyebrow">Confidential &nbsp;·&nbsp; Multi-Agent Investigation</div>
        <p class="dossier-title">The Research Dossier</p>
    </div>
    <div class="dossier-sub">
        CASE NO. {st.session_state.case_no}<br/>
        STATUS: {"IN PROGRESS" if st.session_state.running else ("CLOSED" if st.session_state.state else "AWAITING TOPIC")}
    </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# ----------------------------------------------------------------------------
# EXHIBIT CARDS (pipeline overview)
# ----------------------------------------------------------------------------
st.markdown("""
<div class="exhibit-row">
    <div class="exhibit-card" style="--accent:#3FA796;">
        <span class="stamp-corner">01</span>
        <span class="exhibit-tag" style="color:#3FA796;">Search Agent</span>
        <p class="exhibit-title">Gathers the leads</p>
        <p class="exhibit-desc">Finds recent, reliable sources on the topic.</p>
    </div>
    <div class="exhibit-card" style="--accent:#D9A441;">
        <span class="stamp-corner">02</span>
        <span class="exhibit-tag" style="color:#D9A441;">Reader Agent</span>
        <p class="exhibit-title">Reads the evidence</p>
        <p class="exhibit-desc">Scrapes the most relevant source in depth.</p>
    </div>
    <div class="exhibit-card" style="--accent:#8C7AE6;">
        <span class="stamp-corner">03</span>
        <span class="exhibit-tag" style="color:#8C7AE6;">Writer</span>
        <p class="exhibit-title">Drafts the report</p>
        <p class="exhibit-desc">Synthesizes findings into a coherent brief.</p>
    </div>
    <div class="exhibit-card" style="--accent:#C1666B;">
        <span class="stamp-corner">04</span>
        <span class="exhibit-tag" style="color:#C1666B;">Critic</span>
        <p class="exhibit-title">Reviews the case</p>
        <p class="exhibit-desc">Checks the draft and flags weak points.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# INPUT FORM
# ----------------------------------------------------------------------------
with st.form("research_form"):
    topic = st.text_input(
        "Topic under investigation",
        placeholder="e.g. Latest advances in solid-state batteries",
        value=st.session_state.topic,
    )
    submitted = st.form_submit_button(
        "Open Case & Investigate",
        use_container_width=True,
        disabled=st.session_state.running,
    )

if submitted:
    if not topic.strip():
        st.warning("Enter a topic before opening the case.")
    else:
        st.session_state.topic = topic
        st.session_state.running = True
        st.session_state.case_no = datetime.now().strftime("%Y%m%d-%H%M")

        status_box = st.status("Investigation underway...", expanded=True)
        try:
            status_box.markdown(
                "<span class='pulse-dot'></span>**Exhibit 01** — Search agent is looking for sources...",
                unsafe_allow_html=True,
            )
            status_box.markdown(
                "<span class='pulse-dot'></span>**Exhibit 02** — Reader agent will scrape the top result...",
                unsafe_allow_html=True,
            )
            status_box.markdown(
                "<span class='pulse-dot'></span>**Exhibit 03** — Writer is drafting the report...",
                unsafe_allow_html=True,
            )
            status_box.markdown(
                "<span class='pulse-dot'></span>**Exhibit 04** — Critic is reviewing the draft...",
                unsafe_allow_html=True,
            )

            # NOTE: run_research_pipeline() executes all four stages internally
            # and only returns once everything is finished, so true live,
            # per-stage progress isn't available without refactoring
            # pipeline.py into a generator. The messages above set
            # expectations up front while the single call is in flight.
            result = run_research_pipeline(topic)

            st.session_state.state = result
            status_box.update(label="Investigation complete — case closed.", state="complete", expanded=False)
        except Exception as e:
            status_box.update(label="Investigation failed.", state="error")
            st.error(f"The pipeline hit an error:\n\n{e}")
        finally:
            st.session_state.running = False
            st.rerun()

# ----------------------------------------------------------------------------
# RESULTS
# ----------------------------------------------------------------------------
if st.session_state.state:
    state = st.session_state.state
    st.divider()
    st.markdown(f"#### Findings — *{st.session_state.topic}*")

    tab_report, tab_feedback, tab_scraped, tab_search = st.tabs(
        ["📄 Exhibit 03 — Report", "🧐 Exhibit 04 — Critic Notes", "📖 Exhibit 02 — Scraped Source", "🔍 Exhibit 01 — Search Leads"]
    )

    with tab_report:
        st.markdown(f"<div class='parchment'>{state.get('report', '_No report generated._')}</div>", unsafe_allow_html=True)
        st.write("")
        st.download_button(
            "Export Report (.md)",
            data=str(state.get("report", "")),
            file_name=f"case_{st.session_state.case_no}_report.md",
            mime="text/markdown",
        )

    with tab_feedback:
        st.markdown(state.get("feedback", "_No feedback generated._"))

    with tab_scraped:
        st.text_area("Scraped content", value=str(state.get("scraped_content", "")), height=380, label_visibility="collapsed")

    with tab_search:
        st.text_area("Raw search results", value=str(state.get("search_results", "")), height=300, label_visibility="collapsed")
else:
    st.info("No open case yet. Enter a topic above and click **Open Case & Investigate**.")