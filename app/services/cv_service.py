from datetime import datetime
import json
from fastapi import UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.database_manager import init_db, init_chromadb
from models.models import Candidate, WorkExperience, RawCV
from services.cv_processor import extract_text_from_pdf, process_cv_to_json
from services.get_file_google_drive import download_pdf_from_google_drive, extract_drive_file_id
from services.ollama_cv import process_cv_with_ollama

session = init_db()
chroma_collection = init_chromadb()


def handle_upload_cv(file: UploadFile):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    raw_text = extract_text_from_pdf(file)
    candidate_data = process_cv_to_json(raw_text)
    candidate = Candidate(
        name=candidate_data.get('name', ''),
        email=candidate_data.get('email', ''),
        phone=candidate_data.get('phone', ''),
        education=candidate_data.get('education', ''),
        skills=json.dumps(candidate_data.get('skills', []))
    )
    session.add(candidate)
    session.flush()
    for exp in candidate_data.get('work_experience', []):
        work_exp = WorkExperience(
            candidate_id=candidate.id,
            company=exp.get('company'),
            position=exp.get('position'),
            start_date=exp.get('start_date'),
            end_date=exp.get('end_date'),
            description=exp.get('description')
        )
        session.add(work_exp)
    raw_cv = RawCV(
        candidate_id=candidate.id,
        raw_text=raw_text,
        source_path=file.filename
    )
    session.add(raw_cv)
    skills_text = " ".join(candidate_data.get('skills', []))
    work_desc = " ".join([exp.get('description', '') for exp in candidate_data.get('work_experience', [])])
    embedding_text = f"{skills_text} {work_desc}"
    chroma_collection.add(
        documents=[embedding_text],
        metadatas=[{"candidate_id": candidate.id}],
        ids=[str(candidate.id)]
    )
    session.commit()
    return {"status": "success", "candidate_id": candidate.id}


def handle_upload_cv_from_drive(google_drive_url: str):
    try:
        file_id = extract_drive_file_id(google_drive_url)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Google Drive URL")
    pdf_bytes, filename = download_pdf_from_google_drive(file_id)
    class DummyUploadFile:
        def __init__(self, file_bytes, filename):
            from io import BytesIO
            self.file = BytesIO(file_bytes)
            self.filename = filename
    dummy_file = DummyUploadFile(pdf_bytes, filename)
    raw_text = extract_text_from_pdf(dummy_file)
    candidate_data = process_cv_to_json(raw_text)
    candidate = Candidate(
        name=candidate_data.get('name', ''),
        email=candidate_data.get('email', ''),
        phone=candidate_data.get('phone', ''),
        education=candidate_data.get('education', ''),
        skills=json.dumps(candidate_data.get('skills', []))
    )
    session.add(candidate)
    session.flush()
    for exp in candidate_data.get('work_experience', []):
        work_exp = WorkExperience(
            candidate_id=candidate.id,
            company=exp.get('company'),
            position=exp.get('position'),
            start_date=exp.get('start_date'),
            end_date=exp.get('end_date'),
            description=exp.get('description')
        )
        session.add(work_exp)
    raw_cv = RawCV(
        candidate_id=candidate.id,
        raw_text=raw_text,
        source_path=filename
    )
    session.add(raw_cv)
    skills_text = " ".join(candidate_data.get('skills', []))
    work_desc = " ".join([exp.get('description', '') for exp in candidate_data.get('work_experience', [])])
    embedding_text = f"{skills_text} {work_desc}"
    chroma_collection.add(
        documents=[embedding_text],
        metadatas=[{"candidate_id": candidate.id}],
        ids=[str(candidate.id)]
    )
    session.commit()
    return {"status": "success", "candidate_id": candidate.id}


def handle_upload_cv_with_ollama(file: UploadFile):
    try:
        # Extract text from PDF
        raw_text = extract_text_from_pdf(file)
        
        # Process with Ollama
        cv_data = process_cv_with_ollama(raw_text)
        
        # Create candidate record
        candidate = Candidate(
            name=cv_data["name"],
            email=cv_data["email"],
            phone=cv_data["phone"],
            education=json.dumps(cv_data["education"]),  # Store as JSON string
            skills=json.dumps(cv_data["skills"]),        # Store as JSON string
            created_at=datetime.utcnow()
        )
        session.add(candidate)
        session.flush()  # Get candidate.id before adding related records
        
        # Save raw CV text
        raw_cv = RawCV(
            candidate_id=candidate.id,
            raw_text=raw_text,
            source_path=file.filename,
            created_at=datetime.utcnow()
        )
        session.add(raw_cv)
        
        # Save work experiences
        for exp in cv_data.get("work_experience", []):
            work_exp = WorkExperience(
                candidate_id=candidate.id,
                company=exp["company"],
                position=exp["position"],
                start_date=exp["start_date"],
                end_date=exp["end_date"],
                description=exp["description"]
            )
            session.add(work_exp)
        
        session.commit()
        return {"message": "CV processed successfully", "candidate_id": candidate.id}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing CV: {e}")
    
def handle_search_candidates(search):
    results = chroma_collection.query(
        query_texts=[search.query],
        n_results=search.max_results
    )
    candidate_ids = [int(meta['candidate_id']) for meta in results['metadatas'][0]]
    candidates = session.query(Candidate).filter(Candidate.id.in_(candidate_ids)).all()
    response = []
    for candidate in candidates:
        work_exps = session.query(WorkExperience).filter(WorkExperience.candidate_id == candidate.id).all()
        response.append({
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "phone": candidate.phone,
            "education": candidate.education,
            "skills": json.loads(candidate.skills),
            "work_experience": [
                {
                    "company": exp.company,
                    "position": exp.position,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date,
                    "description": exp.description
                } for exp in work_exps
            ]
        })
    return JSONResponse(content=response)
