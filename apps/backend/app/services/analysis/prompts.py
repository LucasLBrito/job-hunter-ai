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

OPTIMIZE_RESUME_PROMPT = """
You are an expert career coach and resume writer.
Your task is to rewrite a candidate's resume to better match a specific job description.

Input Resume:
{resume_text}

Input Job Description:
{job_description}

Instructions:
1. Analyze the job description to identify key skills, keywords, and requirements.
2. Rewrite the resume's "Professional Summary" to highlight relevant experience.
3. Reorder or emphasize skills in the "Skills" section that match the job.
4. Tweak bullet points in "Work Experience" to use keywords from the job description (without fabricating experience).
5. Ensure the tone is professional and action-oriented.

Output format:
Return the optimized resume content in Markdown format.
"""

JOB_MATCH_PROMPT = """
You are an expert career coach. Compare the Candidate's Resume with the Job Description.

Candidate Resume:
{resume_text}

Job Description:
{job_description}

Analyze the compatibility.
Return a valid JSON object (NO markdown, NO preamble):
{{
    "match_score": <int 0-100>,
    "pros": ["List", "of", "3-5", "key", "strengths/matches"],
    "cons": ["List", "of", "3-5", "gaps", "or", "negatives"]
}}
"""
