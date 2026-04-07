
from src.services.rag.state import (
    GuardrailEvaluation,
    ThreadState
)

from src.services.rag.prompts import (
    query_evaluation_prompt,
)
from src.services.rag.context import Context
from src.services.rag.nodes.utils import (
    get_latest_query,
)

from typing import Dict, List, Literal
from langgraph.runtime import Runtime
from langchain_google_genai import ChatGoogleGenerativeAI
import logging

logger = logging.getLogger(__name__)

def continue_after_guardrail(state: ThreadState, runtime: Runtime[Context]) -> Literal["continue", "out_of_scope"]:
    """Determine whether to continue or reject based on guardrail results.

    This function checks the guardrail_result score against a threshold.
    If the score is above threshold, continue; otherwise route to out_of_scope.

    :param state: Current agent state with guardrail results
    :param runtime: Runtime context containing guardrail threshold
    :returns: "continue" if score >= threshold, "out_of_scope" otherwise
    """
    guardrail_result = state.get("guardrail_result")
    if not guardrail_result:
        return "continue"

    return "continue" if guardrail_result.is_lecture_related else "out_of_scope"


async def invoke_query_guardrail(state: ThreadState, runtime: Runtime[Context]) -> Dict[str, List[GuardrailEvaluation] | int]:
    """Evaluate the initial query for relevance and clarity."""
    logger.info("NODE: invoke_query_guardrail")
    updates = {}

    query = get_latest_query(state.get("messages"))
    prompt = query_evaluation_prompt.format(query=query)

    logger.info(f"Evaluating query: {query[:50]}...")

    llm = ChatGoogleGenerativeAI(
        model=runtime.context.llm_model,
        temperature=runtime.context.temperature
        ).with_structured_output(GuardrailEvaluation)

    logger.info("Invoking LLM for query evaluation...")
    res = await llm.ainvoke(prompt)

    logger.info(f"Grade result - Is lecture related: {res.is_lecture_related}, Reasoning: {res.reasoning[:50]}...")

    updates["guardrail_result"] = res
    updates["n_llm_calls"] = state.get("n_llm_calls", 0) + 1

    return updates