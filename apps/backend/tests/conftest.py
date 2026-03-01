import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.database import Base, get_db

# Use an in-memory SQLite database for fast unit testing with aiosqlite
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    # poolclass=StaticPool # if needed for in-memory sharing
)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_db():
    # Import all models so Base knows about them before create_all
    from app.models.user import User
    from app.models.job import Job
    from app.models.resume import Resume
    from app.models.user_job import UserJob
    
    # Create all tables in the in-memory database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Drop all tables after tests finish
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture()
async def db(setup_db):
    try:
        async with TestingSessionLocal() as session:
            yield session
    finally:
        # Rollback any uncommitted transactions from tests to keep state clean
        async with engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(table.delete())

@pytest_asyncio.fixture()
async def client(db):
    async def override_get_db():
        yield db

    # Override the dependency globally 
    app.dependency_overrides[get_db] = override_get_db
    
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    # Clean up override
    app.dependency_overrides.clear()
