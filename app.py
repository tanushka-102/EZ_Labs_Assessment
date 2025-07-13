"""
Smart Research Assistant
Author: Tanushka Verma
Description:
This Streamlit web app allows users to upload research documents (PDF/TXT), summarize them, ask document-based questions, and receive logic-based challenges with feedback.
"""

import streamlit as st
import openai
import pdfplumber
import os
import re

# Get OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else "sk-..."

# Extract text from uploaded PDF or TXT file
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
    else:
        return "Unsupported file format."

# Generate a concise summary from the document
def summarize(text):
    prompt = f"Summarize this document in under 150 words:\n\n{text[:3000]}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
        temperature=0.5
    )
    return response.choices[0].text.strip()

# Answer user's questions based on the uploaded document
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
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300,
        temperature=0.3
    )
    return response.choices[0].text.strip()

# Generate logical and comprehension-based questions from the document
def generate_logic_questions(text):
    prompt = f"Generate 3 logic-based or comprehension questions from this document:\n\n{text[:3000]}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300,
        temperature=0.5
    )
    return response.choices[0].text.strip().split("\n")

# Evaluate the user's answer with justification from the document
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
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=250,
        temperature=0.4
    )
    return response.choices[0].text.strip()

# Highlight the supporting text from the document using regex
def find_snippet(text, answer, n_chars=200):
    sentences = re.split(r'(?<=[.!?]) +', text)
    pattern = re.escape(answer[:30])
    for sentence in sentences:
        if re.search(pattern, sentence, re.IGNORECASE):
            return sentence.strip()
    return "Snippet not found."

# Streamlit App UI
st.set_page_config(page_title="Smart Research Assistant", layout="wide")
st.title("📄 Smart Research Assistant")
st.markdown("Upload a research paper or report and get intelligent summaries, question-answering, and logical challenges.")

uploaded_file = st.file_uploader("Upload your PDF or TXT file", type=["pdf", "txt"])

if uploaded_file:
    text = extract_text(uploaded_file)
    st.session_state["document_text"] = text

    st.subheader("📌 Auto Summary")
    summary = summarize(text)
    st.success(summary)

    mode = st.radio("Select Interaction Mode:", ["Ask Anything", "Challenge Me"])

    if mode == "Ask Anything":
        question = st.text_input("Ask a question based on the document")
        if question:
            answer = ask_anything(text, question)
            st.markdown(f"**🤖 Answer:** {answer}")
            highlight = find_snippet(text, answer)
            st.markdown("**📍 Relevant Snippet:**")
            st.code(highlight)

    elif mode == "Challenge Me":
        if st.button("Generate Challenge Questions"):
            questions = generate_logic_questions(text)
            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}:** {q}")
                user_input = st.text_input(f"Your answer to Q{i+1}", key=f"ans_{i}")
                if user_input:
                    feedback = evaluate_user_answer(text, q, user_input)
                    st.markdown(f"**📝 Feedback:** {feedback}")
