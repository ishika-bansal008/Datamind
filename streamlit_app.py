from __future__ import annotations

import html
import json
from datetime import datetime
from typing import Any

import requests
import streamlit as st
import streamlit.components.v1 as components


# -----------------------------------------------------------------------------
# DataMind — Premium Streamlit workspace
# Uses the existing FastAPI endpoints; no Gemini key is exposed to the browser.
# -----------------------------------------------------------------------------

APP_NAME = "DataMind"
DEFAULT_API_URL = "https://datamind-api-gaxe.onrender.com"
SAMPLE_TEXT = """ARTIFICIAL INTELLIGENCE (AI)

Artificial Intelligence is a branch of computer science that enables machines to perform tasks that normally require human intelligence. These tasks include learning, reasoning, problem-solving, understanding languages, recognizing images, and making decisions.

1. TYPES OF ARTIFICIAL INTELLIGENCE

Narrow AI is designed to perform a specific task. Examples include voice assistants, recommendation systems, facial recognition, and spam filters.

General AI is a theoretical form of AI that could perform different intellectual tasks like a human being.

Super AI is a hypothetical form of AI that would exceed human intelligence in almost every field.

2. MACHINE LEARNING

Machine Learning is a subset of Artificial Intelligence. It enables computers to learn patterns from data and make predictions without being explicitly programmed for every situation.

Its main types are supervised learning, unsupervised learning, and reinforcement learning.

3. DEEP LEARNING

Deep Learning is a subset of Machine Learning that uses artificial neural networks with multiple layers. It is useful for recognizing complex patterns in large amounts of data.

4. APPLICATIONS OF AI

Healthcare: AI can help doctors analyze medical images, identify possible diseases, monitor patients, and support medical research.

Education: AI-powered learning platforms can provide personalized learning experiences, automated quizzes, feedback, and virtual tutoring.

Banking: Banks use AI for fraud detection, transaction monitoring, risk analysis, customer support, and identifying unusual financial activities.

Transportation: AI supports route optimization, traffic prediction, driver assistance, and the development of autonomous vehicles.

Agriculture: AI can help monitor crop health, analyze soil conditions, predict weather patterns, and improve irrigation decisions.

5. HOW AI WORKS

Step 1: Data Collection — Gather relevant information from different sources.
Step 2: Data Preparation — Clean and organize the collected data.
Step 3: Model Training — Use an appropriate algorithm to learn patterns from data.
Step 4: Model Evaluation — Test the model using new data and measure its performance.
Step 5: Prediction — Use the trained model to generate predictions or decisions.
Step 6: Improvement — Monitor performance and update the model when necessary.

6. BENEFITS AND CHALLENGES

Benefits include automation of repetitive tasks, faster data analysis, improved productivity, personalized recommendations, and support for research.

Challenges include data privacy concerns, bias in training data, development costs, job displacement in some sectors, and misleading AI-generated information.

CONCLUSION

Artificial Intelligence is transforming how people work, learn, communicate, and solve problems. It should be developed and used responsibly, with appropriate human supervision and attention to privacy, fairness, and safety."""

FORMATS: dict[str, dict[str, str]] = {
    "Flowchart": {"id": "flowchart", "icon": "↳", "desc": "Visualize a process from beginning to end."},
    "Mind Map": {"id": "mindmap", "icon": "◎", "desc": "Explore a central idea and its connections."},
    "Structured Notes": {"id": "structured_notes", "icon": "▤", "desc": "Turn rough material into clear study notes."},
    "Infographic": {"id": "infographic", "icon": "▦", "desc": "Highlight key facts in visual cards."},
    "Timeline": {"id": "timeline", "icon": "◷", "desc": "Arrange events and stages in sequence."},
    "Comparison Table": {"id": "comparison_table", "icon": "⊞", "desc": "Compare concepts side by side."},
    "Step-by-Step Guide": {"id": "step_by_step", "icon": "☷", "desc": "Break a task into actionable steps."},
    "Flashcards": {"id": "flashcards", "icon": "▣", "desc": "Review concepts with question-and-answer cards."},
    "Smart Summary": {"id": "summary", "icon": "≡", "desc": "Capture the essential ideas quickly."},
    "Workflow": {"id": "workflow", "icon": "⇢", "desc": "Map stages, actions, and decisions."},
    "Mermaid Diagram": {"id": "mermaid", "icon": "⌘", "desc": "Generate editable Mermaid diagram syntax."},
    "Presentation": {"id": "presentation", "icon": "▧", "desc": "Organize content into a slide-by-slide outline."},
}


st.set_page_config(
    page_title="DataMind — Knowledge Workspace",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_api_url() -> str:
    try:
        configured = st.secrets.get("API_BASE_URL", DEFAULT_API_URL)
    except Exception:
        configured = DEFAULT_API_URL
    return str(configured).strip().rstrip("/") or DEFAULT_API_URL


API_URL = get_api_url()


@st.cache_data(ttl=60, show_spinner=False)
def check_backend(base_url: str) -> tuple[bool, dict[str, Any] | str]:
    try:
        response = requests.get(f"{base_url}/api/health", timeout=12)
        response.raise_for_status()
        payload = response.json()
        return True, payload if isinstance(payload, dict) else {}
    except requests.RequestException as exc:
        return False, str(exc)
    except ValueError:
        return False, "The backend returned an unreadable health response."


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');
        :root {
          --dm-bg: #0b1120; --dm-sidebar: #080e1b; --dm-panel: #111b2e;
          --dm-panel-2: #15223a; --dm-border: rgba(151,169,207,.15);
          --dm-text: #edf2ff; --dm-muted: #9aa9c6; --dm-subtle: #71819f;
          --dm-accent: #8b8fff; --dm-accent-2: #b0b2ff; --dm-teal: #59d4b5;
        }
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
        .stApp { background: radial-gradient(ellipse at 78% 0%, rgba(86,91,190,.13), transparent 31%), var(--dm-bg); color: var(--dm-text); }
        [data-testid="stHeader"] { background: rgba(11,17,32,.72); }
        [data-testid="stToolbar"] { right: 1rem; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg,#080e1b 0%,#0b1425 100%); border-right: 1px solid var(--dm-border); }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.1rem; }
        [data-testid="stSidebar"] * { color: #dce5fb; }
        [data-testid="stMainBlockContainer"] { max-width: 1480px; padding-top: 1.6rem; padding-bottom: 3rem; }
        h1,h2,h3,h4 { color: var(--dm-text) !important; font-family: 'Manrope','DM Sans',sans-serif !important; letter-spacing: -.035em; }
        p, li, label, .stMarkdown { color: #c1cce1; }
        small { color: var(--dm-muted); }
        .dm-brand { display:flex; align-items:center; gap:11px; padding: 3px 4px 20px; }
        .dm-logo { width:39px; height:39px; display:grid; place-items:center; border-radius:13px; color:white; font-size:21px; font-weight:800; background:linear-gradient(145deg,#9396ff,#5d64d9); box-shadow:0 8px 24px rgba(105,111,244,.28); }
        .dm-brand-name { font-family:'Manrope',sans-serif; color:#f4f6ff; font-size:19px; line-height:1.05; font-weight:800; letter-spacing:-.7px; }
        .dm-brand-tag { color:#7888a7; font-size:8px; letter-spacing:1.7px; font-weight:800; margin-top:5px; }
        .dm-side-label { color:#71809d; font-size:9px; letter-spacing:1.7px; font-weight:800; margin:19px 0 8px 4px; }
        .dm-workspace { display:flex; gap:9px; align-items:center; background:rgba(144,156,193,.07); border:1px solid var(--dm-border); border-radius:13px; padding:11px; margin-bottom:13px; }
        .dm-workspace-icon { width:29px; height:29px; display:grid; place-items:center; border-radius:9px; background:#e5e7ff; color:#5f62d1; font-weight:900; }
        .dm-workspace strong { display:block; color:#eef2ff; font-size:11px; }
        .dm-workspace span { display:block; color:#7e8eac; font-size:9px; margin-top:3px; }
        .dm-side-note { border:1px solid rgba(139,143,255,.2); background:linear-gradient(140deg,rgba(93,101,198,.17),rgba(27,43,72,.35)); border-radius:13px; padding:13px; margin-top:16px; }
        .dm-side-note strong { color:#f0f2ff; font-size:11px; }
        .dm-side-note p { color:#98a7c3; font-size:10px; line-height:1.55; margin:7px 0 0; }
        .dm-topline { display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:17px; }
        .dm-breadcrumb { color:#8190ad; font-size:10px; letter-spacing:.08em; text-transform:uppercase; font-weight:800; }
        .dm-status { display:inline-flex; align-items:center; gap:7px; border:1px solid rgba(89,212,181,.2); background:rgba(61,181,150,.08); border-radius:100px; padding:7px 11px; color:#80e2c8; font-size:10px; font-weight:700; white-space:nowrap; }
        .dm-status-dot { width:6px; height:6px; border-radius:50%; background:#59d4b5; box-shadow:0 0 0 4px rgba(89,212,181,.11); }
        .dm-status.offline { color:#ffc0a8; border-color:rgba(255,143,110,.2); background:rgba(255,143,110,.08); }
        .dm-status.offline .dm-status-dot { background:#ff9b78; box-shadow:0 0 0 4px rgba(255,155,120,.1); }
        .dm-hero { position:relative; overflow:hidden; border:1px solid rgba(148,157,255,.19); border-radius:22px; padding:27px 30px 25px; background:linear-gradient(115deg,rgba(30,42,77,.92),rgba(17,29,50,.94) 58%,rgba(29,39,78,.83)); box-shadow:0 18px 55px rgba(0,0,0,.15); margin-bottom:21px; }
        .dm-hero:after { content:''; position:absolute; width:250px; height:250px; right:-75px; top:-135px; border-radius:50%; background:radial-gradient(circle,rgba(141,143,255,.25),transparent 68%); pointer-events:none; }
        .dm-eyebrow { display:flex; align-items:center; gap:8px; text-transform:uppercase; color:#a9adff; letter-spacing:1.8px; font-size:9px; font-weight:800; margin-bottom:12px; }
        .dm-eyebrow:before { content:''; width:19px; height:1px; background:#858aff; }
        .dm-hero h1 { font-size:clamp(25px,3vw,38px); line-height:1.13; max-width:760px; margin:0 0 10px; color:#f5f7ff !important; }
        .dm-hero h1 span { color:#a9abff; }
        .dm-hero p { color:#aebbd3; max-width:660px; font-size:12px; line-height:1.7; margin:0; }
        .dm-pills { display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }
        .dm-pill { border:1px solid rgba(174,185,225,.16); background:rgba(10,17,34,.25); border-radius:100px; padding:6px 10px; color:#c6d0e7; font-size:9px; font-weight:700; }
        .dm-section-head { display:flex; justify-content:space-between; align-items:end; gap:12px; margin:18px 0 11px; }
        .dm-section-head h3 { font-size:17px; margin:0; }
        .dm-section-head p { font-size:10px; color:#8292af; margin:4px 0 0; }
        .dm-step { color:#9299ff; font-size:9px; letter-spacing:1.4px; font-weight:800; text-transform:uppercase; }
        .dm-card-title { font-size:12px; color:#ecf1ff; font-weight:800; margin-bottom:5px; }
        .dm-card-desc { color:#8797b4; font-size:10px; line-height:1.55; }
        .dm-format-icon { width:34px; height:34px; display:grid; place-items:center; border-radius:11px; color:#b2b4ff; background:rgba(139,143,255,.12); border:1px solid rgba(139,143,255,.13); font-size:18px; margin-bottom:12px; }
        .dm-format-selected { border:1px solid rgba(139,143,255,.45); background:linear-gradient(145deg,rgba(110,115,222,.17),rgba(27,37,65,.72)); border-radius:14px; padding:12px; }
        .dm-metric { border:1px solid var(--dm-border); background:rgba(20,31,52,.78); border-radius:14px; padding:13px 15px; min-height:76px; }
        .dm-metric-label { color:#8292b0; text-transform:uppercase; letter-spacing:1px; font-size:8px; font-weight:800; }
        .dm-metric-value { color:#f2f5ff; font-family:'Manrope'; font-size:21px; font-weight:800; margin-top:5px; }
        .dm-metric-sub { color:#7c8ca9; font-size:9px; margin-top:2px; }
        .dm-result-head { padding:19px 20px; border:1px solid var(--dm-border); border-radius:17px; background:linear-gradient(130deg,rgba(23,37,61,.95),rgba(17,26,45,.95)); margin:8px 0 14px; }
        .dm-result-title { color:#f3f5ff; font-family:'Manrope'; font-weight:800; font-size:22px; letter-spacing:-.6px; margin:5px 0 7px; }
        .dm-result-meta { color:#8292ae; font-size:10px; }
        .dm-ai-tag { display:inline-block; border:1px solid rgba(89,212,181,.19); background:rgba(89,212,181,.08); border-radius:99px; color:#78ddc1; padding:5px 9px; font-size:9px; font-weight:800; letter-spacing:.4px; }
        .dm-fallback-tag { display:inline-block; border:1px solid rgba(240,183,111,.22); background:rgba(240,183,111,.08); border-radius:99px; color:#f0c58e; padding:5px 9px; font-size:9px; font-weight:800; }
        .dm-insight-tag { display:inline-block; border:1px solid rgba(139,143,255,.2); background:rgba(139,143,255,.08); border-radius:99px; color:#bdc0ff; padding:5px 9px; font-size:9px; margin:3px 4px 3px 0; }
        .dm-muted { color:#8191ad; font-size:10px; }
        div[data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--dm-border) !important; background:rgba(17,27,46,.62); border-radius:16px !important; }
        div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input { background:#0d1729 !important; color:#edf2ff !important; border:1px solid rgba(145,164,201,.18) !important; border-radius:12px !important; }
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div { background:#101b30; border-color:rgba(145,164,201,.18); border-radius:10px; }
        div[data-testid="stFileUploader"] section { background:rgba(14,24,42,.65); border:1px dashed rgba(145,164,201,.3); border-radius:14px; }
        div[data-testid="stFileUploader"] section:hover { border-color:#858aff; }
        .stButton > button, .stDownloadButton > button { border-radius:10px; border:1px solid rgba(145,164,201,.2); background:#17243b; color:#e8edff; font-weight:700; font-size:11px; min-height:39px; transition:all .18s ease; }
        .stButton > button:hover, .stDownloadButton > button:hover { border-color:rgba(147,151,255,.65); color:#fff; background:#202d4a; }
        .stButton > button[kind="primary"] { background:linear-gradient(110deg,#777ce9,#6268d9); border:1px solid rgba(177,180,255,.45); color:#fff; box-shadow:0 8px 23px rgba(102,107,221,.22); }
        .stButton > button[kind="primary"]:hover { background:linear-gradient(110deg,#888dff,#7076e8); border-color:#b5b7ff; }
        div[data-testid="stTabs"] button { color:#9baac5; font-size:11px; }
        div[data-testid="stTabs"] button[aria-selected="true"] { color:#bfc1ff; }
        div[data-testid="stAlert"] { border-radius:12px; }
        div[data-testid="stMetric"] { background:rgba(20,31,52,.7); border:1px solid var(--dm-border); border-radius:13px; padding:12px; }
        div[data-testid="stMetricLabel"] { color:#8796b1; }
        div[data-testid="stMetricValue"] { color:#eff2ff; }
        hr { border-color:rgba(145,164,201,.13); }
        code { color:#c7c9ff !important; }
        .dm-footer { text-align:center; color:#647490; font-size:9px; padding:24px 0 4px; letter-spacing:.4px; }
        @media (max-width: 760px) {
          [data-testid="stMainBlockContainer"] { padding:1rem .8rem 2rem; }
          .dm-hero { padding:21px 18px; }
          .dm-topline { align-items:flex-start; flex-direction:column; }
          .dm-result-title { font-size:19px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "page": "Create",
        "source_text": "",
        "last_result": None,
        "last_options": None,
        "last_source_text": "",
        "history": [],
        "saved_projects": [],
        "notification": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def section_head(step: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="dm-section-head"><div><div class="dm-step">{step}</div>'
        f'<h3>{title}</h3><p>{subtitle}</p></div></div>',
        unsafe_allow_html=True,
    )


def render_sidebar(backend_ok: bool, backend_info: Any) -> str:
    with st.sidebar:
        st.markdown(
            '<div class="dm-brand"><div class="dm-logo">✳</div><div>'
            '<div class="dm-brand-name">DataMind</div>'
            '<div class="dm-brand-tag">MASTER KNOWLEDGE WORKSPACE</div></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="dm-workspace"><div class="dm-workspace-icon">D</div><div>'
            '<strong>Personal workspace</strong><span>Knowledge Studio · v3.0</span></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="dm-side-label">WORKSPACE</div>', unsafe_allow_html=True)
        page = st.radio(
            "Workspace navigation",
            ["Create", "History", "Saved projects"],
            index=["Create", "History", "Saved projects"].index(st.session_state.page)
            if st.session_state.page in ["Create", "History", "Saved projects"] else 0,
            label_visibility="collapsed",
            format_func=lambda item: {"Create": "✦  New transformation", "History": "◷  Recent history", "Saved projects": "▣  Saved projects"}[item],
            key="dm_navigation",
        )
        st.session_state.page = page
        st.markdown('<div class="dm-side-label">WORKSPACE STATUS</div>', unsafe_allow_html=True)
        if backend_ok:
            st.markdown('<div class="dm-status"><span class="dm-status-dot"></span> API connected</div>', unsafe_allow_html=True)
            if isinstance(backend_info, dict):
                mode = backend_info.get("mode") or backend_info.get("provider") or "Ready"
                st.caption(f"Backend: {mode}")
        else:
            st.markdown('<div class="dm-status offline"><span class="dm-status-dot"></span> API unreachable</div>', unsafe_allow_html=True)
            st.caption("The app UI is available, but transformations need the API.")
        st.markdown(
            '<div class="dm-side-note"><strong>✧ Built for clearer thinking</strong>'
            '<p>Turn dense information into structured knowledge, useful visuals and learning assets.</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="dm-footer">DATAMIND · THINK CLEARER</div>', unsafe_allow_html=True)
    return page


def build_options() -> dict[str, str]:
    with st.sidebar:
        st.markdown('<div class="dm-side-label">TRANSFORMATION SETTINGS</div>', unsafe_allow_html=True)
        format_label = st.selectbox("Output format", list(FORMATS.keys()), index=2, key="dm_format")
        detail = st.select_slider("Level of detail", options=["short", "medium", "detailed"], value="detailed", format_func=lambda x: x.title(), key="dm_detail")
        language = st.selectbox("Output language", ["English", "Hindi", "Hinglish"], key="dm_language")
        complexity = st.selectbox("Complexity", ["beginner", "intermediate", "advanced"], format_func=str.title, key="dm_complexity")
        audience = st.selectbox("Designed for", ["students", "professionals", "developers", "general users"], format_func=lambda x: x.title(), key="dm_audience")
        visual_style = st.selectbox("Visual direction", ["professional", "minimal", "colorful"], format_func=str.title, key="dm_visual_style")
        st.caption("These settings are sent with each transformation request.")
    return {
        "format": FORMATS[format_label]["id"],
        "detail": detail,
        "language": language,
        "complexity": complexity,
        "audience": audience,
        "visual_style": visual_style,
    }


def readable_error(response: requests.Response) -> str:
    try:
        payload = response.json()
        detail = payload.get("detail", payload.get("message", payload))
        if isinstance(detail, list):
            return "; ".join(str(item.get("msg", item)) for item in detail)
        return str(detail)
    except ValueError:
        return response.text[:600] or f"Request failed with status {response.status_code}."


def run_text_transform(source: str, options: dict[str, str]) -> dict[str, Any]:
    response = requests.post(
        f"{API_URL}/api/transform",
        json={"text": source, **options},
        timeout=(10, 150),
    )
    if not response.ok:
        raise RuntimeError(f"API error {response.status_code}: {readable_error(response)}")
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("The API returned an unexpected response format.")
    return payload


def run_file_transform(uploaded_file: Any, options: dict[str, str]) -> dict[str, Any]:
    file_bytes = uploaded_file.getvalue()
    files = {"file": (uploaded_file.name, file_bytes, uploaded_file.type or "application/octet-stream")}
    response = requests.post(
        f"{API_URL}/api/transform/file",
        data=options,
        files=files,
        timeout=(10, 180),
    )
    if not response.ok:
        raise RuntimeError(f"API error {response.status_code}: {readable_error(response)}")
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("The API returned an unexpected response format.")
    return payload


def refine_result(result: dict[str, Any], instruction: str, language: str, complexity: str) -> dict[str, Any]:
    response = requests.post(
        f"{API_URL}/api/refine",
        json={"instruction": instruction, "result": result, "language": language, "complexity": complexity},
        timeout=(10, 150),
    )
    if not response.ok:
        raise RuntimeError(f"API error {response.status_code}: {readable_error(response)}")
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("The API returned an unexpected response format.")
    return payload


def add_to_history(result: dict[str, Any], source: str, options: dict[str, str]) -> None:
    item = {
        "id": result.get("id") or f"{datetime.now().timestamp()}",
        "title": result.get("title") or "Untitled transformation",
        "format": result.get("format") or options.get("format", "transformation"),
        "created_at": result.get("created_at") or datetime.now().isoformat(),
        "result": result,
        "source": source,
        "options": options,
    }
    history = st.session_state.history
    history.insert(0, item)
    st.session_state.history = history[:30]


def mermaid_html(code: str) -> str:
    # Mermaid is rendered inside an isolated component iframe with strict security.
    safe_code = json.dumps(code)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body{{margin:0;background:#f9fbff;color:#26324a;font-family:Arial,sans-serif;}}
.wrap{{min-height:360px;padding:20px;display:flex;align-items:center;justify-content:center;overflow:auto;}}
#diagram{{width:100%;display:flex;justify-content:center;}}
#diagram svg{{max-width:100%;height:auto;}}
#error{{display:none;color:#9b4b48;background:#fff0ee;border:1px solid #f0d2ce;padding:12px 15px;border-radius:10px;font-size:13px;}}
</style></head><body><div class="wrap"><div id="diagram"></div><div id="error"></div></div>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
const source = {safe_code};
mermaid.initialize({{startOnLoad:false,securityLevel:'strict',theme:'base',fontFamily:'Arial, sans-serif',flowchart:{{htmlLabels:false,curve:'basis',useMaxWidth:true,nodeSpacing:42,rankSpacing:48}},themeVariables:{{background:'#f9fbff',primaryColor:'#eef0ff',primaryTextColor:'#202943',primaryBorderColor:'#858be3',secondaryColor:'#e4f5ef',secondaryTextColor:'#202943',secondaryBorderColor:'#63ad98',tertiaryColor:'#fff3e4',tertiaryTextColor:'#202943',tertiaryBorderColor:'#d7a567',lineColor:'#8791b2',textColor:'#202943',edgeLabelBackground:'#ffffff',fontSize:'15px'}}}});
try {{ const {{svg}} = await mermaid.render('datamind-diagram', source); document.getElementById('diagram').innerHTML = svg; }}
catch (err) {{ const box=document.getElementById('error'); box.style.display='block'; box.textContent='Diagram preview could not be rendered: '+String(err?.message||err).split('\\n')[0]; }}
</script></body></html>"""


def table_to_columns(table: dict[str, Any]) -> dict[str, list[Any]] | None:
    headers = table.get("headers")
    rows = table.get("rows")
    if not isinstance(headers, list) or not isinstance(rows, list) or not headers:
        return None
    columns: dict[str, list[Any]] = {}
    for index, header in enumerate(headers):
        name = str(header) or f"Column {index + 1}"
        columns[name] = [row[index] if isinstance(row, list) and index < len(row) else "" for row in rows]
    return columns


def render_cards(cards: list[Any], fmt: str) -> None:
    if not cards:
        return
    st.markdown("#### Generated learning assets")
    if fmt == "flashcards":
        for index, item in enumerate(cards, 1):
            if not isinstance(item, dict):
                continue
            question = item.get("question") or f"Card {index}"
            answer = item.get("answer") or "Answer not provided."
            with st.expander(f"{index:02d}  ·  {question}"):
                st.markdown(answer)
    else:
        for start in range(0, len(cards), 3):
            group = cards[start:start + 3]
            cols = st.columns(len(group))
            for col, item in zip(cols, group):
                if not isinstance(item, dict):
                    continue
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{item.get('title') or f'Insight {start + 1}'}**")
                        st.markdown(str(item.get("body") or item.get("description") or item.get("content") or ""))


def render_source_coverage(result: dict[str, Any]) -> None:
    coverage = result.get("coverage")
    if isinstance(coverage, dict) and coverage.get("trackable"):
        expected = coverage.get("expected_count", 0)
        actual = coverage.get("actual_count", 0)
        missing = coverage.get("missing_count", 0)
        c1, c2, c3 = st.columns(3)
        c1.metric("Records detected", actual)
        c2.metric("Expected records", expected)
        c3.metric("Not extracted", missing)
        if coverage.get("warning"):
            if missing:
                st.warning(coverage["warning"])
            else:
                st.info(coverage["warning"])
        elif coverage.get("complete"):
            st.success("All records detected in the extracted source have been preserved.")
    source_table = result.get("source_table") or result.get("table")
    if isinstance(source_table, dict):
        columns = table_to_columns(source_table)
        if columns:
            st.markdown("#### Complete source register")
            st.dataframe(columns, use_container_width=True, hide_index=True)
    source_items = result.get("source_items")
    if isinstance(source_items, list) and source_items:
        st.markdown("#### Extracted source items")
        for index, item in enumerate(source_items, 1):
            if isinstance(item, dict):
                st.markdown(f"**{index}. {item.get('label') or f'Item {index}'}**  \n{item.get('details') or ''}")
            else:
                st.markdown(f"{index}. {item}")


def build_result_markdown(result: dict[str, Any]) -> str:
    parts = [f"# {result.get('title') or 'DataMind result'}", f"Format: {result.get('format') or 'transformation'}", "", str(result.get("content") or "")]
    important_words = result.get("important_words") or []
    important_lines = result.get("important_lines") or []
    if important_words:
        parts += ["", "## Important words", "", ", ".join(map(str, important_words))]
    if important_lines:
        parts += ["", "## Important lines extracted from source", ""]
        parts.extend(f"{index}. {line}" for index, line in enumerate(important_lines, 1))
    return "\n".join(parts)


def render_result(result: dict[str, Any]) -> None:
    fmt = str(result.get("format") or "transformation")
    label = next((name for name, value in FORMATS.items() if value["id"] == fmt), fmt.replace("_", " ").title())
    is_fallback = result.get("mode") in {"demo", "demo-fallback"}
    status_tag = '<span class="dm-fallback-tag">LOCAL FALLBACK</span>' if is_fallback else '<span class="dm-ai-tag">✦ GEMINI AI</span>'
    created = result.get("created_at") or "Just now"
    if isinstance(created, str) and "T" in created:
        created = created.replace("T", " ").replace("+00:00", " UTC")[:19]
    st.markdown(
        f'<div class="dm-result-head"><div class="dm-step">TRANSFORMATION COMPLETE</div>'
        f'<div class="dm-result-title">{html.escape(str(result.get("title") or label))}</div>'
        f'<div class="dm-result-meta">{html.escape(label)} &nbsp;·&nbsp; {html.escape(str(created))} &nbsp;&nbsp; {status_tag}</div></div>',
        unsafe_allow_html=True,
    )
    if is_fallback:
        st.warning("This result was produced by the local fallback because Gemini was unavailable, busy, or not configured. Check the backend logs to confirm AI mode.")
    if result.get("ai_error"):
        st.caption(str(result["ai_error"]))
    if result.get("source_truncated"):
        st.warning("The AI context was compacted. Review the complete source register below for source coverage.")

    important_words = result.get("important_words") or []
    if important_words:
        tags = "".join(f'<span class="dm-insight-tag">{html.escape(str(word)[:70])}</span>' for word in important_words[:30])
        st.markdown(f"<div style='margin:10px 0 16px'>{tags}</div>", unsafe_allow_html=True)

    tab_overview, tab_visual, tab_source, tab_raw = st.tabs(["✦  Overview", "▧  Visual output", "◫  Source & coverage", "{}  Raw data"])
    with tab_overview:
        st.markdown(str(result.get("content") or "No written explanation was returned."))
        important_lines = result.get("important_lines") or []
        if important_lines:
            with st.expander("Important lines extracted from the original source"):
                for line in important_lines:
                    st.markdown(f"- {line}")
    with tab_visual:
        mermaid = result.get("mermaid")
        if mermaid:
            st.markdown("#### Diagram preview")
            components.html(mermaid_html(str(mermaid)), height=430, scrolling=True)
            with st.expander("View / copy Mermaid source"):
                st.code(str(mermaid), language="mermaid")
                st.download_button("Download Mermaid source", data=str(mermaid), file_name="datamind-diagram.mmd", mime="text/plain", key="download_mermaid")
        else:
            st.info("No diagram was returned for this output format. Explore the generated cards or table below.")
        render_cards(result.get("cards") or [], fmt)
        table = result.get("table")
        if isinstance(table, dict):
            columns = table_to_columns(table)
            if columns:
                st.markdown("#### Generated table")
                st.dataframe(columns, use_container_width=True, hide_index=True)
    with tab_source:
        render_source_coverage(result)
        if not result.get("coverage") and not result.get("source_items") and not result.get("source_table"):
            st.caption("No separate source-register metadata was returned for this result.")
    with tab_raw:
        st.json(result, expanded=True)

    st.markdown("#### Export your work")
    export_col1, export_col2, export_col3 = st.columns(3)
    export_markdown = build_result_markdown(result)
    with export_col1:
        st.download_button("↓  Markdown", data=export_markdown, file_name="datamind-result.md", mime="text/markdown", use_container_width=True, key="download_result_md")
    with export_col2:
        st.download_button("↓  JSON", data=json.dumps(result, ensure_ascii=False, indent=2), file_name="datamind-result.json", mime="application/json", use_container_width=True, key="download_result_json")
    with export_col3:
        if result.get("mermaid"):
            st.download_button("↓  Diagram code", data=str(result["mermaid"]), file_name="datamind-diagram.mmd", mime="text/plain", use_container_width=True, key="download_result_mmd")
        else:
            st.download_button("↓  Source text", data=st.session_state.get("last_source_text", ""), file_name="datamind-source.txt", mime="text/plain", use_container_width=True, key="download_source_text")


def render_create_page(options: dict[str, str], backend_ok: bool) -> None:
    st.markdown(
        '<div class="dm-hero"><div class="dm-eyebrow">INTELLIGENT KNOWLEDGE WORKSPACE</div>'
        '<h1>From raw information to<br><span>clear understanding.</span></h1>'
        '<p>Bring your notes, research and documents into one focused workspace. DataMind structures the information into useful explanations, learning assets and visual knowledge.</p>'
        '<div class="dm-pills"><span class="dm-pill">✦ AI-powered transformation</span><span class="dm-pill">12 output formats</span><span class="dm-pill">PDF · DOCX · TXT · CSV · JSON</span></div></div>',
        unsafe_allow_html=True,
    )

    stat1, stat2, stat3 = st.columns(3)
    with stat1:
        st.markdown('<div class="dm-metric"><div class="dm-metric-label">OUTPUT FORMATS</div><div class="dm-metric-value">12</div><div class="dm-metric-sub">One source, multiple ways to learn</div></div>', unsafe_allow_html=True)
    with stat2:
        st.markdown('<div class="dm-metric"><div class="dm-metric-label">INPUT TYPES</div><div class="dm-metric-value">7+</div><div class="dm-metric-sub">Text and common document formats</div></div>', unsafe_allow_html=True)
    with stat3:
        st.markdown(f'<div class="dm-metric"><div class="dm-metric-label">BACKEND STATUS</div><div class="dm-metric-value" style="font-size:18px;color:{"#72dfc2" if backend_ok else "#ffad91"}">{"Connected" if backend_ok else "Offline"}</div><div class="dm-metric-sub">Render API · health check</div></div>', unsafe_allow_html=True)

    section_head("01 / SOURCE MATERIAL", "Start with your information", "Paste raw text or upload a document. Keep the original source as complete as possible.")
    input_method = st.radio(
        "Choose your source",
        ["Paste text", "Upload document"],
        horizontal=True,
        label_visibility="collapsed",
        key="dm_input_method",
    )
    source_text = ""
    uploaded_file = None
    if input_method == "Paste text":
        top_a, top_b = st.columns([1, 4])
        with top_a:
            if st.button("↳  Load sample", use_container_width=True):
                st.session_state.source_text = SAMPLE_TEXT
        with top_b:
            st.caption("Try the sample content, or paste your own notes, topic, research or project data.")
        source_text = st.text_area(
            "Source text",
            key="source_text",
            height=245,
            placeholder="Paste your raw information here…\n\nExample: Explain Artificial Intelligence, Machine Learning and their real-world applications.",
            label_visibility="collapsed",
        )
        st.caption(f"{len(source_text):,} characters · Recommended: clear, complete source material")
    else:
        uploaded_file = st.file_uploader(
            "Drop a file here or browse your device",
            type=["pdf", "docx", "txt", "md", "csv", "json"],
            help="Supported: PDF, DOCX, TXT, Markdown, CSV and JSON. Backend upload limit is configured on Render.",
            key="dm_document_upload",
        )
        if uploaded_file:
            st.success(f"Ready to process: {uploaded_file.name} · {uploaded_file.size / 1024:.1f} KB")

    section_head("02 / OUTPUT DESIGN", "Choose how you want to understand it", "Select a format in the sidebar, then generate your structured result.")
    selected = next((name for name, item in FORMATS.items() if item["id"] == options["format"]), "Structured Notes")
    with st.container(border=True):
        format_a, format_b = st.columns([1.1, 4])
        with format_a:
            st.markdown(f'<div class="dm-format-selected"><div class="dm-format-icon">{FORMATS[selected]["icon"]}</div><div class="dm-card-title">{selected}</div><div class="dm-card-desc">Selected format</div></div>', unsafe_allow_html=True)
        with format_b:
            st.markdown(f"**{FORMATS[selected]['desc']}**")
            st.caption(f"{options['detail'].title()} detail · {options['language']} · {options['complexity'].title()} level · {options['audience'].title()}")
            st.caption("Need a different format? Change Output format in the left settings panel.")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    generate_col, helper_col = st.columns([1.3, 3.7])
    with generate_col:
        generate = st.button("✦  Generate transformation", type="primary", use_container_width=True, disabled=not backend_ok)
    with helper_col:
        st.caption("Your Gemini key stays on the backend. DataMind sends the source and selected settings to your Render API.")

    if generate:
        if uploaded_file is None and not source_text.strip():
            st.warning("Add some source text or upload a document before generating.")
        else:
            try:
                with st.spinner("DataMind is organizing your source into clear knowledge…"):
                    result = run_file_transform(uploaded_file, options) if uploaded_file is not None else run_text_transform(source_text, options)
                st.session_state.last_result = result
                st.session_state.last_options = options
                st.session_state.last_source_text = result.get("source_text") or source_text or ""
                history_source = st.session_state.last_source_text
                add_to_history(result, history_source, options)
                st.success("Transformation completed. Your result is ready below.")
            except requests.Timeout:
                st.error("The request timed out. Render may be waking up or the document may be large. Please try again.")
            except requests.RequestException as exc:
                st.error(f"Could not reach the DataMind backend: {exc}")
            except Exception as exc:
                st.error(str(exc))

    result = st.session_state.get("last_result")
    if result:
        section_head("03 / YOUR RESULT", "Knowledge, made clearer", "Review the result, inspect its visuals and export the parts you need.")
        render_result(result)
        with st.expander("✦  Refine this result with another instruction"):
            st.caption("Ask DataMind to simplify, expand, reorganize or explain the current result differently.")
            instruction = st.text_input("Refinement instruction", placeholder="e.g. Make this easier for a BCA first-year student…", key="dm_refine_instruction")
            refine_col, refine_note = st.columns([1, 3])
            with refine_col:
                refine_clicked = st.button("Apply refinement", type="primary", use_container_width=True, disabled=not backend_ok or not bool(instruction.strip()), key="dm_refine_button")
            with refine_note:
                st.caption("Uses your existing POST /api/refine endpoint.")
            if refine_clicked:
                try:
                    with st.spinner("Refining your result…"):
                        updated = refine_result(result, instruction.strip(), options["language"], options["complexity"])
                    st.session_state.last_result = updated
                    st.session_state.last_source_text = st.session_state.get("last_source_text", "")
                    add_to_history(updated, st.session_state.last_source_text, options)
                    st.success("Your result has been refined.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Refinement failed: {exc}")
        save_col, reset_col, spacer = st.columns([1.2, 1.2, 4])
        with save_col:
            if st.button("▣  Save to projects", use_container_width=True):
                saved = st.session_state.saved_projects
                if not any(item.get("id") == result.get("id") for item in saved):
                    saved.insert(0, {"id": result.get("id"), "title": result.get("title"), "format": result.get("format"), "created_at": result.get("created_at"), "result": result, "source": st.session_state.get("last_source_text", ""), "options": options})
                    st.session_state.saved_projects = saved
                st.success("Saved in this session's project library.")
        with reset_col:
            if st.button("＋  New analysis", use_container_width=True):
                st.session_state.last_result = None
                st.session_state.source_text = ""
                st.rerun()


def render_library_page(page: str) -> None:
    is_history = page == "History"
    items = st.session_state.history if is_history else st.session_state.saved_projects
    title = "Recent history" if is_history else "Saved projects"
    st.markdown(f'<div class="dm-eyebrow">YOUR WORKSPACE</div><h2 style="margin-top:0">{title}</h2><p class="dm-muted">{ "Your latest transformations from this active session." if is_history else "Projects you chose to keep in this active session."}</p>', unsafe_allow_html=True)
    if not items:
        with st.container(border=True):
            st.markdown("### Your workspace is ready for its first result")
            st.caption("Create a transformation and it will appear here. Session history is temporary and may reset when the session ends.")
            if st.button("＋  Create a transformation", type="primary"):
                st.session_state.page = "Create"
                st.rerun()
        return
    query = st.text_input("Search this workspace", placeholder="Search by title or format…", key=f"search_{page}")
    filtered = [item for item in items if query.lower() in f"{item.get('title','')} {item.get('format','')}".lower()]
    st.caption(f"{len(filtered)} item(s)")
    for index, item in enumerate(filtered):
        with st.container(border=True):
            col_info, col_button = st.columns([4, 1])
            with col_info:
                st.markdown(f"**{item.get('title') or 'Untitled transformation'}**")
                st.caption(f"{str(item.get('format') or 'transformation').replace('_',' ').title()} · {str(item.get('created_at') or 'Recently')[:19]}")
            with col_button:
                if st.button("Open result", key=f"open_{page}_{index}", use_container_width=True):
                    st.session_state.last_result = item.get("result")
                    st.session_state.last_source_text = item.get("source", "")
                    st.session_state.last_options = item.get("options", {})
                    st.session_state.page = "Create"
                    st.rerun()


def main() -> None:
    init_state()
    inject_styles()
    backend_ok, backend_info = check_backend(API_URL)
    page = render_sidebar(backend_ok, backend_info)
    options = build_options()

    st.markdown(
        f'<div class="dm-topline"><div class="dm-breadcrumb">WORKSPACE <span style="color:#505f7b">/</span> {page.upper()}</div>'
        f'<div class="dm-status {"" if backend_ok else "offline"}"><span class="dm-status-dot"></span>{"System operational" if backend_ok else "Backend unavailable"}</div></div>',
        unsafe_allow_html=True,
    )

    if page == "Create":
        render_create_page(options, backend_ok)
    else:
        render_library_page(page)

    st.markdown('<div class="dm-footer">DATAMIND · TURN RAW DATA INTO CLEAR UNDERSTANDING</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
