from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ApplicationStatus(str, enum.Enum):
    """Application status enum"""
    PENDING = "pending"
    APPLIED = "applied"
    REVIEWING = "reviewing"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(Base):
    """Job application tracking"""
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=True)
    
    # Application info
    status = Column(SQLEnum(ApplicationStatus), default=ApplicationStatus.PENDING)
    application_method = Column(String(50), nullable=True)  # whatsapp, web, auto
    cover_letter = Column(Text, nullable=True)
    
    # Tracking
    applied_via_platform = Column(String(50), nullable=True)  # linkedin, indeed, company_website
    confirmation_url = Column(Text, nullable=True)
    confirmation_screenshot = Column(Text, nullable=True)  # path to screenshot
    
    # Communication log
    notes = Column(Text, nullable=True)
    interview_dates = Column(Text, nullable=True)  # JSON array
    
    # Timestamps
    applied_at = Column(DateTime(timezone=True), nullable=True)
    last_status_update = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    
    def __repr__(self):
        return f"<Application {self.id} - Status: {self.status}>"
