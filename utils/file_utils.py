from io import StringIO
import pdfplumber
import logging

# Optional: set up logging
logging.basicConfig(level=logging.INFO)

def extract_text(uploaded_file):
    if uploaded_file is None:
        return "❌ No file uploaded."

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):
        try:
            logging.info("📄 Extracting text from PDF...")
            text = ""
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if not text.strip():
                return "❌ No text found in PDF."
            return text.strip()
        except Exception as e:
            logging.error(f"PDF extraction error: {e}")
            return f"❌ Failed to extract PDF text: {e}"

    elif file_name.endswith(".txt"):
        try:
            logging.info("📄 Extracting text from TXT...")
            return uploaded_file.read().decode("utf-8").strip()
        except Exception as e:
            logging.error(f"TXT extraction error: {e}")
            return f"❌ Failed to extract TXT text: {e}"

    else:
        return "❌ Unsupported file format. Please upload a PDF or TXT file."
