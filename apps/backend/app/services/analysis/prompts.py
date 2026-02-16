EXTRACT_RESUME_DATA_PROMPT = """
You are an expert technical recruiter and AI resume parser. 
Your task is to extract structured data from the provided resume text.

Input Text:
{resume_text}

Please analyze the text and return a valid JSON object with the following structure:
{{
    "ai_summary": "A professional summary of the candidate's profile (max 3 sentences)",
    "years_of_experience": <int_estimated_total_years>,
    "technical_skills": ["List", "of", "technical", "skills", "tools", "languages"],
    "soft_skills": ["List", "of", "soft", "skills"],
    "education": [
        {{
            "degree": "Degree Name",
            "institution": "University/School Name",
            "year": "Graduation Year (or range)"
        }}
    ],
    "work_experience": [
        {{
            "role": "Job Title",
            "company": "Company Name",
            "duration": "Duration/Dates",
            "description": "Brief description of responsibilities"
        }}
    ],
    "certifications": ["List", "of", "certifications"]
}}

Rules:
1. Return ONLY valid JSON. No markdown formatting (```json), no preambles.
2. If a field cannot be found, return null or empty list/string as appropriate.
3. For years_of_experience, estimate based on the work history if not explicitly stated.
4. Normalize skills to title case (e.g., "Python", "React").
"""
