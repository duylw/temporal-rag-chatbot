from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.chunk import Chunk
from src.schemas.chunk import ChunkResponse

import uuid

class ChunkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, video_id: uuid.UUID) -> ChunkResponse | None:
        result = await self.session.get(Chunk, video_id)
        return result
    
    async def list(self,
                   limit: int = 10,
                   offset: int = 0
                   ) -> list[ChunkResponse]:
        result = await self.session.execute(
            select(Chunk).limit(limit).offset(offset)
        )
        return result.scalars().all()