import json
from typing import List, Optional
from app.models.user import User
from app.models.resume import Resume
from app.services.scrapers.models import ScrapedJob
from app.models.job import Job

class ScoringService:
    @staticmethod
    def extract_skills_and_preferences(user: User, resume: Optional[Resume] = None) -> dict:
        """Extracts skills and preferences from user and recent resume."""
        resume_skills = []
        if resume:
            try:
                raw_skills = json.loads(resume.technical_skills) if resume.technical_skills else []
                resume_skills = [str(s).lower() for s in raw_skills if s]
            except:
                pass
        
        user_techs = []
        try:
            raw_techs = json.loads(user.technologies) if user.technologies else []
            user_techs = [str(s).lower() for s in raw_techs if s]
        except:
            pass
            
        user_work_models = []
        try:
            user_work_models = json.loads(user.work_models) if user.work_models else []
        except:
            pass
            
        user_job_titles = []
        try:
            user_job_titles = json.loads(user.job_titles) if user.job_titles else []
        except:
            pass
            
        user_locations = []
        try:
            user_locations = json.loads(user.preferred_locations) if user.preferred_locations else []
        except:
            pass
            
        return {
            "all_skills": list(set(resume_skills + user_techs)),
            "job_titles": user_job_titles,
            "work_models": user_work_models,
            "locations": user_locations,
            "salary_min": user.salary_min,
            "seniority": user.seniority_level
        }

    @staticmethod
    def calculate_score(job, preferences: dict) -> int:
        """
        Calculates a 0-100 score for a job (either ScrapedJob or Job model)
        based on extracted preferences.
        """
        score = 0.0
        max_score = 0.0
        
        # Unified attribute access for both Job (SQLAlchemy) and ScrapedJob (Pydantic)
        job_title = str(getattr(job, "title", "") or "").lower()
        job_desc = str(getattr(job, "description", "") or "").lower()
        job_reqs = str(getattr(job, "requirements", "") or "").lower()
        job_text = f"{job_title} {job_desc} {job_reqs}"
        
        job_is_remote = getattr(job, "is_remote", False)
        job_salary_max = getattr(job, "salary_max", None)
        job_location = str(getattr(job, "location", "") or "").lower()

        # 1. Technology/Skill Match (weight: 35)
        all_skills = preferences.get("all_skills", [])
        if all_skills:
            max_score += 35
            match_count = sum(1 for skill in all_skills if skill in job_text)
            score += (match_count / max(len(all_skills), 1)) * 35
            
        # 2. Job Title Match (weight: 25)
        user_job_titles = preferences.get("job_titles", [])
        if user_job_titles:
            max_score += 25
            title_match = any(t.lower() in job_title for t in user_job_titles)
            if title_match:
                score += 25
            else:
                # Partial match
                partial = sum(1 for t in user_job_titles if any(word in job_title for word in t.lower().split()))
                score += (partial / max(len(user_job_titles), 1)) * 15
                
        # 3. Work Model Match (weight: 15)
        user_work_models = preferences.get("work_models", [])
        if user_work_models:
            max_score += 15
            user_wants_remote = any(m.lower() in ["remote", "remoto"] for m in user_work_models)
            user_wants_hybrid = any(m.lower() in ["hybrid", "híbrido", "hibrido"] for m in user_work_models)
            
            if user_wants_remote and job_is_remote:
                score += 15
            elif user_wants_hybrid and ("hybrid" in job_text or "híbrido" in job_text):
                score += 15
            elif not user_wants_remote and not job_is_remote:
                score += 10
                
        # 4. Salary Match (weight: 10)
        user_salary_min = preferences.get("salary_min")
        if user_salary_min and job_salary_max:
            max_score += 10
            if job_salary_max >= user_salary_min:
                score += 10
            elif job_salary_max >= user_salary_min * 0.8:
                score += 5
                
        # 5. Location Match (weight: 10)
        user_locations = preferences.get("locations", [])
        if user_locations and job_location:
            max_score += 10
            loc_match = any(loc.lower() in job_location for loc in user_locations)
            if loc_match:
                score += 10
                
        # 6. Seniority Match (weight: 5)
        user_seniority = preferences.get("seniority")
        if user_seniority:
            max_score += 5
            seniority_lower = user_seniority.lower()
            if seniority_lower in job_title or seniority_lower in job_text:
                score += 5
                
        final_score = min(int((score / max_score) * 100), 95) if max_score > 0 else 0
        return final_score
