from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User model for authentication and profile"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # Profile info
    phone = Column(String(20), nullable=True)
    whatsapp_number = Column(String(20), nullable=True)
    
    # Preferences (JSON)
    technologies = Column(Text, nullable=True)  # JSON string: ["Python", "React"]
    job_titles = Column(Text, nullable=True)    # JSON string: ["Backend Engineer", "Data Scientist"]
    work_models = Column(Text, nullable=True)   # JSON string: ["Remote", "Hybrid"]
    employment_types = Column(Text, nullable=True) # JSON string: ["Full-time", "Contract"]
    company_styles = Column(Text, nullable=True)   # JSON string: ["Startup", "Big Tech"]
    seniority_level = Column(String(50), nullable=True)
    preferred_locations = Column(Text, nullable=True)  # JSON string: ["São Paulo", "Remote"]
    salary_min = Column(Integer, nullable=True)
    salary_max = Column(Integer, nullable=True)
    benefits = Column(Text, nullable=True)         # JSON string: ["Health Insurance", "GymPass"]
    industries = Column(Text, nullable=True)       # JSON string: ["Fintech", "Healthtech"]
    
    # Automation Config (API Keys & Email)
    gemini_api_key = Column(String(255), nullable=True)
    openai_api_key = Column(String(255), nullable=True)
    
    smtp_email = Column(String(255), nullable=True)
    smtp_password = Column(String(255), nullable=True) # Stored locally for MVP (ideal: encrypt)
    smtp_server = Column(String(255), default="smtp.gmail.com")
    smtp_port = Column(Integer, default=587)
    
    # WhatsApp Config
    whatsapp_api_token = Column(String(255), nullable=True)
    whatsapp_phone_number_id = Column(String(50), nullable=True)
    whatsapp_business_account_id = Column(String(50), nullable=True)
    
    # Azure Config
    azure_document_endpoint = Column(String(255), nullable=True)
    azure_document_key = Column(String(255), nullable=True)
    
    # Status & Logistics
    current_status = Column(String(50), nullable=True)  # e.g. "Employed", "Open to work"
    reason_for_search = Column(String(100), nullable=True) # e.g. "Better salary", "Career growth"
    open_to_relocation = Column(Boolean, default=False)
    availability = Column(String(50), nullable=True)    # e.g. "Immediate", "2 weeks"
    
    is_preferences_complete = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User {self.email}>"
