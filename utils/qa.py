import re
import random
from transformers import pipeline

qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

def answer_question(context, question):
    return qa_pipeline({"context": context, "question": question})

def highlight_snippet(text, answer, context_size=250):
    answer_text = answer['answer']
    pattern = re.escape(answer_text[:30])
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        start = max(match.start() - context_size // 2, 0)
        end = min(match.end() + context_size // 2, len(text))
        return text[start:end].strip()
    return "Snippet not found."

def generate_challenge_questions(text, num_questions=3):
    sentences = re.split(r'(?<=[.!?]) +', text)
    selected = random.sample(sentences, min(num_questions, len(sentences)))
    return [f"Explain: '{s.strip()}'" for s in selected if len(s.strip()) > 30]
