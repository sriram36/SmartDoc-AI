from sqlalchemy.orm import Session
from . import models, schemas
from uuid import UUID

# Document CRUD operations
def create_document(db: Session, user_id: UUID, document: schemas.DocumentCreate):
    db_document = models.Document(user_id=user_id, **document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document(db: Session, document_id: UUID, user_id: UUID):
    return db.query(models.Document).filter(
        models.Document.id == document_id, 
        models.Document.user_id == user_id
    ).first()

def list_documents(db: Session, user_id: UUID):
    return db.query(models.Document).filter(models.Document.user_id == user_id).all()

def delete_document(db: Session, document_id: UUID, user_id: UUID):
    document = get_document(db, document_id, user_id)
    if document:
        # Delete associated summaries first
        db.query(models.Summary).filter(models.Summary.document_id == document_id).delete()
        db.delete(document)
        db.commit()
    return document

# Summary CRUD operations
def create_summary(db: Session, summary: schemas.SummaryCreate):
    db_summary = models.Summary(**summary.dict())
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary

def get_summary_by_document(db: Session, document_id: UUID, user_id: UUID):
    return db.query(models.Summary).join(models.Document).filter(
        models.Summary.document_id == document_id,
        models.Document.user_id == user_id
    ).first()

def get_summary(db: Session, summary_id: UUID):
    return db.query(models.Summary).filter(models.Summary.id == summary_id).first()

def list_summaries_by_user(db: Session, user_id: UUID):
    return db.query(models.Summary).join(models.Document).filter(
        models.Document.user_id == user_id
    ).all()

# Admin operations
def get_all_users(db: Session):
    return db.query(models.User).all()

def get_all_documents(db: Session):
    return db.query(models.Document).all()