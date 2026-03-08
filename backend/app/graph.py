"""
Agent Graph with LangGraph Workflow

This module creates the LangGraph workflow where:
- The selected LLM (OpenAI/Gemini/Ollama) acts as the intelligent agent
- It decides when to use tools to retrieve information
- Local file tools provide university-specific information
- The same LLM generates the final user-facing responses
"""

from typing import Annotated, Sequence, TypedDict, Optional, Literal
from langchain_core.messages import BaseMessage, SystemMessage, AIMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.postgres import PostgresSaver

from app.llm_provider import get_current_llm, llm_provider
from app.tools import available_tools
from app.config import DATABASE_URL_SYNC
from app.query_router import classify_query, get_routing_context, get_domain_tools_for_query


def sanitize_messages(messages: list[BaseMessage]) -> list[BaseMessage]:
    """
    Remove orphaned tool_calls that have no matching ToolMessage response.
    
    LLMs sometimes emit tool_calls in an AIMessage, but if the tool
    execution fails or is skipped the follow-up ToolMessage is missing.
    Passing such orphaned calls back into the model causes errors with
    most providers.  This helper strips those dangling calls.
    """
    # Collect IDs of all ToolMessages in the conversation
    tool_msg_ids: set[str] = set()
    for m in messages:
        if isinstance(m, ToolMessage) and hasattr(m, "tool_call_id"):
            tool_msg_ids.add(m.tool_call_id)

    cleaned: list[BaseMessage] = []
    for m in messages:
        if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
            # Keep only tool_calls that have a corresponding ToolMessage
            valid_calls = [tc for tc in m.tool_calls if tc["id"] in tool_msg_ids]
            if valid_calls:
                m = m.copy()
                m.tool_calls = valid_calls
                cleaned.append(m)
            else:
                # Drop tool_calls entirely but keep text content if any
                if m.content:
                    cleaned.append(AIMessage(content=m.content))
                # else skip the message entirely
        else:
            cleaned.append(m)
    return cleaned


# Define the Agent's State
class AgentState(TypedDict):
    """State maintained throughout the conversation."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


def agent_node(state: AgentState) -> AgentState:
    """
    Agent Node - Uses the selected LLM with domain-aware tool routing
    
    The LLM analyzes the user's question and decides:
    1. Whether to use tools to retrieve information from local files
    2. Which tools to call and with what parameters
    3. How to generate the response
    
    Domain-aware routing classifies the query and dynamically binds
    only the relevant domain tools, improving accuracy and reducing
    unnecessary tool calls.
    """
    print("---NODE: AGENT LLM---")
    
    # Get the current LLM
    llm = get_current_llm(temperature=0.3)
    
    # Extract the latest user message for domain classification
    user_messages = [m for m in state["messages"] if hasattr(m, 'type') and m.type == 'human']
    latest_query = ""
    if user_messages:
        latest_query = user_messages[-1].content if hasattr(user_messages[-1], 'content') else str(user_messages[-1])
    elif state["messages"]:
        # Fallback: try the last message tuple format
        last = state["messages"][-1]
        if isinstance(last, tuple) and len(last) == 2:
            latest_query = last[1]
        elif hasattr(last, 'content'):
            latest_query = last.content
    
    # Check if model supports tools
    if llm_provider.supports_tools():
        print("Using LLM with tool support")
        
        # Domain-aware routing: classify query and select relevant tools
        domain_tools = get_domain_tools_for_query(latest_query)
        routing_context = get_routing_context(latest_query)
        routing_result = classify_query(latest_query)
        
        print(f"Domain routing: {[d.value for d in routing_result.domains]} "
              f"(scores: {routing_result.scores})")
        print(f"Binding {len(domain_tools)} tool(s): "
              f"{[t.name for t in domain_tools]}")
        
        llm_with_tools = llm.bind_tools(domain_tools)
        
        system_message = SystemMessage(content=f"""You are a helpful university chatbot assistant with access to local university information files.

{routing_context}

HOW TO RESPOND:
1. For ANY question, ALWAYS use the appropriate tool first to search the university knowledge base
2. If the tools return relevant information, answer BASED ON that information and cite it as from the university knowledge base
3. If the tools return "The related data is not present" or no relevant information is found, you MAY still answer the question using your general knowledge, BUT you MUST clearly add a disclaimer like:
   "⚠️ *Note: This answer is based on general knowledge and was not retrieved from the university knowledge base.*"

Your knowledge base is organized in categories:
1. Academic: Calendars, schedules, dates, holidays
2. Administrative: Policies, procedures, contact info, fees, financial aid, scholarships, refunds
3. Educational: Course materials and resources

Available tools (USE THESE FIRST):
- search_university_info: For policies, procedures, programs, fees, financial aid, services (Administrative)
- search_academic_calendar: For dates, holidays, deadlines, events (Academic)
- check_if_date_is_holiday: To verify if a specific date is a holiday
- get_university_contact_info: For department contact information
- search_educational_resources: For course materials and educational content
- search_all_domains: For queries spanning multiple topics or unclear domain

Tool selection guide:
- Questions about tuition, payments, fees, scholarships, refunds → use search_university_info
- Questions about dates, holidays, deadlines → use search_academic_calendar or check_if_date_is_holiday
- Questions about contact info → use get_university_contact_info
- Questions about courses, materials, programming, subjects → use search_educational_resources
- General questions → use search_educational_resources first, then answer with general knowledge if not found
- Multi-domain questions (e.g. "refund policy if I drop a course") → use tools from ALL relevant domains

IMPORTANT: Always search the knowledge base first. Only fall back to general knowledge if the tools find nothing. Always be transparent about the source of your answer.""")
        
        messages = [system_message] + list(state["messages"])
        response = llm_with_tools.invoke(messages)
    else:
        print("Using LLM WITHOUT tool support - direct responses only")
        
        system_message = SystemMessage(content="""You are a helpful university chatbot assistant.

Provide clear, concise, and helpful responses to user questions. Answer to the best of your knowledge about university-related topics including:
- Academic programs and courses
- Tuition and fees
- Academic calendars and deadlines
- University policies and procedures
- General educational topics

Be friendly, informative, and professional. If you don't know something specific to this university, say so honestly.""")
        
        messages = [system_message] + list(state["messages"])
        response = llm.invoke(messages)
    
    return {"messages": [response]}


def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """Decide whether to call tools or end."""
    print("---DECISION: SHOULD CONTINUE?---")
    
    last_message = state["messages"][-1]
    
    # Check if model supports tools first
    if not llm_provider.supports_tools():
        print("NO: Model doesn't support tools, ending")
        return "end"
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print(f"YES: Calling {len(last_message.tool_calls)} tool(s)")
        return "tools"
    else:
        print("NO: Ending")
        return "end"


# Create tool node for executing tools
tool_node = ToolNode(available_tools)


def create_agent_graph():
    """
    Creates and compiles the agent graph.
    
    Flow:
    1. User question → Agent LLM (decides if tools needed)
    2. If tools needed → Execute tools → Back to Agent
    3. Agent generates response → End
    """
    print("---CREATING AGENT GRAPH---")
    
    # Initialize PostgreSQL checkpointer for persistent conversation memory
    try:
        checkpointer = PostgresSaver.from_conn_string(DATABASE_URL_SYNC)
        checkpointer.setup()  # Creates checkpoint tables if they don't exist
        print("PostgreSQL checkpointer initialized - conversation history will persist across restarts")
    except Exception as e:
        print(f"Warning: Could not initialize PostgreSQL checkpointer: {e}")
        print("Falling back to no checkpointer - conversation history will not persist")
        checkpointer = None
    
    # Build the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        }
    )
    
    # Tools loop back to agent for processing results
    workflow.add_edge("tools", "agent")
    
    # Compile with checkpointer
    app = workflow.compile(checkpointer=checkpointer)
    
    print("Agent graph compiled successfully")
    return app


# For testing
if __name__ == "__main__":
    app = create_agent_graph()
    
    test_questions = [
        "How can I pay my tuition fees?",
        "What is SQL and do we use it at the university?",
        "Is November 1 a holiday?",
    ]
    
    thread_config = {"configurable": {"thread_id": "test-session"}}
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"QUESTION: {question}")
        print('='*60)
        
        result = app.invoke(
            {"messages": [("user", question)]},
            config=thread_config
        )
        
        final_message = result["messages"][-1]
        print(f"\nANSWER: {final_message.content}")
        print('='*60)
