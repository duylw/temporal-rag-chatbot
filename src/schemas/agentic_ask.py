from pydantic import BaseModel, ConfigDict
from langchain_core.documents import Document

class AgenticAskResponse(BaseModel):
    query: str
    rewritten_query: str
    answer: str
    sources: list[Document]
    n_iterations: int
    execution_time: float
    guardrail_result: str | None


    model_config = ConfigDict(from_attributes=True)