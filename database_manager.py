import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import chromadb
from chromadb.config import Settings
from models.models import Base, Candidate, WorkExperience, RawCV

def init_db():
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/cv_database")
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

def init_chromadb():
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )
    collection = client.get_or_create_collection(
        name="candidate_embeddings",
        metadata={"hnsw:space": "cosine"}
    )
    return collection