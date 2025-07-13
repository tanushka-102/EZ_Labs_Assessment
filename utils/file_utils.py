from io import StringIO
import pdfplumber

def extract_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
        except Exception as e:
            return f"❌ Failed to extract PDF text: {e}"
    elif uploaded_file.name.endswith(".txt"):
        try:
            return uploaded_file.read().decode("utf-8")
        except Exception as e:
            return f"❌ Failed to extract TXT text: {e}"
    else:
        return "❌ Unsupported file format."
