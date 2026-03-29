from pydantic import BaseModel

class VideoBase(BaseModel):
    name: str
    url: str

class VideoResponse(VideoBase):
    id: str