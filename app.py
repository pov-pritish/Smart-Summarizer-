"""
Smart AI Email & Text Summarizer
---------------------------------
A polished Streamlit app that summarizes emails, articles, or any long text
using Google's Gemini API. Supports pasted text and drag-and-drop file
uploads (.txt / .docx).

Author: Pritish
"""

import io
import re
import time

import streamlit as st

# docx reading is optional -- app still works without it for .txt files
try:
    import docx  # python-docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import google.genai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


# --------------------------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Text or Email Summarizer",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------------------------------
# STYLING — professional theme + translucent watermark
# --------------------------------------------------------------------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* App background gradient */
        .stApp {
            background: linear-gradient(160deg, #0f172a 0%, #1e293b 45%, #0f172a 100%);
        }

        /* Main title */
        .main-title {
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 2.6rem;
            text-align: center;
            background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
            padding-top: 0.5rem;
        }

        .subtitle {
            text-align: center;
            color: #94a3b8;
            font-size: 1.05rem;
            margin-bottom: 1.8rem;
        }

        /* Card container look for main content */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        div[data-testid="stTextArea"] textarea {
            background-color: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 12px;
            color: #e2e8f0;
            font-size: 0.95rem;
        }

        div[data-testid="stFileUploader"] {
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px dashed rgba(148, 163, 184, 0.4);
            border-radius: 12px;
            padding: 0.6rem;
        }

        /* Buttons */
        .stButton > button {
            width: 100%;
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 10px;
            padding: 0.65rem 1rem;
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(139, 92, 246, 0.45);
            color: white;
        }

        /* Summary result card */
        .summary-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-left: 4px solid #8b5cf6;
            border-radius: 12px;
            padding: 1.4rem 1.6rem;
            color: #e2e8f0;
            line-height: 1.65;
            font-size: 1rem;
            margin-top: 1rem;
        }

        .meta-row {
            display: flex;
            justify-content: space-between;
            color: #64748b;
            font-size: 0.8rem;
            margin-top: 0.5rem;
        }

        /* Translucent watermark, diagonally placed */
        .watermark {
            position: fixed;
            bottom: 18px;
            right: 24px;
            font-family: 'Poppins', sans-serif;
            font-size: 0.85rem;
            font-weight: 600;
            color: rgba(226, 232, 240, 0.18);
            letter-spacing: 0.5px;
            pointer-events: none;
            z-index: 1000;
            user-select: none;
        }

        .watermark-bg {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-28deg);
            font-family: 'Poppins', sans-serif;
            font-size: 5.5rem;
            font-weight: 700;
            color: rgba(226, 232, 240, 0.035);
            white-space: nowrap;
            pointer-events: none;
            z-index: 0;
            user-select: none;
        }

        /* Highlighted word-count control */
        .word-target-box {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.16), rgba(139, 92, 246, 0.10));
            border: 1px solid rgba(139, 92, 246, 0.4);
            border-radius: 14px;
            padding: 1rem 1.4rem 0.4rem 1.4rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 0 24px rgba(139, 92, 246, 0.12);
        }
        .word-target-label {
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            font-size: 1rem;
            color: #e0e7ff;
            margin-bottom: 0.2rem;
        }
        .word-target-sub {
            color: #94a3b8;
            font-size: 0.82rem;
            margin-bottom: 0.4rem;
        }

        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
    </style>

    <div class="watermark-bg">MADE BY PRITISH</div>
    <div class="watermark">Made by Pritish</div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# HEADER
# --------------------------------------------------------------------------
st.markdown('<div class="main-title">Text or Email Summarizer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Paste an email, article, or any long text — or drop a file — and get a clean summary in seconds.</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# SIDEBAR — settings
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value="",
        placeholder="Paste your own Gemini API key (optional)",
        help="Get a free key at https://aistudio.google.com/app/apikey. "
             "Left empty by default — if you don't add one, a built-in "
             "offline summarizer is used instead.",
    )

    summary_style = st.radio(
        "Style",
        ["Paragraph", "Bullet points"],
        horizontal=True,
    )

    st.markdown("---")
    st.subheader("👤 About the developer")
    st.markdown(
        """
        **Pritish** \n
        📧 [pritishkantibala@gmail.com](mailto:pritishkantibala@gmail.com)\n
        💻 [GitHub](https://github.com/pov-pritish)\n
        🔗 [LinkedIn](https://linkedin.com/in/pov-pritish)
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.caption("Built with Streamlit + Gemini API")
    st.caption("© Pritish — Smart AI Email & Text Summarizer")


# --------------------------------------------------------------------------
# SUMMARIZATION LOGIC
# --------------------------------------------------------------------------
def call_gemini_api(text: str, key: str, target_words: int, style: str) -> str:
    """Send the text to Gemini and return a generated summary of a target length."""
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    format_instruction = (
        "Format the summary as clear bullet points."
        if style == "Bullet points"
        else "Format the summary as flowing paragraph(s)."
    )

    prompt = (
        "You are a professional summarization assistant. Summarize the following "
        f"text in approximately {target_words} words (a little under is fine, "
        "don't go significantly over). Preserve the key facts, names, dates, "
        "and any action items. Do not add information that isn't in the text. "
        f"{format_instruction}\n\n"
        f"TEXT:\n\"\"\"\n{text}\n\"\"\""
    )

    response = model.generate_content(prompt)
    return response.text.strip()


def fallback_summarizer(text: str, target_words: int, style: str = "Paragraph") -> str:
    """
    A simple offline extractive summarizer used when no API key is provided,
    so the app remains fully functional as a live demo. Picks the highest-
    scoring sentences, in original order, until the target word count is
    reached (won't overshoot by more than one sentence).
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]

    if len(sentences) <= 1:
        picked = sentences
    else:
        # crude frequency-based scoring
        words = re.findall(r"[a-zA-Z']+", text.lower())
        stopwords = {
            "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "to",
            "of", "in", "on", "for", "with", "as", "at", "by", "this", "that", "it",
            "be", "from", "will", "has", "have", "had", "not", "which", "their",
        }
        freq = {}
        for w in words:
            if w not in stopwords:
                freq[w] = freq.get(w, 0) + 1

        scores = []
        for i, sent in enumerate(sentences):
            sent_words = re.findall(r"[a-zA-Z']+", sent.lower())
            score = sum(freq.get(w, 0) for w in sent_words)
            scores.append((score, i, sent))

        # greedily add sentences by score until we hit the target word budget
        by_score = sorted(scores, key=lambda x: x[0], reverse=True)
        chosen = []
        running_words = 0
        for score, i, sent in by_score:
            if running_words >= target_words and chosen:
                break
            chosen.append((score, i, sent))
            running_words += len(sent.split())

        chosen_sorted = sorted(chosen, key=lambda x: x[1])  # restore original order
        picked = [s for _, _, s in chosen_sorted]

    if style == "Bullet points":
        return "\n".join(f"- {s}" for s in picked)
    return " ".join(picked)


def generate_summary(text: str) -> str:
    if api_key and GENAI_AVAILABLE:
        try:
            return call_gemini_api(text, api_key, target_words, summary_style)
        except Exception as e:
            st.warning(f"Gemini API call failed ({e}). Falling back to offline summarizer.")
            return fallback_summarizer(text, target_words, summary_style)
    else:
        return fallback_summarizer(text, target_words, summary_style)


def extract_text_from_docx(file_obj) -> str:
    document = docx.Document(io.BytesIO(file_obj.read()))
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())


def word_count(text: str) -> int:
    return len(text.split())


# --------------------------------------------------------------------------
# HIGHLIGHTED CONTROL — target summary word count
# --------------------------------------------------------------------------
st.markdown(
    """
    <div class="word-target-box">
        <div class="word-target-label">🎯 Target Summary Length</div>
        <div class="word-target-sub">Choose roughly how many words you want the summary to be.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
target_words = st.slider(
    "Target summary length (words)",
    min_value=10,
    max_value=1000,
    value=80,
    step=10,
    label_visibility="collapsed",
)
st.markdown(
    f"<p style='text-align:center; color:#c4b5fd; font-weight:600; margin-top:-0.8rem; margin-bottom:1.4rem;'>"
    f"~ {target_words} words</p>",
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------
# MAIN INPUT AREA
# --------------------------------------------------------------------------
tab1, tab2 = st.tabs(["📋 Paste Text", "📁 Upload File"])

source_text = ""

with tab1:
    user_input = st.text_area(
        "Paste your long email, text, or article here:",
        height=250,
        placeholder="Paste your email, article, or notes here...",
    )
    if st.button("✨ Summarize Now", key="btn_text"):
        if user_input.strip() == "":
            st.warning("Please paste some text first.")
        else:
            source_text = user_input

with tab2:
    uploaded_file = st.file_uploader(
        "Drag and drop a .txt or .docx file here",
        type=["txt", "docx"],
    )
    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith(".docx"):
                if not DOCX_AVAILABLE:
                    st.error("python-docx is not installed. Add it to requirements.txt.")
                    file_contents = ""
                else:
                    file_contents = extract_text_from_docx(uploaded_file)
            else:
                file_contents = uploaded_file.read().decode("utf-8", errors="ignore")

            with st.expander("Preview extracted text"):
                st.text(file_contents[:2000] + ("..." if len(file_contents) > 2000 else ""))

            if st.button("✨ Summarize Uploaded File", key="btn_file"):
                if file_contents.strip() == "":
                    st.warning("The uploaded file appears to be empty.")
                else:
                    source_text = file_contents
        except Exception as e:
            st.error(f"Couldn't read that file: {e}")


# --------------------------------------------------------------------------
# GENERATE + DISPLAY SUMMARY
# --------------------------------------------------------------------------
if source_text:
    with st.spinner("Analyzing text..."):
        start = time.time()
        summary = generate_summary(source_text)
        elapsed = time.time() - start

    st.success("Done!")

    # Convert markdown-style bullets ("- item" / "* item") into a real HTML
    # list so they render correctly inside the styled card, whether the
    # summary came from Gemini or the offline fallback.
    lines = [l.strip() for l in summary.splitlines() if l.strip()]
    is_bullets = lines and all(l.startswith(("-", "*")) for l in lines)

    if is_bullets:
        items = "".join(f"<li>{l.lstrip('-* ').strip()}</li>" for l in lines)
        summary_html = f"<ul style='margin:0; padding-left:1.2rem;'>{items}</ul>"
    else:
        summary_html = summary.replace("\n", "<br><br>")

    st.markdown(f'<div class="summary-card">{summary_html}</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="meta-row">
            <span>Original: {word_count(source_text)} words</span>
            <span>Summary: {word_count(summary)} words</span>
            <span>Generated in {elapsed:.1f}s</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.download_button(
        "⬇️ Download Summary",
        data=summary,
        file_name="summary.txt",
        mime="text/plain",
    )
