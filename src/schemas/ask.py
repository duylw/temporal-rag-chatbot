from pydantic import BaseModel, ConfigDict

class AskRequest(BaseModel):
    question: str
    video_id: str  # UUID as string

class AskResponse(BaseModel):
    answer: str

    model_config = ConfigDict(from_attributes=True)