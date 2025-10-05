#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

import streamlit as st
import requests
import itertools
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import threading
import uvicorn

# --------------------------
# 🔑 Configuration
# --------------------------
MODELS = itertools.cycle([
    "meta-llama/llama-3.3-70b-instruct",
    "qwen/qwen2.5-coder-32b-instruct",
    "meta-llama/llama-3.2-3b-instruct",
    "qwen/qwen2.5-72b-instruct",
    "mistralai/mistral-nemo",
    "google/gemma-2-9b",
    "mistralai/mistral-7b-instruct"
])

API_KEY = "Bearer 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"  # ⚠️ Replace with your real key
API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": API_KEY,
    "HTTP-Referer": "http://localhost",
    "X-Title": "MyLocalAI-Web",
    "Content-Type": "application/json"
}


# --------------------------
# 🧠 Ask AI Function
# --------------------------
def ask_ai(question):
    for model in MODELS:
        payload = {"model": model, "messages": [{"role": "user", "content": question}]}
        try:
            response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
        except Exception as e:
            return f"⚠️ Connection error with **{model}**: {e}"

        if response.status_code != 200:
            continue

        try:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception:
            continue

    return "❌ All models failed. Please check your API key or internet connection."


# --------------------------
# 🌐 FastAPI Setup (runs separately)
# --------------------------
app = FastAPI(title="Local AI API")

@app.get("/ask")
def api_ask(question: str = Query(..., description="Your question to the AI")):
    """Example: http://localhost:8000/ask?question=Hello"""
    answer = ask_ai(question)
    return JSONResponse({"question": question, "answer": answer})


def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)  # separate port for API


# Run FastAPI in the background
threading.Thread(target=run_fastapi, daemon=True).start()


# --------------------------
# 💬 Streamlit UI
# --------------------------
st.set_page_config(page_title="Multi-Model AI Assistant", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
        body {background-color: #0e1117; color: white;}
        .stTextInput > div > div > input {background-color: #1c1f26; color: white; border-radius: 10px;}
        .stButton>button {background-color: #0078ff; color: white; border-radius: 10px; padding: 10px 20px;}
        .stMarkdown h1, h2, h3 {color: #00c4ff;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Multi-Model AI Assistant")
st.markdown("### Free, fast & smart — powered by OpenRouter’s free AI models.")

question = st.text_area("📝 Ask me anything:", placeholder="e.g., Explain the solar system with a table...")

if st.button("🚀 Generate Answer"):
    if not API_KEY or "your_api_key_here" in API_KEY:
        st.error("⚠️ Please paste your valid OpenRouter API key in the code.")
    elif question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking... 💭"):
            answer = ask_ai(question)
        st.markdown("---")
        st.markdown(f"### 🤖 **Answer:**\n\n{answer}")

st.markdown("---")
st.caption("💡 Tip: Type a question and hit **Enter** or click the button. Each request cycles through multiple free models automatically.")
