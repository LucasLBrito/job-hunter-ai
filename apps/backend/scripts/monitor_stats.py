import asyncio
import time
import os
import sys

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from sqlalchemy import select, func
from app.database import AsyncSessionLocal
from app.models.job import Job
from app.models.resume import Resume
from app.models.user import User

async def get_stats():
    async with AsyncSessionLocal() as db:
        jobs_count = await db.execute(select(func.count(Job.id)))
        resumes_count = await db.execute(select(func.count(Resume.id)))
        users_count = await db.execute(select(func.count(User.id)))
        
        # Try Mongo stats if available
        raw_count = "N/A"
        processed_count = "N/A"
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
            MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "job_lake")
            client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=2000)
            db_mongo = client[MONGO_DB_NAME]
            raw_count = await db_mongo["raw_jobs"].count_documents({})
            processed_count = await db_mongo["raw_jobs"].count_documents({"status": "processed"})
        except Exception:
            pass
            
        return {
            "jobs_sql": jobs_count.scalar() or 0,
            "resumes_sql": resumes_count.scalar() or 0,
            "users_sql": users_count.scalar() or 0,
            "mongo_total": raw_count,
            "mongo_processed": processed_count
        }

def start_monitoring(hours=2, interval_minutes=10, log_file="monitor_log.txt"):
    duration_secs = hours * 3600
    interval_secs = interval_minutes * 60
    start_time = time.time()
    
    print(f"Iniciando monitoramento por {hours} horas. Atualizacoes a cada {interval_minutes} minutos.")
    print(f"Logs serao salvos no arquivo: {log_file}")
    
    with open(log_file, "a") as f:
        f.write(f"\n--- Novo Ciclo de Monitoramento Iniciado em {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
    
    while time.time() - start_time < duration_secs:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        try:
            stats = asyncio.run(get_stats())
            log_line = (f"[{timestamp}] "
                        f"PostgreSQL/SQLite -> Vagas: {stats['jobs_sql']} | Curriculos: {stats['resumes_sql']} | Usuarios: {stats['users_sql']} || "
                        f"MongoDB -> Total Brutal: {stats['mongo_total']} | Processadas: {stats['mongo_processed']}\n")
        except Exception as e:
            log_line = f"[{timestamp}] ERRO ao buscar dados: {e}\n"
            
        print(log_line.strip())
        
        with open(log_file, "a") as f:
            f.write(log_line)
            f.flush()
            
        # Calcula quanto falta e dorme
        elapsed = time.time() - start_time
        if elapsed >= duration_secs:
            break
            
        remaining_sleep = min(interval_secs, duration_secs - elapsed)
        time.sleep(remaining_sleep)
        
    print("Monitoramento finalizado.")
    with open(log_file, "a") as f:
        f.write(f"--- Monitoramento Finalizado as {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")

if __name__ == "__main__":
    start_monitoring()
