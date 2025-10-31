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

from models.agent import Agent as AgentModel
from schemas.agent import AgentCreate, AgentInDB
from core.config import settings


class AgentService:
    def __init__(self, db: Session):
        self.db = db
        # Generate encryption key from settings or create a default one
        # In production, this should be stored securely
        self._encryption_key = self._get_or_create_encryption_key()
    
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
            max_iterations=agent_data.max_iterations,
            memory_type=agent_data.memory_type,
            streaming_enabled=agent_data.streaming_enabled,
            human_in_loop=agent_data.human_in_loop,
            recursion_limit=agent_data.recursion_limit,
            api_key_encrypted=encrypted_api_key
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

    async def chat_with_agent(self, agent_id: str, message: str) -> str:
        """Chat with an agent"""
        try:
            return await self.execute_agent(agent_id, message)
        except Exception as e:
            # Log the error for debugging
            print(f"Error chatting with agent {agent_id}: {str(e)}")
            # Return a more user-friendly error message
            if "API key" in str(e):
                return "Invalid API key. Please check your API key configuration."
            elif "401" in str(e):
                return "Authentication failed. Please verify your API key."
            elif "403" in str(e):
                return "Access forbidden. Please check your API key permissions."
            else:
                return f"Error communicating with the agent: {str(e)}"
    
    async def execute_agent(self, agent_id: str, input_text: str) -> str:
        """Execute an agent with the given input"""
        agent = await self.get_agent(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        try:
            # Create the LangGraph agent based on configuration
            langgraph_agent = self._create_langgraph_agent(agent)
            
            # Execute the agent with the appropriate input format based on agent type
            if agent.agent_type == "react":
                # ReAct agents expect messages format
                response = langgraph_agent.invoke({"messages": [HumanMessage(content=input_text)]})
            else:
                # Other agents (plan-execute, reflection, custom) expect input format
                response = langgraph_agent.invoke({"input": input_text})
            
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
            except:
                # Fallback to string representation
                return str(final_message)
        except Exception as e:
            # Handle API errors more gracefully
            error_msg = str(e)
            print(f"Error executing agent {agent_id}: {error_msg}")
            
            # Check for common API errors
            if "API key" in error_msg or "401" in error_msg:
                raise ValueError("Invalid API key. Please check your API key configuration.")
            elif "403" in error_msg:
                raise ValueError("Access forbidden. Please check your API key permissions.")
            elif "429" in error_msg:
                raise ValueError("Rate limit exceeded. Please try again later.")
            else:
                raise ValueError(f"Error communicating with the agent: {error_msg}")
    
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
    
    def _create_langgraph_agent(self, agent_config: AgentInDB):
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
            return self._create_plan_execute_agent(llm, agent_config)
        elif agent_config.agent_type == "reflection":
            return self._create_reflection_agent(llm, agent_config)
        else:  # custom
            return self._create_custom_agent(llm, agent_config)
    
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
                api_key=openai_api_key
            )
        elif provider == "anthropic" and anthropic_key_available:
            return ChatAnthropic(
                model=model,
                temperature=temperature,
                anthropic_api_key=anthropic_api_key
            )
        elif provider == "groq" and groq_key_available:
            return ChatGroq(
                model=model,
                temperature=temperature,
                groq_api_key=groq_api_key
            )
        # Add other providers as needed
        elif openai_key_available:
            # Default to OpenAI if provider not recognized but key is available
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=openai_api_key
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
            # Define a web search tool
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
            
            # Define a calculation tool
            @tool
            def calculator(expression: str) -> str:
                """Perform mathematical calculations.
                
                Args:
                    expression: Mathematical expression to evaluate
                    
                Returns:
                    Result of the calculation
                """
                try:
                    # Simple evaluation - in practice, you'd want to be more careful about security
                    result = eval(expression)
                    return str(result)
                except Exception as e:
                    return f"Error calculating '{expression}': {str(e)}"
            
            # Define a general information tool
            @tool
            def get_general_info(topic: str) -> str:
                """Get general information about a topic.
                
                Args:
                    topic: Topic to get information about
                    
                Returns:
                    Information about the topic
                """
                info_prompt = PromptTemplate.from_template("""You are an encyclopedia. 
                Provide concise, accurate information about the following topic: {topic}""")
                
                chain = info_prompt | llm | StrOutputParser()
                try:
                    result = chain.invoke({"topic": topic})
                    return result
                except Exception as e:
                    return f"Information about '{topic}': [Information would appear here]"
            
            # Create the tools list
            tools = [web_search, calculator, get_general_info]
            
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
    
    def _create_plan_execute_agent(self, llm, agent_config):
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
            planner_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
For the user request, create a detailed plan with steps. Each step should be a single actionable item.

User Request: {{input}}

Plan:""")
            
            chain = planner_prompt | llm | StrOutputParser()
            plan = chain.invoke({"input": state["input"]})
            return {"agent_plan": plan}
        
        # Executor node - executes the plan
        def executor_node(state: PlanExecuteState):
            """Execute the plan steps"""
            system_prompt = agent_config.system_prompt or "You are an expert at executing plans."
            executor_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Here is the plan to execute:
{{agent_plan}}

Execute the next step and return the result.

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
    
    def _create_reflection_agent(self, llm, agent_config):
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
            agent_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Provide a response to the user request.

User Request: {{input}}

Response:""")
            
            chain = agent_prompt | llm | StrOutputParser()
            draft = chain.invoke({"input": state["input"]})
            return {"agent_draft": draft}
        
        # Critique node - evaluates the response
        def critique_node(state: ReflectionState):
            """Critique the initial response"""
            system_prompt = agent_config.system_prompt or "You are an expert reviewer."
            critique_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Review the following response for quality, accuracy, and completeness. Point out any issues or improvements.

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
            revision_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Improve the response based on the critique.

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
    
    def _create_custom_agent(self, llm, agent_config):
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
            analysis_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
You are an expert problem analyzer. Analyze the following user request and determine the best approach to address it.

User Request: {{input}}

Analysis:""")
            
            chain = analysis_prompt | llm | StrOutputParser()
            analysis = chain.invoke({"input": state["input"]})
            return {"agent_analysis": analysis}
        
        # Action node - takes action based on analysis
        def action_node(state: CustomAgentState):
            """Take action based on analysis"""
            system_prompt = agent_config.system_prompt or "You are a helpful assistant."
            action_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
You are an expert problem solver. Based on the analysis, determine the best action to take to address the user request.

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
            result_prompt = PromptTemplate.from_template(f"""{system_prompt}
            
Provide a clear, comprehensive response to the user's request based on the action taken.

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