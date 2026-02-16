from app.services.preprocess import preprocess
from app.services import llmModel
from app.models import ItemUpdate, Item, Document
from sqlmodel import select

async def summarize(file):
    preprocessed = await preprocess.preprocess_input(file)
    clean_text = preprocessed["clean_text"]
    massage = [{"role": "system", "content": "You are a helpful assistant designed to summarize text. Provide a concise summary of the following text."},
               {"role": "user", "content": clean_text}]
    
    outputs = await llmModel.generate_text(massage, max_length=512)
        
    return outputs

def generate_item_summry(item_id, session):
    statment = select(Document).where(Document.owner_id == item_id)
    documents = session.exec(statment).all()

    if not documents:
        return
    
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if len(documents) == 1:
        item_summary = documents[0].summary
    else:
        item_summary = "\n\n---\n\n".join(d.summary for d in documents)


    item_in = ItemUpdate(summary=item_summary)

    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)

    session.add(item)
    session.commit()
    session.refresh(item)
    return item_summary