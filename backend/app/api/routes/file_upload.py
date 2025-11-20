from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.api.deps import CurrentUser, SessionDep
from app.models import Message
from app.services.preprocess import preprocess
from app.services.summarization import model as summarization_model

router = APIRouter(prefix="/upload", tags=["file_upload"])

@router.post("/", response_model=Message)
async def upload_file(
     *, session: SessionDep, current_user: CurrentUser,file: UploadFile = File(...)
) -> Message:
     print(f"Received file: {file.filename}")
     summary = await summarization_model.summarize(file)
     print(f"Summary: {summary}")
     return Message(message=f"File '{file.filename}' uploaded successfully")