import streamlit as st
import pdfplumber
import os
import re
import random
import time
import io
from transformers import pipeline

# Load pipelines
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

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

# Summarize document text
def summarize_text(text):
    chunks = [text[i:i+1024] for i in range(0, len(text), 1024)]
    summary = ""
    for chunk in chunks:
        summary += summarizer(chunk, max_length=150, min_length=40, do_sample=False)[0]['summary_text'] + "\n"
    return summary.strip()

# QA based on document
def answer_question(context, question):
    return qa_pipeline({"context": context, "question": question})

# Highlight the supporting snippet
def highlight_snippet(text, answer, context_size=250):
    answer_text = answer['answer']
    pattern = re.escape(answer_text[:30])
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        start = max(match.start() - context_size // 2, 0)
        end = min(match.end() + context_size // 2, len(text))
        snippet = text[start:end]
        return snippet.strip()
    return "Snippet not found."

# Generate logic/comprehension challenge questions
def generate_challenge_questions(text, num_questions=3):
    sentences = re.split(r'(?<=[.!?]) +', text)
    selected = random.sample(sentences, min(num_questions, len(sentences)))
    return [f"Explain: '{s.strip()}'" for s in selected if len(s.strip()) > 30]

# Streamlit UI
st.set_page_config(page_title="Smart Research Assistant (No API Key)", layout="wide")
st.title("🧠 Smart Research Assistant (No OpenAI Key)")
with st.spinner("Loading model and preparing UI..."):
    time.sleep(1.5)
st.markdown("Upload a research paper and get summaries, question-answering, or challenge mode interaction.")

uploaded_file = st.file_uploader("Upload your PDF or TXT file", type=["pdf", "txt"])

if uploaded_file:
    text = extract_text(uploaded_file)
    st.session_state["document_text"] = text
    st.session_state.setdefault("challenge_responses", {})

    st.subheader("📌 Document Summary")
    if st.button("Generate Summary"):
        with st.spinner("Summarizing document..."):
            summary = summarize_text(text)
            st.success("Summary generated:")
            st.write(summary)

    st.subheader("🧭 Choose Your Interaction Mode")
    mode = st.radio("Select Mode:", ["Ask Anything", "Challenge Me"])

    if mode == "Ask Anything":
        st.subheader("💬 Ask a Question")
        question = st.text_input("Ask something based on the document")
        if question:
            with st.spinner("Thinking..."):
                answer = answer_question(text, question)
                st.success("Answer:")
                st.write(answer['answer'])

                st.markdown("**📍 Relevant Snippet:**")
                snippet = highlight_snippet(text, answer)
                st.code(snippet)

    elif mode == "Challenge Me":
        st.subheader("🧠 Comprehension Challenge")
        if st.button("Generate Challenge Questions"):
            questions = generate_challenge_questions(text)
            st.session_state["challenge_questions"] = questions

        if "challenge_questions" in st.session_state:
            for idx, q in enumerate(st.session_state["challenge_questions"]):
                st.markdown(f"**Q{idx+1}:** {q}")
                user_input = st.text_area(f"Your response to Q{idx+1}", key=f"resp_{idx}")
                if user_input:
                    st.session_state["challenge_responses"][q] = user_input
                    st.info("✅ Answer saved. Review it yourself or discuss with peers.")

            if st.button("Download My Responses"):
                response_text = ""
                for q, a in st.session_state["challenge_responses"].items():
                    response_text += f"{q}\nAnswer: {a}\n\n"
                b = io.BytesIO()
                b.write(response_text.encode())
                b.seek(0)
                st.download_button("📄 Download Responses", b, file_name="my_responses.txt", mime="text/plain")
