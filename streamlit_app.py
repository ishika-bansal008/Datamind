from __future__ import annotations

import html
import json
import math
import os
import re
from io import BytesIO
from datetime import datetime
from typing import Any
from uuid import uuid4

import requests
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageDraw, ImageFont


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
        "last_result_token": None,
        "dm_editor_token": None,
        "dm_editor_content": "",
        "dm_editor_original_content": "",
        "dm_content_edited": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def activate_result(result: dict[str, Any]) -> None:
    """Set a newly generated/opened result and reset its editable text buffer."""
    token = str(uuid4())
    result = dict(result)
    original = normalize_item_labels_in_text(str(result.get("content") or ""))
    result["content"] = original
    st.session_state.last_result = result
    st.session_state.last_result_token = token
    st.session_state.dm_editor_token = token
    st.session_state.dm_editor_content = original
    st.session_state.dm_editor_original_content = original
    st.session_state.dm_content_edited = False


def reset_editor_to_original() -> None:
    """Streamlit button callback: reset the editor before widgets are rebuilt."""
    st.session_state.dm_editor_content = st.session_state.get("dm_editor_original_content", "")


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
            answer = item.get("answer") or item.get("body") or "Answer not provided."
            question = item.get("question") or item.get("title") or ""
            if _is_generic_item_label(question):
                question = _derive_item_title(str(answer), index)
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
                    body = str(item.get("body") or item.get("description") or item.get("content") or "")
                    card_title = item.get("title") or item.get("label") or ""
                    if _is_generic_item_label(card_title):
                        card_title = _derive_item_title(body, start + 1)
                    st.markdown(f"**{card_title or 'Key insight'}**")
                    st.markdown(body)


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
                details = str(item.get("details") or item.get("description") or item.get("content") or "")
                label = item.get("label") or item.get("title") or ""
                if _is_generic_item_label(label):
                    label = _derive_item_title(details, index)
                st.markdown(f"**{index}. {label or 'Source insight'}**  \n{details}")
            else:
                details = str(item)
                st.markdown(f"**{index}. {_derive_item_title(details, index)}**  \n{details}")


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


def build_result_pdf(title: str, format_label: str, content: str) -> bytes:
    """Create a readable multi-page PDF of the editable text result."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import (
            HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
        )
    except ImportError as exc:
        raise RuntimeError("PDF export needs ReportLab. Add reportlab to requirements.txt and redeploy.") from exc

    output = BytesIO()
    regular_name, bold_name = "Helvetica", "Helvetica-Bold"
    font_candidates = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
    ]
    for regular_path, bold_path in font_candidates:
        try:
            if os.path.exists(regular_path) and os.path.exists(bold_path):
                if "DataMindUnicode" not in pdfmetrics.getRegisteredFontNames():
                    pdfmetrics.registerFont(TTFont("DataMindUnicode", regular_path))
                    pdfmetrics.registerFont(TTFont("DataMindUnicode-Bold", bold_path))
                    pdfmetrics.registerFontFamily(
                        "DataMindUnicode", normal="DataMindUnicode",
                        bold="DataMindUnicode-Bold", italic="DataMindUnicode",
                        boldItalic="DataMindUnicode-Bold",
                    )
                regular_name, bold_name = "DataMindUnicode", "DataMindUnicode-Bold"
                break
        except Exception:
            continue

    doc = SimpleDocTemplate(
        output, pagesize=A4,
        rightMargin=19 * mm, leftMargin=19 * mm,
        topMargin=22 * mm, bottomMargin=20 * mm,
        title=title or "DataMind result", author="DataMind",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DMTitle", parent=styles["Title"], fontName=bold_name,
        fontSize=21, leading=27, textColor=colors.HexColor("#222B4A"),
        alignment=TA_LEFT, spaceAfter=5 * mm,
    )
    meta_style = ParagraphStyle(
        "DMMeta", parent=styles["Normal"], fontName=regular_name,
        fontSize=8.5, leading=12, textColor=colors.HexColor("#68748C"),
        spaceAfter=7 * mm,
    )
    body_style = ParagraphStyle(
        "DMBody", parent=styles["BodyText"], fontName=regular_name,
        fontSize=9.5, leading=15, textColor=colors.HexColor("#27334A"),
        spaceAfter=3 * mm, wordWrap="CJK",
    )
    h1_style = ParagraphStyle(
        "DMH1", parent=styles["Heading1"], fontName=bold_name,
        fontSize=16, leading=20, textColor=colors.HexColor("#454DB5"),
        spaceBefore=5 * mm, spaceAfter=2.5 * mm,
    )
    h2_style = ParagraphStyle(
        "DMH2", parent=styles["Heading2"], fontName=bold_name,
        fontSize=12.5, leading=17, textColor=colors.HexColor("#287E78"),
        spaceBefore=4 * mm, spaceAfter=2 * mm,
    )
    bullet_style = ParagraphStyle(
        "DMBullet", parent=body_style, leftIndent=5 * mm,
        firstLineIndent=-3 * mm, spaceAfter=1.8 * mm,
    )
    small_style = ParagraphStyle(
        "DMSmall", parent=body_style, fontSize=8, leading=11,
        textColor=colors.HexColor("#68748C"),
    )

    def inline_markup(value: str) -> str:
        safe = html.escape(value, quote=False)
        safe = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", safe)
        safe = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", safe)
        safe = re.sub(r"`([^`]+)`", r"<font name='DataMindUnicode'>\1</font>" if regular_name.startswith("DataMind") else r"<font name='Helvetica'>\1</font>", safe)
        return safe

    story: list[Any] = [
        Paragraph(html.escape(title or "DataMind Result"), title_style),
        Paragraph(f"{html.escape(format_label)} &nbsp;·&nbsp; Generated with DataMind", meta_style),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#D8DEEB"), spaceAfter=5 * mm),
    ]

    lines = str(content or "No written result was returned.").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    index = 0
    while index < len(lines):
        raw = lines[index].strip()
        if not raw:
            story.append(Spacer(1, 1.2 * mm))
            index += 1
            continue

        # Markdown tables.
        if raw.startswith("|") and index + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[index + 1]):
            table_lines = [raw]
            index += 1
            if index < len(lines):
                index += 1  # skip markdown separator row
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            parsed = [[cell.strip() for cell in row.strip().strip("|").split("|")] for row in table_lines]
            if parsed:
                max_cols = max(len(row) for row in parsed)
                data = []
                for ridx, row in enumerate(parsed):
                    cells = row + [""] * (max_cols - len(row))
                    data.append([Paragraph(inline_markup(cell), small_style if ridx else bullet_style) for cell in cells])
                table_obj = Table(data, repeatRows=1, hAlign="LEFT")
                table_obj.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9ECFF")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#28346A")),
                    ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#D7DEEA")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]))
                story.extend([table_obj, Spacer(1, 3 * mm)])
            continue

        if raw.startswith("### "):
            story.append(Paragraph(inline_markup(raw[4:]), h2_style))
        elif raw.startswith("## "):
            story.append(Paragraph(inline_markup(raw[3:]), h1_style))
        elif raw.startswith("# "):
            story.append(Paragraph(inline_markup(raw[2:]), h1_style))
        elif re.match(r"^[-*+]\s+", raw):
            item_text = re.sub(r"^[-*+]\s+", "", raw)
            story.append(Paragraph("&bull;&nbsp; " + inline_markup(item_text), bullet_style))
        elif re.match(r"^\d+[.)]\s+", raw):
            story.append(Paragraph(inline_markup(raw), bullet_style))
        else:
            story.append(Paragraph(inline_markup(raw), body_style))
        index += 1

    def draw_page(canvas: Any, document: Any) -> None:
        canvas.saveState()
        page_w, page_h = A4
        canvas.setStrokeColor(colors.HexColor("#DDE3EF"))
        canvas.setLineWidth(0.6)
        canvas.line(19 * mm, page_h - 14 * mm, page_w - 19 * mm, page_h - 14 * mm)
        canvas.setFont(regular_name, 7.5)
        canvas.setFillColor(colors.HexColor("#7A879D"))
        canvas.drawString(19 * mm, 11 * mm, "DATAMIND  ·  TURN RAW INFORMATION INTO CLEAR UNDERSTANDING")
        canvas.drawRightString(page_w - 19 * mm, 11 * mm, f"Page {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    return output.getvalue()



# ============================================================================
# VISUAL OUTPUT ENGINE
# Converts the API's structured text / cards / tables / Mermaid into real PNGs.
# This is a local renderer: it does not depend on a separate image-generation API.
# ============================================================================

VISUAL_PALETTES = {
    "professional": {
        "bg": "#0B1120", "panel": "#121E34", "panel2": "#182844",
        "line": "#53658B", "text": "#F1F4FF", "muted": "#A8B7D2",
        "accent": "#9296FF", "accent2": "#5BD5B8", "warm": "#F3BE7A",
        "soft": "#202F4E", "white": "#FFFFFF",
    },
    "minimal": {
        "bg": "#F4F6FA", "panel": "#FFFFFF", "panel2": "#EAF0F8",
        "line": "#C8D2E2", "text": "#172238", "muted": "#53627A",
        "accent": "#4D63B8", "accent2": "#178C78", "warm": "#BA782E",
        "soft": "#E8EDF5", "white": "#FFFFFF",
    },
    "colorful": {
        "bg": "#10172B", "panel": "#1B2743", "panel2": "#25375B",
        "line": "#6678A6", "text": "#F7F8FF", "muted": "#C0CBE2",
        "accent": "#A78BFA", "accent2": "#4DD8C0", "warm": "#FFBD75",
        "soft": "#303E62", "white": "#FFFFFF",
    },
}


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a broadly available font; Pillow's default is the final fallback."""
    candidates = []
    if bold:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        ])
    else:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ])
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _clean_text(value: Any) -> str:
    text = str(value or "")
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[`*_>#]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: Any, max_width: int) -> list[str]:
    text = _clean_text(text)
    if not text:
        return []
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        try:
            width = draw.textbbox((0, 0), candidate, font=font)[2]
        except Exception:
            width = len(candidate) * 9
        if width <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_wrapped(
    draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: Any,
    fill: str, max_width: int, line_gap: int = 8, max_lines: int | None = None,
) -> int:
    x, y = xy
    lines = _wrap_text(draw, text, font, max_width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        if lines:
            lines[-1] = lines[-1].rstrip(" .") + "…"
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, y), line, font=font)
        y += (bbox[3] - bbox[1]) + line_gap
    return y


def _new_visual(title: str, fmt_label: str, palette: dict[str, str], height: int = 1100) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    width = 1600
    height = max(850, min(4200, int(height)))
    image = Image.new("RGB", (width, height), palette["bg"])
    draw = ImageDraw.Draw(image)
    # subtle top accent and large workspace panel
    draw.rounded_rectangle((38, 34, width - 38, height - 34), radius=34, fill=palette["panel"], outline=palette["line"], width=2)
    draw.rounded_rectangle((38, 34, width - 38, 52), radius=8, fill=palette["accent"])
    draw.text((92, 83), "DATAMIND  /  VISUAL KNOWLEDGE", font=_font(23, True), fill=palette["accent"])
    heading = _clean_text(title)[:110] or "Your transformation"
    title_font = _font(48, True)
    while len(heading) > 18 and draw.textbbox((0, 0), heading, font=title_font)[2] > 1410:
        current_size = getattr(title_font, "size", 48)
        if current_size <= 30:
            break
        title_font = _font(current_size - 2, True)
    draw.text((92, 137), heading, font=title_font, fill=palette["text"])
    draw.text((94, 207), fmt_label.upper() + "  •  GENERATED FROM YOUR SOURCE", font=_font(18, True), fill=palette["muted"])
    return image, draw


GENERIC_ITEM_LABEL = re.compile(
    r"^(?:item|section|point|key\s*idea|key\s*point|insight|entry|card|element|topic|concept)(?:\s*#?\s*\d+)?$",
    re.IGNORECASE,
)

# These are metadata labels occasionally emitted by the API's structured
# breakdown prompt. They describe a field, not the subject of a section.
_METADATA_LABELS = {
    "domain",
    "real problem / use case",
    "real problem/use case",
    "problem / use case",
    "problem/use case",
    "ai technologies listed in source",
    "technologies listed in source",
    "technologies",
    "tools and technologies",
}

_NOT_SPECIFIED = re.compile(
    r"^(?:not separately specified(?: in (?:the )?source)?|not specified(?: in (?:the )?source)?|"
    r"not provided|not mentioned|not available|none|n/?a|unknown)\.?$",
    re.IGNORECASE,
)


def _is_generic_item_label(value: Any) -> bool:
    """Recognize plain and wrapped placeholders such as 'Item 2 (Item 2)'."""
    candidate = _clean_text(value)
    candidate = re.sub(r"^\d{1,3}[.)]\s*", "", candidate)
    candidate = re.sub(
        r"\s*\((?:item|section|point|card|entry|topic|concept)\s*#?\s*\d+\)\s*$",
        "",
        candidate,
        flags=re.IGNORECASE,
    )
    candidate = candidate.strip(" .:—–-#")
    return not candidate or bool(GENERIC_ITEM_LABEL.fullmatch(candidate))


def _smart_title(value: str) -> str:
    """Convert extracted subject text into a readable heading while preserving acronyms."""
    value = re.sub(r"\s+", " ", str(value or "")).strip(" .:;—–-#")
    if not value:
        return "Source overview"
    # If the source heading is all caps, convert it to title case.
    if value.isupper():
        value = value.title()
        words = value.split()
        minor_words = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "with"}
        value = " ".join(word.lower() if index and word.lower() in minor_words else word for index, word in enumerate(words))
    else:
        value = value[0].upper() + value[1:]
    for acronym in ("AI", "ML", "API", "PDF", "JSON", "HTML", "CSS", "SQL", "NLP", "CPU", "GPU", "IoT"):
        value = re.sub(rf"\b{re.escape(acronym.title())}\b", acronym, value, flags=re.IGNORECASE)
    return value[:90].rstrip(" .:;—–-")


def _title_seed_from_block(body: str) -> str:
    """Extract useful subject text from ordinary prose or labelled API fields."""
    candidates: list[tuple[int, str]] = []
    for raw in str(body or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        line = re.sub(r"^[-*+•]\s*", "", line)
        line = re.sub(r"^\d{1,3}[.)]\s*", "", line)
        line = re.sub(r"^\*\*(.*?)\*\*\s*", r"\1 ", line).strip()
        if not line:
            continue

        field = re.match(r"^([^:]{2,75}):\s*(.*)$", line)
        if field:
            label = _clean_text(field.group(1)).lower().strip()
            value = _clean_text(field.group(2))
            normalized_label = re.sub(r"\s+", " ", label)
            if normalized_label in _METADATA_LABELS:
                if not value or _NOT_SPECIFIED.fullmatch(value):
                    continue
                # The real-problem/use-case value is the best clue to the topic.
                priority = 0 if "problem" in normalized_label or "use case" in normalized_label else 2
                candidates.append((priority, value))
                continue
            if _NOT_SPECIFIED.fullmatch(value):
                continue

        # Ignore boilerplate field values even if the label was slightly different.
        if _NOT_SPECIFIED.fullmatch(line):
            continue
        candidates.append((1, line))

    if not candidates:
        return _clean_text(body)
    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]


def _derive_item_title(body: str, index: int = 1) -> str:
    """Generate a meaningful heading from a section's actual subject/content."""
    text = _title_seed_from_block(body)
    if not text:
        return "Source overview"

    # The API sometimes prefixes its description with the actual topic in ALL CAPS:
    # 'TYPES OF ARTIFICIAL INTELLIGENCE Narrow AI is designed...'
    upper_prefix = re.match(
        r"^([A-Z][A-Z0-9&/()+-]*(?:\s+[A-Z][A-Z0-9&/()+-]*){1,8}?)(?=\s+[A-Z][a-z])",
        text,
    )
    if upper_prefix:
        phrase = _smart_title(upper_prefix.group(1))
        if len(phrase.split()) >= 2 and not _is_generic_item_label(phrase):
            return phrase

    # A descriptive phrase before a colon is usually a good semantic label.
    prefix_match = re.match(r"^([^:—–]{2,58})\s*[:—–]\s*(.+)$", text)
    if prefix_match:
        candidate = prefix_match.group(1).strip(" -–—:*")
        if not _is_generic_item_label(candidate) and len(candidate.split()) <= 8:
            return _smart_title(candidate)

    # Prefer the subject phrase before a definition/action verb.
    sentence = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0]
    sentence = re.sub(r"^(?:this|these|the following|in this section)\s+", "", sentence, flags=re.I)
    subject_match = re.match(
        r"^(.{2,72}?)\s+\b(?:is|are|refers to|means|describes|enables|allows|helps|supports|provides|uses|include|includes|consists of|works|can|could|will|should|offers|contains|represents|plays|forms|uses)\b",
        sentence,
        re.I,
    )
    if subject_match:
        candidate = _clean_text(subject_match.group(1)).strip(" .,:;—–-")
        if candidate and not _is_generic_item_label(candidate):
            # Expand a single broad word when the description identifies a clear domain.
            domain_titles = [
                (r"medical|doctor|patient|hospital|clinical|diagnos", "Healthcare Applications"),
                (r"school|student|teacher|classroom|curriculum|learning", "Education Applications"),
                (r"bank|transaction|fraud|payment|finance|credit", "Banking Applications"),
                (r"vehicle|traffic|transport|route|driving|road", "Transportation Applications"),
                (r"crop|soil|farm|irrigation|agricultur", "Agriculture Applications"),
                (r"movie|music|video|streaming|recommend", "Personalized Recommendations"),
            ]
            if len(candidate.split()) == 1:
                for pattern, domain_title in domain_titles:
                    if re.search(pattern, text, re.I):
                        return domain_title
            return _smart_title(candidate)

    # Fall back to the first informative words, not 'Concept 1' or 'Item 1'.
    stop = {
        "the", "a", "an", "this", "these", "those", "it", "they", "there", "here",
        "is", "are", "was", "were", "can", "could", "should", "would", "will", "may",
        "might", "must", "has", "have", "had", "be", "been", "being", "to", "of", "for",
        "and", "or", "but", "in", "on", "at", "by", "with", "from", "as", "that", "which",
        "their", "its", "into", "using", "use", "used", "also", "often", "many",
        "domain", "problem", "real", "technologies", "listed", "source",
    }
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9&'/-]*", sentence)
    chosen: list[str] = []
    for word in words:
        if word.lower() in stop:
            continue
        chosen.append(word)
        if len(chosen) >= 5:
            break
    if chosen:
        return _smart_title(" ".join(chosen))
    return "Source overview"


def _placeholder_heading_parts(line: str) -> tuple[str, str] | None:
    """Return (number, placeholder title) for '1. Item 1 (Item 1)' style lines."""
    candidate = re.sub(r"^\s*#{1,6}\s*", "", str(line or "")).strip()
    candidate = re.sub(r"^\s*[-*+•]\s*", "", candidate).strip()
    candidate = re.sub(r"^\*\*(.*?)\*\*$", r"\1", candidate).strip()
    match = re.match(r"^(?:(\d{1,3})[.)]\s+)?(.+?)\s*$", candidate)
    if not match:
        return None
    number = match.group(1) or ""
    title = match.group(2).strip().strip("*")
    if _is_generic_item_label(title):
        return number, title
    return None


def _is_next_section_boundary(line: str) -> bool:
    candidate = str(line or "").strip()
    if not candidate:
        return False
    if re.match(r"^#{1,6}\s+", candidate):
        return True
    if _placeholder_heading_parts(candidate):
        return True
    numbered = re.match(r"^\d{1,3}[.)]\s+(.+)$", candidate)
    if numbered:
        title = _clean_text(numbered.group(1))
        return len(title) <= 95 and len(title.split()) <= 13 and not re.search(r"[.!?]$", title)
    return False


def normalize_item_labels_in_text(content: str) -> str:
    """Replace placeholder item headings with subjects derived from their section content."""
    lines = str(content or "").splitlines()
    output: list[str] = []
    i = 0
    section_index = 0

    while i < len(lines):
        raw = lines[i]
        placeholder = _placeholder_heading_parts(raw)
        if not placeholder:
            # Remove empty metadata emitted by the analysis template; it adds no information.
            stripped = re.sub(r"^\s*[-*+•]\s*", "", raw).strip()
            field = re.match(r"^([^:]{2,75}):\s*(.*)$", stripped)
            if field:
                label = re.sub(r"\s+", " ", _clean_text(field.group(1)).lower()).strip()
                value = _clean_text(field.group(2))
                if label in _METADATA_LABELS and _NOT_SPECIFIED.fullmatch(value):
                    i += 1
                    continue
                if label in {"real problem / use case", "real problem/use case", "problem / use case", "problem/use case"} and value:
                    # The API often repeats the actual topic in all-caps before its explanation.
                    active_heading = next((line for line in reversed(output) if line.strip()), "")
                    active_heading = re.sub(r"^#{1,6}\s*", "", active_heading).strip()
                    active_heading = re.sub(r"^\d{1,3}[.)]\s*", "", active_heading)
                    if active_heading:
                        value = re.sub(r"^" + re.escape(active_heading) + r"\s+", "", value, flags=re.IGNORECASE).strip()
                    prefix = raw[:len(raw) - len(raw.lstrip())]
                    bullet = "- " if re.match(r"^\s*[-*+•]\s*", raw) else ""
                    output.append(f"{prefix}{bullet}{value or field.group(2)}")
                    i += 1
                    continue
            # This sentence is a mechanical preface, not useful result content.
            if _clean_text(raw).lower() in {"complete project by project breakdown", "project by project breakdown", "complete breakdown"}:
                i += 1
                continue
            output.append(raw)
            i += 1
            continue

        section_index += 1
        number, _old_label = placeholder
        block: list[str] = []
        j = i + 1
        while j < len(lines) and not _is_next_section_boundary(lines[j]):
            block.append(lines[j])
            j += 1
        heading = _derive_item_title("\n".join(block), section_index)
        if number:
            output.append(f"### {number}. {heading}")
        else:
            output.append(f"### {heading}")
        i += 1

    while output and not output[0].strip():
        output.pop(0)
    return "\n".join(output)

def _parse_content_sections(content: str) -> list[dict[str, str]]:
    """Parse headings, numbered sections, bold labels and ITEM N blocks."""
    sections: list[dict[str, str]] = []
    current_title = "Overview"
    current_lines: list[str] = []

    def flush() -> None:
        nonlocal current_lines, current_title
        body = _clean_text(" ".join(current_lines))
        if body:
            title = current_title
            if _is_generic_item_label(title) or title.lower() == "overview":
                title = _derive_item_title(body, len(sections) + 1)
            sections.append({"title": title[:110], "body": body[:650]})
        current_lines = []

    for raw in str(content or "").splitlines():
        line = raw.strip()
        if not line:
            continue

        # Markdown headings.
        heading = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if heading:
            flush()
            current_title = re.sub(r"^\d{1,3}[.)]\s+", "", _clean_text(heading.group(1))) or "Overview"
            continue

        # Remove common markdown emphasis around labels before parsing.
        normalized = re.sub(r"^\*\*(.*?)\*\*\s*", r"\1 ", line)
        normalized = normalized.strip()

        # AI outputs sometimes literally label blocks ITEM 1, ITEM 2, etc.
        item_match = re.match(
            r"^(?:[-*+]\s*)?(?:\*\*)?(?:item|section|point|key\s*idea|key\s*point|insight|entry|card)\s*#?\s*\d+\s*(?:\*\*)?\s*(?::|[-—–.)])?\s*(.*)$",
            normalized,
            re.I,
        )
        if item_match:
            flush()
            remainder = _clean_text(item_match.group(1))
            # If the text after ITEM N is a short heading, retain it as the title.
            if remainder and len(remainder) <= 78 and not re.search(r"[.!?]$", remainder):
                current_title = remainder
            else:
                current_title = "Overview"
                if remainder:
                    current_lines.append(remainder)
            continue

        # Bold standalone heading, e.g. **Applications of AI**.
        bold_heading = re.match(r"^\*\*(.+?)\*\*\s*:?\s*$", line)
        if bold_heading:
            flush()
            current_title = _clean_text(bold_heading.group(1)) or "Overview"
            continue

        # Numbered heading or numbered sentence.
        numbered = re.match(r"^(\d{1,3})[.)]\s+(.+)$", normalized)
        if numbered:
            candidate = _clean_text(numbered.group(2))
            is_heading = (
                _is_generic_item_label(candidate)
                or (
                    len(candidate) <= 95
                    and (candidate.isupper() or not re.search(r"[.!?]$", candidate))
                    and len(candidate.split()) <= 13
                )
            )
            flush()
            if is_heading:
                current_title = candidate
            else:
                current_title = "Overview"
                current_lines.append(candidate)
            continue

        # Structured metadata is a field inside the current section, not a section heading.
        colon_label = re.match(r"^(?:[-*+•]\s*)?([^:]{2,75}):\s*(.+)$", normalized)
        if colon_label:
            candidate = _clean_text(colon_label.group(1))
            value = _clean_text(colon_label.group(2))
            normalized_label = re.sub(r"\s+", " ", candidate.lower()).strip()
            if normalized_label in _METADATA_LABELS:
                if value and not _NOT_SPECIFIED.fullmatch(value):
                    if "problem" in normalized_label or "use case" in normalized_label:
                        current_lines.append(value)
                    else:
                        current_lines.append(f"{candidate}: {value}")
                continue
            if not _is_generic_item_label(candidate) and len(candidate.split()) <= 8:
                flush()
                current_title = candidate
                current_lines.append(value)
                continue

        # Keep bullet/list text as section content, but remove visual markdown marks.
        normalized = re.sub(r"^[-*+]\s+", "", normalized)
        normalized = re.sub(r"^\*\*(.+?)\*\*\s*[:—-]\s*", r"\1: ", normalized)
        current_lines.append(_clean_text(normalized))

    flush()
    return sections[:12]


def _extract_visual_items(result: dict[str, Any]) -> list[dict[str, str]]:
    """Prefer meaningful labels; replace placeholder ITEM N labels with content-derived titles."""
    content_sections = _parse_content_sections(str(result.get("content") or ""))
    prefer_content = bool(result.get("_prefer_content", False))

    cards: list[dict[str, str]] = []
    raw_cards = result.get("cards")
    if isinstance(raw_cards, list):
        for index, card in enumerate(raw_cards, 1):
            if isinstance(card, dict):
                title = _clean_text(card.get("title") or card.get("question") or card.get("label") or "")
                body = _clean_text(
                    card.get("body") or card.get("description") or card.get("content")
                    or card.get("answer") or card.get("details") or ""
                )
                if _is_generic_item_label(title):
                    if not body:
                        continue
                    title = _derive_item_title(body, index)
                if title or body:
                    cards.append({"title": (title or _derive_item_title(body, index))[:110], "body": body[:500]})
            elif card:
                body = _clean_text(card)
                cards.append({"title": _derive_item_title(body, index), "body": body[:500]})

    # When the user has edited the written result, regenerate the visual from that text.
    if prefer_content and content_sections:
        items = content_sections
    elif cards:
        items = cards
        if len(items) < 3 and content_sections:
            seen = {item["title"].lower() for item in items}
            for section in content_sections:
                if section["title"].lower() not in seen:
                    items.append(section)
                    seen.add(section["title"].lower())
                if len(items) >= 10:
                    break
    else:
        items = content_sections

    if not items:
        important = result.get("important_lines") or []
        if isinstance(important, list):
            for index, line in enumerate(important, 1):
                body = _clean_text(line)
                if body:
                    items.append({"title": _derive_item_title(body, index), "body": body[:500]})

    if not items:
        words = result.get("important_words") or []
        if isinstance(words, list) and words:
            items = [{"title": _clean_text(word), "body": "Important concept identified in the source."} for word in words[:10]]

    if not items:
        source = _clean_text(result.get("source_text") or result.get("content") or "No structured details were returned.")
        sentences = re.split(r"(?<=[.!?])\s+", source)
        items = [
            {"title": _derive_item_title(sentence, index), "body": sentence[:500]}
            for index, sentence in enumerate(sentences[:8], 1) if sentence
        ]

    # One final guard: never expose generic ITEM/SECTION placeholders in the visual labels.
    normalized_items: list[dict[str, str]] = []
    for index, item in enumerate(items[:12], 1):
        title = _clean_text(item.get("title", ""))
        body = _clean_text(item.get("body", ""))
        if _is_generic_item_label(title):
            title = _derive_item_title(body, index)
        if title or body:
            normalized_items.append({"title": title or _derive_item_title(body, index), "body": body})
    return normalized_items


def _extract_flow_nodes(result: dict[str, Any], items: list[dict[str, str]]) -> list[dict[str, str]]:
    mermaid = str(result.get("mermaid") or "")
    nodes: list[dict[str, str]] = []
    # Read common Mermaid flowchart node syntax: A[Label] --> B[Label].
    matches = re.findall(r"[A-Za-z0-9_]+\s*[\[({]([^\]})]+)[\])}]", mermaid)
    for index, label in enumerate(matches):
        label = _clean_text(label.strip('"\''))
        if label and all(node["title"].lower() != label.lower() for node in nodes):
            matched_item = next(
                (item for item in items if item["title"].lower() == label.lower()),
                items[index] if index < len(items) else None,
            )
            nodes.append({
                "title": label[:100],
                "body": (matched_item.get("body", "")[:220] if matched_item else ""),
            })
    if len(nodes) >= 2:
        return nodes[:9]
    step_items = []
    for item in items:
        title = item["title"]
        if re.search(r"step|stage|phase|process|collect|prepare|train|evaluate|predict|improve", title, re.I):
            step_items.append(item)
    return (step_items or items)[:9]


def _rounded_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], palette: dict[str, str], accent: str | None = None, radius: int = 24) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=palette["panel2"], outline=accent or palette["line"], width=2)
    if accent:
        draw.rounded_rectangle((box[0], box[1], box[0] + 12, box[3]), radius=6, fill=accent)


def _draw_flowchart(title: str, fmt: str, items: list[dict[str, str]], palette: dict[str, str]) -> Image.Image:
    nodes = items[:8]
    height = 360 + len(nodes) * 175
    image, draw = _new_visual(title, fmt, palette, height)
    x1, x2 = 200, 1400
    node_h = 112
    start_y = 285
    for index, item in enumerate(nodes):
        y = start_y + index * 155
        if index:
            cx = 800
            draw.line((cx, y - 43, cx, y - 13), fill=palette["accent2"], width=6)
            draw.polygon([(cx - 12, y - 20), (cx + 12, y - 20), (cx, y - 5)], fill=palette["accent2"])
        accent = palette["accent"] if index % 2 == 0 else palette["accent2"]
        _rounded_card(draw, (x1, y, x2, y + node_h), palette, accent)
        draw.ellipse((x1 + 25, y + 27, x1 + 82, y + 84), fill=accent)
        num = str(index + 1)
        draw.text((x1 + 44, y + 38), num, font=_font(23, True), fill="#10172A", anchor="mm")
        draw.text((x1 + 110, y + 19), item["title"][:85], font=_font(25, True), fill=palette["text"])
        if item.get("body"):
            _draw_wrapped(draw, (x1 + 110, y + 58), item["body"], _font(17), palette["muted"], 1000, 5, 2)
    draw.text((92, image.height - 85), f"{len(nodes)} stages  •  Follow the sequence from top to bottom", font=_font(18), fill=palette["muted"])
    return image


def _draw_mindmap(title: str, fmt: str, items: list[dict[str, str]], palette: dict[str, str]) -> Image.Image:
    nodes = items[:8]
    image, draw = _new_visual(title, fmt, palette, 1250)
    cx, cy = 800, 690
    radius_x, radius_y = 545, 365
    positions = []
    for i in range(len(nodes)):
        angle = -math.pi / 2 + (2 * math.pi * i / max(1, len(nodes)))
        px = int(cx + radius_x * math.cos(angle))
        py = int(cy + radius_y * math.sin(angle))
        positions.append((px, py))
        draw.line((cx, cy, px, py), fill=palette["line"], width=7)
    # Center topic node
    draw.rounded_rectangle((cx - 245, cy - 92, cx + 245, cy + 92), radius=38, fill=palette["accent"], outline=palette["white"], width=2)
    _draw_wrapped(draw, (cx - 200, cy - 34), title[:70], _font(30, True), "#10172A", 400, 5, 3)
    accents = [palette["accent2"], palette["warm"], palette["accent"], "#80B9FF"]
    for i, (item, (px, py)) in enumerate(zip(nodes, positions)):
        w, h = 360, 150
        box = (px - w // 2, py - h // 2, px + w // 2, py + h // 2)
        accent = accents[i % len(accents)]
        _rounded_card(draw, box, palette, accent)
        _draw_wrapped(draw, (box[0] + 24, box[1] + 20), item["title"], _font(22, True), palette["text"], w - 48, 5, 2)
        if item.get("body"):
            _draw_wrapped(draw, (box[0] + 24, box[1] + 69), item["body"], _font(15), palette["muted"], w - 48, 4, 3)
    draw.text((92, image.height - 85), "Central idea connected to related concepts", font=_font(18), fill=palette["muted"])
    return image


def _draw_timeline(title: str, fmt: str, items: list[dict[str, str]], palette: dict[str, str]) -> Image.Image:
    nodes = items[:10]
    height = 340 + len(nodes) * 165
    image, draw = _new_visual(title, fmt, palette, height)
    x_line = 220
    top = 300
    draw.line((x_line, top + 20, x_line, top + (len(nodes) - 1) * 145 + 100), fill=palette["accent"], width=8)
    for i, item in enumerate(nodes):
        y = top + i * 145
        accent = palette["accent2"] if i % 2 else palette["accent"]
        draw.ellipse((x_line - 20, y + 22, x_line + 20, y + 62), fill=accent, outline=palette["white"], width=2)
        _rounded_card(draw, (300, y, 1390, y + 112), palette, accent)
        date_match = re.search(r"\b(\d{4}|\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b", item["title"], re.I)
        label = date_match.group(0) if date_match else f"{i + 1:02d}"
        draw.text((330, y + 17), label.upper(), font=_font(15, True), fill=accent)
        draw.text((550, y + 15), item["title"][:62], font=_font(22, True), fill=palette["text"])
        if item.get("body"):
            _draw_wrapped(draw, (550, y + 54), item["body"], _font(15), palette["muted"], 780, 4, 2)
    return image


def _draw_comparison(title: str, fmt: str, result: dict[str, Any], items: list[dict[str, str]], palette: dict[str, str]) -> Image.Image:
    table = result.get("table") if isinstance(result.get("table"), dict) else {}
    headers = table.get("headers") if isinstance(table.get("headers"), list) else []
    rows = table.get("rows") if isinstance(table.get("rows"), list) else []
    if not headers or not rows:
        headers = ["Concept", "Explanation"]
        rows = [[it["title"], it.get("body", "")] for it in items[:8]]
    headers = [str(h) for h in headers[:4]]
    rows = [r if isinstance(r, list) else [str(r)] for r in rows[:10]]
    cols = max(1, len(headers))
    height = 350 + (len(rows) + 1) * 125
    image, draw = _new_visual(title, fmt, palette, height)
    left, right, top = 90, 1510, 285
    usable = right - left
    col_w = usable // cols
    draw.rounded_rectangle((left, top, right, top + 94), radius=18, fill=palette["accent"])
    for c, header in enumerate(headers):
        x = left + c * col_w + 19
        _draw_wrapped(draw, (x, top + 29), header, _font(20, True), "#10172A", col_w - 36, 4, 2)
    y = top + 104
    for ri, row in enumerate(rows):
        draw.rounded_rectangle((left, y, right, y + 112), radius=15, fill=palette["panel2"] if ri % 2 == 0 else palette["soft"], outline=palette["line"], width=1)
        for c in range(cols):
            value = str(row[c]) if c < len(row) else ""
            x = left + c * col_w + 19
            _draw_wrapped(draw, (x, y + 19), value, _font(17, c == 0), palette["text"] if c == 0 else palette["muted"], col_w - 36, 5, 4)
        y += 121
    return image


def _draw_flashcards(title: str, fmt: str, items: list[dict[str, str]], palette: dict[str, str]) -> Image.Image:
    nodes = items[:10]
    rows = math.ceil(len(nodes) / 2)
    height = 320 + rows * 320
    image, draw = _new_visual(title, fmt, palette, height)
    gap, card_w, card_h = 36, 690, 270
    for i, item in enumerate(nodes):
        col, row = i % 2, i // 2
        x = 92 + col * (card_w + gap)
        y = 285 + row * 310
        accent = palette["accent"] if i % 2 == 0 else palette["accent2"]
        _rounded_card(draw, (x, y, x + card_w, y + card_h), palette, accent)
        draw.text((x + 28, y + 22), f"FLASHCARD  {i + 1:02d}", font=_font(15, True), fill=accent)
        question = item["title"]
        answer = item.get("body") or "Review this key concept from your source material."
        _draw_wrapped(draw, (x + 28, y + 62), question, _font(25, True), palette["text"], card_w - 56, 6, 3)
        draw.line((x + 28, y + 145, x + card_w - 28, y + 145), fill=palette["line"], width=2)
        _draw_wrapped(draw, (x + 28, y + 166), answer, _font(17), palette["muted"], card_w - 56, 5, 5)
    return image


def _draw_infographic(title: str, fmt: str, result: dict[str, Any], items: list[dict[str, str]], palette: dict[str, str]) -> Image.Image:
    nodes = items[:9]
    rows = math.ceil(len(nodes) / 3)
    height = 390 + rows * 270 + 120
    image, draw = _new_visual(title, fmt, palette, height)
    # Summary banner
    summary = _clean_text(result.get("summary") or (nodes[0]["body"] if nodes else "A visual overview of the key ideas."))
    draw.rounded_rectangle((92, 280, 1508, 405), radius=22, fill=palette["soft"], outline=palette["line"], width=2)
    _draw_wrapped(draw, (125, 309), summary, _font(20, True), palette["text"], 1340, 7, 3)
    colors = [palette["accent"], palette["accent2"], palette["warm"]]
    card_w, card_h, gap_x, gap_y = 440, 220, 30, 28
    for i, item in enumerate(nodes):
        col, row = i % 3, i // 3
        x = 92 + col * (card_w + gap_x)
        y = 445 + row * (card_h + gap_y)
        accent = colors[i % len(colors)]
        _rounded_card(draw, (x, y, x + card_w, y + card_h), palette, accent)
        draw.ellipse((x + 24, y + 22, x + 76, y + 74), fill=accent)
        draw.text((x + 50, y + 48), str(i + 1), font=_font(19, True), fill="#10172A", anchor="mm")
        _draw_wrapped(draw, (x + 95, y + 27), item["title"], _font(21, True), palette["text"], card_w - 120, 4, 2)
        if item.get("body"):
            _draw_wrapped(draw, (x + 26, y + 100), item["body"], _font(16), palette["muted"], card_w - 52, 5, 5)
    return image


def _draw_editorial(title: str, fmt: str, items: list[dict[str, str]], palette: dict[str, str]) -> Image.Image:
    nodes = items[:10]
    rows = math.ceil(len(nodes) / 2)
    height = 330 + rows * 235 + 80
    image, draw = _new_visual(title, fmt, palette, height)
    for i, item in enumerate(nodes):
        col, row = i % 2, i // 2
        x = 92 + col * 720
        y = 285 + row * 220
        accent = palette["accent"] if i % 2 == 0 else palette["accent2"]
        _rounded_card(draw, (x, y, x + 680, y + 188), palette, accent)
        _draw_wrapped(draw, (x + 28, y + 26), item["title"], _font(23, True), palette["text"], 620, 5, 2)
        if item.get("body"):
            _draw_wrapped(draw, (x + 28, y + 76), item["body"], _font(16), palette["muted"], 620, 5, 5)
    return image




def _draw_presentation(title: str, fmt: str, items: list[dict[str, str]], palette: dict[str, str]) -> Image.Image:
    nodes = items[:8]
    rows = math.ceil(len(nodes) / 2)
    height = 350 + rows * 330
    image, draw = _new_visual(title, fmt, palette, height)
    slide_w, slide_h = 680, 285
    for i, item in enumerate(nodes):
        col, row = i % 2, i // 2
        x, y = 92 + col * 720, 285 + row * 310
        accent = palette["accent"] if i % 2 == 0 else palette["accent2"]
        draw.rounded_rectangle((x, y, x + slide_w, y + slide_h), radius=20, fill=palette["panel2"], outline=palette["line"], width=2)
        draw.rounded_rectangle((x, y, x + slide_w, y + 16), radius=8, fill=accent)
        draw.text((x + 25, y + 38), f"SLIDE {i + 1:02d}", font=_font(15, True), fill=accent)
        _draw_wrapped(draw, (x + 25, y + 82), item["title"], _font(27, True), palette["text"], slide_w - 50, 6, 2)
        if item.get("body"):
            _draw_wrapped(draw, (x + 25, y + 150), item["body"], _font(17), palette["muted"], slide_w - 50, 5, 4)
        draw.text((x + slide_w - 30, y + slide_h - 33), "DATAMIND", font=_font(11, True), fill=palette["muted"], anchor="ra")
    return image


def _draw_summary(title: str, fmt: str, result: dict[str, Any], items: list[dict[str, str]], palette: dict[str, str]) -> Image.Image:
    nodes = items[:6]
    image, draw = _new_visual(title, fmt, palette, 1120)
    summary = _clean_text(result.get("summary") or (nodes[0]["body"] if nodes else "A concise overview of the source information."))
    draw.rounded_rectangle((92, 282, 1508, 490), radius=26, fill=palette["soft"], outline=palette["line"], width=2)
    draw.text((128, 312), "THE BIG PICTURE", font=_font(17, True), fill=palette["accent"])
    _draw_wrapped(draw, (128, 357), summary, _font(24, True), palette["text"], 1330, 8, 4)
    draw.text((94, 535), "KEY TAKEAWAYS", font=_font(17, True), fill=palette["accent2"])
    for i, item in enumerate(nodes):
        row = i // 2
        col = i % 2
        x = 92 + col * 720
        y = 585 + row * 145
        accent = palette["accent"] if i % 2 == 0 else palette["accent2"]
        _rounded_card(draw, (x, y, x + 680, y + 118), palette, accent)
        draw.ellipse((x + 20, y + 32, x + 64, y + 76), fill=accent)
        draw.text((x + 42, y + 54), str(i + 1), font=_font(17, True), fill="#10172A", anchor="mm")
        _draw_wrapped(draw, (x + 85, y + 18), item["title"], _font(19, True), palette["text"], 560, 4, 2)
        if item.get("body"):
            _draw_wrapped(draw, (x + 85, y + 56), item["body"], _font(14), palette["muted"], 560, 4, 2)
    return image


def build_visual_png(result: dict[str, Any], requested_format: str | None = None, visual_style: str = "professional") -> bytes:
    """Build a real PNG visual for every DataMind output format."""
    fmt = str(requested_format or result.get("format") or "structured_notes").lower().replace(" ", "_")
    # Resolve friendly names and backend aliases.
    aliases = {
        "mind_map": "mindmap", "structured_notes": "structured_notes",
        "step_by_step_guide": "step_by_step", "smart_summary": "summary",
        "comparison_table": "comparison_table", "mermaid_diagram": "mermaid",
    }
    fmt = aliases.get(fmt, fmt)
    label = next((name for name, data in FORMATS.items() if data["id"] == fmt), fmt.replace("_", " ").title())
    title = str(result.get("title") or label or "DataMind Visual")
    palette = VISUAL_PALETTES.get(visual_style, VISUAL_PALETTES["professional"])
    items = _extract_visual_items(result)

    if fmt in {"flowchart", "workflow", "mermaid"}:
        image = _draw_flowchart(title, label, _extract_flow_nodes(result, items), palette)
    elif fmt in {"mindmap", "mind_map"}:
        image = _draw_mindmap(title, label, items, palette)
    elif fmt == "timeline":
        image = _draw_timeline(title, label, items, palette)
    elif fmt == "comparison_table":
        image = _draw_comparison(title, label, result, items, palette)
    elif fmt == "flashcards":
        image = _draw_flashcards(title, label, items, palette)
    elif fmt == "infographic":
        image = _draw_infographic(title, label, result, items, palette)
    elif fmt in {"step_by_step", "step-by-step"}:
        image = _draw_flowchart(title, label, items, palette)
    elif fmt == "presentation":
        image = _draw_presentation(title, label, items, palette)
    elif fmt == "summary":
        image = _draw_summary(title, label, result, items, palette)
    else:
        # Structured notes and any future formats receive an editorial board.
        image = _draw_editorial(title, label, items, palette)

    output = BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()


def render_result(result: dict[str, Any]) -> None:
    selected_options_for_result = st.session_state.get("last_options") or {}
    fmt = str(selected_options_for_result.get("format") or result.get("format") or "transformation")
    label = next(
        (name for name, value in FORMATS.items() if value["id"] == fmt),
        fmt.replace("_", " ").title(),
    )

    # Keep an editable buffer tied to the currently active result.
    active_token = st.session_state.get("last_result_token")
    if not active_token:
        active_token = str(uuid4())
        st.session_state.last_result_token = active_token
    if st.session_state.get("dm_editor_token") != active_token:
        original_content = str(result.get("content") or "")
        st.session_state.dm_editor_token = active_token
        st.session_state.dm_editor_content = original_content
        st.session_state.dm_editor_original_content = original_content
        st.session_state.dm_content_edited = False

    edited_content = str(st.session_state.get("dm_editor_content", result.get("content") or ""))
    display_result = dict(result)
    display_result["content"] = edited_content
    if st.session_state.get("dm_content_edited"):
        display_result["_prefer_content"] = True

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

    visual_result = dict(display_result)
    visual_result.setdefault("source_text", st.session_state.get("last_source_text", ""))
    if st.session_state.get("dm_content_edited"):
        # The edited text becomes the source of truth for the regenerated visual.
        visual_result["cards"] = []
        visual_result["table"] = None
        visual_result["_prefer_content"] = True

    overview_tab, edit_tab, visual_tab, source_tab, raw_tab = st.tabs(
        ["✦  Overview", "✎  Edit text & PDF", "▧  Visual output", "◫  Source & coverage", "{}  Raw data"]
    )
    with overview_tab:
        st.markdown(edited_content or "No written explanation was returned.")
        important_lines = result.get("important_lines") or []
        if important_lines:
            with st.expander("Important lines from the original source"):
                for line in important_lines:
                    st.markdown(f"- {line}")

    with edit_tab:
        st.markdown("#### Make the result yours")
        st.caption("Edit the generated explanation below. Apply your changes to update the overview and visual output, or download the current draft as a PDF.")
        current_edit = st.text_area(
            "Editable result text",
            key="dm_editor_content",
            height=390,
            label_visibility="collapsed",
            placeholder="Your generated result will appear here. Edit headings, explanations, examples or wording…",
        )
        # Compare against the currently applied result, not the first AI draft.
        changed = current_edit != str(result.get("content") or "")
        edit_col, reset_col, edit_status_col = st.columns([1.25, 1.0, 2.2], vertical_alignment="center")
        with edit_col:
            apply_edits = st.button(
                "✓  Apply text changes", type="primary", use_container_width=True,
                disabled=not changed, key="dm_apply_text_edits",
            )
        with reset_col:
            st.button(
                "Reset original", use_container_width=True,
                disabled=not changed, key="dm_reset_text_edits",
                on_click=reset_editor_to_original,
            )
        with edit_status_col:
            st.caption("Unsaved edits" if changed else "Text is up to date")

        if apply_edits:
            updated_result = dict(result)
            updated_result["content"] = current_edit
            st.session_state.last_result = updated_result
            st.session_state.dm_editor_content = current_edit
            st.session_state.dm_content_edited = True
            # Preserve the edited copy in the in-session history as a new revision.
            add_to_history(
                updated_result,
                st.session_state.get("last_source_text", ""),
                st.session_state.get("last_options") or {},
            )
            st.success("Your edits are applied. The Overview and Visual Output now use your updated text.")
            st.rerun()

        pdf_col, md_col, hint_col = st.columns([1.15, 1.15, 2.2], vertical_alignment="center")
        slug = re.sub(r"[^a-z0-9]+", "-", str(result.get("title") or "datamind-result").lower()).strip("-")[:48] or "datamind-result"
        with pdf_col:
            try:
                pdf_bytes = build_result_pdf(str(result.get("title") or "DataMind result"), label, current_edit)
                st.download_button(
                    "↓  Download text as PDF", pdf_bytes,
                    file_name=f"{slug}.pdf", mime="application/pdf",
                    use_container_width=True, key="dm_download_editable_pdf",
                )
            except Exception as exc:
                st.error(f"PDF export failed: {exc}")
        with md_col:
            st.download_button(
                "↓  Download text", current_edit,
                file_name=f"{slug}.txt", mime="text/plain",
                use_container_width=True, key="dm_download_editable_txt",
            )
        with hint_col:
            st.caption("PDF export includes the text currently visible in this editor, including edits not yet applied.")

    with visual_tab:
        selected_options = st.session_state.get("last_options") or {}
        selected_visual_style = selected_options.get("visual_style", "professional")
        selected_format = selected_options.get("format") or fmt
        try:
            visual_png = build_visual_png(visual_result, selected_format, selected_visual_style)
            st.markdown("#### Your generated visual")
            st.caption("The visual is generated from your structured result. Apply text edits to refresh the visual using your updated wording.")
            st.image(visual_png, use_container_width=True)
            slug = re.sub(r"[^a-z0-9]+", "-", str(result.get("title") or label).lower()).strip("-")[:48] or "visual"
            st.download_button(
                "↓  Download visual as PNG",
                data=visual_png,
                file_name=f"datamind-{slug}.png",
                mime="image/png",
                type="primary",
                use_container_width=True,
                key="download_visual_png",
            )
        except Exception as exc:
            st.error(f"Could not create the visual image: {exc}")

        mermaid = result.get("mermaid")
        if mermaid:
            with st.expander("Interactive Mermaid preview and source"):
                components.html(mermaid_html(str(mermaid)), height=420, scrolling=True)
                st.code(str(mermaid), language="mermaid")
                st.download_button(
                    "Download editable Mermaid source", str(mermaid),
                    file_name="datamind-diagram.mmd", mime="text/plain",
                    key="download_mermaid_source",
                )
        with st.expander("View the structured visual data"):
            render_cards(result.get("cards") or [], fmt)
            table = result.get("table")
            if isinstance(table, dict):
                columns = table_to_columns(table)
                if columns:
                    st.dataframe(columns, use_container_width=True, hide_index=True)

    with source_tab:
        render_source_coverage(result)
        if not result.get("coverage") and not result.get("source_items") and not result.get("source_table"):
            st.caption("No separate source-register metadata was returned for this result.")

    with raw_tab:
        st.json(display_result, expanded=True)

    st.markdown("#### Export your work")
    exp1, exp2, exp3, exp4, exp5 = st.columns(5)
    result_slug = re.sub(r"[^a-z0-9]+", "-", str(result.get("title") or "datamind-result").lower()).strip("-")[:48] or "datamind-result"
    with exp1:
        st.download_button(
            "↓  Visual PNG", build_visual_png(
                visual_result,
                (st.session_state.get("last_options") or {}).get("format") or fmt,
                (st.session_state.get("last_options") or {}).get("visual_style", "professional"),
            ),
            file_name=f"{result_slug}-visual.png", mime="image/png",
            use_container_width=True, key="download_result_png",
        )
    with exp2:
        st.download_button(
            "↓  Text PDF", build_result_pdf(str(result.get("title") or "DataMind result"), label, edited_content),
            file_name=f"{result_slug}.pdf", mime="application/pdf",
            use_container_width=True, key="download_result_pdf",
        )
    with exp3:
        st.download_button(
            "↓  Markdown", build_result_markdown(display_result),
            file_name=f"{result_slug}.md", mime="text/markdown",
            use_container_width=True, key="download_result_markdown",
        )
    with exp4:
        st.download_button(
            "↓  JSON", json.dumps(display_result, ensure_ascii=False, indent=2),
            file_name=f"{result_slug}.json", mime="application/json",
            use_container_width=True, key="download_result_json",
        )
    with exp5:
        if result.get("mermaid"):
            st.download_button(
                "↓  Diagram code", str(result["mermaid"]),
                file_name=f"{result_slug}.mmd", mime="text/plain",
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
                activate_result(result)
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
                    activate_result(updated)
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
                    activate_result(item.get("result") or {})
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
