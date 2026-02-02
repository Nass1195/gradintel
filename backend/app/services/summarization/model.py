from app.services.preprocess import preprocess
from app.services import llmModel

async def summarize(file):
    preprocessed = await preprocess.preprocess_input(file)
    clean_text = preprocessed["clean_text"]
    massage = [{"role": "system", "content": "You are a helpful assistant designed to summarize text. Provide a concise summary of the following text."},
               {"role": "user", "content": clean_text}]
    
    outputs = await llmModel.generate_text(massage, max_length=512)
        
    return outputs

