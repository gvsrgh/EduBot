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
from langgraph.checkpoint.memory import MemorySaver

from app.llm_provider import get_current_llm, llm_provider
from app.tools import available_tools


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


def sanitize_messages(messages: list) -> list:
    """
    Remove orphaned tool_calls from history.
    
    If an AIMessage has tool_calls but is NOT followed by ToolMessages
    for each call, OpenAI rejects the request. Strip those broken pairs.
    """
    from langchain_core.messages import AIMessage, ToolMessage
    sanitized = []
    i = 0
    while i < len(messages):
        msg = messages[i]
        if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", None):
            # Collect the tool_call_ids that need responses
            needed_ids = {tc["id"] for tc in msg.tool_calls}
            # Collect following ToolMessages
            j = i + 1
            found_ids = set()
            while j < len(messages) and isinstance(messages[j], ToolMessage):
                found_ids.add(messages[j].tool_call_id)
                j += 1
            # Only keep if all tool responses are present
            if needed_ids == found_ids:
                sanitized.extend(messages[i:j])
            else:
                print(f"Dropping orphaned tool_calls message (missing responses for: {needed_ids - found_ids})")
            i = j
        else:
            sanitized.append(msg)
            i += 1
    return sanitized


def agent_node(state: AgentState) -> AgentState:
    """
    Agent Node - Uses the selected LLM with or without tools
    
    The LLM analyzes the user's question and decides:
    1. Whether to use tools to retrieve information from local files
    2. Which tools to call and with what parameters
    3. How to generate the response
    """
    print("---NODE: AGENT LLM---")
    
    # Get the current LLM
    llm = get_current_llm(temperature=0.3)
    
    # Check if model supports tools
    if llm_provider.supports_tools():
        print("Using LLM with tool support")
        llm_with_tools = llm.bind_tools(available_tools)
        
        system_message = SystemMessage(content="""You are a helpful university chatbot assistant with access to ONLY local university information files.

CRITICAL RULES:
1. You can ONLY answer questions using information from the university knowledge base files
2. You MUST use the available tools to search for information before answering
3. If the tools return "The related data is not present" or no relevant information is found, you MUST inform the user that you don't have that information
4. NEVER use your general knowledge or training data to answer questions
5. NEVER make up or infer information that isn't explicitly in the files

Your capabilities:
1. Search university files organized in categories:
   - Academic: Calendars, schedules, dates, holidays
   - Administrative: Policies, procedures, contact info, fees
   - Educational: Course materials and resources

2. Available tools (YOU MUST USE THESE):
   - search_university_info: For policies, procedures, programs, fees, services (Administrative)
   - search_academic_calendar: For dates, holidays, deadlines, events (Academic)
   - check_if_date_is_holiday: To verify if a specific date is a holiday
   - get_university_contact_info: For department contact information
   - search_educational_resources: For course materials and educational content
   - search_all_domains: Search ALL categories at once when the question spans multiple topics or the domain is unclear

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
- Questions about courses, materials → use search_educational_resources
- Questions spanning multiple topics or unclear domain → use search_all_domains
- Questions about general topics (like "What is SQL?" or "Who is Trump?") → use search_educational_resources first, if no data found, respond: "I apologize, but I don't have information about [topic] in my university knowledge base. I can only answer questions about our university's academics, policies, schedules, and resources."

If tools return "The related data is not present" or find nothing:
"I apologize, but I don't have that specific information in my knowledge base yet. The related data has not been uploaded to the system. I can only provide information about our university that has been added to my knowledge base."

REMEMBER: You are a university-specific assistant. Stay within your knowledge base. Do not answer from general knowledge.""")
        
        messages = [system_message] + sanitize_messages(list(state["messages"]))
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
        
        messages = [system_message] + sanitize_messages(list(state["messages"]))
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
    
    # Initialize in-memory checkpointer for conversation memory
    try:
        checkpointer = MemorySaver()
        print("Memory checkpointer initialized")
    except Exception as e:
        print(f"Warning: Could not initialize checkpointer: {e}")
        print("Conversation history will not persist")
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
