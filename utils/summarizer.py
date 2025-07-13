from transformers import pipeline

# use smaller model that works well on cloud
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_text(text):
    chunks = [text[i:i+1024] for i in range(0, len(text), 1024)]
    summary = ""
    for chunk in chunks:
        summary += summarizer(chunk, max_length=150, min_length=40, do_sample=False)[0]['summary_text'] + "\n"
    return summary.strip()
