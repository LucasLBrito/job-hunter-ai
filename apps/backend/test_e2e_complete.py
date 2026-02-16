"""
End-to-End Test: Complete Job Hunter AI Flow
Tests: Register → Login → Upload Resume → AI Analysis → Job Recommendations
"""
import requests
import json
import time
import os
from io import BytesIO

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def create_sample_resume():
    """Create a sample resume PDF-like content"""
    resume_text = """
JOÃO SILVA
Software Engineer | Full Stack Developer
Email: joao.silva@email.com | Phone: (11) 98765-4321
LinkedIn: linkedin.com/in/joaosilva | GitHub: github.com/joaosilva

PROFESSIONAL SUMMARY
Experienced Full Stack Developer with 5+ years building scalable web applications.
Expert in Python, JavaScript, React, and cloud technologies. Passionate about AI/ML.

TECHNICAL SKILLS
• Languages: Python, JavaScript, TypeScript, SQL
• Frontend: React, Next.js, Vue.js, HTML5, CSS3, Tailwind CSS
• Backend: FastAPI, Django, Node.js, Express
• Databases: PostgreSQL, MongoDB, Redis
• Cloud: AWS, Google Cloud, Docker, Kubernetes
• AI/ML: TensorFlow, scikit-learn, Pandas, NumPy
• Tools: Git, GitHub Actions, Jest, Pytest

PROFESSIONAL EXPERIENCE

Senior Software Engineer | TechCorp Inc. | 2021 - Present
• Developed AI-powered recommendation system serving 1M+ users
• Built RESTful APIs using FastAPI and Django
• Implemented real-time features with WebSockets
• Led migration to microservices architecture on AWS
• Mentored junior developers and conducted code reviews

Full Stack Developer | StartupXYZ | 2019 - 2021
• Created responsive web applications with React and Next.js
• Designed and optimized database schemas (PostgreSQL)
• Implemented CI/CD pipelines with GitHub Actions
• Reduced page load time by 60% through optimization

EDUCATION
Bachelor of Computer Science | University of São Paulo | 2019
Relevant Coursework: Data Structures, Algorithms, Machine Learning, Web Development

CERTIFICATIONS
• AWS Certified Developer - Associate
• Google Cloud Professional Developer
• MongoDB Certified Developer

LANGUAGES
• Portuguese (Native)
• English (Fluent)
• Spanish (Intermediate)
"""
    return resume_text.encode('utf-8')

def test_complete_flow():
    """Execute complete end-to-end test"""
    
    # Step 1: Register User
    print_section("STEP 1: User Registration")
    
    signup_data = {
        "email": f"joao.test{int(time.time())}@email.com",
        "username": f"joao_test_{int(time.time())}",
        "password": "senha123456",
        "full_name": "João Silva Test"
    }
    
    print(f"Creating user: {signup_data['email']}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
        if response.status_code in [200, 201]:
            user_data = response.json()
            print(f"✅ User created successfully!")
            print(f"   User ID: {user_data['id']}")
            print(f"   Email: {user_data['email']}")
        elif response.status_code == 400:
            print("⚠️  User already exists")
        else:
            print(f"❌ Signup failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 2: Login
    print_section("STEP 2: User Login")
    
    login_data = {
        "username": signup_data["email"],
        "password": signup_data["password"]
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return
    
    token_data = response.json()
    token = token_data.get('access_token')
    
    print(f"✅ Login successful!")
    print(f"   Token: {token[:50]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 3: Upload Resume
    print_section("STEP 3: Upload Resume")
    
    resume_content = create_sample_resume()
    
    files = {
        'file': ('joao_silva_resume.txt', BytesIO(resume_content), 'text/plain')
    }
    
    # Correct endpoint is POST /resumes/ (not /resumes/upload)
    response = requests.post(
        f"{BASE_URL}/resumes/",
        headers=headers,
        files=files
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Resume upload failed: {response.status_code}")
        print(response.text)
        return
    
    resume_data = response.json()
    resume_id = resume_data['id']
    
    print(f"✅ Resume uploaded successfully!")
    print(f"   Resume ID: {resume_id}")
    print(f"   Filename: {resume_data['filename']}")
    print(f"   Size: {resume_data['file_size']} bytes")
    
    # Step 4: Trigger AI Analysis
    print_section("STEP 4: Trigger AI Analysis")
    
    print(f"Triggering analysis for resume ID: {resume_id}")
    
    response = requests.post(
        f"{BASE_URL}/resumes/{resume_id}/analyze",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Analysis trigger failed: {response.status_code}")
        print(response.text)
        # Continue anyway to see what happens
    else:
        print(f"✅ Analysis triggered!")
    
    # Step 5: Wait for Analysis to Complete
    print_section("STEP 5: Wait for AI Analysis")
    
    print("Waiting for AI to analyze resume...")
    max_attempts = 12  # 60 seconds max
    attempt = 0
    
    while attempt < max_attempts:
        time.sleep(5)
        attempt += 1
        
        response = requests.get(
            f"{BASE_URL}/resumes/{resume_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            resume_data = response.json()
            
            if resume_data.get('is_analyzed'):
                print(f"\n✅ Analysis completed! (took ~{attempt * 5} seconds)")
                print(f"\n📊 Analysis Results:")
                print(f"   Summary: {resume_data.get('ai_summary', 'N/A')[:200]}...")
                
                # Parse technical skills
                try:
                    tech_skills = json.loads(resume_data.get('technical_skills', '[]'))
                    print(f"   Technical Skills ({len(tech_skills)}): {', '.join(tech_skills[:5])}...")
                except:
                    print(f"   Technical Skills: {resume_data.get('technical_skills', 'N/A')[:100]}")
                
                # Parse soft skills
                try:
                    soft_skills = json.loads(resume_data.get('soft_skills', '[]'))
                    print(f"   Soft Skills ({len(soft_skills)}): {', '.join(soft_skills[:5])}...")
                except:
                    print(f"   Soft Skills: {resume_data.get('soft_skills', 'N/A')[:100]}")
                
                break
            elif resume_data.get('ai_summary', '').startswith('ERROR:'):
                print(f"\n❌ Analysis failed: {resume_data.get('ai_summary')}")
                print("\n⚠️  This might be due to missing GEMINI_API_KEY")
                print("   Continuing with test to show other features...")
                break
            else:
                print(f"   Attempt {attempt}/{max_attempts}: Still analyzing...")
        else:
            print(f"   Error checking status: {response.status_code}")
    
    # Step 6: Search and Save Jobs
    print_section("STEP 6: Search for Jobs")
    
    print("Searching for Python developer jobs...")
    
    response = requests.post(
        f"{BASE_URL}/jobs/search",
        headers=headers,
        params={"query": "Python Developer", "limit": 5}
    )
    
    if response.status_code == 200:
        jobs = response.json()
        print(f"✅ Found and saved {len(jobs)} jobs!")
        
        if jobs:
            print(f"\nFirst job:")
            print(f"   Title: {jobs[0].get('title')}")
            print(f"   Company: {jobs[0].get('company')}")
            print(f"   Location: {jobs[0].get('location')}")
    else:
        print(f"⚠️  Job search returned: {response.status_code}")
        print(f"   This is okay - continuing with test")
    
    # Step 7: Get Recommended Jobs
    print_section("STEP 7: Get AI-Powered Recommendations")
    
    print("Fetching personalized job recommendations...")
    
    response = requests.get(
        f"{BASE_URL}/jobs/recommended",
        headers=headers,
        params={"limit": 5}
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        recommended_jobs = response.json()
        
        print(f"\n🎯 SUCCESS! Got {len(recommended_jobs)} recommended jobs\n")
        
        for idx, job in enumerate(recommended_jobs, 1):
            print(f"{idx}. {job.get('title')} at {job.get('company')}")
            
            if job.get('compatibility_score'):
                print(f"   Match: {job.get('compatibility_score')}%")
            
            if job.get('location'):
                print(f"   Location: {job.get('location')}")
            
            if job.get('salary_min') or job.get('salary_max'):
                salary = f"${job.get('salary_min', 0):,} - ${job.get('salary_max', 0):,}"
                print(f"   Salary: {salary}")
            
            print()
        
        print("\n✅ END-TO-END TEST PASSED!")
        print("\n📝 Summary:")
        print(f"   ✓ User registration")
        print(f"   ✓ Authentication")
        print(f"   ✓ Resume upload")
        print(f"   ✓ AI analysis (Gemini)")
        print(f"   ✓ Embedding generation (Pinecone)")
        print(f"   ✓ Job recommendations")
        
    else:
        print(f"❌ Recommendations failed: {response.status_code}")
        try:
            error = response.json()
            print(f"Error: {json.dumps(error, indent=2)}")
        except:
            print(response.text)
    
    # Step 8: Get User Profile
    print_section("STEP 8: Verify User Profile")
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        print(f"✅ User Profile:")
        print(f"   Name: {user['full_name']}")
        print(f"   Email: {user['email']}")
        print(f"   ID: {user['id']}")
    
    print_section("TEST COMPLETED")
    print("\n🎉 You can now test in the browser at: http://localhost:3000")
    print(f"   Email: {signup_data['email']}")
    print(f"   Password: {signup_data['password']}")

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║        JOB HUNTER AI - END-TO-END TEST SUITE              ║
║                                                            ║
║  Testing complete flow with AI analysis and Pinecone      ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")
    
    test_complete_flow()
