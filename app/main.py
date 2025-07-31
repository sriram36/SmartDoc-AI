from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from uuid import UUID
from . import crud, schemas, models
from .auth import get_current_user, get_admin_user, get_db, auth_router
from .ai import smart_document_summary
from .utils import extract_text_from_file
from .emailer import send_summary_notification
from .database import engine
import os

app = FastAPI(title="SmartDoc AI - Document Summarization API")

# Debug: Print the database URL
print(f"Database URL: {os.getenv('DATABASE_URL')}")

# Create database tables on startup
try:
    models.Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")
except Exception as e:
    print(f"❌ Database initialization error: {e}")
    raise e

app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Welcome to SmartDoc AI - Your Intelligent Document Summarization Service!"}

# Document Upload Endpoint
@app.post("/upload", response_model=schemas.DocumentRead)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """Upload a document (PDF or DOCX) and extract text"""
    try:
        # Extract text from the uploaded file
        extracted_text = extract_text_from_file(file)
        
        # Create document record
        document_data = schemas.DocumentCreate(
            filename=file.filename,
            original_text=extracted_text,
            file_type=file.content_type,
            file_size=file.size
        )
        
        document = crud.create_document(db, user.id, document_data)
        return document
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Document Management Endpoints
@app.get("/documents", response_model=list[schemas.DocumentRead])
def list_documents(
    db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user)
):
    """List all documents for the current user"""
    return crud.list_documents(db, user.id)

@app.get("/documents/{document_id}", response_model=schemas.DocumentRead)
def get_document(
    document_id: UUID, 
    db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user)
):
    """Get a specific document"""
    document = crud.get_document(db, document_id, user.id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@app.delete("/documents/{document_id}", status_code=204)
def delete_document(
    document_id: UUID, 
    db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user)
):
    """Delete a document and its summaries"""
    document = crud.delete_document(db, document_id, user.id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return

# Summarization Endpoints
@app.post("/summarize/{document_id}", response_model=schemas.SummarizeResponse)
def summarize_document(
    document_id: UUID,
    request: schemas.SummarizeRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """Generate AI summary for a document"""
    # Get the document
    document = crud.get_document(db, document_id, user.id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if summary already exists
    existing_summary = crud.get_summary_by_document(db, document_id, user.id)
    if existing_summary:
        return schemas.SummarizeResponse(
            status="already_exists",
            summary_id=existing_summary.id,
            message="Summary already exists for this document"
        )
    
    try:
        # Generate summary using Gemini AI
        ai_result = smart_document_summary(document.original_text, request.length)
        
        if ai_result["status"] == "error":
            raise HTTPException(status_code=500, detail=ai_result["summary"])
        
        # Create summary record
        summary_data = schemas.SummaryCreate(
            document_id=document_id,
            summary_text=ai_result["summary"],
            summary_length=request.length,
            status="completed"
        )
        
        summary = crud.create_summary(db, summary_data)
        
        # Send email notification if user has it enabled
        if user.email_notifications:
            try:
                send_summary_notification(user.email, document.filename, ai_result["summary"])
            except Exception as email_error:
                print(f"Failed to send email notification: {email_error}")
                # Don't fail the request if email fails
        
        return schemas.SummarizeResponse(
            status="completed",
            summary_id=summary.id,
            message="Document summarized successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@app.get("/summary/{document_id}", response_model=schemas.SummaryRead)
def get_summary(
    document_id: UUID,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """Get the summary for a specific document"""
    summary = crud.get_summary_by_document(db, document_id, user.id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary

@app.get("/summaries", response_model=list[schemas.SummaryRead])
def list_summaries(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """List all summaries for the current user"""
    return crud.list_summaries_by_user(db, user.id)

# Admin Endpoints (Role-based access)
@app.get("/admin/users", response_model=list[schemas.UserRead])
def get_all_users(
    admin: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Admin only: Get all users"""
    return crud.get_all_users(db)

@app.get("/admin/documents", response_model=list[schemas.DocumentRead])
def get_all_documents(
    admin: models.User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Admin only: Get all documents"""
    return crud.get_all_documents(db)

# User Profile Management
@app.get("/profile", response_model=schemas.UserRead)
def get_profile(user: models.User = Depends(get_current_user)):
    """Get current user's profile"""
    return user

@app.put("/profile/notifications")
def update_notification_settings(
    enabled: bool,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """Update email notification preferences"""
    user.email_notifications = enabled
    db.commit()
    return {"message": f"Email notifications {'enabled' if enabled else 'disabled'}"}

# File Upload Helper Endpoint (for text extraction preview)
@app.post("/extract-text", response_model=schemas.FileUploadResponse)
def extract_text_from_upload(
    file: UploadFile = File(...),
    user: models.User = Depends(get_current_user)
):
    """Extract text from uploaded file without saving to database"""
    try:
        extracted_text = extract_text_from_file(file)
        return schemas.FileUploadResponse(
            file_name=file.filename,
            extracted_text=extracted_text
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))