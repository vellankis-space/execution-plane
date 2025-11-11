import uuid
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_core.language_models import FakeListLLM
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq
import hashlib
import base64
from cryptography.fernet import Fernet

from services.memory_service import MemoryService
from services.tools_service import ToolsService
from middleware.pii_middleware import create_pii_middleware_from_config, PIIMiddleware

from models.agent import Agent as AgentModel
from schemas.agent import AgentCreate, AgentInDB
from core.config import settings
from sqlalchemy import text


class AgentService:
    def __init__(self, db: Session):
        self.db = db
        # Generate encryption key from settings or create a default one
        # In production, this should be stored securely
        self._encryption_key = self._get_or_create_encryption_key()
        
        # Initialize memory service for mem0 integration
        self.memory_service = MemoryService()
        
        # Initialize tools service for external tools
        self.tools_service = ToolsService()
        
        # Ensure database schema compatibility (add columns if missing)
        try:
            self._ensure_schema()
        except Exception as e:
            # Do not fail service init if schema check fails; log and continue
            print(f"Schema check warning: {e}")

    def _ensure_schema(self):
        """Ensure required columns exist; add them if missing (SQLite safe)."""
        # Only run for SQLite-like DBs where PRAGMA is supported; otherwise skip
        try:
            conn = self.db.connection()
            # Check agents table columns
            result = conn.execute(text("PRAGMA table_info(agents)")).fetchall()
            columns = {row[1] for row in result}
            # Add tool_configs column if missing
            if "tool_configs" not in columns:
                print("Adding missing 'tool_configs' column to agents table (auto-fix)...")
                conn.execute(text("ALTER TABLE agents ADD COLUMN tool_configs JSON"))
            # Add pii_config column if missing (backward-compat)
            if "pii_config" not in columns:
                print("Adding missing 'pii_config' column to agents table (auto-fix)...")
                conn.execute(text("ALTER TABLE agents ADD COLUMN pii_config JSON"))
        except Exception as e:
            # Re-raise to be caught by caller; helpful for logging only
            raise e
    
    def _get_or_create_encryption_key(self) -> bytes:
        # In production, this should come from a secure environment variable
        key_source = settings.SECRET_KEY.encode() if hasattr(settings, 'SECRET_KEY') and settings.SECRET_KEY else b'mech_agent_default_secret_key_32bytes!'
        # Ensure the key is 32 bytes for Fernet
        return base64.urlsafe_b64encode(hashlib.sha256(key_source).digest())
    
    def _encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key for storage"""
        f = Fernet(self._encryption_key)
        return f.encrypt(api_key.encode()).decode()
    
    def _decrypt_api_key(self, encrypted_api_key: str) -> str:
        """Decrypt API key for use"""
        f = Fernet(self._encryption_key)
        return f.decrypt(encrypted_api_key.encode()).decode()
    
    async def create_agent(self, agent_data: AgentCreate) -> AgentInDB:
        """Create a new agent in the database"""
        agent_id = str(uuid.uuid4())
        
        # Encrypt the API key before storing
        encrypted_api_key = None
        if agent_data.api_key:
            encrypted_api_key = self._encrypt_api_key(agent_data.api_key)
        
        db_agent = AgentModel(
            agent_id=agent_id,
            name=agent_data.name,
            agent_type=agent_data.agent_type,
            llm_provider=agent_data.llm_provider,
            llm_model=agent_data.llm_model,
            temperature=agent_data.temperature,
            system_prompt=agent_data.system_prompt,
            tools=agent_data.tools,
            tool_configs=agent_data.tool_configs,
            max_iterations=agent_data.max_iterations,
            memory_type=agent_data.memory_type,
            streaming_enabled=agent_data.streaming_enabled,
            human_in_loop=agent_data.human_in_loop,
            recursion_limit=agent_data.recursion_limit,
            api_key_encrypted=encrypted_api_key,
            pii_config=agent_data.pii_config
        )
        
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        print(f"Agent committed to database: {db_agent.agent_id}")
        
        return AgentInDB.model_validate(db_agent)
    
    async def get_agent(self, agent_id: str) -> Optional[AgentInDB]:
        """Retrieve an agent by ID"""
        db_agent = self.db.query(AgentModel).filter(AgentModel.agent_id == agent_id).first()
        if db_agent:
            return AgentInDB.model_validate(db_agent)
        return None

    async def get_agents(self) -> List[AgentInDB]:
        """Retrieve all agents"""
        db_agents = self.db.query(AgentModel).all()
        return [AgentInDB.model_validate(agent) for agent in db_agents]
    
    async def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent by ID"""
        db_agent = self.db.query(AgentModel).filter(AgentModel.agent_id == agent_id).first()
        if db_agent:
            self.db.delete(db_agent)
            self.db.commit()
            return True
        return False

    async def chat_with_agent(self, agent_id: str, message: str, thread_id: Optional[str] = None) -> str:
        """Chat with an agent"""
        try:
            # Use thread_id if provided (session-based), otherwise use agent_id (persistent)
            session_id = thread_id if thread_id else f"agent_{agent_id}"
            
            # Get agent config to check for PII filtering
            agent = await self.get_agent(agent_id)
            if not agent:
                raise ValueError("Agent not found")
            
            # Apply PII filtering to input if configured
            filtered_message = message
            if agent.pii_config:
                pii_middleware = create_pii_middleware_from_config(agent.pii_config)
                if pii_middleware:
                    filtered_message = pii_middleware.process_message(message, message_type="input")
            
            # Execute the agent and get response
            response = await self.execute_agent(agent_id, filtered_message, session_id=session_id)
            
            # Apply PII filtering to output if configured
            if agent.pii_config:
                pii_middleware = create_pii_middleware_from_config(agent.pii_config)
                if pii_middleware:
                    response = pii_middleware.process_message(response, message_type="output")
            
            # Store the interaction in mem0 memory if enabled
            # Store both user and assistant messages to preserve conversation context
            if self.memory_service.is_enabled():
                try:
                    # Get agent to access its LLM configuration
                    agent = await self.get_agent(agent_id)
                    if agent:
                        # Store both messages for full conversational context
                        # Mem0 is configured to extract user-specific facts
                        interaction = [
                            {"role": "user", "content": message},
                            {"role": "assistant", "content": response}
                        ]
                        self.memory_service.add_memory(
                            interaction, 
                            user_id=session_id, 
                            agent_id=agent_id,
                            llm_provider=agent.llm_provider,
                            llm_model=agent.llm_model
                        )
                except Exception as mem_error:
                    print(f"Error storing memory: {mem_error}")
            
            return response
        except Exception as e:
            # Log the error for debugging
            print(f"Error chatting with agent {agent_id}: {str(e)}")
            # Return a more user-friendly error message
            error_msg = str(e)
            # Check for specific API key errors from LLM providers
            if (("API key" in error_msg or "401" in error_msg) and 
                ("OpenAI" in error_msg or "Anthropic" in error_msg or "Groq" in error_msg or "api_key" in error_msg.lower())):
                return "Invalid API key. Please check your API key configuration."
            elif "403" in error_msg and ("OpenAI" in error_msg or "Anthropic" in error_msg or "Groq" in error_msg):
                return "Access forbidden. Please check your API key permissions."
            elif "429" in error_msg and ("OpenAI" in error_msg or "Anthropic" in error_msg or "Groq" in error_msg):
                return "Rate limit exceeded. Please try again later."
            else:
                return f"Error communicating with the agent: {error_msg}"
    
    async def execute_agent(self, agent_id: str, input_text: str, session_id: Optional[str] = None) -> str:
        """Execute an agent with the given input"""
        agent = await self.get_agent(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        # Apply PII filtering to input if configured
        filtered_input = input_text
        if agent.pii_config:
            pii_middleware = create_pii_middleware_from_config(agent.pii_config)
            if pii_middleware:
                filtered_input = pii_middleware.process_message(input_text, message_type="input")
        
        try:
            # Use session_id if provided (session-based), otherwise use agent_id (persistent)
            user_id = session_id if session_id else f"agent_{agent_id}"
            
            # Retrieve relevant memories from mem0 if enabled
            memory_context = ""
            if self.memory_service.is_enabled():
                try:
                    memories = self.memory_service.search_memory(
                        query=filtered_input,
                        user_id=user_id,
                        agent_id=agent_id,
                        top_k=5,  # Increased from 3 to 5 for more context
                        llm_provider=agent.llm_provider,
                        llm_model=agent.llm_model
                    )
                    
                    # Build memory context string
                    if memories:
                        memory_context = "\nRelevant information from previous conversations:\n"
                        for i, memory in enumerate(memories, 1):
                            memory_content = memory.get('memory', '') if isinstance(memory, dict) else str(memory)
                            memory_context += f"{i}. {memory_content}\n"
                        # Note: Memory context is from previous trusted conversations and should not be PII filtered
                except Exception as mem_error:
                    print(f"Error retrieving memory context: {mem_error}")
            
            # Retrieve knowledge base context with timeout
            knowledge_context = ""
            try:
                import asyncio
                from services.knowledge_base_service import KnowledgeBaseService
                kb_service = KnowledgeBaseService(self.db)
                # Add 10 second timeout for KB queries to prevent hanging
                knowledge_context = await asyncio.wait_for(
                    kb_service.query_agent_knowledge(agent_id, filtered_input, top_k=5),
                    timeout=10.0
                )
                # Note: Knowledge base content is trusted and should not be PII filtered
                if knowledge_context:
                    print(f"Retrieved KB context for agent {agent_id}: {len(knowledge_context)} chars")
            except asyncio.TimeoutError:
                print(f"Knowledge base query timed out for agent {agent_id}")
            except Exception as kb_error:
                print(f"Error retrieving knowledge base context: {kb_error}")
                import traceback
                traceback.print_exc()
            
            # Create the LangGraph agent based on configuration with memory context
            langgraph_agent = self._create_langgraph_agent(agent, memory_context)
            
            # Prepare messages with context from mem0 memory if enabled
            messages = [HumanMessage(content=filtered_input)]
            
            # For ReAct agents, we'll add memory context to the system prompt
            # For other agents, we'll handle it in their specific implementations
            if agent.agent_type == "react":
                # Add memory context to system prompt for ReAct agents
                system_content = agent.system_prompt or "You are a helpful AI assistant."
                
                # Add available tools information to prevent tool hallucination
                if hasattr(agent, 'tools') and agent.tools:
                    tool_names = agent.tools
                    if tool_names:
                        system_content += f"\n\nAvailable tools: {', '.join(tool_names)}. You can only use these tools. Do not attempt to use any other tools."
                
                if knowledge_context:
                    system_content += f"\n\n{knowledge_context}"
                if memory_context:
                    system_content += f"\n\n{memory_context}"
                # Enforce concise response style
                system_content += "\n\nGuidelines: Keep responses concise (<=120 words). Use at most 5 bullet points. Ask at most one clarifying question only if necessary. Avoid long introductions."
                messages.insert(0, SystemMessage(content=system_content))
            
            # Execute the agent with the appropriate input format based on agent type
            # Add timeout to prevent hanging on slow LLM responses
            import asyncio
            try:
                if agent.agent_type == "react":
                    # ReAct agents expect messages format
                    response = await asyncio.wait_for(
                        asyncio.to_thread(langgraph_agent.invoke, {"messages": messages}),
                        timeout=90.0  # 90 second timeout for LLM calls (increased for FireCrawl)
                    )
                else:
                    # Other agents (plan-execute, reflection, custom) expect input format
                    # For these, we'll add the memory context to the input
                    enhanced_input = filtered_input
                    if knowledge_context or memory_context:
                        context_parts = []
                        if knowledge_context:
                            context_parts.append(knowledge_context)
                        if memory_context:
                            context_parts.append(memory_context)
                        enhanced_input = f"{filtered_input}\n\nContext:\n" + "\n\n".join(context_parts)
                    
                    response = await asyncio.wait_for(
                        asyncio.to_thread(langgraph_agent.invoke, {"input": enhanced_input}),
                        timeout=90.0
                    )
            except asyncio.TimeoutError:
                raise ValueError("Agent response timed out. The LLM provider may be slow or unreachable. Please try again.")
            except Exception as e:
                # Handle API errors more gracefully
                error_msg = str(e)
                print(f"Error executing agent {agent_id}: {error_msg}")
                
                # Check for specific API key errors from LLM providers
                if (("API key" in error_msg or "401" in error_msg) and 
                    ("OpenAI" in error_msg or "Anthropic" in error_msg or "Groq" in error_msg or "api_key" in error_msg.lower())):
                    raise ValueError("Invalid API key. Please check your API key configuration.")
                elif "403" in error_msg and ("OpenAI" in error_msg or "Anthropic" in error_msg or "Groq" in error_msg):
                    raise ValueError("Access forbidden. Please check your API key permissions.")
                elif "429" in error_msg and ("OpenAI" in error_msg or "Anthropic" in error_msg or "Groq" in error_msg):
                    raise ValueError("Rate limit exceeded. Please try again later.")
                elif "tool_use_failed" in error_msg or "Failed to call a function" in error_msg:
                    # Handle tool execution failures more gracefully
                    raise ValueError("Tool execution failed. This may be due to rate limiting, network issues, or missing API keys. Please try again or check your tool configuration.")
                else:
                    # For non-API key errors, re-raise the original exception
                    raise e
            
            # Extract the final response
            # Handle different response formats
            if isinstance(response, dict):
                if "messages" in response and len(response["messages"]) > 0:
                    # Standard format with messages key
                    final_message = response["messages"][-1]
                elif "agent_result" in response:
                    # Custom agent result
                    final_message = response["agent_result"]
                elif "agent_revision" in response:
                    # Reflection agent result
                    final_message = response["agent_revision"]
                elif "response" in response:
                    # Plan-execute agent result
                    final_message = response["response"]
                else:
                    # Direct response in dict
                    final_message = response
            else:
                # Direct response object
                final_message = response
                
            # Return the content if available, otherwise convert to string
            try:
                if hasattr(final_message, 'content') and final_message.content is not None:
                    return str(final_message.content)
                elif isinstance(final_message, dict):
                    # If it's a dict, try to get content or convert to string
                    return str(final_message.get('content', str(final_message)))
                else:
                    return str(final_message)
            except Exception as e:
                # Fallback to string representation
                return str(final_message)
        except Exception as e:
            # Handle any unexpected errors in the chat_with_agent method
            print(f"Unexpected error in chat_with_agent for agent {agent_id}: {e}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"An unexpected error occurred while processing your request: {str(e)}")
    
    async def stream_agent(self, websocket, agent_id: str):
        """Stream agent responses via WebSocket"""
        agent = await self.get_agent(agent_id)
        if not agent:
            await websocket.send_text(json.dumps({"error": "Agent not found"}))
            await websocket.close()
            return
        
        # For streaming, we would implement a callback mechanism
        # This is a simplified version - in practice, you'd need to handle
        # the streaming properly with LangGraph's streaming capabilities
        await websocket.send_text(json.dumps({"status": "Streaming not fully implemented in this example"}))
        await websocket.close()
    
    def _create_langgraph_agent(self, agent_config: AgentInDB, memory_context: str = ""):
        """Create a LangGraph agent based on the configuration"""
        # Decrypt the user API key if available
        user_api_key = None
        if hasattr(agent_config, 'api_key_encrypted') and agent_config.api_key_encrypted:
            try:
                user_api_key = self._decrypt_api_key(agent_config.api_key_encrypted)
            except Exception as e:
                print(f"Warning: Could not decrypt API key for agent {agent_config.agent_id}: {e}")
        
        # Initialize the LLM based on provider and user API key
        llm = self._initialize_llm(
            agent_config.llm_provider,
            agent_config.llm_model,
            agent_config.temperature,
            user_api_key
        )
        
        # Create the agent graph based on type
        if agent_config.agent_type == "react":
            return self._create_react_agent(llm, agent_config)
        elif agent_config.agent_type == "plan-execute":
            return self._create_plan_execute_agent(llm, agent_config, memory_context)
        elif agent_config.agent_type == "reflection":
            return self._create_reflection_agent(llm, agent_config, memory_context)
        else:  # custom
            return self._create_custom_agent(llm, agent_config, memory_context)
    
    def _initialize_llm(self, provider: str, model: str, temperature: float, user_api_key: Optional[str] = None):
        """Initialize the LLM based on provider and user API key"""
        # Use user-provided API key if available, otherwise fall back to system keys
        openai_api_key = user_api_key or settings.OPENAI_API_KEY
        anthropic_api_key = user_api_key or settings.ANTHROPIC_API_KEY
        groq_api_key = user_api_key or settings.GROQ_API_KEY
        
        # Check if API keys are available
        openai_key_available = bool(openai_api_key and openai_api_key.strip())
        anthropic_key_available = bool(anthropic_api_key and anthropic_api_key.strip())
        groq_key_available = bool(groq_api_key and groq_api_key.strip())
        
        if provider == "openai" and openai_key_available:
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=openai_api_key,
                max_tokens=300
            )
        elif provider == "anthropic" and anthropic_key_available:
            return ChatAnthropic(
                model=model,
                temperature=temperature,
                anthropic_api_key=anthropic_api_key,
                max_tokens=300
            )
        elif provider == "groq" and groq_key_available:
            return ChatGroq(
                model=model,
                temperature=temperature,
                groq_api_key=groq_api_key,
                max_tokens=300
            )
        # Add other providers as needed
        elif openai_key_available:
            # Default to OpenAI if provider not recognized but key is available
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=openai_api_key,
                max_tokens=300
            )
        else:
            # Return a mock LLM that provides informative responses when no API key is available
            # Note: FakeListLLM doesn't support tools, so we need to handle this case specially
            return FakeListLLM(responses=[
                f"I'm a {model} agent simulation. In a real deployment, I would connect to the {provider} API to generate responses.",
                f"This is a simulated response from a {model} model. Please configure your {provider} API key to get real responses.",
                f"Mock response from {provider} {model} model. Add your API key to .env file to enable real functionality."
            ])
    
    def _create_react_agent(self, llm, agent_config):
        """Create a generic ReAct agent with adaptable tools"""
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        
        # Check if the LLM supports tools (bind_tools method)
        # FakeListLLM doesn't support tools, so we need to handle this case
        if hasattr(llm, 'bind_tools'):
            # Start with empty tools list - all tools come from external services
            tools = []
            
            # Add external tools if configured
            if hasattr(agent_config, 'tools') and agent_config.tools:
                try:
                    # Get tool configurations if available
                    tool_configs = {}
                    if hasattr(agent_config, 'tool_configs') and agent_config.tool_configs:
                        tool_configs = agent_config.tool_configs
                    
                    print(f"DEBUG: Agent tools requested: {agent_config.tools}")
                    print(f"DEBUG: Agent tool_configs: {tool_configs}")
                    
                    # Handle MCP tools separately since they need async initialization
                    mcp_tools = []
                    other_tools = []
                    
                    for tool_name in agent_config.tools:
                        if tool_name == "mcp_database" and tool_configs.get("mcp_database"):
                            # MCP tools need async handling - they'll be added later
                            pass
                        else:
                            other_tools.append(tool_name)
                    
                    print(f"DEBUG: Non-MCP tools to load: {other_tools}")
                    
                    # Get non-MCP external tools first
                    if other_tools:
                        external_tools = self.tools_service.get_tools(other_tools, tool_configs)
                        tools.extend(external_tools)
                        print(f"DEBUG: External tools loaded: {[t.name for t in external_tools]}")
                    
                    print(f"Loaded {len(tools)} external tools: {[t.name for t in tools]}")
                except Exception as e:
                    print(f"Error loading external tools: {e}")
            
            # Ensure at least one tool is available - add a basic fallback if no tools configured
            if not tools:
                # Define a basic web search tool as fallback if no external tools configured
                @tool
                def web_search(query: str) -> str:
                    """Search the web for information.
                    
                    Args:
                        query: Search query
                        
                    Returns:
                        Summary of search results
                    """
                    # This is a placeholder - in a real implementation, you would connect to a search API
                    search_prompt = PromptTemplate.from_template("""You are a search engine simulator. 
                    Provide a relevant response for the search query: {query}""")
                    
                    chain = search_prompt | llm | StrOutputParser()
                    try:
                        result = chain.invoke({"query": query})
                        return result
                    except Exception as e:
                        return f"Search results for '{query}': [Simulated results would appear here]"
                
                tools.append(web_search)
            
            # Create the ReAct agent with the LLM and tools
            react_agent = create_react_agent(llm, tools)
            # Return the already compiled agent
            return react_agent
        else:
            # For LLMs that don't support tools (like FakeListLLM), create a simple chat agent
            from langgraph.graph import StateGraph, START
            from typing import Annotated
            from typing_extensions import TypedDict
            from operator import add
            from langchain_core.messages import HumanMessage, AIMessage
            
            class MessagesState(TypedDict):
                messages: Annotated[list, add]
            
            def call_model(state: MessagesState):
                # For mock LLMs, just return a response
                # Get the last message content
                last_message = state["messages"][-1] if state["messages"] else ""
                content = getattr(last_message, 'content', str(last_message))
                
                # Get a response from the mock LLM
                response = llm.invoke(content)
                return {"messages": [AIMessage(content=response)]}
            
            # Create a simple state graph for mock LLMs
            workflow = StateGraph(MessagesState)
            workflow.add_node("call_model", call_model)
            workflow.add_edge(START, "call_model")
            workflow.add_edge("call_model", END)
            
            # Compile without checkpointer
            return workflow.compile()
    
    def _create_plan_execute_agent(self, llm, agent_config, memory_context: str = ""):
        """Create a generic Plan & Execute agent for complex multi-step tasks"""
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        
        # Define state for the agent
        from typing import Annotated, Sequence, TypedDict
        from langgraph.graph import add_messages
        
        class PlanExecuteState(TypedDict):
            input: str
            agent_plan: str
            past_steps: Annotated[Sequence[str], add_messages]
            response: str
        
        # Planner node - creates a plan
        def planner_node(state: PlanExecuteState):
            """Create a plan for executing the user request"""
            system_prompt = agent_config.system_prompt or "You are an expert at creating plans for complex tasks."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            planner_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
For the user request, create a SHORT plan of up to 5 steps. Each step must be a single actionable line. Be concise.

User Request: {{input}}

Plan:""")
            
            chain = planner_prompt | llm | StrOutputParser()
            plan = chain.invoke({"input": state["input"]})
            return {"agent_plan": plan}
        
        # Executor node - executes the plan
        def executor_node(state: PlanExecuteState):
            """Execute the plan steps"""
            system_prompt = agent_config.system_prompt or "You are an expert at executing plans."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            executor_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Here is the plan to execute (concise execution, <=100 words):
{{agent_plan}}

Execute the next step and return a brief result.

Previous steps: {{past_steps}}

Next step result:""")
            
            chain = executor_prompt | llm | StrOutputParser()
            result = chain.invoke({
                "agent_plan": state["agent_plan"],
                "past_steps": "\n".join(state["past_steps"]) if state["past_steps"] else "None"
            })
            
            return {"past_steps": [result]}
        
        # Create the workflow
        workflow = StateGraph(PlanExecuteState)
        
        # Add nodes
        workflow.add_node("planner", planner_node)
        workflow.add_node("executor", executor_node)
        
        # Add edges
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "executor")
        workflow.add_edge("executor", END)
        
        # Compile without checkpointer
        return workflow.compile()
    
    def _create_reflection_agent(self, llm, agent_config, memory_context: str = ""):
        """Create a generic Reflection agent that improves its responses through self-evaluation"""
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from typing import Annotated, Sequence, TypedDict
        from langgraph.graph import add_messages
        
        class ReflectionState(TypedDict):
            input: str
            agent_draft: str
            agent_critique: str
            agent_revision: str
        
        # Agent node - generates initial response
        def agent_node(state: ReflectionState):
            """Generate initial response"""
            system_prompt = agent_config.system_prompt or "You are a helpful AI assistant."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            agent_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Provide a concise response to the user request (<=120 words, up to 5 bullets if needed).

User Request: {{input}}

Response:""")
            
            chain = agent_prompt | llm | StrOutputParser()
            draft = chain.invoke({"input": state["input"]})
            return {"agent_draft": draft}
        
        # Critique node - evaluates the response
        def critique_node(state: ReflectionState):
            """Critique the initial response"""
            system_prompt = agent_config.system_prompt or "You are an expert reviewer."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            critique_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Review the following response for quality, accuracy, and unnecessary verbosity. Suggest how to make it shorter while preserving key information.

Response: {{agent_draft}}

User Request: {{input}}

Critique:""")
            
            chain = critique_prompt | llm | StrOutputParser()
            critique = chain.invoke({"agent_draft": state["agent_draft"], "input": state["input"]})
            return {"agent_critique": critique}
        
        # Revision node - improves based on critique
        def revision_node(state: ReflectionState):
            """Revise the response based on critique"""
            system_prompt = agent_config.system_prompt or "You are an expert editor."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            revision_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Improve the response based on the critique. Make it concise (<=120 words) and to the point.

Original Response: {{agent_draft}}

Critique: {{agent_critique}}

User Request: {{input}}

Improved Response:""")
            
            chain = revision_prompt | llm | StrOutputParser()
            revision = chain.invoke({
                "agent_draft": state["agent_draft"], 
                "agent_critique": state["agent_critique"],
                "input": state["input"]
            })
            return {"agent_revision": revision}
        
        # Create the workflow
        workflow = StateGraph(ReflectionState)
        
        # Add nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("critique", critique_node)
        workflow.add_node("revision", revision_node)
        
        # Add edges
        workflow.set_entry_point("agent")
        workflow.add_edge("agent", "critique")
        workflow.add_edge("critique", "revision")
        workflow.add_edge("revision", END)
        
        # Compile without checkpointer
        return workflow.compile()
    
    def _create_custom_agent(self, llm, agent_config, memory_context: str = ""):
        """Create a flexible custom agent graph for specialized workflows"""
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from typing import Annotated, Sequence, TypedDict
        from langgraph.graph import add_messages
        
        class CustomAgentState(TypedDict):
            input: str
            agent_analysis: str
            agent_action: str
            agent_result: str
        
        # Analysis node - analyzes the request
        def analysis_node(state: CustomAgentState):
            """Analyze the user request and determine the approach"""
            system_prompt = agent_config.system_prompt or "You are a helpful assistant."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            analysis_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
You are an expert problem analyzer. Provide a brief analysis (3-5 bullet points max).

User Request: {{input}}

Analysis:""")
            
            chain = analysis_prompt | llm | StrOutputParser()
            analysis = chain.invoke({"input": state["input"]})
            return {"agent_analysis": analysis}
        
        # Action node - takes action based on analysis
        def action_node(state: CustomAgentState):
            """Take action based on analysis"""
            system_prompt = agent_config.system_prompt or "You are a helpful assistant."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            action_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
You are an expert problem solver. Based on the analysis, determine the best action. Keep it brief (<=80 words).

Analysis: {{agent_analysis}}

User Request: {{input}}

Action:""")
            
            chain = action_prompt | llm | StrOutputParser()
            action = chain.invoke({"agent_analysis": state["agent_analysis"], "input": state["input"]})
            return {"agent_action": action}
        
        # Result formatter node - formats the result
        def result_node(state: CustomAgentState):
            """Format the final result"""
            system_prompt = agent_config.system_prompt or "You are a helpful assistant."
            if memory_context:
                system_prompt += f"\n\n{memory_context}"
                
            result_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Provide a clear, concise response to the user's request based on the action taken (<=120 words, up to 5 bullets).

Action Taken: {{agent_action}}

User Request: {{input}}

Final Response:""")
            
            chain = result_prompt | llm | StrOutputParser()
            result = chain.invoke({
                "agent_action": state["agent_action"], 
                "input": state["input"]
            })
            return {"agent_result": result}
        
        # Create the workflow
        workflow = StateGraph(CustomAgentState)
        
        # Add nodes
        workflow.add_node("analysis", analysis_node)
        workflow.add_node("action", action_node)
        workflow.add_node("result", result_node)
        
        # Add edges
        workflow.set_entry_point("analysis")
        workflow.add_edge("analysis", "action")
        workflow.add_edge("action", "result")
        workflow.add_edge("result", END)
        
        # Compile without checkpointer
        return workflow.compile()