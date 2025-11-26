from typing import List, Dict, Any, Optional, Sequence
import logging
import asyncio
from langgraph.graph import StateGraph, END
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage, BaseMessage

from engine.types import AgentState
from engine.tool_adapter import adapt_mcp_to_langchain
from engine.executor import ToolExecutor

logger = logging.getLogger(__name__)

class AgentBuilder:
    """Builds a LangGraph agent with MCP tool support."""
    
    def __init__(self, llm: Runnable, recursion_limit: int = 50):
        """
        Initialize AgentBuilder.
        
        Args:
            llm: The language model to use
            recursion_limit: Maximum number of agent iterations (default: 50)
                            This is the single source of truth for iteration limits.
        """
        self.llm = llm
        self.tools = []
        self.external_tools = []
        # Rate limiting protection
        self.consecutive_rate_limits = 0
        self.adaptive_delay = 0.0 
        # Recursion limit from agent config (single source of truth)
        self.max_iterations = recursion_limit
        
    def add_mcp_tool(self, mcp_tool_def: Dict[str, Any]):
        """Add an MCP tool definition to the agent."""
        adapted_tool = adapt_mcp_to_langchain(mcp_tool_def)
        # MCP tools are executed via fastmcp_manager, not external_tools
        # Just add the adapted schema for LLM binding
        self.tools.append(adapted_tool)

    def add_tool(self, tool: Any):
        """Add a LangChain tool or MCP tool definition."""
        if isinstance(tool, dict):
            self.add_mcp_tool(tool)
        else:
            # Assume it's a LangChain tool
            self.tools.append(tool)
            self.external_tools.append(tool)
            
    def build(self, system_prompt: str = ""):
        """Build the StateGraph."""
        
        # Initialize executor with external tools and increased delay
        self.tool_executor = ToolExecutor(external_tools=self.external_tools, tool_call_delay=1.0)
        
        # Bind tools to LLM
        if self.tools:
            logger.info(f"📋 Binding {len(self.tools)} tools to LLM")
            
            # Log tool names for debugging
            tool_names = []
            for tool in self.tools:
                if isinstance(tool, dict):
                    tool_name = tool.get("function", {}).get("name", "unknown")
                    tool_names.append(tool_name)
                else:
                    tool_names.append(getattr(tool, 'name', 'unknown'))
            logger.info(f"  Tool names: {', '.join(tool_names[:10])}{'...' if len(tool_names) > 10 else ''}")
            
            # For Groq models, we need to use strict mode and tool_choice to force proper function calling
            # Groq's smaller models (like llama-3.1-8b-instant) have poor function calling support
            # and may generate malformed XML-like function calls instead of proper JSON
            try:
                # Try binding with strict mode first (works for newer Groq models)
                llm_with_tools = self.llm.bind_tools(self.tools, tool_choice="auto")
                logger.info("✅ Tools bound successfully with tool_choice='auto'")
            except Exception as e:
                # Fallback to standard binding
                logger.warning(f"Failed to bind with tool_choice, using standard binding: {e}")
                try:
                    llm_with_tools = self.llm.bind_tools(self.tools)
                    logger.info("✅ Tools bound successfully (without tool_choice)")
                except Exception as e2:
                    logger.error(f"❌ Failed to bind tools at all: {e2}")
                    raise Exception(f"Tool binding failed: {e2}")
        else:
            logger.warning("⚠️ No tools to bind - agent will run in conversational mode")
            llm_with_tools = self.llm
            
        # Define the agent node with rate limiting protection
        async def agent_node(state: AgentState, config: RunnableConfig):
            # Track iterations to prevent infinite loops
            iteration_count = state.get("iteration_count", 0)
            iteration_count += 1
            
            # Hard limit on iterations
            if iteration_count > self.max_iterations:
                logger.warning(f"Reached max iterations ({self.max_iterations}). Stopping agent.")
                return {
                    "messages": [AIMessage(content=f"I've reached the maximum number of iterations ({self.max_iterations}). Here's what I found so far based on the tools I've used.")],
                    "iteration_count": iteration_count
                }
            
            messages = state["messages"]
            # Ensure system prompt is the first message if provided
            if system_prompt and not isinstance(messages[0], SystemMessage):
                messages = [SystemMessage(content=system_prompt)] + list(messages)
            elif system_prompt and isinstance(messages[0], SystemMessage):
                 # Update existing system prompt
                 messages = [SystemMessage(content=system_prompt)] + list(messages)[1:]

            # Apply adaptive delay if recent rate limits
            if self.adaptive_delay > 0:
                logger.info(f"⏱️ Adaptive backoff: {self.adaptive_delay}s (rate limit protection)")
                await asyncio.sleep(self.adaptive_delay)

            try:
                response = await llm_with_tools.ainvoke(messages, config)
                
                # Success - gradually reduce adaptive delay
                self.consecutive_rate_limits = 0
                if self.adaptive_delay > 0:
                    self.adaptive_delay = max(0, self.adaptive_delay - 1.0)
                    logger.info(f"Rate limit cleared. Reducing delay to {self.adaptive_delay}s")
                
                return {"messages": [response], "iteration_count": iteration_count}
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Detect rate limit errors (429)
                if "429" in error_msg or "rate limit" in error_msg or "too many requests" in error_msg:
                    self.consecutive_rate_limits += 1
                    # Exponential backoff: 2s, 4s, 8s, 16s, 30s (capped)
                    self.adaptive_delay = min(30, 2 ** self.consecutive_rate_limits)
                    logger.warning(f"⚠️ Rate limit hit (#{self.consecutive_rate_limits}). Setting adaptive delay to {self.adaptive_delay}s")
                    
                    # Stop if too many consecutive rate limits
                    if self.consecutive_rate_limits >= 5:
                        logger.error("Too many consecutive rate limits. Stopping agent.")
                        return {
                            "messages": [AIMessage(content="I'm experiencing repeated rate limits from the API. Please try again in a few moments.")],
                            "iteration_count": iteration_count
                        }
                    
                    # Re-raise to trigger retry
                    raise
                else:
                    # Other errors - re-raise
                    logger.error(f"Agent node error: {e}")
                    raise
            
        # Define the tools node with SEQUENTIAL execution
        async def tools_node(state: AgentState):
            messages = state["messages"]
            last_message = messages[-1]
            
            if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
                return {"messages": []}
            
            # SEQUENTIAL EXECUTION: Process only the FIRST tool call
            # After this tool completes, the agent will see the result and decide the next action
            # This prevents parallel execution and allows the agent to reason step-by-step
            tool_calls = last_message.tool_calls
            
            if len(tool_calls) > 1:
                logger.info(f"🔧 Agent requested {len(tool_calls)} tools, but executing FIRST tool only (sequential mode)")
                logger.info(f"   Executing: {tool_calls[0].get('name', 'unknown')}")
                logger.info(f"   Queued: {[tc.get('name', 'unknown') for tc in tool_calls[1:]]}")
            else:
                logger.info(f"🔧 Executing single tool: {tool_calls[0].get('name', 'unknown')}")
            
            # Execute only the first tool call
            first_tool_call = [tool_calls[0]]
            tool_results = await self.tool_executor.execute_tools(first_tool_call)
            
            return {"messages": tool_results}
            
        # Define the conditional edge
        def should_continue(state: AgentState):
            messages = state["messages"]
            last_message = messages[-1]
            
            if isinstance(last_message, AIMessage) and last_message.tool_calls:
                return "tools"
            return END
            
        # Build the graph
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tools_node)
        
        workflow.set_entry_point("agent")
        
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                END: END
            }
        )
        
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
