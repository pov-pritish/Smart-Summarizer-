# ✨ Text or Email Summarizer

A clean, professional web app that summarizes long emails, articles, or
any pasted text — or a `.txt` / `.docx` file — into a short, readable summary.
AI can also be used simply by adding an api key, else it uses built in logic.
Built with **Streamlit** and the **Gemini API**.

**Live demo:** _add your deployed Streamlit Cloud link here after deploying_

![status](https://img.shields.io/badge/status-active-brightgreen)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![streamlit](https://img.shields.io/badge/built%20with-Streamlit-ff4b4b)

---

## Features

- 📋 **Paste text** — a large text area for pasting emails, articles, or notes
- 📁 **Drag & drop upload** — supports `.txt` and `.docx` files
- ✨ **AI summarization** — powered by Google's Gemini API
- 🎛️ **Adjustable summary length & style** — very short to detailed, paragraph or bullets
- 🧠 **Offline fallback summarizer** — the app still works and produces a summary
  even without an API key, so it's always demo-ready
- ⬇️ **Download the summary** as a `.txt` file
- 🎨 **Polished dark UI** with a translucent watermark signature

---

## How it works

1. The user pastes text or drags a file into the browser.
2. Streamlit reads that input into a Python string.
3. On clicking **Summarize**, the text is sent to the Gemini API with a
   carefully crafted prompt (length + style controlled by the sidebar).
4. The generated summary is returned and rendered in a styled card, with word
   counts and generation time shown below it.

---

## Getting started locally

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/smart-ai-email-summarizer.git
cd smart-ai-email-summarizer

# 2. Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Gemini API key
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml and paste your key

# 5. Run the app
streamlit run app.py
```

Get a free Gemini API key at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).

> No API key? The app automatically falls back to a built-in offline
> summarizer, so it's still fully functional for demos and recruiters.

---

## Deploying on Streamlit Community Cloud

1. Push this repo to your GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, pick this repo and `app.py` as the entry point.
4. Under **Advanced settings → Secrets**, paste:
   ```toml
   GEMINI_API_KEY = "your-real-key-here"
   ```
5. Click **Deploy**. Your app will be live at a `*.streamlit.app` URL.

---

## Project structure

```
smart-ai-email-summarizer/
├── app.py                          # Main Streamlit app
├── requirements.txt                # Python dependencies
├── .streamlit/
│   ├── config.toml                 # Theme settings
│   └── secrets.toml.example        # Template for API key (copy → secrets.toml)
├── .gitignore
└── README.md
```

---

## Tech stack

- [Streamlit](https://streamlit.io/) — web app framework
- [Google Generative AI SDK](https://ai.google.dev/) — Gemini API for summarization
- [python-docx](https://python-docx.readthedocs.io/) — reading `.docx` uploads

---

## Author

**Pritish** — built as a first end-to-end AI project, from prompt design to
deployment.
