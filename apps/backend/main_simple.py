from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import Dict

# Simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Job Hunter AI",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("🚀 Starting up Job Hunter AI...")
    logger.info("✅ Server initialized successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down Job Hunter AI...")


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {
        "message": "🎯 Job Hunter AI API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "message": "✅ All systems operational"
    }

# --- SIMULAÇÃO DE ENDPOINTS REAIS PARA TESTE DE FLUXO ---

# DB Simulado em memória
fake_users_db = {}
fake_jobs_db = []

@app.post("/api/v1/auth/signup")
async def signup(user: Dict[str, str]):
    """Simula registro de usuário"""
    if user["email"] in fake_users_db:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Email already registered")
    
    fake_users_db[user["email"]] = user
    return {
        "id": len(fake_users_db),
        "email": user["email"],
        "username": user["username"],
        "is_active": True
    }

@app.post("/api/v1/auth/login")
async def login(credentials: Dict[str, str]):
    """Simula login e retorno de token"""
    email = credentials.get("username") or credentials.get("email")
    if email not in fake_users_db:
         from fastapi import HTTPException
         raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "access_token": f"fake-jwt-token-for-{email}",
        "token_type": "bearer"
    }

@app.get("/api/v1/jobs")
async def list_jobs():
    """Simula listagem de vagas mocks"""
    if not fake_jobs_db:
        # Seed inicial para não vir vazio
        fake_jobs_db.append({
            "id": 1,
            "title": "Python Developer",
            "company": "Tech Corp",
            "location": "Remote",
            "salary_min": 8000
        })
    return fake_jobs_db

@app.post("/api/v1/jobs")
async def create_job(job: Dict[str, str]):
    """Simula criação de vaga"""
    new_job = {**job, "id": len(fake_jobs_db) + 1}
    fake_jobs_db.append(new_job)
    return new_job

# --------------------------------------------------------

@app.get("/test")
async def test_endpoint() -> Dict[str, str]:
    """Test endpoint para validação"""
    return {
        "message": "🧪 Test successful!",
        "python_version": "3.14.3",
        "framework": "FastAPI"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
