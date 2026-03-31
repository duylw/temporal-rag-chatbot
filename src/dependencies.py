from src.services.user import UserService
from src.services.video import VideoService
from src.services.chunk import ChunkService

from src.database.session import async_session_maker, get_db_session
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_community.retrievers import BM25Retriever

from fastapi import Depends, HTTPException, Request

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

def get_user_service(dependency_session: AsyncSession = Depends(get_db_session)):
    return UserService(dependency_session)

def get_video_service(dependency_session: AsyncSession = Depends(get_db_session)):
    return VideoService(dependency_session)

def get_chunk_service(dependency_session: AsyncSession = Depends(get_db_session)):
    return ChunkService(dependency_session)

def get_bm25_retriever(request: Request) -> BM25Retriever:
    retriever = getattr(request.app.state, "bm25_retriever", None)
    if not retriever:
        # Prevent errors if queried before data exists
        raise HTTPException(
            status_code=503, 
            detail="BM25 Search index is not yet built or the database is empty."
        )
    return retriever