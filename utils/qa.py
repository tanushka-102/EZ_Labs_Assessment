
import re
import random
from transformers import pipeline

# Initialize pipeline once
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

def answer_question(context, question):
    try:
        if not context or not question:
            return {"answer": "No context or question provided."}
        return qa_pipeline({"context": context[:4000], "question": question})
    except Exception as e:
        return {"answer": f"⚠️ Error: {str(e)}"}

def highlight_snippet(text, answer, context_size=250):
    answer_text = answer.get("answer", "")
    if not answer_text:
        return "No snippet found."
    pattern = re.escape(answer_text[:30])
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        start = max(match.start() - context_size // 2, 0)
        end = min(match.end() + context_size // 2, len(text))
        return text[start:end].strip()
    return "Snippet not found."

def generate_challenge_questions(text, num_questions=3):
    sentences = re.split(r'(?<=[.!?]) +', text)
    candidates = [s.strip() for s in sentences if len(s.strip()) > 30]
    if not candidates:
        return ["⚠️ Not enough valid content for questions."]
    selected = random.sample(candidates, min(num_questions, len(candidates)))
    return [f"Explain: '{s}'" for s in selected]
