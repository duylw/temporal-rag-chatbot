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
from src.services.rag.nodes.utils import (
    get_latest_query,
    get_latest_context,
    format_context,
    extract_sources_from_tool_messages,
    trim_messages,
    filter_messages
)

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.documents import Document
from typing import Dict, Literal, List

from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

def continue_after_guardrail(state: ThreadState, runtime: Runtime[Context]) -> Literal["continue", "out_of_scope"]:
    """Determine whether to continue or reject based on guardrail results.

    This function checks the guardrail_result score against a threshold.
    If the score is above threshold, continue; otherwise route to out_of_scope.

    :param state: Current agent state with guardrail results
    :param runtime: Runtime context containing guardrail threshold
    :returns: "continue" if score >= threshold, "out_of_scope" otherwise
    """
    user_query_grade = state.get("user_query_grade")
    if not user_query_grade:
        return "continue"

    return "continue" if user_query_grade.is_lecture_related else "out_of_scope"


async def query_guardrail(state: ThreadState, runtime: Runtime[Context]) -> Dict[str, QueryEvaluation | int]:
    """Evaluate the initial query for relevance and clarity."""
    
    updates = {}

    query = get_latest_query(state.get("messages"))
    
    prompt = query_evaluation_prompt.format(query=query)
    llm = ChatGoogleGenerativeAI(
        model=runtime.context.llm_model,
        temperature=runtime.context.temperature
        ).with_structured_output(QueryEvaluation)
    
    res = await llm.ainvoke(prompt)
    
    updates["user_query_grade"] = res
    updates["n_llm_calls"] = state.get("n_llm_calls", 0) + 1

    return updates

async def out_of_scope_response(state: ThreadState, runtime: Runtime[Context]) -> Dict[str, AIMessage]:
    """Generate a polite out-of-scope response when the query is not relevant."""
    updates = {}

    query = get_latest_query(state.get("messages"))
    prompt = f"Generate a polite response in Vietnamese explaining that the assistant cannot answer the query: '{query}' because it is outside the scope of the lecture materials. The response should guide the user to ask questions related to the lecture content, concepts, or logistics. Noted that only return the content without any preamble or explanation."

    llm = ChatGoogleGenerativeAI(
        model=runtime.context.llm_model,
        temperature=runtime.context.temperature
    )

    res = await llm.ainvoke(prompt)
    updates["messages"] = [AIMessage(content=res.content)]

    return updates

async def query_rewrite(state: ThreadState, runtime: Runtime[Context]) -> Dict[str, str | HumanMessage | int]:
    """Rewrite the query for better retrieval."""

    updates = {}

    original_query = state.get("original_query") or state.get("messages")[0].content
    current_iteration = state.get("n_iterations", 0)

    # If it is the first iteration
    if state.get("n_iterations", 0) == 0:
        prompt = query_rewrite_prompt.format(
        query=original_query or "No query provided!",
        previous_refined_query="N/A",
        suggestion="N/A",
        reasoning="N/A"
    )
    else:
        prompt = query_rewrite_prompt.format(
            query=original_query or "No query provided!",
            previous_refined_query=state.get("rewritten_query", "N/A"),
            suggestion=state.get("answer_grade").suggestion or "N/A",
            reasoning=state.get("answer_grade").reasoning or "N/A"
        )

    llm = ChatGoogleGenerativeAI(
        model=runtime.context.llm_model,
        temperature=runtime.context.temperature
    )

    res = await llm.ainvoke(prompt)
    rewritten_query = res.content

    updates["messages"] = [HumanMessage(content=rewritten_query)]
    updates["rewritten_query"] = rewritten_query
    updates["n_llm_calls"] = state.get("n_llm_calls", 0) + 1

    return updates

async def get_relevant_documents(state: ThreadState, runtime: Runtime[Context]) -> Dict[str, Document]:
    """Retrieve relevant documents for context building"""

    updates = {}

    # Create tool calls for retrieval.
    updates["messages"] = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": f"retrieve_{state.get('n_iterations', 0)}",
                    "name": "hybrid_search",
                    "args": {
                        "query": state.get("rewritten_query", ""),
                    }
                }
            ]
        )
    ]

    return updates

async def rerank(state: ThreadState, runtime: Runtime[Context]) -> Dict[str, Document]:
    """Re-ranking retrieved documents for better precision"""
    pass

async def generate_answer(state: ThreadState, runtime: Runtime[Context]) -> Dict[str, str | int]:
    """Generate answer from context"""
    updates = {}

    context = get_latest_context(state.get("messages", []))
    source = extract_sources_from_tool_messages(context)
    query = get_latest_query(state.get("messages", []))

    norm_context = format_context(source)

    prompt = answer_generation_prompt.format(query=query, context=norm_context)

    llm = ChatGoogleGenerativeAI(
        model=runtime.context.llm_model,
        temperature=runtime.context.temperature
    )
    res = await llm.ainvoke(prompt)

    updates["answer"] = res.content
    updates["n_llm_calls"] = state.get("n_llm_calls", 0) + 1

    return updates

async def grade_answer(state: ThreadState, runtime: Runtime[Context]) -> Dict[str, AnswerGrade | str | int]:
    """Grade the answer"""
    updates = {}

    answer = state.get("answer", "")
    query = get_latest_query(state.get("messages", []))
    prompt = answer_grade_prompt.format(query=query, generated_answer=answer)

    llm = ChatGoogleGenerativeAI(
        model=runtime.context.llm_model,
        temperature=runtime.context.temperature
    ).with_structured_output(AnswerGrade)

    res = await llm.ainvoke(prompt)

    updates["answer_grade"] = res

    is_relevant = res.is_relevant
    current_iteration = state.get("n_iterations", 0)
    max_iterations = runtime.context.n_iterations

    if not is_relevant:
        # Loop if no relevant answer and we haven't hit max iterations
        if current_iteration < max_iterations - 1:
            updates["n_iterations"] = current_iteration + 1
            updates["routing_decision"] = "rewrite_query"
        else: # If we've hit max iterations, provide a fallback response and end the loop
            fallback_msg = (
                f"Xin lỗi, tôi không thể tìm thấy nội dung bài giảng phù hợp để giải đáp câu hỏi trên sau {max_iterations} nỗ lực tìm kiếm.\n\n"
                "Nguyên nhân có thể là do:\n"
                "1. Nội dung này không nằm trong phạm vi các slide hoặc bài giảng hiện có.\n"
                "2. Các từ khóa bạn sử dụng chưa khớp với thuật ngữ chuyên ngành được dùng trong bài giảng.\n\n"
                "Bạn vui lòng kiểm tra lại câu hỏi hoặc sử dụng thêm các thuật ngữ tiếng Anh chuyên ngành (nếu có) để tôi có thể hỗ trợ tốt hơn."
            )
            updates["answer"] = fallback_msg
            updates["routing_decision"] = "response"
    else:
        updates["routing_decision"] = "response"

    return updates

async def response(state: ThreadState, runtime: Runtime[Context]) -> Dict[str, AIMessage]:
    """Return the final response and clean up state"""

    updates = {}

    updates["messages"] = [AIMessage(content=state.get("answer", ""))]

    return updates

if __name__ == "__main__":
    # This is just for testing the individual nodes. The actual orchestration happens in the agent.
    import asyncio
    from langgraph.graph import START, END, StateGraph
    from langgraph.prebuilt import tools_condition, ToolNode
    from src.services.rag.tools import create_retriever_tool
    from langchain_chroma import Chroma
    from src.services.rag.config import GraphConfig
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from dotenv import load_dotenv
    load_dotenv() # Load environment variables from .env file
    async def test():
        test_md = "src/services/rag/nodes/test.md"
        
        settings = GraphConfig()

        embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model
        )

        chroma = Chroma(
            embedding_function=embeddings,
            host=settings.settings.CHROMA_HOST,
            port="8008",
        )
        vectordb_retriever = chroma.as_retriever()

        hybrid_search = create_retriever_tool(vectordb_retriever=vectordb_retriever, top_k=10)
        tools = [hybrid_search]

        workflow = StateGraph(ThreadState, context_schema=Context)
        workflow.add_node(query_guardrail, "query_guardrail")
        workflow.add_node(out_of_scope_response, "out_of_scope_response")
        workflow.add_node(query_rewrite, "query_rewrite")
        workflow.add_node(get_relevant_documents, "get_relevant_documents")
        workflow.add_node("search_tool", ToolNode(tools))
        workflow.add_node(generate_answer, "generate_answer")
        workflow.add_node(grade_answer, "grade_answer")
        workflow.add_node(response, "response")

        workflow.add_edge(START, "query_guardrail")

        workflow.add_conditional_edges(
            "query_guardrail",
            continue_after_guardrail,
            {"continue": "query_rewrite", "out_of_scope": "out_of_scope_response"}
        )

        workflow.add_edge("out_of_scope_response", END)
        workflow.add_edge("query_rewrite", "get_relevant_documents")

        workflow.add_conditional_edges(
            "get_relevant_documents",
            tools_condition,
            {"tools": "search_tool"}
        )
        workflow.add_edge("search_tool", "generate_answer")
        workflow.add_edge("generate_answer", "grade_answer")

        workflow.add_conditional_edges(
            "grade_answer",
            lambda state: state.get("routing_decision", "response"),
            {"response": "response", "rewrite_query": "query_rewrite"}
        )

        workflow.add_edge("response", END)

        agent = workflow.compile()

        context = Context(
            n_iterations=2
        )
        inital_state = {
            "messages": [
                HumanMessage(content="Cách thức hoạt động của cơ chế self-attention")
            ],
            "n_iterations": 0,
            "n_llm_calls": 0
        }        
        final_state = await agent.ainvoke(inital_state, context=context)

        with open(test_md, "w", encoding="utf-8") as f:
            f.write("# Test Log\n\n")
            for mess in final_state["messages"]:
                role = "User" if isinstance(mess, HumanMessage) else "Assistant"
                role = "Tool" if isinstance(mess, ToolMessage) else role

                f.write(f"## {role} Message\n\n")
                if hasattr(mess, "tool_calls") and mess.tool_calls:
                    f.write("### Tool Calls\n\n")
                    for call in mess.tool_calls:
                        f.write(f"- **Tool Name**: {call['name']}\n")
                        f.write(f"  - **Args**: {call['args']}\n")
                        f.write(f"  - **ID**: {call['id']}\n\n")
                else:
                    f.write(f"{mess.content}\n\n")

    asyncio.run(test())