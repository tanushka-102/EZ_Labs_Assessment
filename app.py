import streamlit as st
import time
import io
from utils.file_utils import extract_text
from utils.summarizer import summarize_text
from utils.qa import answer_question, highlight_snippet, generate_challenge_questions

# --- Page Configuration ---
st.set_page_config(
    page_title="Smart Research Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- Custom Dark Theme Styling ---
st.markdown("""
    <style>
        .main { background-color: #0e1117; color: #f1f1f1; }
        div[data-testid="stSidebar"] { background-color: #161a25; }
        h1, h2, h3, .st-emotion-cache-1v0mbdj { color: #ff4b4b; }
        .stButton>button, .stDownloadButton>button {
            background-color: #ff4b4b;
            color: white;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title and Description ---
st.title("🧠 Smart Research Assistant (No API Key Needed)")
with st.spinner("Loading model and preparing UI..."):
    time.sleep(1.5)

st.markdown("Upload a research paper and get summaries, answers, or challenge questions instantly.")

# --- File Upload ---
uploaded_file = st.file_uploader("📎 Upload your PDF or TXT file", type=["pdf", "txt"])

if uploaded_file:
    st.success("✅ File uploaded successfully!")
    st.markdown(f"""
        - **Uploaded File Name:** {uploaded_file.name}  
        - **Uploaded File Type:** {uploaded_file.type}  
        - **Uploaded File Size (bytes):** {uploaded_file.size}
    """)
    
    try:
        text = extract_text(uploaded_file)
        st.session_state["document_text"] = text
        st.session_state.setdefault("challenge_responses", {})

        # --- Summary Section ---
        st.subheader("📌 Document Summary")
        if st.button("📝 Generate Summary"):
            with st.spinner("Summarizing document..."):
                summary = summarize_text(text)
                st.success("✅ Summary generated!")
                with st.expander("🔍 Click to view summary"):
                    st.write(summary)

        # --- Tabs for Interactions ---
        st.subheader("🧭 Choose Your Interaction Mode")
        tab1, tab2 = st.tabs(["💬 Ask Anything", "🧠 Challenge Me"])

        # --- Q&A Mode ---
        with tab1:
            question = st.text_input("💬 Ask something based on the document")
            if question:
                with st.spinner("Thinking..."):
                    answer = answer_question(text, question)
                    st.success("🟢 Answer:")
                    st.write(answer['answer'])

                    st.markdown("📍 **Relevant Snippet:**")
                    snippet = highlight_snippet(text, answer)
                    st.code(snippet)

        # --- Challenge Mode ---
        with tab2:
            if st.button("🎯 Generate Challenge Questions"):
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
    except Exception as e:
        st.error("❌ Error while processing the file. Please try a different format or smaller file.")
        st.code(str(e))

# --- Footer ---
st.markdown("""
<hr>
🔧 Built with ❤️ by **Tanushka Verma** | Powered by 🦾 Transformers + Streamlit  
""", unsafe_allow_html=True)
