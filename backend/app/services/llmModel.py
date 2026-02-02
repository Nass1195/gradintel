from transformers import pipeline
import torch

llm_model = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-3B-Instruct",
    device="cpu"
)

async def generate_text(messages, max_length=512):
    outputs = llm_model(messages, max_length=max_length,max_new_tokens=512, do_sample=False)
    return outputs[0]["generated_text"][-1]["content"]

