from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "user"

class UserRead(UserBase):
    id: UUID
    role: str
    email_notifications: bool
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    filename: str
    original_text: str
    file_type: str

class DocumentCreate(DocumentBase):
    file_size: Optional[int] = None

class DocumentRead(DocumentBase):
    id: UUID
    user_id: UUID
    file_size: Optional[int]
    upload_time: datetime

    class Config:
        from_attributes = True

class SummaryBase(BaseModel):
    summary_text: str
    summary_length: Optional[str] = "medium"

class SummaryCreate(SummaryBase):
    document_id: UUID
    status: Optional[str] = "completed"

class SummaryRead(SummaryBase):
    id: UUID
    document_id: UUID
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class FileUploadResponse(BaseModel):
    file_name: str
    extracted_text: str

# Request/Response models for API
class SummarizeRequest(BaseModel):
    length: Optional[str] = "medium"  # short, medium, long

class SummarizeResponse(BaseModel):
    status: str
    summary_id: Optional[UUID] = None
    message: str