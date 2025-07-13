"""
Smart Research Assistant
Author: Tanushka Verma
"""

import streamlit as st
import openai
import pdfplumber
import os
import re
import requests
from streamlit_lottie import st_lottie

# App Config
st.set_page_config(page_title="Smart Research Assistant 🤖", page_icon="📄", layout="wide")

# Load animation from LottieFiles
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

ai_lottie = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_j1adxtyb.json")

# OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else "sk-..."

# UI Header
st.markdown("<h1 style='text-align: center; color: #6C63FF;'>📄 Smart Research Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:18px;'>Summarize research documents, ask intelligent questions, and get logic-based challenges – all in one app.</p>", unsafe_allow_html=True)
st.divider()

# Sidebar with animation
with st.sidebar:
    st_lottie(ai_lottie, height=200, key="ai")
    st.markdown("### 💡 Instructions")
    st.markdown("- Upload a research document (PDF or TXT)")
    st.markdown("- Choose a mode: ask questions or test your logic")
    st.markdown("- View AI-generated answers with supporting snippets")

# Extract text
def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    elif uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    return "Unsupported file format."

# AI Functions
def summarize(text):
    prompt = f"Summarize this document in under 150 words:\n\n{text[:3000]}"
    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=200, temperature=0.5
    )
    return response.choices[0].text.strip()

def ask_anything(text, question, chat_history=""):
    prompt = f"""
You are a helpful assistant. Answer questions strictly based on the document. Include paragraph-based justification.

Document:
{text[:3000]}

Chat History:
{chat_history}

User Question:
{question}

Answer (with justification):
"""
    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=300, temperature=0.3
    )
    return response.choices[0].text.strip()

def generate_logic_questions(text):
    prompt = f"Generate 3 logic-based or comprehension questions from this document:\n\n{text[:3000]}"
    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=300, temperature=0.5
    )
    return response.choices[0].text.strip().split("\n")

def evaluate_user_answer(text, question, user_answer):
    prompt = f"""
Evaluate the following user answer based on the document provided. Justify if it's correct or not.

Document:
{text[:3000]}

Question:
{question}

User Answer:
{user_answer}

Feedback (with justification):
"""
    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=250, temperature=0.4
    )
    return response.choices[0].text.strip()

def find_snippet(text, answer, n_chars=200):
    sentences = re.split(r'(?<=[.!?]) +', text)
    pattern = re.escape(answer[:30])
    for sentence in sentences:
        if re.search(pattern, sentence, re.IGNORECASE):
            return sentence.strip()
    return "Snippet not found."

# Upload and Process
uploaded_file = st.file_uploader("📤 Upload PDF or TXT Document", type=["pdf", "txt"])

if uploaded_file:
    text = extract_text(uploaded_file)
    st.session_state["document_text"] = text

    st.subheader("📌 AI-Generated Summary")
    summary = summarize(text)
    st.success(summary)

    st.markdown("### 🎯 Choose Your Mode")
    mode = st.radio("", ["💬 Ask Anything", "🧠 Challenge Me"])

    if mode == "💬 Ask Anything":
        question = st.text_input("🔍 Ask a question based on the document")
        if question:
            st.markdown("#### 🤖 Assistant's Response")
            answer = ask_anything(text, question)
            st.info(answer)

            highlight = find_snippet(text, answer)
            st.markdown("#### 📍 Relevant Snippet")
            st.code(highlight)

    elif mode == "🧠 Challenge Me":
        if st.button("Generate Questions"):
            questions = generate_logic_questions(text)
            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}:** {q}")
                user_input = st.text_input(f"📝 Your Answer to Q{i+1}", key=f"answer_{i}")
                if user_input:
                    feedback = evaluate_user_answer(text, q, user_input)
                    st.markdown(f"✅ **Feedback:** {feedback}")

# Footer
st.markdown("<hr><center><small style='color:gray;'>🚀 Made with Streamlit & OpenAI by <b>Tanushka Verma</b></small></center>", unsafe_allow_html=True)
