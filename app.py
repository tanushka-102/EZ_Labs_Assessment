"""
Smart Research Assistant
Author: Tanushka Verma
"""

import streamlit as st
import pdfplumber
import re
import requests
from openai import OpenAI

# Load OpenAI client (v1+ API style)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else "sk-...")

# App config
st.set_page_config(page_title="Smart Research Assistant 🤖", page_icon="📄", layout="wide")

# Optional: Lottie animation
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None

try:
    from streamlit_lottie import st_lottie
    lottie_ai = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_j1adxtyb.json")
    with st.sidebar:
        st_lottie(lottie_ai, height=200)
except:
    pass

# Sidebar
with st.sidebar:
    st.markdown("## 💡 How to Use")
    st.markdown("- Upload a PDF or TXT document")
    st.markdown("- Choose a mode to interact")
    st.markdown("- Ask questions or take a logic challenge")
    st.markdown("---")
    st.markdown("🚀 Built by **Tanushka Verma**")

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

# Summarize
def summarize(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You summarize academic documents clearly."},
            {"role": "user", "content": f"Summarize this document in under 150 words:\n\n{text[:3000]}"}
        ],
        max_tokens=200,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

# Ask Anything
def ask_anything(text, question):
    prompt = f"""
Answer strictly based on the following document. Provide clear paragraph-based justification.

Document:
{text[:3000]}

User Question:
{question}

Answer with justification:
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a research assistant bot."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# Generate Logic Questions
def generate_logic_questions(text):
    prompt = f"Generate 3 logic-based or comprehension questions from this document:\n\n{text[:3000]}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a logic professor."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.5
    )
    return response.choices[0].message.content.strip().split("\n")

# Evaluate Answer
def evaluate_user_answer(text, question, user_answer):
    prompt = f"""
Evaluate this user answer based on the document. Give feedback with reasoning.

Document:
{text[:3000]}

Question:
{question}

User Answer:
{user_answer}

Feedback:
"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a research evaluator."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=250,
        temperature=0.4
    )
    return response.choices[0].message.content.strip()

# Find supporting snippet
def find_snippet(text, answer):
    sentences = re.split(r'(?<=[.!?]) +', text)
    pattern = re.escape(answer[:30])
    for sentence in sentences:
        if re.search(pattern, sentence, re.IGNORECASE):
            return sentence.strip()
    return "Snippet not found."

# Header
st.markdown("<h1 style='text-align:center;'>📄 Smart Research Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Summarize, explore, and test your understanding with AI.</p>", unsafe_allow_html=True)
st.divider()

# File Upload
uploaded_file = st.file_uploader("📤 Upload PDF or TXT Document", type=["pdf", "txt"])

if uploaded_file:
    with st.spinner("📖 Reading your document..."):
        text = extract_text(uploaded_file)
    st.session_state["document_text"] = text

    st.subheader("📌 AI-Generated Summary")
    with st.spinner("🧠 Generating summary..."):
        summary = summarize(text)
    st.success(summary)

    # Interaction Mode
    st.markdown("### 🎯 Choose a Mode")
    mode = st.selectbox("Select:", ["💬 Ask Me Anything", "🧠 Challenge Me (Logic Q&A)"])
    st.markdown("---")

    # Ask Anything Mode
    if mode == "💬 Ask Me Anything":
        question = st.text_input("💬 Ask a question based on the document:")
        if question:
            with st.spinner("🤖 Generating answer..."):
                answer = ask_anything(text, question)
            st.markdown("#### 🧑‍🎓 You Asked:")
            st.code(question)

            st.markdown("#### 🤖 Assistant Answer")
            st.info(answer)

            snippet = find_snippet(text, answer)
            st.markdown("#### 📍 Supporting Snippet")
            st.code(snippet)

    # Challenge Mode
    elif mode == "🧠 Challenge Me (Logic Q&A)":
        if st.button("🎲 Generate Logic Questions"):
            with st.spinner("🧩 Creating questions..."):
                questions = generate_logic_questions(text)

            st.markdown("### 📝 Answer these:")
            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}:** {q}")
                user_input = st.text_input(f"✏️ Your Answer for Q{i+1}", key=f"ans_{i}")
                if user_input:
                    with st.spinner("🔍 Evaluating..."):
                        feedback = evaluate_user_answer(text, q, user_input)
                    st.markdown(f"✅ **Feedback:** {feedback}")

# Footer
st.markdown("<hr><center><small style='color:gray;'>✨ Made with ❤️ by <b>Tanushka Verma</b></small></center>", unsafe_allow_html=True)
