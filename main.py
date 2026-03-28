from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.users import router as users_router
from contextlib import asynccontextmanager

from src.database.session import engine
from src.models.base import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs when the server starts
    async with engine.begin() as conn:
        # Create all tables defined in your models
        await conn.run_sync(Base.metadata.create_all)
    
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)