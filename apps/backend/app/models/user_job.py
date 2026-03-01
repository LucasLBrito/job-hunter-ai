from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class UserJob(Base):
    """
    Stores the compatibility score between a User and a Job.
    This allows each user to have their own score for every job,
    so scores are not shared/overwritten across users.
    """
    __tablename__ = "user_jobs"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)

    # Scores & metadata
    compatibility_score = Column(Float, nullable=True)  # 0-100 based on ScoringService
    # Status tracking: "new", "viewed", "applied", "rejected", "saved"
    status = Column(String(50), default="new", nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="user_jobs")
    job = relationship("Job", back_populates="user_jobs")

    # A user can only have one score entry per job
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_user_job"),
    )

    def __repr__(self):
        return f"<UserJob user={self.user_id} job={self.job_id} score={self.compatibility_score}>"
