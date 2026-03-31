from typing import TypedDict, Annotated, List
from pydantic import BaseModel, Field
import operator


from langchain_core.documents import Document
from langchain_core.messages import AnyMessage

class QueryEvaluation(BaseModel):
    is_lecture_related: bool = Field(
            description="Boolean flag indicating whether the user's query is strictly relevant to the academic content, concepts, or logistics of the specific lecture."
    )

    reasoning: str = Field(
        description="A brief analytical explanation justifying the relevance decision, highlighting specific academic keywords or themes identified in the query."
    )

    feedback: str = Field(
        description="A polite, student-facing message providing guidance. If irrelevant, it explains the assistant's scope; if relevant, it confirms the intent to search the lecture materials. Must be in Vietnamese."
    )

class ResponseGrade(BaseModel):
  is_relevant: bool = Field(description="Is the answer relevant to the query?")
  suggestion: str = Field(description="Suggestion for improving the answer")
  reasoning: str = Field(description="Reasoning for the answer")


class ThreadState(TypedDict):
  messages: Annotated[list[AnyMessage], operator.add] # Chat messages
  user_query: str
  user_query_grade: QueryEvaluation
  previous_refined_query: str
  last_retrieved_docs: List[Document]
  last_response: str
  last_response_grade: ResponseGrade

  n_iterations: int
  n_llm_calls: int