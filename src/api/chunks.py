from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.chunk import ChunkResponse

from src.dependencies import get_chunk_service

router = APIRouter(prefix="/chunks", tags=["Chunks"])

@router.get("/", response_model=list[ChunkResponse])
async def list_chunks(
    chunk_service = Depends(get_chunk_service),
    limit: int = 10,
    offset: int = 0
):
    # Placeholder implementation
    return await chunk_service.list_chunks(limit, offset)

@router.get("/{chunk_id}", response_model=ChunkResponse)
async def get_chunk(
    chunk_id: str, 
    chunk_service = Depends(get_chunk_service)

):
    # Placeholder implementation
    chunk = await chunk_service.get_chunk_by_id(chunk_id)

    if chunk is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Chunk not found"
            )
    return chunk