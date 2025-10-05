#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

import os
import threading
import streamlit as st
import requests
import itertools
from fastapi import FastAPI, Query
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

API_KEY = os.getenv("API_KEY", "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")
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
# 🌐 Streamlit Web UI
# --------------------------
def run_streamlit():
    st.set_page_config(page_title="Multi-Model AI Assistant", page_icon="🤖", layout="centered")

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


# --------------------------
# ⚙️ FastAPI (for direct access)
# --------------------------
api = FastAPI()

@api.get("/api/ask")
def api_ask(question: str = Query(..., description="Ask a question to the AI")):
    answer = ask_ai(question)
    return {"question": question, "answer": answer}


# --------------------------
# 🧩 Run both servers
# --------------------------
if __name__ == "__main__":
    threading.Thread(target=lambda: os.system("streamlit run PAI.py --server.port=8501 --server.address=0.0.0.0"), daemon=True).start()
    uvicorn.run(api, host="0.0.0.0", port=8000)
