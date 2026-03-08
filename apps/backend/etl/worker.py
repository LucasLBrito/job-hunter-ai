import asyncio
import os
import sys
import logging
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient

# Configuração para importar o app do projeto principal
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from app.db.session import async_session_maker
from app.models.job import Job
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# --- CONFIGURAÇÕES ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "job_lake")
BATCH_SIZE = 100

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- INICIALIZAÇÃO MONGO ---
mongo_client = AsyncIOMotorClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB_NAME]
raw_jobs_collection = mongo_db["raw_jobs"]

async def process_batch():
    logger.info(f"Looking for pending jobs in MongoDB...")
    
    # Busca 100 vagas com status pending_processing
    cursor = raw_jobs_collection.find({"status": "pending_processing"}).limit(BATCH_SIZE)
    raw_jobs = await cursor.to_list(length=BATCH_SIZE)
    
    if not raw_jobs:
        logger.info("No pending jobs found. Sleeping...")
        return 0

    logger.info(f"Processing batch of {len(raw_jobs)} jobs.")
    
    async with async_session_maker() as pg_db:
        processed_count = 0
        
        for raw_job in raw_jobs:
            try:
                success = await process_and_save_job(pg_db, raw_job)
                
                # Atualizando o status no Mongo
                new_status = "processed" if success else "error_processing"
                await raw_jobs_collection.update_one(
                    {"_id": raw_job["_id"]},
                    {"$set": {"status": new_status, "processed_at": datetime.now(timezone.utc)}}
                )
                
                if success:
                    processed_count += 1
            except Exception as e:
                logger.error(f"Error processing job {raw_job.get('_id', 'unknown')}: {str(e)}")
                await raw_jobs_collection.update_one(
                    {"_id": raw_job["_id"]},
                    {"$set": {"status": "error_processing", "error_message": str(e)}}
                )
        return processed_count


async def process_and_save_job(pg_db: AsyncSession, raw_data: dict) -> bool:
    """
    Limpa o HTML e salva no banco relacional (PostgreSQL).
    Retorna True se salvou com sucesso.
    """
    source_url = raw_data.get("url")
    external_id = raw_data.get("_id") # Idealmente deve ser um hash único da URL (ex: url_hash)
    
    if not external_id or not source_url:
        return False
        
    # Extrair/Limpar dados base do HTML ou JSON salvo
    raw_html = raw_data.get("raw_html", "")
    title = raw_data.get("title", "")
    company = raw_data.get("company", "")
    description = raw_data.get("description", "")
    
    # Se o crawler salvou raw_html bruto sem parsear, o ETL pode fazer isso aqui:
    if raw_html and (not description or not title):
        soup = BeautifulSoup(raw_html, "html.parser")
        # Exemplo simples de fallback (O ideal é ter regras por source)
        if not title:
            title_tag = soup.find('h1')
            title = title_tag.text.strip() if title_tag else "Sem Título"
        if not description:
            description = soup.text.strip()[:1000] # Simplificação
            
    # --- Normalização ---
    title = title.strip()
    company = company.strip()
    
    location = raw_data.get("location", "")
    is_remote = False
    
    # Regra simples de Detecção de Remoto
    location_lower = str(location).lower()
    description_lower = str(description).lower()
    if any(keyword in location_lower for keyword in ["remoto", "remote", "home office", "teletrabalho"]):
        is_remote = True
    elif any(keyword in title.lower() for keyword in ["remoto", "remote"]):
        is_remote = True
        
    # --- Deduplicação Inteligente no Postgres ---
    # Verifica se já existe um `external_id`
    stmt = select(Job).where(Job.external_id == str(external_id))
    result = await pg_db.execute(stmt)
    existing_job = result.scalars().first()
    
    if existing_job:
        logger.debug(f"Job {external_id} already exists in DB. Skipping insert.")
        return True # Já existe, mas o processamento terminou com sucesso = Ignorar no Mongo
        
    # Ou por URL
    stmt_url = select(Job).where(Job.source_url == source_url)
    result_url = await pg_db.execute(stmt_url)
    existing_job_url = result_url.scalars().first()
    
    if existing_job_url:
        logger.debug(f"Job with URL {source_url} already exists. Skipping insert.")
        return True
        
    # Regras adicionais de negócios, salário parse, extração de tech poderiam ser inseridas aqui

    new_job = Job(
        external_id=str(external_id),
        title=title,
        company=company,
        description=description,
        location=location,
        is_remote=is_remote,
        source_platform=raw_data.get("source", "crawler"),
        source_url=source_url,
        posted_date=datetime.now(timezone.utc), # Ideal é extrair a data real da vaga
    )
    
    pg_db.add(new_job)
    await pg_db.commit()
    logger.info(f"Saved job to DB: {title} na {company}")
    return True

async def worker_loop():
    logger.info("ETL Worker started.")
    while True:
        try:
            processed = await process_batch()
            if processed == 0:
                await asyncio.sleep(60) # Espera 1 minuto se não tiver nada
            else:
                await asyncio.sleep(5)  # Pequena pausa entre lotes para não sufocar a CPU
        except Exception as e:
            logger.error(f"Fatal erro no Worker loop: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("ETL Worker stopped.")
