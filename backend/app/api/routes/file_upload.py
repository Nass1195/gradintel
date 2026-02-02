from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.api.deps import CurrentUser, SessionDep
from app.models import Message
from app.services.preprocess import preprocess
from app.services.summarization import model as summarization_model
from app.services.quiz import quiz as quiz_model

router = APIRouter(prefix="/upload", tags=["file_upload"])

@router.post("/", response_model=Message)
async def upload_file(
     *, session: SessionDep, current_user: CurrentUser,file: UploadFile = File(...)
) -> Message:
     print(f"Received file: {file.filename}")
     summary = await summarization_model.summarize(file)
     return Message(message=summary)


@router.post("/quiz", response_model=quiz_model.QuizResponse)
async def generate_quiz_endpoint(
     *, session: SessionDep, current_user: CurrentUser,file: UploadFile = File(...)
) -> quiz_model.QuizResponse:
     print(f"Received file for quiz generation: {file.filename}")
     quiz = await quiz_model.generate_quiz(file)
     return quiz