from datetime import datetime
import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, Text, DateTime, JSON
from pgvector.sqlalchemy import Vector



# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    summary: str | None = Field(default=None, sa_column=Column(Text))



# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore
    summary: str | None = Field(default=None, sa_column=Column(Text))


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")
    documents: list["Document"] = Relationship(back_populates="owner", cascade_delete=True)
    chat_messages: list["ChatMessage"] = Relationship(back_populates="owner", cascade_delete=True)
    quiz_questions: list["QuizQuestion"] = Relationship(back_populates="item", cascade_delete=True)


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int

class DocumentBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    content: str | None = Field(default=None, sa_column=Column(Text))
    summary: str | None = Field(default=None, sa_column=Column(Text))

class Document(DocumentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="item.id", nullable=False, ondelete="CASCADE"
    )
    owner: Item | None = Relationship(back_populates="documents")
    chunks: list["Chunk"] = Relationship(back_populates="document", cascade_delete=True)


class DocumentCreate(DocumentBase):
    pass

class DocumentPublic(SQLModel):
    id: uuid.UUID
    title: str
    summary: str | None

class DocumentsPublic(SQLModel):
    data: list[DocumentPublic]

class ChatMessageBase(SQLModel):
    message: str = Field(sa_column=Column(Text))
    role: str = Field(max_length=20, index=True) 
    created_at: datetime = Field(default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True)))

class ChatMessage(ChatMessageBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="item.id", nullable=False, ondelete="CASCADE", index=True
    )
    owner: Item | None = Relationship(back_populates="chat_messages")

class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessagePublic(SQLModel):
    message: str
    role: str
    created_at: datetime

class ChatMessagesPublic(SQLModel):
    data: list[ChatMessagePublic]


class ChunkBase(SQLModel):
    content: str = Field(sa_column=Column(Text))
    chunk_index: int = Field(index=True)
    embedding: list[float] = Field(sa_column=Column(Vector(768))) 


class Chunk(ChunkBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document_id: uuid.UUID = Field(
        foreign_key="document.id", nullable=False, ondelete="CASCADE", index=True
    )
    document: Document | None = Relationship(back_populates="chunks")

class ChunkCreate(ChunkBase):
    pass



class QuizBase(SQLModel):   
    question: str = Field(sa_column=Column(Text))
    options: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    correct_answer: str = Field(sa_column=Column(Text))

class QuizQuestion(QuizBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    item_id: uuid.UUID = Field(
        foreign_key="item.id", nullable=False, ondelete="CASCADE", index=True
    )
    item: Item | None = Relationship(back_populates="quiz_questions")

class QuizQuestionsCreate(SQLModel):
    questions: list[QuizBase]

class QuizQuestionPublic(QuizBase):
    id: uuid.UUID

class QuizPublic(SQLModel):
    questions: list[QuizQuestionPublic]



# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class UploadResponse(SQLModel):
    document: DocumentPublic
    summary: str