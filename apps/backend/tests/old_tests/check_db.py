import asyncio
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.resume import Resume

# Forcing synchronous checks for simplicity
engine = create_engine("sqlite:///../../local_database/database.db")
Session = sessionmaker(bind=engine)

def check_db():
    session = Session()
    r = session.query(Resume).filter(Resume.id == 2).first()
    if r:
        print(f"FOUND RESUME: id={r.id} path={r.file_path} analyzed={r.is_analyzed}")
        print("Raw text snippet:", r.raw_text[:200] if r.raw_text else None)
        print("Summary:", r.ai_summary)
    else:
        print("RESUME 2 NOT FOUND IN DB!")
    session.close()

if __name__ == "__main__":
    check_db()
