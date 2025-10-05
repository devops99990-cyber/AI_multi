#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

import streamlit as st
import requests
import itertools
import threading
import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

# ==========================
# 🔑 Configuration
# ==========================
MODELS = itertools.cycle([
    "meta-llama/llama-3.3-70b-instruct",
    "qwen/qwen2.5-coder-32b-instruct",
    "meta-llama/llama-3.2-3b-instruct",
    "qwen/qwen2.5-72b-instruct",
    "mistralai/mistral-nemo",
    "google/gemma-2-9b",
    "mistralai/mistral-7b-instruct"
])

API_KEY = "Bearer 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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": API_KEY,
    "HTTP-Referer": "http://localhost",
    "X-Title": "LocalAI",
    "Content-Type": "application/json"
}

# ==========================
# 🧠 Ask AI Function
# ==========================
def ask_ai(question: str):
    for model in MODELS:
        payload = {"model": model, "messages": [{"role": "user", "content": question}]}
        try:
            print(f"🟢 Trying {model}")
            response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                print(f"⚠️ {model} failed: {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout on {model}")
        except Exception as e:
            print(f"❌ Error with {model}: {e}")
    return "❌ All models failed or took too long. Please check your API key or network."

# ==========================
# 🌐 FastAPI Setup
# ==========================
app = FastAPI(title="Local AI API")

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/ask")
def api_ask(question: str = Query(..., description="Your question for the AI")):
    answer = ask_ai(question)
    return JSONResponse({"question": question, "answer": answer})

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8010, log_level="error")

threading.Thread(target=run_fastapi, daemon=True).start()

# ==========================
# 💬 Streamlit UI
# ==========================
st.set_page_config(page_title="Multi-Model AI Assistant", page_icon="🤖", layout="centered")

st.markdown("""
<style>
body {background-color:#0e1117;color:white;}
.stTextInput > div > div > input {background-color:#1c1f26;color:white;border-radius:10px;}
.stButton>button {background-color:#0078ff;color:white;border-radius:10px;padding:10px 20px;}
h1,h2,h3 {color:#00c4ff;}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

st.title("🤖 Multi-Model AI Assistant")
st.markdown("### Free, fast & smart — powered by OpenRouter’s AI models.")

question = st.text_area("📝 Ask me anything:", placeholder="e.g., Explain the solar system...")

if st.button("🚀 Generate Answer"):
    if not API_KEY or "xxxx" in API_KEY:
        st.error("⚠️ Please insert your valid OpenRouter API key.")
    elif question.strip() == "":
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Thinking... 💭"):
                response = requests.get(f"http://localhost:8010/ask", params={"question": question}, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    st.markdown("---")
                    st.markdown(f"### 🤖 **Answer:**\n\n{data['answer']}")
                else:
                    st.error(f"⚠️ API Error {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"⚠️ Failed to connect to API: {e}")

st.markdown("---")
st.caption("💡 Tip: Type a question or use the link → http://localhost:8010/ask?question=Hello")


