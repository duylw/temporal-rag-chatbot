import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.chunk import ChunkRepository
from src.models.chunk import Chunk

class ChunkService:
    def __init__(self, session: AsyncSession):
        self.repository = ChunkRepository(session)

    async def get_chunk_by_id(self, chunk_id: str) -> Chunk | None:
        # Convert the string to a UUID object to match the parameter
        target_uuid = uuid.UUID(chunk_id)
        
        return await self.repository.get_by_id(target_uuid)
    
    async def list_chunks(self, limit: int = 10, offset: int = 0) -> list[Chunk]:
        return await self.repository.list(limit, offset)