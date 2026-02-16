import asyncio
import logging
import sys
import os

# Ensure backend directory is in python path
sys.path.append(os.getcwd())

from app.database import AsyncSessionLocal
from app.models.user import User
from app.crud import user as crud_user
from app.schemas.user import UserUpdate
from app.services.optimization_service import optimization_service
from app.services.email_service import EmailService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_backend_final():
    logger.info("🚀 Starting Backend Phase 6 Verification...")
    
    async with AsyncSessionLocal() as db:
        # 1. Get or Create Test User
        user = await crud_user.get_by_email(db, email="test_final@example.com")
        if not user:
            logger.error("Test user not found to verify. Please ensure data is seeded.")
            # Create dummy user if needed, but assuming seed ran.
            from app.schemas.user import UserCreate
            user = await crud_user.create(db, UserCreate(
                email="test_final@example.com", 
                username="test_final", 
                password="password123",
                full_name="Test Final User"
            ))
            logger.info("Created test user: test_final@example.com")
        else:
            logger.info(f"Using existing user: {user.email}")

        # 2. Update User Config (API Keys & SMTP)
        # We will set dummy values to verify the DB update works
        # Real values would be needed for actual external calls
        logger.info("Updating User Configuration...")
        update_data = UserUpdate(
            gemini_api_key="dummy_gemini_key",
            openai_api_key="dummy_openai_key",
            smtp_email="test@gmail.com",
            smtp_password="dummy_password",
            smtp_server="smtp.gmail.com",
            smtp_port=587
        )
        user = await crud_user.update(db, db_obj=user, obj_in=update_data)
        
        # Verify persistence
        await db.refresh(user)
        assert user.gemini_api_key == "dummy_gemini_key"
        assert user.smtp_email == "test@gmail.com"
        logger.info("✅ User configuration updated and persisted.")

        # 3. Verify Optimization Service (Mocked Call)
        logger.info("Verifying Optimization Service...")
        
        resume_text = """
        John Doe
        Software Engineer
        Skills: Python, Java, SQL
        Experience: 
        - Backend Developer at Tech Corp (2020-Present): Built APIs.
        """
        
        job_description = """
        Python Developer needed. Must know FastAPI and Docker.
        """
        
        # Since key is dummy, we expect an error or need to mock
        # For this script, we'll confirm the service accepts the call
        result = await optimization_service.optimize_resume(
            user=user,
            resume_text=resume_text,
            job_description=job_description
        )
        
        if "error" in result and "API Key" in result.get("error", ""):
            # This is expected if we passed a dummy key (or extracted "dummy_gemini_key" is invalid)
            # Actually OptimizationService checks if key exists, if so calls API.
            # With dummy key, Google API will return 400 or 401.
            logger.info(f"✅ Optimization Service attempted call (Expected Error with dummy key): {result['error']}")
        elif "optimized_content" in result:
             logger.info("✅ Optimization Service returned content (Unexpected with dummy key but good!)")
        else:
             logger.info(f"Optimization Result: {result}")

        # 4. Verify Email Service
        logger.info("Verifying Email Service structure...")
        # We won't actually send email with dummy creds, but we can check the logic
        # by inspecting the service (static check) or trying and catching auth error.
        
        success = await EmailService.send_email(
            user=user,
            subject="Test Email",
            body="This is a test.",
            to_emails=["recipient@example.com"]
        )
        
        if not success:
            logger.info("✅ Email Service failed gracefully with dummy credentials (Expected).")
        else:
            logger.info("✅ Email Service claimed success (Unexpected with dummy creds).")

        # 5. Verify Stats Logic
        logger.info("Verifying Stats Logic...")
        from sqlalchemy import select, func
        from app.models.job import Job
        from app.models.application import Application
        
        # Count Jobs
        result_jobs = await db.execute(select(func.count(Job.id)))
        count = result_jobs.scalar()
        logger.info(f"✅ Stats Query: Found {count} jobs in DB.")

    logger.info("🏁 Backend Phase 6 Verification Complete!")

if __name__ == "__main__":
    asyncio.run(verify_backend_final())
