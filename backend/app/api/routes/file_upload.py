from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.api.deps import CurrentUser, SessionDep
from app.models import Message

router = APIRouter(prefix="/upload", tags=["file_upload"])

@router.post("/", response_model=Message)
async def upload_file(
     *, session: SessionDep, current_user: CurrentUser,file: UploadFile = File(...)
) -> Message:
     print(f"Received file: {file.filename}")
     return Message(message=f"File '{file.filename}' uploaded successfully")