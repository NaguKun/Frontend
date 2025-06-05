from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from app.core.config import settings
# from app.db.session import get_db
from app.services.cv_processor.processor import CVProcessor
from app.services.llm.extractor import InformationExtractor
from app.schemas.candidate import CandidateCreate
from app.crud import candidate as candidate_crud
from google.oauth2 import service_account


router = APIRouter()

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_google_drive_service():
    """Get Google Drive service using a Service Account."""
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = settings.GOOGLE_DRIVE_CREDENTIALS_FILE

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build('drive', 'v3', credentials=credentials)


@router.post("/upload", response_model=CandidateCreate)
async def upload_cv(
    file: UploadFile = File(...)
):
    """
    Upload and process a CV file to Google Drive.
    The file will be processed to extract information and create a candidate profile.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    try:
        # Read file content
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File size exceeds maximum allowed size"
            )

        # Upload to Google Drive
        drive_service = get_google_drive_service()
        file_metadata = {
            'name': file.filename,
            'parents': [settings.GOOGLE_DRIVE_FOLDER_ID]
        }
        
        media = MediaIoBaseUpload(
            io.BytesIO(content),
            mimetype='application/pdf',
            resumable=True
        )
        
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        file_id = uploaded_file.get('id')
        
        # Process the CV
        processor = CVProcessor()
        cv_text = processor.extract_text(content)
        
        # Extract information using LLM
        extractor = InformationExtractor()
        candidate_data = extractor.extract_information(cv_text)
        
        # Add Google Drive file ID to candidate data
        candidate_data_dict = candidate_data.model_dump()
        candidate_data_dict['cv_file_id'] = file_id
        candidate_data = CandidateCreate(**candidate_data_dict)
        
        # Generate embeddings
        embeddings = extractor.generate_embeddings(candidate_data, cv_text)
        
        # Create candidate profile with embeddings
        candidate = candidate_crud.create_candidate(
            candidate_data=candidate_data,
            embeddings=embeddings
        )
        
        return candidate
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing CV: {str(e)}"
        )

@router.post("/upload/batch", response_model=List[CandidateCreate])
async def upload_multiple_cvs(
    files: List[UploadFile] = File(...)
):
    """
    Upload and process multiple CV files in batch.
    """
    results = []
    errors = []
    
    for file in files:
        try:
            result = await upload_cv(file=file)
            results.append(result)
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    if errors:
        # Return partial results with errors
        return {
            "successful_uploads": results,
            "failed_uploads": errors
        }
    
    return results 