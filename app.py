"""
Smart Research Assistant
Author: Tanushka Verma
"""

import streamlit as st
import openai
import pdfplumber
import re
import requests

# Streamlit app configuration
st.set_page_config(page_title="Smart Research Assistant 🤖", page_icon="📄", layout="wide")

# Load Lottie animation (optional)
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
    pass  # skip if not available

# Sidebar instructions
with st.sidebar:
    st.markdown("## 💡 Instructions")
    st.markdown("- Upload a research document (PDF or TXT)")
    st.markdown("- Select a mode: Ask or Challenge")
    st.markdown("- Get intelligent summaries and answers")
    st.markdown("---")
    st.markdown("🚀 Built by **Tanushka Verma**")

# OpenAI key
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else "sk-..."

# Extract text from file
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

# Summarization using GPT
def summarize(text):
    prompt = f"Summarize this document in under 150 words:\n\n{text[:3000]}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

# Ask Anything
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
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a document-based assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# Generate challenge questions
def generate_logic_questions(text):
    prompt = f"Generate 3 logic-based or comprehension questions from this document:\n\n{text[:3000]}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a logical professor generating questions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.5
    )
    return response.choices[0].message.content.strip().split("\n")

# Evaluate answer
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
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a feedback bot."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=250,
        temperature=0.4
    )
    return response.choices[0].message.content.strip()

# Snippet finder
def find_snippet(text, answer):
    sentences = re.split(r'(?<=[.!?]) +', text)
    pattern = re.escape(answer[:30])
    for sentence in sentences:
        if re.search(pattern, sentence, re.IGNORECASE):
            return sentence.strip()
    return "Snippet not found."

# UI Header
st.markdown("<h1 style='text-align:center; color:#6C63FF;'>📄 Smart Research Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:18px;'>Summarize, explore, and test your knowledge on any document using AI.</p>", unsafe_allow_html=True)
st.divider()

# File Upload
uploaded_file = st.file_uploader("📤 Upload PDF or TXT Document", type=["pdf", "txt"])

if uploaded_file:
    with st.spinner("🔍 Extracting text..."):
        text = extract_text(uploaded_file)
    st.session_state["document_text"] = text

    st.subheader("📌 AI-Generated Summary")
    with st.spinner("🧠 Thinking..."):
        summary = summarize(text)
    st.success(summary)

    # Interaction Mode
    st.markdown("### 🎯 Choose Your Mode")
    mode = st.selectbox("Select interaction mode:", ["💬 Ask Me Anything", "🧠 Challenge Me (Logic-based Q&A)"])

    st.markdown("---")

    if mode == "💬 Ask Me Anything":
        question = st.text_input("🔍 Ask a question based on the document")
        if question:
            with st.spinner("🤖 Answering..."):
                answer = ask_anything(text, question)
            st.markdown("#### 🧑‍🎓 You Asked:")
            st.code(question)

            st.markdown("#### 🤖 Assistant’s Answer")
            st.info(answer)

            snippet = find_snippet(text, answer)
            st.markdown("#### 📍 Supporting Snippet")
            st.code(snippet)

    elif mode == "🧠 Challenge Me (Logic-based Q&A)":
        if st.button("🎲 Generate Logic Questions"):
            with st.spinner("📚 Generating questions..."):
                questions = generate_logic_questions(text)

            st.markdown("### 📝 Answer the following questions:")
            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}:** {q}")
                user_input = st.text_input(f"✏️ Your Answer to Q{i+1}", key=f"ans_{i}")
                if user_input:
                    with st.spinner("🔍 Evaluating..."):
                        feedback = evaluate_user_answer(text, q, user_input)
                    st.markdown(f"✅ **Feedback:** {feedback}")

# Footer
st.markdown("<hr><center><small style='color:gray;'>✨ Made with ❤️ by <b>Tanushka Verma</b> using OpenAI & Streamlit</small></center>", unsafe_allow_html=True)
