
import json
import requests
import streamlit as st

DEFAULT_API_URL = "https://datamind-api-gaxe.onrender.com"

st.set_page_config(
    page_title="DataMind",
    page_icon="🧠",
    layout="wide"
)

try:
    API_URL = st.secrets.get(
        "API_BASE_URL",
        DEFAULT_API_URL
    ).rstrip("/")
except Exception:
    API_URL = DEFAULT_API_URL


FORMATS = {
    "Flowchart": "flowchart",
    "Mind Map": "mindmap",
    "Structured Notes": "structured_notes",
    "Infographic": "infographic",
    "Timeline": "timeline",
    "Comparison Table": "comparison_table",
    "Step-by-Step Guide": "step_by_step",
    "Flashcards": "flashcards",
    "Smart Summary": "summary",
    "Workflow": "workflow",
    "Mermaid Diagram": "mermaid",
    "Presentation": "presentation"
}


def get_error(response):
    try:
        body = response.json()
        detail = body.get("detail", body)

        if isinstance(detail, list):
            return "; ".join(
                str(item.get("msg", item))
                for item in detail
            )

        return str(detail)

    except ValueError:
        return response.text[:500]


# Header
st.title("🧠 DataMind")
st.caption("Turn Raw Data Into Clear Understanding.")

st.write(
    "Transform your raw information into structured "
    "notes, flowcharts, mind maps and other formats."
)

# Sidebar settings
with st.sidebar:

    st.header("⚙️ Transformation Settings")

    selected_format = st.selectbox(
        "Output Format",
        list(FORMATS.keys())
    )

    detail = st.selectbox(
        "Detail Level",
        ["short", "medium", "detailed"],
        index=2
    )

    language = st.selectbox(
        "Language",
        ["English", "Hindi", "Hinglish"]
    )

    complexity = st.selectbox(
        "Complexity",
        ["beginner", "intermediate", "advanced"]
    )

    audience = st.selectbox(
        "Audience",
        ["students", "professionals",
         "developers", "general users"]
    )

    visual_style = st.selectbox(
        "Visual Style",
        ["professional", "minimal", "colorful"]
    )

    st.divider()

    if st.button("Test Backend Connection"):
        try:
            health = requests.get(
                f"{API_URL}/api/health",
                timeout=30
            )
            health.raise_for_status()

            info = health.json()
            st.success("Backend Connected!")
            st.json(info)

        except requests.RequestException as e:
            st.error(f"Backend Error: {e}")


# Input settings
st.subheader("1. Add Your Source Data")

input_mode = st.radio(
    "Choose input method",
    ["Paste Text", "Upload Document"],
    horizontal=True
)

raw_text = ""
uploaded_file = None

if input_mode == "Paste Text":

    raw_text = st.text_area(
        "Enter your text or topic",
        height=250,
        placeholder="Paste your raw data here..."
    )

else:

    uploaded_file = st.file_uploader(
        "Upload your document",
        type=["pdf", "docx", "txt", "md", "csv", "json"]
    )


# Transformation options
options = {
    "format": FORMATS[selected_format],
    "detail": detail,
    "language": language,
    "complexity": complexity,
    "audience": audience,
    "visual_style": visual_style
}


# Transform button
if st.button(
    "🚀 Transform with DataMind",
    type="primary",
    use_container_width=True
):

    try:

        with st.spinner(
            "DataMind is processing your information..."
        ):

            if input_mode == "Paste Text":

                if not raw_text.strip():
                    st.warning("Please enter some text first.")
                    st.stop()

                payload = {
                    "text": raw_text,
                    **options
                }

                response = requests.post(
                    f"{API_URL}/api/transform",
                    json=payload,
                    timeout=120
                )

            else:

                if uploaded_file is None:
                    st.warning("Please upload a document.")
                    st.stop()

                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type or
                        "application/octet-stream"
                    )
                }

                response = requests.post(
                    f"{API_URL}/api/transform/file",
                    data=options,
                    files=files,
                    timeout=120
                )

            if not response.ok:
                st.error(
                    f"API Error {response.status_code}: "
                    f"{get_error(response)}"
                )
            else:
                result = response.json()
                st.session_state["result"] = result
                st.success("Transformation completed!")

    except requests.exceptions.Timeout:
        st.error(
            "Request timed out. Please try again."
        )

    except requests.exceptions.RequestException as e:
        st.error(f"Connection failed: {e}")

    except ValueError:
        st.error("Invalid response received from backend.")


# Display results
result = st.session_state.get("result")

if result:

    st.divider()

    st.subheader("2. Transformation Results")

    st.title(
        result.get("title", "DataMind Result")
    )

    st.markdown(
        result.get("content", "No content available.")
    )

    if result.get("mermaid"):

        with st.expander("View Mermaid Diagram Source"):
            st.code(
                result["mermaid"],
                language="mermaid"
            )

    if result.get("cards"):

        with st.expander("View Generated Cards"):
            st.json(result["cards"])

    if result.get("table"):

        with st.expander("View Generated Table Data"):
            st.json(result["table"])

    with st.expander("View Complete Result Data"):

        st.json(result)

    st.download_button(
        "⬇️ Download Result JSON",
        data=json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        ),
        file_name="datamind-result.json",
        mime="application/json"
    )
