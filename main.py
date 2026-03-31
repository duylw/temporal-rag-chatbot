from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.users import router as users_router
from src.api.videos import router as videos_router
from src.api.chunks import router as chunks_router
from src.api.ask import router as ask_router
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import engine
from src.models.base import Base
from src.database.seed import seed_db_if_empty, seed_vector_db_if_empty

from src.services.bm25 import make_bm25_retriever

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts
    async with engine.begin() as conn:
        # Create all tables defined in your models
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        # Optionally seed the database with initial data if it's empty
        await seed_db_if_empty(session)
    
    seed_vector_db_if_empty() # Synchonous

    # Create and store the BM25 retriever in the app state for later use
    bm25_retriever = make_bm25_retriever()
    app.state.bm25_retriever = bm25_retriever

    yield

app = FastAPI(lifespan=lifespan)

app.include_router(users_router)
app.include_router(videos_router)
app.include_router(chunks_router)
app.include_router(ask_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)