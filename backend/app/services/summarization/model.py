from transformers import pipeline
from app.services.preprocess import preprocess

summarizer = pipeline("summarization", model="google/bigbird-pegasus-large-arxiv")

async def summarize(file):
    preprocessed = await preprocess.preprocess_input(file)
    chunks = preprocessed["chunks"]
    summaries = ""
    # Generate summary
    for chunk in chunks:
        summary = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
        summaries += summary[0]['summary_text'] + " "
        
    return summaries

