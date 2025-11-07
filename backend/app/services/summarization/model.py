from transformers import pipeline
from app.services.preprocess import preprocess
# load a summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize():
    preprocessed = preprocess.preprocess_input("backend/app/services/summarization/a.pdf")
    clean_text = preprocessed["clean_text"]

    # Generate summary
    summary = summarizer(clean_text, max_length=120, min_length=30, do_sample=False)

    return summary[0]['summary_text']


print(summarize())