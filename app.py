import streamlit as st
import pdfplumber
import re
from openai import OpenAI

# Set up OpenAI API client using secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set page config
st.set_page_config(page_title="📄 Smart Research Assistant", layout="wide")
st.title("📄 Smart Research Assistant")
st.markdown(
    "Upload a research paper or report and get intelligent **summaries**, **question-answering**, and **logic challenges**."
)

# File text extractor
def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join([page.extract_text() or "" for page in pdf.pages])
    elif uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    return "❌ Unsupported file format."

# Chat-based call
def ask_openai(prompt, temperature=0.5, max_tokens=300):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()

# Summarize document
def summarize(text):
    prompt = f"Summarize this research document in under 150 words:\n\n{text[:3000]}"
    return ask_openai(prompt, temperature=0.4, max_tokens=250)

# Answer with justification
def ask_anything(text, question):
    prompt = f"""You are an AI assistant. Use only the following document to answer.
Document:
{text[:3000]}

User Question:
{question}

Answer (with justification from document):"""
    return ask_openai(prompt)

# Generate logic-based challenge questions
def generate_logic_questions(text):
    prompt = f"Generate 3 logic-based or comprehension questions from this academic document:\n\n{text[:3000]}"
    result = ask_openai(prompt)
    return [line for line in result.split("\n") if line.strip()]

# Evaluate user answer
def evaluate_answer(text, question, user_answer):
    prompt = f"""Evaluate the following answer using the given document. Justify if it's correct or not.

Document:
{text[:3000]}

Question:
{question}

User Answer:
{user_answer}

Feedback with justification:"""
    return ask_openai(prompt, temperature=0.3)

# Snippet finder from answer
def find_snippet(text, answer):
    sentences = re.split(r'(?<=[.!?]) +', text)
    pattern = re.escape(answer[:30])
    for sentence in sentences:
        if re.search(pattern, sentence, re.IGNORECASE):
            return sentence.strip()
    return "Snippet not found."

# File uploader
uploaded_file = st.file_uploader("📤 Upload your PDF or TXT file", type=["pdf", "txt"])

# Main logic
if uploaded_file:
    text = extract_text(uploaded_file)
    st.session_state["document_text"] = text

    st.subheader("🧠 AI-Generated Summary")
    with st.spinner("Generating summary..."):
        summary = summarize(text)
        st.success(summary)

    # Mode selector
    st.subheader("🔧 Choose an Interaction Mode")
    mode = st.radio("Select:", ["Ask Anything", "Challenge Me"])

    if mode == "Ask Anything":
        question = st.text_input("💬 Ask a question based on the document:")
        if question:
            with st.spinner("Thinking..."):
                answer = ask_anything(text, question)
                st.markdown(f"**🤖 Answer:** {answer}")
                snippet = find_snippet(text, answer)
                st.markdown("**📍 Supporting Snippet from Document:**")
                st.code(snippet)

    elif mode == "Challenge Me":
        if st.button("🧩 Generate Challenge Questions"):
            questions = generate_logic_questions(text)
            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}:** {q}")
                user_input = st.text_input(f"📝 Your answer to Q{i+1}:", key=f"ans_{i}")
                if user_input:
                    feedback = evaluate_answer(text, q, user_input)
                    st.markdown(f"**✅ Feedback:** {feedback}")
