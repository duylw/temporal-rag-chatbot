from src.services.rag.state import (
    QueryEvaluation,
    AnswerGrade,
    ThreadState
)

from src.services.rag.context import Context
from langgraph.runtime import Runtime

from src.services.rag.prompts import (
    query_evaluation_prompt,
    query_rewrite_prompt,
    answer_generation_prompt,
    answer_grade_prompt
)

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

async def query_evaluate(state: ThreadState, runtime: Runtime[Context]) -> ThreadState:
    """Evaluate the initial query for relevance and clarity."""
    prompt = query_evaluation_prompt.format(query=state.get("original_query", "No query provided"))
    llm = ChatGoogleGenerativeAI(
        model=runtime.context.llm_model,
        temperature=runtime.context.temperature
        ).with_structured_output(QueryEvaluation)
    
    res = await llm.ainvoke(prompt)
    
    return {
        "user_query_grade": res,
        "n_llm_calls": state.get("n_llm_calls", 0) + 1,
    }

async def query_rewrite(state: ThreadState, runtime: Runtime[Context]) -> ThreadState:
    """Rewrite the query for better retrieval."""

    answer_grade=state.get("answer_grade", None)


    if not state.get("user_query_grade"):
        

    prompt = query_rewrite_prompt.format(
        query=state.get("original_query", "No query provided"),
        previous_refined_query=state.get("rewritten_query", "N/A") if state.get("n_iterations") else "N/A",
        suggestion=state.get("user_query_grade").feedback if state.get("n_iterations") else "N/A",
        reasoning=state.get("user_query_grade").reasoning if state.get("n_iterations") else "N/A"
    )
    llm = ChatGoogleGenerativeAI(
        model=runtime.context.llm_model,
        temperature=runtime.context.temperature
    )
    res = await llm.ainvoke(prompt)
    return {
        "rewritten_query": res,
        "n_llm_calls": state.get("n_llm_calls", 0) + 1,
    }

async def get_relevant_documents(state: ThreadState, runtime: Runtime[Context]) -> ThreadState:
    """Retrieve relevant documents for context building"""
    pass

async def rerank(state: ThreadState, runtime: Runtime[Context]) -> ThreadState:
    """Re-ranking retrieved documents for better precision"""
    pass

async def generate_answer(state: ThreadState, runtime: Runtime[Context]) -> ThreadState:
    """Generate answer from context"""
    pass

async def grade_answer(state: ThreadState, runtime: Runtime[Context]) -> ThreadState:
    """Grade the answer"""
    pass

async def response(state: ThreadState, runtime: Runtime[Context]) -> ThreadState:
    """Return the final response and clean up state"""
    pass

if __name__ == "__main__":
    # This is just for testing the individual nodes. The actual orchestration happens in the agent.
    import asyncio

    async def test():
        state = {
            "messages": [],
            "original_query": "What is the difference between supervised and unsupervised learning?",
            "rewritten_query": "",
            "user_query_grade": None,
            "relevant_sources": [],
            "answer": "",
            "answer_grade": None,
            "n_iterations": 0,
            "n_llm_calls": 0
        }
            
        context = Context()
        runtime = Runtime(context=context)
        new_state = await query_evaluate(state, runtime)
        print(new_state)

    asyncio.run(test())