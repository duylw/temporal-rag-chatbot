from typing import TypedDict, Annotated, List, Optional
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

class AnswerGrade(BaseModel):
    is_relevant: bool = Field(description="Is the answer relevant to the query?")
    suggestion: str = Field(description="Suggestion for improving the answer")
    reasoning: str = Field(description="Reasoning for the answer")


class ThreadState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add] # Chat messages
    
    original_query: Optional[str]
    rewritten_query: Optional[str]
    user_query_grade: Optional[QueryEvaluation]

    source: List[Document]
    answer: Optional[str]
    answer_grade: Optional[AnswerGrade]
    routing_decision: Optional[str]

    routing_decision: Optional[str]
    n_iterations: int
    n_llm_calls: int