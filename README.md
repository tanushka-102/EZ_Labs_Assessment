# EZ_Labs_Assessment
# 🧠 Smart Research Assistant

A simple AI-powered tool to upload research documents, generate summaries, ask questions, and test your understanding — all without needing an API key.

🔗 **Live App:** [Smart Research Assistant](https://ezlabsassessmentintern.streamlit.app/)

---

## 📦 Setup Instructions

1. **Clone this repository**  
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

cpp
Copy
Edit

2. **Create virtual environment (optional but recommended)**  
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

markdown
Copy
Edit

3. **Install dependencies**  
pip install -r requirements.txt

markdown
Copy
Edit

4. **Run the Streamlit app**  
streamlit run app.py

yaml
Copy
Edit

---

## ⚙️ Architecture / Working Flow

- **File Upload**: Supports `.pdf` and `.txt` using `pdfplumber` and UTF-8 decoding.
- **Text Summarization**: Uses `sshleifer/distilbart-cnn-12-6` model from HuggingFace via `transformers` to generate concise summaries.
- **Question Answering**: Uses `distilbert-base-uncased-distilled-squad` to answer user questions based on the uploaded content.
- **Challenge Me Mode**: Randomly generates 3 questions from the document to test the user's understanding.
- **Download Responses**: All challenge answers can be saved as a `.txt` file.

---

## 🖼️ Screenshots

Screenshots of the working app are included in the repository to demonstrate the interface and features. These show how the app looks for summary generation, Q&A, and challenge question features.

---

## 📁 Folder Structure

.
├── app.py
├── requirements.txt
├── runtime.txt
├── README.md
└── utils
├── file_utils.py
├── summarizer.py
└── qa.py

yaml
Copy
Edit

---

## ✨ Features

- No API key required
- Clean UI with Streamlit
- Works with research papers in PDF or TXT
- Fully open-source and deployable

---

## 🔗 Try It Live

[Click here to open the app](https://ezlabsassessmentintern.streamlit.app/)
