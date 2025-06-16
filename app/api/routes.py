from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from services.cv_service import handle_upload_cv, handle_upload_cv_from_drive, handle_search_candidates, handle_upload_cv_with_ollama
from db.database_manager import init_db
from sqlalchemy.orm import Session

router = APIRouter()

class CandidateSearch(BaseModel):
    query: str
    max_results: int = 10

@router.post("/upload_cv/")
async def upload_cv(file: UploadFile = File(...)):
    return handle_upload_cv(file)

@router.post("/upload_cv_from_drive/")
async def upload_cv_from_drive(google_drive_url: str = Form(...)):
    return handle_upload_cv_from_drive(google_drive_url)

@router.post("/search_candidates/")
async def search_candidates(search: CandidateSearch):
    return handle_search_candidates(search)

@router.post("/upload_cv_ollama/")
async def upload_cv_ollama(file: UploadFile = File(...)):
    return handle_upload_cv_with_ollama(file)