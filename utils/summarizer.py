from transformers import pipeline

def get_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_text(text):
    summarizer = get_summarizer()
    chunks = [text[i:i+1024] for i in range(0, len(text), 1024)]
    summary = ""
    for chunk in chunks:
        result = summarizer(chunk, max_length=150, min_length=40, do_sample=False)
        summary += result[0]['summary_text'] + "\n"
    return summary.strip()
