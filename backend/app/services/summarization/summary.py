from app.api.deps import SessionDep
import asyncio

from app.services import llmModel
from app.models import ItemUpdate, Item, Document
from app.services.preprocess.preprocess import chunk_text 
from sqlmodel import select
from fastapi import HTTPException

async def summarize_file(text: str) -> str:

    chunks = chunk_text(text, max_len=20000, overlap=2000)

    chunks_summaries = []

    print(len(chunks))

    tasks = [summarize(chunk) for chunk in chunks]

    chunks_summaries = await asyncio.gather(*tasks)

    text = "\n\n".join(chunks_summaries)
    massage = [{"role": "system", "content": "Create a coherent final summary from these section summaries."},
               {"role": "user", "content": text}]
    
    outputs = await llmModel.generate_text(massage, max_length=512)
        
    return outputs

async def summarize(text: str) -> str:
    massage = [{"role": "system", "content": "You are a helpful assistant designed to summarize text. Provide a concise summary of the following text."},
               {"role": "user", "content": text}]
    
    outputs = await llmModel.generate_text(massage, max_length=512)
        
    return outputs



async def generate_item_summary(item_id: str, session: SessionDep) -> str:
 
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    statement = select(Document).where(Document.owner_id == item_id)
    documents = session.exec(statement).all()
    

    if not documents:
        outputs = ""
    elif len(documents) == 1:
        outputs = documents[0].summary
    else:
        item_summary = "\n\n".join(d.summary for d in documents)
        massage = [{"role": "system", "content": "Create a coherent final summary from these section summaries."},
                   {"role": "user", "content": item_summary}]
        outputs = await llmModel.generate_text(massage, max_length=512)


    item_in = ItemUpdate(summary=outputs)

    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)

    session.add(item)
    session.commit()
    session.refresh(item)
    return outputs