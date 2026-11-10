from typing import List, Optional, Any, Union
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.personas import ROLE_PERSONA_PROMPTS, DEFAULT_STAYEASE_SYSTEM_PROMPT
from app.core.tools import HOTEL_OPERATIONAL_TOOLS
from app.core.fallback import execute_local_operational_fallback
from app.hotel.guardrails import HotelGuardrails
from app.config.settings import settings
from app.common.logger import get_logger

logger = get_logger(__name__)

def get_response_from_ai_agents(
    llm_id: str,
    query: List[Any],
    allowed_search: bool = False,
    system_prompt: Optional[str] = None,
    active_role: str = "General"
) -> str:
    """
    Executes the StayEase Multi-Role AI Agent with complete tool bindings and input/output guardrails.
    Features 3-layer resilience:
    1. Primary Groq LLM (with explicit auth, multi-turn history, timeout & retries)
    2. Fallback Groq LLM (alternate model if primary fails)
    3. Deterministic Local Operational Fallback Engine (guarantees 100% uptime with zero 500 errors)
    """
    # Extract last user query text for safety guardrails and fallback
    last_user_query = ""
    for m in reversed(query):
        if isinstance(m, dict):
            if m.get("role") == "user":
                last_user_query = m.get("content", "")
                break
        elif isinstance(m, str):
            last_user_query = m
            break
    if not last_user_query and query:
        last_user_query = str(query[-1])

    # 1. Enforce Input Guardrails
    is_safe, violation_msg = HotelGuardrails.check_input_safety(last_user_query)
    if not is_safe:
        return violation_msg

    logger.info("Initializing StayEase AI Agent in role '%s' with model: %s", active_role, llm_id)

    # Format full multi-turn conversation messages for LangGraph
    lc_messages = []
    for m in query:
        if isinstance(m, dict):
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "assistant":
                lc_messages.append(AIMessage(content=content))
            else:
                lc_messages.append(HumanMessage(content=content))
        elif isinstance(m, str):
            lc_messages.append(HumanMessage(content=m))

    # Clone operational tools list
    tools = list(HOTEL_OPERATIONAL_TOOLS)

    # Add Tavily web search if requested
    if allowed_search:
        try:
            tools.append(TavilySearch(max_results=2))
        except Exception as e:
            logger.warning("Could not initialize TavilySearch tool: %s", e)

    # Determine prompt based on role persona
    base_persona = ROLE_PERSONA_PROMPTS.get(active_role, DEFAULT_STAYEASE_SYSTEM_PROMPT)
    prompt = f"{base_persona}\n\nCustom Instructions: {system_prompt.strip()}" if (system_prompt and system_prompt.strip()) else base_persona

    # Candidate models for failover
    candidate_models = [llm_id]
    for alt in ["openai/gpt-oss-20b", "qwen/qwen3.8-27b", "openai/gpt-oss-120b"]:
        if alt not in candidate_models:
            candidate_models.append(alt)

    # Layer 1 & 2: Try Cloud LLMs
    for model_name in candidate_models:
        try:
            llm = ChatGroq(
                model=model_name,
                api_key=settings.GROQ_API_KEY,
                temperature=0.2,
                max_retries=2,
                request_timeout=35
            )
            agent = create_react_agent(
                model=llm,
                tools=tools,
                prompt=prompt
            )
            state = {"messages": lc_messages}
            response = agent.invoke(state)

            messages = response.get("messages", [])
            ai_messages = [message.content for message in messages if isinstance(message, AIMessage) and message.content]

            raw_response = ai_messages[-1] if ai_messages else "Request processed successfully."
            return HotelGuardrails.filter_response(raw_response)

        except Exception as groq_err:
            logger.warning("Groq invocation failed on model '%s': %s. Retrying...", model_name, groq_err)

    # Layer 3: Deterministic Local Operational Fallback Engine
    logger.info("Executing local operational fallback engine for query: '%s' (role: %s)", last_user_query, active_role)
    fallback_raw = execute_local_operational_fallback(last_user_query, active_role)
    return HotelGuardrails.filter_response(fallback_raw)
