from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Job(Base):
    """Job listing model"""
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(255), unique=True, index=True, nullable=False)  # Unique ID from source
    
    # Job info
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    
    # Location
    location = Column(String(255), nullable=True)
    is_remote = Column(Boolean, default=False)
    
    # Salary
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    salary_currency = Column(String(10), default="BRL")
    
    # Source
    source_platform = Column(String(50), nullable=False)  # linkedin, indeed, remoteok
    source_url = Column(Text, nullable=False)
    
    # AI Analysis
    compatibility_score = Column(Float, nullable=True)  # 0-100
    ai_summary = Column(Text, nullable=True)
    extracted_technologies = Column(Text, nullable=True)  # JSON string
    culture_fit_score = Column(Float, nullable=True)  # 0-100
    company_research = Column(Text, nullable=True)  # JSON string with company info
    
    # Smart Analysis
    pros = Column(Text, nullable=True) # JSON list
    cons = Column(Text, nullable=True) # JSON list
    
    # Status
    is_active = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False)
    is_hidden = Column(Boolean, default=False)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    posted_date = Column(DateTime(timezone=True), nullable=True)
    found_date = Column(DateTime(timezone=True), server_default=func.now())
    analyzed_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    applications = relationship("Application", back_populates="job")
    
    def __repr__(self):
        return f"<Job {self.title} at {self.company}>"
