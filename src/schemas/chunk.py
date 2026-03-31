from pydantic import BaseModel, ConfigDict
import uuid

class ChunkBase(BaseModel):
    content: str
    timestamp: int
    duration: int

class ChunkResponse(ChunkBase):
    id: uuid.UUID  # UUID as string
    video_id: uuid.UUID  # UUID as string

    model_config = ConfigDict(from_attributes=True) 