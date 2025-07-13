from transformers import pipeline

# Using a faster summarization model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

def summarize_text(text):
    chunks = [text[i:i+1024] for i in range(0, len(text), 1024)]
    summary = ""
    for chunk in chunks:
        try:
            result = summarizer(chunk, max_length=120, min_length=30, do_sample=False)
            summary += result[0]['summary_text'].strip() + "\n\n"
        except Exception as e:
            summary += f"\n[Chunk failed to summarize: {str(e)}]\n"
    return summary.strip()
