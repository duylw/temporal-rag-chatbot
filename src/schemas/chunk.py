from pydantic import BaseModel
import uuid

class ChunkBase(BaseModel):
    content: str
    timestamp: int
    duration: int

class ChunkResponse(ChunkBase):
    id: uuid.UUID  # UUID as string
    video_id: uuid.UUID  # UUID as string

    class Config:
        orm_mode = True