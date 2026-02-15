from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class Resume(Base):
    """Resume/CV model"""
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # File info
    filename = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)  # bytes
    file_type = Column(String(50), nullable=True)  # pdf, docx
    
    # Extracted data (from Azure DI + LLM)
    raw_text = Column(Text, nullable=True)
    structured_data = Column(Text, nullable=True)  # JSON string
    
    # Skills analysis
    technical_skills = Column(Text, nullable=True)  # JSON array
    soft_skills = Column(Text, nullable=True)  # JSON array
    certifications = Column(Text, nullable=True)  # JSON array
    education = Column(Text, nullable=True)  # JSON object
    work_experience = Column(Text, nullable=True)  # JSON array
    
    # Summary
    ai_summary = Column(Text, nullable=True)
    years_of_experience = Column(Integer, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_analyzed = Column(Boolean, default=False)
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    analyzed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Resume {self.filename}>"
