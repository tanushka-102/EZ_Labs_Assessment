import streamlit as st
import time
import io
import random
from utils.file_utils import extract_text
from utils.summarizer import summarize_text
from utils.qa import answer_question, highlight_snippet, generate_challenge_questions

st.set_page_config(page_title="Smart Research Assistant", layout="wide")
st.title("🧠 Smart Research Assistant")

with st.spinner("Loading model and preparing UI..."):
    time.sleep(1.5)

st.markdown("Upload a research paper and get summaries, answers, or challenge questions.")

uploaded_file = st.file_uploader("Upload your PDF or TXT file", type=["pdf", "txt"])

if uploaded_file:
    st.success("✅ File uploaded successfully!")
    st.write(f"**Uploaded File Name:** {uploaded_file.name}")
    st.write(f"**Uploaded File Type:** {uploaded_file.type}")
    st.write(f"**Uploaded File Size (bytes):** {uploaded_file.size}")

    text = extract_text(uploaded_file)
    st.session_state["document_text"] = text
    st.session_state.setdefault("challenge_responses", {})

if uploaded_file:
    text = extract_text(uploaded_file)
    st.session_state["document_text"] = text
    st.session_state.setdefault("challenge_responses", {})

    st.subheader("📌 Document Summary")
    if st.button("Generate Summary", key="gen_summary_btn"):
        st.session_state["generate_summary"] = True

    if st.session_state.get("generate_summary", False):
        with st.spinner("Summarizing document..."):
            try:
                summary = summarize_text(text[:4000])  # limit to avoid overrun
                st.success("✅ Summary generated:")
                st.write(summary)
            except Exception as e:
                st.error(f"❌ Error while summarizing: {e}")
            finally:
                st.session_state["generate_summary"] = False


    st.subheader("🧭 Choose Your Interaction Mode")
    mode = st.radio("Select Mode:", ["Ask Anything", "Challenge Me"])

    if mode == "Ask Anything":
        question = st.text_input("💬 Ask something based on the document")
        if question:
            with st.spinner("Thinking..."):
                answer = answer_question(text, question)
                st.success("Answer:")
                st.write(answer['answer'])

                st.markdown("**📍 Relevant Snippet:**")
                snippet = highlight_snippet(text, answer)
                st.code(snippet)

    elif mode == "Challenge Me":
        if st.button("Generate Challenge Questions"):
            questions = generate_challenge_questions(text)
            st.session_state["challenge_questions"] = questions

        if "challenge_questions" in st.session_state:
            for idx, q in enumerate(st.session_state["challenge_questions"]):
                st.markdown(f"**Q{idx+1}:** {q}")
                user_input = st.text_area(f"Your response to Q{idx+1}", key=f"resp_{idx}")
                if user_input:
                    st.session_state["challenge_responses"][q] = user_input
                    st.info("✅ Answer saved.")

            if st.button("📄 Download My Responses"):
                response_text = ""
                for q, a in st.session_state["challenge_responses"].items():
                    response_text += f"{q}\nAnswer: {a}\n\n"
                b = io.BytesIO()
                b.write(response_text.encode())
                b.seek(0)
                st.download_button("📥 Download Responses", b, file_name="my_responses.txt", mime="text/plain")
