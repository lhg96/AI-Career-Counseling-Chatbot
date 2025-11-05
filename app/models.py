from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

Base = declarative_base()

# 1. 상담 기록 데이터 스키마
class CounsellingMeta(BaseModel):
    student_idx: str = Field(..., example="S-0001")
    counseling_idx: int = Field(..., example=1)
    counsellor_idx: str = Field(..., example="T-0001")
    counselling_purpose: str
    counselling_satisfaction: Optional[int] = Field(None, ge=1, le=5)
    counselling_date: datetime

class Utterance(BaseModel):
    speaker_idx: str
    utterance: str
    utterance_idx: int
    utterance_delaytime: float

class Conversation(BaseModel):
    conv_category: str
    self_eval: List[int]
    utterances: List[Utterance]

class CounsellingRecord(BaseModel):
    meta: CounsellingMeta
    conversation: Dict[str, Conversation]

# 2. 학생 기초정보 스키마
class Survey(BaseModel):
    question: str
    answer: int = Field(..., ge=1, le=5)

class PreliminaryInspection(BaseModel):
    grade: str
    counselling_purpose: str
    surveys: List[Survey]

class StudentMetaBasics(BaseModel):
    index: str = Field(..., example="S-0001")
    school_type: str
    region: Optional[str]
    gender: Optional[str]
    preliminary_inspection: PreliminaryInspection

# 3. 직업 기초 데이터 스키마
class JobInformation(BaseModel):
    index: str = Field(..., example="J-001")
    category: str
    name: str
    detail_information: Dict[str, str] = Field(...)
    annual_expectedIncome: int
    required_ability: List[str]
    related_departments: List[str]
    
    class Config:
        arbitrary_types_allowed = True

# 4. 전문가 라벨링 데이터 스키마
class Highlight(BaseModel):
    start_idx: int
    end_idx: int
    
    class Config:
        arbitrary_types_allowed = True

class CounsellingSummary(BaseModel):
    counseling_idx: int
    highlights: List[Highlight]
    summary: str
    
    class Config:
        arbitrary_types_allowed = True

class JobRecommendation(BaseModel):
    priority: int
    job_category_idx: int
    
    class Config:
        arbitrary_types_allowed = True

class ExpertLabeling(BaseModel):
    student_idx: str
    counselling_summaries: List[CounsellingSummary]
    recommended_job_categories: Optional[List[JobRecommendation]] = None
    
    class Config:
        arbitrary_types_allowed = True

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    student_idx = Column(String(10), unique=True, nullable=False)  # S-0001 format
    school_level = Column(String(10), nullable=False)  # 초등/중등/고등
    counselling_sessions = relationship("CounsellingSession", back_populates="student")

class CounsellingSession(Base):
    __tablename__ = 'counselling_sessions'
    
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    counseling_idx = Column(Integer, nullable=False)  # Session number for this student
    summary = Column(Text, nullable=False)
    student = relationship("Student", back_populates="counselling_sessions")
    highlights = relationship("Highlight", back_populates="session")

class Highlight(Base):
    __tablename__ = 'highlights'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('counselling_sessions.id'), nullable=False)
    start_idx = Column(Integer, nullable=False)  # Start index in the summary text
    end_idx = Column(Integer, nullable=False)    # End index in the summary text
    content = Column(Text, nullable=False)       # The highlighted text
    session = relationship("CounsellingSession", back_populates="highlights")

def init_db(db_path):
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine
