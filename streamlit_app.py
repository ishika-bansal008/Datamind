from __future__ import annotations

import html
import json
from datetime import datetime
from typing import Any
from uuid import uuid4

import requests
import streamlit as st
import streamlit.components.v1 as components


# ============================================================================
# DATAMIND | Streamlit Edition
# Frontend-only update. Existing FastAPI endpoints and payload structure kept.
# ============================================================================

APP_NAME = "DataMind"
DEFAULT_API_URL = "https://datamind-api-gaxe.onrender.com"

FORMATS: dict[str, dict[str, str]] = {
    "Flowchart": {
        "id": "flowchart", "icon": "↳",
        "desc": "Visualize a process from beginning to end.",
        "best_for": "Processes, workflows, decision paths and step sequences.",
    },
    "Mind Map": {
        "id": "mindmap", "icon": "◎",
        "desc": "Explore a central idea and its connected concepts.",
        "best_for": "Brainstorming, topic revision and understanding relationships.",
    },
    "Structured Notes": {
        "id": "structured_notes", "icon": "▤",
        "desc": "Turn rough material into organized, easy-to-study notes.",
        "best_for": "Class notes, research, long topics and study material.",
    },
    "Infographic": {
        "id": "infographic", "icon": "▦",
        "desc": "Present key facts as concise visual information blocks.",
        "best_for": "Quick understanding, facts, highlights and summaries.",
    },
    "Timeline": {
        "id": "timeline", "icon": "◷",
        "desc": "Arrange events, milestones or stages in chronological order.",
        "best_for": "History, project milestones and event sequences.",
    },
    "Comparison Table": {
        "id": "comparison_table", "icon": "⊞",
        "desc": "Compare concepts, products or ideas side by side.",
        "best_for": "Differences, similarities, pros and cons.",
    },
    "Step-by-Step Guide": {
        "id": "step_by_step", "icon": "☷",
        "desc": "Break a complex task into clear, actionable steps.",
        "best_for": "Tutorials, procedures, practical tasks and how-to guides.",
    },
    "Flashcards": {
        "id": "flashcards", "icon": "▣",
        "desc": "Create question-and-answer cards for active recall.",
        "best_for": "Exam revision, definitions and self-testing.",
    },
    "Smart Summary": {
        "id": "summary", "icon": "≡",
        "desc": "Extract the essential ideas without losing the main meaning.",
        "best_for": "Long documents, articles and fast reading.",
    },
    "Workflow": {
        "id": "workflow", "icon": "⇢",
        "desc": "Map stages, actions, roles and decision points.",
        "best_for": "Operations, systems and repeatable processes.",
    },
    "Mermaid Diagram": {
        "id": "mermaid", "icon": "⌘",
        "desc": "Generate editable diagram syntax using Mermaid.",
        "best_for": "Technical documentation and diagrams you can edit later.",
    },
    "Presentation": {
        "id": "presentation", "icon": "▧",
        "desc": "Organize information into a slide-by-slide presentation outline.",
        "best_for": "Class presentations, project pitches and briefings.",
    },
}

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


st.set_page_config(
    page_title="DataMind — Turn Information Into Understanding",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def get_api_url() -> str:
    """Read API URL from Streamlit secrets; use the supplied Render URL by default."""
    try:
        value = st.secrets.get("API_BASE_URL", DEFAULT_API_URL)
    except Exception:
        value = DEFAULT_API_URL
    return str(value).strip().rstrip("/") or DEFAULT_API_URL


API_URL = get_api_url()


@st.cache_data(ttl=45, show_spinner=False)
def check_backend(base_url: str) -> tuple[bool, dict[str, Any] | str]:
    try:
        response = requests.get(f"{base_url}/api/health", timeout=15)
        response.raise_for_status()
        data = response.json()
        return True, data if isinstance(data, dict) else {}
    except requests.RequestException as exc:
        return False, str(exc)
    except ValueError:
        return False, "The API returned an unreadable health response."


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');
        :root {
          --bg:#0b1120; --sidebar:#080e1b; --panel:#111b2e; --panel2:#15223a;
          --border:rgba(151,169,207,.15); --text:#edf2ff; --muted:#9aa9c6;
          --subtle:#71819f; --accent:#8b8fff; --accent2:#b0b2ff; --teal:#59d4b5;
        }
        html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
        .stApp { background:radial-gradient(ellipse at 78% 0%,rgba(86,91,190,.13),transparent 33%),var(--bg); color:var(--text); }
        [data-testid="stHeader"] { background:rgba(11,17,32,.82); }
        [data-testid="stSidebar"] { background:linear-gradient(180deg,#080e1b 0%,#0b1425 100%); border-right:1px solid var(--border); }
        [data-testid="stSidebar"] > div:first-child { padding-top:1rem; }
        [data-testid="stSidebar"] * { color:#dce5fb; }
        [data-testid="stMainBlockContainer"] { max-width:1260px; padding-top:1.15rem; padding-bottom:3rem; }
        h1,h2,h3,h4 { color:var(--text)!important; font-family:'Manrope','DM Sans',sans-serif!important; letter-spacing:-.035em; }
        p,li,label,.stMarkdown { color:#c1cce1; }
        .dm-brand { display:flex; align-items:center; gap:10px; padding:3px 4px 20px; }
        .dm-logo { width:39px;height:39px;display:grid;place-items:center;border-radius:13px;color:white;font-size:21px;font-weight:800;background:linear-gradient(145deg,#9396ff,#5d64d9);box-shadow:0 8px 24px rgba(105,111,244,.28); }
        .dm-brand-name { color:#f4f6ff;font-family:'Manrope';font-size:19px;line-height:1.05;font-weight:800;letter-spacing:-.7px; }
        .dm-brand-tag { color:#7888a7;font-size:8px;letter-spacing:1.55px;font-weight:800;margin-top:5px; }
        .dm-side-label { color:#71809d;font-size:9px;letter-spacing:1.7px;font-weight:800;margin:18px 0 8px 4px; }
        .dm-workspace { display:flex;gap:9px;align-items:center;background:rgba(144,156,193,.07);border:1px solid var(--border);border-radius:13px;padding:11px;margin-bottom:13px; }
        .dm-workspace-icon { width:29px;height:29px;display:grid;place-items:center;border-radius:9px;background:#e5e7ff;color:#5f62d1;font-weight:900; }
        .dm-workspace strong { display:block;color:#eef2ff;font-size:11px; }
        .dm-workspace span { display:block;color:#7e8eac;font-size:9px;margin-top:3px; }
        .dm-side-note { border:1px solid rgba(139,143,255,.2);background:linear-gradient(140deg,rgba(93,101,198,.17),rgba(27,43,72,.35));border-radius:13px;padding:13px;margin-top:16px; }
        .dm-side-note strong { color:#f0f2ff;font-size:11px; }
        .dm-side-note p { color:#98a7c3;font-size:10px;line-height:1.55;margin:7px 0 0; }
        .dm-topline { display:flex;justify-content:space-between;align-items:center;gap:12px;margin:0 0 14px; }
        .dm-breadcrumb { color:#8190ad;font-size:9px;letter-spacing:.1em;text-transform:uppercase;font-weight:800; }
        .dm-status { display:inline-flex;align-items:center;gap:7px;border:1px solid rgba(89,212,181,.2);background:rgba(61,181,150,.08);border-radius:100px;padding:6px 10px;color:#80e2c8;font-size:9px;font-weight:700;white-space:nowrap; }
        .dm-status-dot { width:6px;height:6px;border-radius:50%;background:#59d4b5;box-shadow:0 0 0 4px rgba(89,212,181,.11); }
        .dm-status.offline { color:#ffc0a8;border-color:rgba(255,143,110,.2);background:rgba(255,143,110,.08); }
        .dm-status.offline .dm-status-dot { background:#ff9b78;box-shadow:0 0 0 4px rgba(255,155,120,.1); }
        .dm-hero { display:flex;justify-content:space-between;align-items:center;gap:22px;border:1px solid rgba(148,157,255,.18);border-radius:17px;padding:17px 21px;background:linear-gradient(112deg,rgba(30,42,77,.88),rgba(17,29,50,.94) 62%,rgba(29,39,78,.72));box-shadow:0 12px 34px rgba(0,0,0,.12);margin-bottom:18px; }
        .dm-hero-copy { min-width:0; }
        .dm-eyebrow { display:flex;align-items:center;gap:8px;text-transform:uppercase;color:#a9adff;letter-spacing:1.7px;font-size:8px;font-weight:800;margin-bottom:6px; }
        .dm-eyebrow:before { content:'';width:17px;height:1px;background:#858aff; }
        .dm-hero h1 { font-size:clamp(20px,2.2vw,27px);line-height:1.15;margin:0 0 5px;color:#f5f7ff!important; }
        .dm-hero h1 span { color:#a9abff; }
        .dm-hero p { color:#aebbd3;max-width:730px;font-size:10.5px;line-height:1.55;margin:0; }
        .dm-hero-aside { flex:0 0 auto;display:flex;flex-direction:column;gap:6px;align-items:flex-end; }
        .dm-pill { border:1px solid rgba(174,185,225,.16);background:rgba(10,17,34,.25);border-radius:100px;padding:5px 9px;color:#c6d0e7;font-size:8px;font-weight:700;white-space:nowrap; }
        .dm-section { display:flex;justify-content:space-between;align-items:end;gap:12px;margin:16px 0 9px; }
        .dm-section h3 { font-size:16px;margin:2px 0 0; }
        .dm-section p { font-size:9.5px;color:#8292af;margin:3px 0 0; }
        .dm-step { color:#9299ff;font-size:8px;letter-spacing:1.45px;font-weight:800;text-transform:uppercase; }
        .dm-section-number { color:#6c7b99;font-size:9px;font-weight:700; }
        .dm-format-panel { display:flex;align-items:center;gap:13px;border:1px solid rgba(139,143,255,.26);background:linear-gradient(115deg,rgba(99,105,205,.14),rgba(17,27,46,.7));border-radius:12px;padding:11px 13px;margin:6px 0 10px; }
        .dm-format-icon { flex:0 0 auto;width:37px;height:37px;display:grid;place-items:center;border-radius:11px;color:#b2b4ff;background:rgba(139,143,255,.13);border:1px solid rgba(139,143,255,.17);font-size:19px; }
        .dm-format-name { color:#edf1ff;font-size:11px;font-weight:800;margin-bottom:3px; }
        .dm-format-desc { color:#9cacca;font-size:9.5px;line-height:1.45; }
        .dm-format-use { color:#7788a8;font-size:8.5px;margin-top:3px; }
        .dm-help-chip { display:inline-block;border:1px solid rgba(139,143,255,.18);background:rgba(139,143,255,.07);border-radius:100px;padding:4px 8px;color:#b8bbff;font-size:8px;font-weight:700; }
        .dm-result-head { padding:17px 19px;border:1px solid var(--border);border-radius:15px;background:linear-gradient(130deg,rgba(23,37,61,.95),rgba(17,26,45,.95));margin:8px 0 13px; }
        .dm-result-title { color:#f3f5ff;font-family:'Manrope';font-weight:800;font-size:21px;letter-spacing:-.6px;margin:4px 0 6px; }
        .dm-result-meta { color:#8292ae;font-size:9px; }
        .dm-ai-tag,.dm-fallback-tag { display:inline-block;border-radius:99px;padding:4px 8px;font-size:8px;font-weight:800; }
        .dm-ai-tag { border:1px solid rgba(89,212,181,.19);background:rgba(89,212,181,.08);color:#78ddc1; }
        .dm-fallback-tag { border:1px solid rgba(240,183,111,.22);background:rgba(240,183,111,.08);color:#f0c58e; }
        .dm-insight-tag { display:inline-block;border:1px solid rgba(139,143,255,.2);background:rgba(139,143,255,.08);border-radius:99px;color:#bdc0ff;padding:5px 8px;font-size:8px;margin:3px 4px 3px 0; }
        .dm-footer { text-align:center;color:#647490;font-size:8px;padding:22px 0 4px;letter-spacing:.5px; }
        div[data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--border)!important;background:rgba(17,27,46,.48);border-radius:14px!important; }
        div[data-testid="stTextArea"] textarea,div[data-testid="stTextInput"] input { background:#0d1729!important;color:#edf2ff!important;border:1px solid rgba(145,164,201,.18)!important;border-radius:10px!important; }
        div[data-testid="stSelectbox"] div[data-baseweb="select"]>div { background:#101b30;border-color:rgba(145,164,201,.18);border-radius:10px; }
        div[data-testid="stFileUploader"] section { background:rgba(14,24,42,.65);border:1px dashed rgba(145,164,201,.3);border-radius:12px; }
        div[data-testid="stFileUploader"] section:hover { border-color:#858aff; }
        .stButton>button,.stDownloadButton>button { border-radius:10px;border:1px solid rgba(145,164,201,.2);background:#17243b;color:#e8edff;font-weight:700;font-size:10px;min-height:37px;transition:all .18s ease; }
        .stButton>button:hover,.stDownloadButton>button:hover { border-color:rgba(147,151,255,.65);color:#fff;background:#202d4a; }
        .stButton>button[kind="primary"] { background:linear-gradient(110deg,#777ce9,#6268d9);border:1px solid rgba(177,180,255,.45);color:#fff;box-shadow:0 8px 23px rgba(102,107,221,.2); }
        .stButton>button[kind="primary"]:hover { background:linear-gradient(110deg,#888dff,#7076e8);border-color:#b5b7ff; }
        div[data-testid="stTabs"] button { color:#9baac5;font-size:10px; }
        div[data-testid="stTabs"] button[aria-selected="true"] { color:#bfc1ff; }
        div[data-testid="stAlert"] { border-radius:11px; }
        hr { border-color:rgba(145,164,201,.13); }
        code { color:#c7c9ff!important; }
        @media(max-width:760px) {
          [data-testid="stMainBlockContainer"] { padding:1rem .75rem 2rem; }
          .dm-hero { align-items:flex-start;flex-direction:column;padding:15px;gap:10px; }
          .dm-hero-aside { flex-direction:row;align-items:flex-start;flex-wrap:wrap; }
          .dm-topline { align-items:flex-start; }
          .dm-result-title { font-size:18px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults: dict[str, Any] = {
        "page": "Create",
        "source_text": "",
        "last_result": None,
        "last_options": None,
        "last_source_text": "",
        "history": [],
        "saved_projects": [],
        "dm_input_method": "Paste text",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar(backend_ok: bool, backend_info: Any) -> str:
    with st.sidebar:
        st.markdown(
            '<div class="dm-brand"><div class="dm-logo">✳</div><div>'
            '<div class="dm-brand-name">DataMind</div>'
            '<div class="dm-brand-tag">INTELLIGENT KNOWLEDGE STUDIO</div></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="dm-workspace"><div class="dm-workspace-icon">D</div><div>'
            '<strong>Personal workspace</strong><span>Transform · Understand · Create</span></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="dm-side-label">NAVIGATION</div>', unsafe_allow_html=True)
        pages = ["Create", "History", "Saved projects"]
        current = st.session_state.page if st.session_state.page in pages else "Create"
        page = st.radio(
            "Workspace navigation", pages,
            index=pages.index(current),
            format_func=lambda value: {
                "Create": "✦  New transformation",
                "History": "◷  Recent history",
                "Saved projects": "▣  Saved projects",
            }[value],
            label_visibility="collapsed",
            key="dm_navigation",
        )
        st.session_state.page = page
        st.markdown('<div class="dm-side-label">SYSTEM STATUS</div>', unsafe_allow_html=True)
        if backend_ok:
            st.markdown('<div class="dm-status"><span class="dm-status-dot"></span> API connected</div>', unsafe_allow_html=True)
            if isinstance(backend_info, dict):
                mode = backend_info.get("mode") or backend_info.get("provider") or "Ready"
                st.caption(f"Render API · {mode}")
        else:
            st.markdown('<div class="dm-status offline"><span class="dm-status-dot"></span> API unavailable</div>', unsafe_allow_html=True)
            st.caption("The workspace is ready. API requests may fail until the backend responds.")
        if st.button("↻  Check connection", use_container_width=True, key="dm_check_api"):
            check_backend.clear()
            st.rerun()
        st.markdown(
            '<div class="dm-side-note"><strong>✧ One source. Clearer thinking.</strong>'
            '<p>Turn dense information into useful explanations, structured notes and visual knowledge.</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="dm-footer">DATAMIND · THINK CLEARER</div>', unsafe_allow_html=True)
    return page


def section_head(step: str, title: str, subtitle: str, number: str = "") -> None:
    number_html = f'<div class="dm-section-number">{number}</div>' if number else ""
    st.markdown(
        f'<div class="dm-section"><div><div class="dm-step">{step}</div>'
        f'<h3>{html.escape(title)}</h3><p>{html.escape(subtitle)}</p></div>{number_html}</div>',
        unsafe_allow_html=True,
    )


def build_options() -> dict[str, str]:
    """All transformation choices live in the main Output Design section."""
    format_names = list(FORMATS.keys())

    with st.container(border=True):
        format_col, detail_col = st.columns([1.65, 1])
        with format_col:
            selected_format = st.selectbox(
                "Output format",
                format_names,
                index=format_names.index("Structured Notes"),
                help="Choose the structure DataMind should create from your source.",
                key="dm_format_main",
            )
        with detail_col:
            detail = st.selectbox(
                "Level of detail",
                ["short", "medium", "detailed"],
                index=2,
                format_func=str.title,
                help="Choose how much explanation and supporting detail to include.",
                key="dm_detail_main",
            )

        selected = FORMATS[selected_format]
        st.markdown(
            f'<div class="dm-format-panel"><div class="dm-format-icon">{selected["icon"]}</div>'
            f'<div><div class="dm-format-name">{html.escape(selected_format)}</div>'
            f'<div class="dm-format-desc">{html.escape(selected["desc"])}</div>'
            f'<div class="dm-format-use">Best for: {html.escape(selected["best_for"])}</div></div></div>',
            unsafe_allow_html=True,
        )

        lang_col, complexity_col, audience_col = st.columns(3)
        with lang_col:
            language = st.selectbox(
                "Output language", ["English", "Hindi", "Hinglish"],
                index=0, key="dm_language_main",
            )
        with complexity_col:
            complexity = st.selectbox(
                "Complexity", ["beginner", "intermediate", "advanced"],
                index=0, format_func=str.title, key="dm_complexity_main",
            )
        with audience_col:
            audience = st.selectbox(
                "Made for", ["students", "professionals", "developers", "general users"],
                index=0, format_func=str.title, key="dm_audience_main",
            )

        visual_col, custom_col = st.columns([1, 2])
        with visual_col:
            visual_style = st.selectbox(
                "Visual style", ["professional", "minimal", "colorful"],
                index=0, format_func=str.title, key="dm_visual_style_main",
            )
        with custom_col:
            st.markdown(
                '<div style="padding:8px 2px 0;color:#8292af;font-size:9px;line-height:1.55">'
                '<b style="color:#cbd5ee">Your output, your settings.</b><br>'
                'Choose the format, language, depth and audience before generating. '
                'These options are sent with your source to the DataMind API.</div>',
                unsafe_allow_html=True,
            )

    return {
        "format": selected["id"],
        "detail": detail,
        "language": language,
        "complexity": complexity,
        "audience": audience,
        "visual_style": visual_style,
    }


def readable_error(response: requests.Response) -> str:
    try:
        payload = response.json()
        detail = payload.get("detail", payload.get("message", payload)) if isinstance(payload, dict) else payload
        if isinstance(detail, list):
            return "; ".join(str(item.get("msg", item)) if isinstance(item, dict) else str(item) for item in detail)
        return str(detail)
    except ValueError:
        return response.text[:700] or f"Request failed with status {response.status_code}."


def run_text_transform(source: str, options: dict[str, str]) -> dict[str, Any]:
    response = requests.post(
        f"{API_URL}/api/transform",
        json={"text": source, **options},
        timeout=(12, 180),
    )
    if not response.ok:
        raise RuntimeError(f"API error {response.status_code}: {readable_error(response)}")
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("The API returned an unexpected response format.")
    return payload


def run_file_transform(uploaded_file: Any, options: dict[str, str]) -> dict[str, Any]:
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type or "application/octet-stream",
        )
    }
    response = requests.post(
        f"{API_URL}/api/transform/file",
        data=options,
        files=files,
        timeout=(12, 210),
    )
    if not response.ok:
        raise RuntimeError(f"API error {response.status_code}: {readable_error(response)}")
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("The API returned an unexpected response format.")
    return payload


def refine_result(
    result: dict[str, Any], instruction: str,
    language: str, complexity: str,
) -> dict[str, Any]:
    response = requests.post(
        f"{API_URL}/api/refine",
        json={
            "instruction": instruction,
            "result": result,
            "language": language,
            "complexity": complexity,
        },
        timeout=(12, 180),
    )
    if not response.ok:
        raise RuntimeError(f"API error {response.status_code}: {readable_error(response)}")
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("The API returned an unexpected response format.")
    return payload


def add_to_history(result: dict[str, Any], source: str, options: dict[str, str]) -> None:
    item = {
        "id": result.get("id") or str(uuid4()),
        "title": result.get("title") or "Untitled transformation",
        "format": result.get("format") or options.get("format", "transformation"),
        "created_at": result.get("created_at") or datetime.now().isoformat(),
        "result": result,
        "source": source,
        "options": options.copy(),
    }
    history = st.session_state.history
    history.insert(0, item)
    st.session_state.history = history[:40]


def mermaid_html(code: str) -> str:
    safe_code = json.dumps(code)
    diagram_id = f"dm-{uuid4().hex}"
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
html,body{{margin:0;background:#f9fbff;color:#26324a;font-family:Arial,sans-serif;}}
.wrap{{min-height:350px;padding:18px;display:flex;align-items:center;justify-content:center;overflow:auto;}}
#diagram{{width:100%;display:flex;justify-content:center;}}
#diagram svg{{max-width:100%;height:auto;}}
#error{{display:none;color:#9b4b48;background:#fff0ee;border:1px solid #f0d2ce;padding:12px 15px;border-radius:10px;font-size:13px;}}
</style></head><body><div class="wrap"><div id="diagram"></div><div id="error"></div></div>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
const source = {safe_code};
mermaid.initialize({{startOnLoad:false,securityLevel:'strict',theme:'base',fontFamily:'Arial, sans-serif',flowchart:{{htmlLabels:false,curve:'basis',useMaxWidth:true,nodeSpacing:42,rankSpacing:48}},themeVariables:{{background:'#f9fbff',primaryColor:'#eef0ff',primaryTextColor:'#202943',primaryBorderColor:'#858be3',secondaryColor:'#e4f5ef',secondaryTextColor:'#202943',secondaryBorderColor:'#63ad98',tertiaryColor:'#fff3e4',tertiaryTextColor:'#202943',tertiaryBorderColor:'#d7a567',lineColor:'#8791b2',textColor:'#202943',edgeLabelBackground:'#ffffff',fontSize:'15px'}}}});
try {{ const {{svg}} = await mermaid.render('{diagram_id}', source); document.getElementById('diagram').innerHTML = svg; }}
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
        columns[name] = [
            row[index] if isinstance(row, list) and index < len(row) else ""
            for row in rows
        ]
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
            with st.expander(f"{index:02d} · {question}"):
                st.markdown(answer)
        return
    for start in range(0, len(cards), 3):
        group = cards[start:start + 3]
        columns = st.columns(len(group))
        for column, item in zip(columns, group):
            if not isinstance(item, dict):
                continue
            with column:
                with st.container(border=True):
                    st.markdown(f"**{item.get('title') or f'Insight {start + 1}'}**")
                    st.markdown(str(item.get("body") or item.get("description") or item.get("content") or ""))


def render_source_coverage(result: dict[str, Any]) -> None:
    coverage = result.get("coverage")
    if isinstance(coverage, dict) and coverage.get("trackable"):
        col1, col2, col3 = st.columns(3)
        col1.metric("Records detected", coverage.get("actual_count", 0))
        col2.metric("Expected records", coverage.get("expected_count", 0))
        col3.metric("Not extracted", coverage.get("missing_count", 0))
        if coverage.get("warning"):
            if coverage.get("missing_count"):
                st.warning(coverage["warning"])
            else:
                st.info(coverage["warning"])
        elif coverage.get("complete"):
            st.success("All detected source records have been preserved.")

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
    parts = [
        f"# {result.get('title') or 'DataMind result'}",
        f"Format: {result.get('format') or 'transformation'}",
        "",
        str(result.get("content") or ""),
    ]
    words = result.get("important_words") or []
    lines = result.get("important_lines") or []
    if words:
        parts += ["", "## Important words", "", ", ".join(map(str, words))]
    if lines:
        parts += ["", "## Important lines extracted from source", ""]
        parts.extend(f"{index}. {line}" for index, line in enumerate(lines, 1))
    if result.get("mermaid"):
        parts += ["", "## Mermaid diagram", "", "```mermaid", str(result["mermaid"]), "```"]
    return "\n".join(parts)


def render_result(result: dict[str, Any]) -> None:
    fmt = str(result.get("format") or "transformation")
    label = next(
        (name for name, value in FORMATS.items() if value["id"] == fmt),
        fmt.replace("_", " ").title(),
    )
    is_fallback = result.get("mode") in {"demo", "demo-fallback"}
    status_tag = (
        '<span class="dm-fallback-tag">DEMO / FALLBACK</span>'
        if is_fallback else '<span class="dm-ai-tag">✦ AI RESULT</span>'
    )
    created = result.get("created_at") or "Just now"
    if isinstance(created, str) and "T" in created:
        created = created.replace("T", " ").replace("+00:00", " UTC")[:19]

    title = html.escape(str(result.get("title") or label))
    st.markdown(
        '<div class="dm-result-head"><div class="dm-step">TRANSFORMATION COMPLETE</div>'
        f'<div class="dm-result-title">{title}</div>'
        f'<div class="dm-result-meta">{html.escape(label)} &nbsp;·&nbsp; '
        f'{html.escape(str(created))} &nbsp;&nbsp; {status_tag}</div></div>',
        unsafe_allow_html=True,
    )
    if is_fallback:
        st.warning("This result came from the backend fallback mode. Check Render logs and Gemini configuration to confirm live AI processing.")
    if result.get("ai_error"):
        st.caption(str(result["ai_error"]))
    if result.get("source_truncated"):
        st.warning("The AI context was compacted. Review the source and coverage section for available source details.")

    important_words = result.get("important_words") or []
    if important_words:
        tags = "".join(
            f'<span class="dm-insight-tag">{html.escape(str(word)[:70])}</span>'
            for word in important_words[:30]
        )
        st.markdown(f"<div style='margin:9px 0 14px'>{tags}</div>", unsafe_allow_html=True)

    overview_tab, visual_tab, source_tab, raw_tab = st.tabs(
        ["✦  Overview", "▧  Visual output", "◫  Source & coverage", "{}  Raw data"]
    )
    with overview_tab:
        st.markdown(str(result.get("content") or "No written explanation was returned."))
        important_lines = result.get("important_lines") or []
        if important_lines:
            with st.expander("Important lines from the original source"):
                for line in important_lines:
                    st.markdown(f"- {line}")

    with visual_tab:
        mermaid = result.get("mermaid")
        if mermaid:
            st.markdown("#### Diagram preview")
            components.html(mermaid_html(str(mermaid)), height=420, scrolling=True)
            with st.expander("View / copy Mermaid source"):
                st.code(str(mermaid), language="mermaid")
                st.download_button(
                    "Download Mermaid source", str(mermaid),
                    file_name="datamind-diagram.mmd", mime="text/plain",
                    key="download_mermaid_source",
                )
        render_cards(result.get("cards") or [], fmt)
        table = result.get("table")
        if isinstance(table, dict):
            columns = table_to_columns(table)
            if columns:
                st.markdown("#### Generated table")
                st.dataframe(columns, use_container_width=True, hide_index=True)
        if not mermaid and not result.get("cards") and not result.get("table"):
            st.info("No separate visual asset was returned for this format. See the Overview tab for the generated content.")

    with source_tab:
        render_source_coverage(result)
        if not result.get("coverage") and not result.get("source_items") and not result.get("source_table"):
            st.caption("No separate source-register metadata was returned for this result.")

    with raw_tab:
        st.json(result, expanded=True)

    st.markdown("#### Export your work")
    exp1, exp2, exp3 = st.columns(3)
    with exp1:
        st.download_button(
            "↓  Markdown", build_result_markdown(result),
            file_name="datamind-result.md", mime="text/markdown",
            use_container_width=True, key="download_result_markdown",
        )
    with exp2:
        st.download_button(
            "↓  JSON", json.dumps(result, ensure_ascii=False, indent=2),
            file_name="datamind-result.json", mime="application/json",
            use_container_width=True, key="download_result_json",
        )
    with exp3:
        if result.get("mermaid"):
            st.download_button(
                "↓  Diagram code", str(result["mermaid"]),
                file_name="datamind-diagram.mmd", mime="text/plain",
                use_container_width=True, key="download_result_diagram",
            )
        else:
            st.download_button(
                "↓  Source text", st.session_state.get("last_source_text", ""),
                file_name="datamind-source.txt", mime="text/plain",
                use_container_width=True, key="download_result_source",
            )


def render_create_page(backend_ok: bool) -> None:
    # Compact product introduction: informative, but deliberately not a tall hero.
    st.markdown(
        '<div class="dm-hero"><div class="dm-hero-copy">'
        '<div class="dm-eyebrow">INTELLIGENT KNOWLEDGE WORKSPACE</div>'
        '<h1>Turn raw information into <span>clear understanding.</span></h1>'
        '<p>DataMind transforms your notes, topics and documents into structured learning assets, explanations and visual knowledge — using one focused workspace.</p>'
        '</div><div class="dm-hero-aside">'
        '<span class="dm-pill">✦ AI-powered transformation</span>'
        '<span class="dm-pill">12 structured output formats</span>'
        '<span class="dm-pill">PDF · DOCX · TXT · CSV · JSON</span>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    section_head(
        "START HERE", "Start your transformation",
        "Add your source first, then personalize the output settings and generate.",
        "01 / 03",
    )

    with st.container(border=True):
        input_method = st.radio(
            "Source type", ["Paste text", "Upload document"],
            horizontal=True, label_visibility="collapsed",
            key="dm_input_method",
        )
        source_text = ""
        uploaded_file = None

        if input_method == "Paste text":
            sample_col, hint_col = st.columns([1, 3])
            with sample_col:
                if st.button("↳  Insert sample data", use_container_width=True, key="dm_insert_sample"):
                    st.session_state.source_text = SAMPLE_TEXT
                    st.rerun()
            with hint_col:
                st.caption("Paste notes, research, a topic, article text or raw information. Keep useful details in the source.")
            source_text = st.text_area(
                "Source material", key="source_text", height=190,
                placeholder=(
                    "Paste your content here…\n\n"
                    "Example: Explain Artificial Intelligence, Machine Learning, "
                    "Deep Learning and their real-world applications."
                ),
                label_visibility="collapsed",
            )
            st.caption(f"{len(source_text):,} characters · Your source is sent to your configured DataMind backend.")
        else:
            uploaded_file = st.file_uploader(
                "Drop a document here or browse your device",
                type=["pdf", "docx", "txt", "md", "csv", "json"],
                help="Supported formats: PDF, DOCX, TXT, Markdown, CSV and JSON. The Render backend upload limit still applies.",
                key="dm_document_upload",
            )
            if uploaded_file:
                st.success(f"Ready to process · {uploaded_file.name} · {uploaded_file.size / 1024:.1f} KB")

    section_head(
        "PERSONALIZE YOUR RESULT", "Output design",
        "Choose the format, detail, language and audience that match your goal.",
        "02 / 03",
    )
    options = build_options()

    section_head(
        "READY WHEN YOU ARE", "Generate your result",
        "DataMind will process your source using the selected output settings.",
        "03 / 03",
    )
    generate_col, status_col = st.columns([1.15, 2.85], vertical_alignment="center")
    with generate_col:
        generate = st.button(
            "✦  Generate transformation",
            type="primary", use_container_width=True,
            key="dm_generate_transformation",
        )
    with status_col:
        if backend_ok:
            st.caption("Connected to your Render API · Your Gemini key remains on the backend.")
        else:
            st.caption("Backend health check is unavailable. You can still try; the request will show the API's actual response.")

    if generate:
        if uploaded_file is None and not source_text.strip():
            st.warning("Add source text or upload a document before generating.")
        else:
            try:
                with st.spinner("DataMind is structuring your information…"):
                    result = (
                        run_file_transform(uploaded_file, options)
                        if uploaded_file is not None
                        else run_text_transform(source_text, options)
                    )
                st.session_state.last_result = result
                st.session_state.last_options = options.copy()
                st.session_state.last_source_text = result.get("source_text") or source_text or ""
                add_to_history(result, st.session_state.last_source_text, options)
                st.success("Transformation complete. Your result is ready below.")
            except requests.Timeout:
                st.error("The request timed out. Render may be waking up, or the source may be large. Please try again.")
            except requests.RequestException as exc:
                st.error(f"Could not reach the DataMind backend: {exc}")
            except Exception as exc:
                st.error(str(exc))

    result = st.session_state.get("last_result")
    if result:
        section_head(
            "YOUR GENERATED KNOWLEDGE", "Transformation result",
            "Review the explanation, visual output and source coverage, then export your work.",
        )
        render_result(result)

        with st.expander("✦  Refine this result"):
            st.caption("Ask DataMind to simplify, expand, reorganize or explain the current result in a different way.")
            instruction = st.text_input(
                "What should change?",
                placeholder="e.g. Explain this for a first-year BCA student with simple examples.",
                key="dm_refine_instruction",
            )
            refine_col, refine_help = st.columns([1.1, 3])
            with refine_col:
                refine_clicked = st.button(
                    "Apply refinement", type="primary", use_container_width=True,
                    disabled=not bool(instruction.strip()), key="dm_refine_button",
                )
            with refine_help:
                st.caption("Uses the existing POST /api/refine endpoint.")
            if refine_clicked:
                previous_options = st.session_state.get("last_options") or options
                try:
                    with st.spinner("Refining your result…"):
                        updated = refine_result(
                            result, instruction.strip(),
                            previous_options.get("language", "English"),
                            previous_options.get("complexity", "beginner"),
                        )
                    st.session_state.last_result = updated
                    add_to_history(
                        updated,
                        st.session_state.get("last_source_text", ""),
                        previous_options,
                    )
                    st.success("Your result has been refined.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Refinement failed: {exc}")

        save_col, new_col, spacer = st.columns([1.25, 1.15, 3.6])
        with save_col:
            if st.button("▣  Save to projects", use_container_width=True, key="dm_save_project"):
                saved = st.session_state.saved_projects
                result_id = result.get("id") or result.get("title")
                if not any((item.get("id") or item.get("title")) == result_id for item in saved):
                    saved.insert(0, {
                        "id": result_id,
                        "title": result.get("title"),
                        "format": result.get("format"),
                        "created_at": result.get("created_at"),
                        "result": result,
                        "source": st.session_state.get("last_source_text", ""),
                        "options": st.session_state.get("last_options") or options,
                    })
                    st.session_state.saved_projects = saved
                st.success("Saved in this session's project library.")
        with new_col:
            if st.button("＋  New transformation", use_container_width=True, key="dm_new_transformation"):
                st.session_state.last_result = None
                st.session_state.last_options = None
                st.session_state.last_source_text = ""
                st.session_state.source_text = ""
                st.rerun()


def render_library_page(page: str) -> None:
    is_history = page == "History"
    items = st.session_state.history if is_history else st.session_state.saved_projects
    title = "Recent history" if is_history else "Saved projects"
    subtitle = (
        "Your latest transformations in this active Streamlit session."
        if is_history else
        "Projects you chose to keep in this active Streamlit session."
    )
    st.markdown(
        f'<div class="dm-eyebrow">YOUR WORKSPACE</div><h2 style="margin-top:0">{title}</h2>'
        f'<p style="color:#8191ad;font-size:10px">{subtitle}</p>',
        unsafe_allow_html=True,
    )
    if not items:
        with st.container(border=True):
            st.markdown("### Your workspace is ready for its first result")
            st.caption("Create a transformation and it will appear here. Session data may reset when the session ends.")
            if st.button("＋  Create a transformation", type="primary", key="dm_empty_library_create"):
                st.session_state.page = "Create"
                st.rerun()
        return

    query = st.text_input("Search workspace", placeholder="Search by title or format…", key=f"dm_search_{page}")
    filtered = [
        item for item in items
        if query.lower() in f"{item.get('title', '')} {item.get('format', '')}".lower()
    ]
    st.caption(f"{len(filtered)} item(s)")
    for index, item in enumerate(filtered):
        with st.container(border=True):
            info_col, action_col = st.columns([4, 1])
            with info_col:
                st.markdown(f"**{item.get('title') or 'Untitled transformation'}**")
                st.caption(
                    f"{str(item.get('format') or 'transformation').replace('_', ' ').title()} · "
                    f"{str(item.get('created_at') or 'Recently')[:19]}"
                )
            with action_col:
                if st.button("Open result", key=f"dm_open_{page}_{index}", use_container_width=True):
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

    st.markdown(
        f'<div class="dm-topline"><div class="dm-breadcrumb">WORKSPACE '
        f'<span style="color:#505f7b">/</span> {html.escape(page.upper())}</div>'
        f'<div class="dm-status {"" if backend_ok else "offline"}">'
        f'<span class="dm-status-dot"></span>'
        f'{"SYSTEM OPERATIONAL" if backend_ok else "API CONNECTION CHECK NEEDED"}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    if page == "Create":
        render_create_page(backend_ok)
    else:
        render_library_page(page)

    st.markdown(
        '<div class="dm-footer">DATAMIND · TURN RAW INFORMATION INTO CLEAR UNDERSTANDING</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
