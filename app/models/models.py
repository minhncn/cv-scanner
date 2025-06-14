from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Candidate(Base):
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    education = Column(Text)
    skills = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    work_experiences = relationship("WorkExperience", back_populates="candidate")
    raw_cvs = relationship("RawCV", back_populates="candidate")

class WorkExperience(Base):
    __tablename__ = 'work_experiences'
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    company = Column(String(255))
    position = Column(String(255))
    start_date = Column(String(50))
    end_date = Column(String(50))
    description = Column(Text)
    candidate = relationship("Candidate", back_populates="work_experiences")

class RawCV(Base):
    __tablename__ = 'raw_cvs'
    id = Column(Integer, primary_key=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    raw_text = Column(Text, nullable=False)
    source_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    candidate = relationship("Candidate", back_populates="raw_cvs")
