import io
from typing import Optional
from fastapi import UploadFile, HTTPException
import docx
import fitz  # PyMuPDF

def extract_text_from_docx(file: UploadFile) -> str:
    """Extract text from DOCX file"""
    try:
        # Read the file content
        content = file.file.read()
        file.file.seek(0)  # Reset file pointer
        
        # Load the document
        doc = docx.Document(io.BytesIO(content))
        
        # Extract text from all paragraphs
        text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        
        return '\n'.join(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting text from DOCX: {str(e)}")

def extract_text_from_pdf(file: UploadFile) -> str:
    """Extract text from PDF file"""
    try:
        # Read the file content
        content = file.file.read()
        file.file.seek(0)  # Reset file pointer
        
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=content, filetype="pdf")
        
        # Extract text from all pages
        text = []
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text.append(page.get_text())
        
        pdf_document.close()
        return '\n'.join(text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting text from PDF: {str(e)}")

def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from uploaded file based on content type"""
    # Check file size (max 2MB)
    if file.size and file.size > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size too large. Maximum size is 2MB.")
    
    # Check content type
    content_type = file.content_type.lower()
    
    if content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file)
    elif content_type == "application/pdf":
        return extract_text_from_pdf(file)
    else:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Please upload DOCX or PDF files only."
        ) 