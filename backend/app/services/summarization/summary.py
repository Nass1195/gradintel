from app.services import llmModel
from app.models import ItemUpdate, Item, Document
from sqlmodel import select
from fastapi import HTTPException

async def summarize_file(chunks):
    chunks_summeries = []

    for chunk in chunks:
        summry = await summarize(chunk)
        chunks_summeries.append(summry)

    text = "\n\n".join(chunk)
    massage = [{"role": "system", "content": "Create a coherent final summary from these section summaries."},
               {"role": "user", "content": text}]
    
    outputs = await llmModel.generate_text(massage, max_length=512)
        
    return outputs

async def summarize(text: str):
    massage = [{"role": "system", "content": "You are a helpful assistant designed to summarize text. Provide a concise summary of the following text."},
               {"role": "user", "content": text}]
    
    outputs = await llmModel.generate_text(massage, max_length=512)
        
    return outputs



async def generate_item_summry(item_id, session):
    statement = select(Document).where(Document.owner_id == item_id)
    documents = session.exec(statement).all()

    if not documents:
        return
    
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if len(documents) == 1:
        item_summary = documents[0].summary
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