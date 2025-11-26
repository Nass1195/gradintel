from transformers import pipeline
import torch
from app.services.preprocess import preprocess

summarizer = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-3B-Instruct",
    device="cpu"
)

async def summarize(file):
    preprocessed = await preprocess.preprocess_input(file)
    clean_text = preprocessed["clean_text"]
    massage = [{"role": "system", "content": "You are a helpful assistant designed to summarize text. Provide a concise summary of the following text."},
               {"role": "user", "content": clean_text}]
    
    outputs = summarizer(massage, max_length=512, do_sample=False)
        
    return outputs[0]["generated_text"][-1]["content"]

