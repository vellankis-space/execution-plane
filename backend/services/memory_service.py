import os
import logging
from typing import List, Dict, Any, Optional
from core.config import settings
from dotenv import load_dotenv

try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
except Exception:
    MEM0_AVAILABLE = False
    Memory = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryService:
    # Class-level cache shared across all instances
    _memory_cache: Dict[str, Any] = {}
    
    def __init__(self):
        # Shared configuration
        self.collection_name = "agent_memories"
        self.embedding_model = "qwen3-embedding:0.6b"
        self.embedding_dim = 1024  # qwen3-embedding:0.6b has 1024 dimensions
        
        # Check if Mem0 is available
        if not MEM0_AVAILABLE:
            logger.error("mem0ai package not available")
        
        load_dotenv()
    
    def _get_api_key(self, llm_provider: str, api_key: Optional[str] = None) -> Optional[str]:
        """Get API key for the specified provider"""
        if api_key:
            return api_key
        
        # Map provider to settings attribute
        provider_key_map = {
            "groq": "GROQ_API_KEY",
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
        }
        
        key_name = provider_key_map.get(llm_provider.lower())
        if key_name:
            return getattr(settings, key_name, None) or os.getenv(key_name, "")
        return None
    
    def _get_memory_instance(self, llm_provider: str, llm_model: str, api_key: Optional[str] = None) -> Optional[Any]:
        """Get or create a cached Memory instance for the specified LLM configuration"""
        if not MEM0_AVAILABLE:
            return None
        
        # Create cache key
        cache_key = f"{llm_provider}:{llm_model}"
        
        # Return cached instance if available (class-level cache)
        if cache_key in MemoryService._memory_cache:
            return MemoryService._memory_cache[cache_key]
        
        try:
            # Get API key
            resolved_api_key = self._get_api_key(llm_provider, api_key)
            if not resolved_api_key:
                logger.debug(f"No API key found for provider {llm_provider}, memory features disabled")
                return None
            
            # Configure Mem0 with agent's LLM and custom extraction prompt
            config = {
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "collection_name": self.collection_name,
                        "path": "/tmp/qdrant",
                        "embedding_model_dims": self.embedding_dim,
                    }
                },
                "embedder": {
                    "provider": "ollama",
                    "config": {
                        "model": self.embedding_model,
                        "ollama_base_url": "http://localhost:11434",
                    }
                },
                "llm": {
                    "provider": llm_provider.lower(),
                    "config": {
                        "model": llm_model,
                        "temperature": 0.1,
                        "max_tokens": 500,  # Reduced from 2000 to save tokens
                        "api_key": resolved_api_key,
                    }
                },
                "version": "v1.1"
            }
            
            memory = Memory.from_config(config)
            MemoryService._memory_cache[cache_key] = memory
            logger.info(f"Mem0 Memory instance created for {llm_provider}/{llm_model}")
            return memory
            
        except Exception as e:
            logger.error(f"Error creating Mem0 Memory instance for {llm_provider}/{llm_model}: {e}")
            return None
    
    def is_enabled(self) -> bool:
        """Check if memory service is enabled and properly configured"""
        return MEM0_AVAILABLE
    
    def add_memory(
        self, 
        messages: List[Dict[str, str]], 
        user_id: str, 
        agent_id: Optional[str] = None,
        llm_provider: str = "groq",
        llm_model: str = "llama-3.1-8b-instant",
        api_key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Add a memory using Mem0 with the agent's LLM configuration
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            user_id: User identifier
            agent_id: Optional agent identifier
            llm_provider: LLM provider to use for memory extraction (groq, openai, anthropic)
            llm_model: LLM model to use for memory extraction
            api_key: Optional API key override
            
        Returns:
            Dictionary with memory addition results or None if service is disabled
        """
        if not self.is_enabled():
            logger.debug("Memory service not enabled, skipping add_memory")
            return None
        
        # Get memory instance for this agent's LLM config
        memory = self._get_memory_instance(llm_provider, llm_model, api_key)
        if not memory:
            logger.debug(f"Could not get memory instance for {llm_provider}/{llm_model}, skipping memory storage")
            return None
            
        try:
            logger.debug(f"Adding memory for user_id: {user_id}, agent_id: {agent_id} using {llm_provider}/{llm_model}")
            
            # Add metadata if agent_id is provided
            metadata = {"agent_id": agent_id} if agent_id else None
            
            # Prepend a system instruction to guide extraction toward user facts
            # This helps Mem0's LLM focus on user information even with assistant messages present
            guided_messages = [
                {
                    "role": "system", 
                    "content": """You are extracting factual information about the USER ONLY.

Extract ONLY these types of facts:
- User's name, location, age, or personal details they share
- User's preferences (favorite things, likes/dislikes)
- User's dietary restrictions or allergies
- User's requirements, goals, or what they are asking for
- User's constraints (budget, time, equipment)
- Context from what the user explicitly states

DO NOT extract:
- What the assistant can do or offers
- The assistant's suggestions or capabilities  
- Generic conversational phrases
- Facts starting with "Can...", "Able to...", "Provides..."

Focus on statements of the form "User prefers X", "User is allergic to Y", "User wants Z"."""
                }
            ] + messages
            
            # Use Mem0's add method with guided messages
            result = memory.add(guided_messages, user_id=user_id, metadata=metadata)
            logger.info(f"Memory added successfully for user_id: {user_id}")
            return result
            
        except Exception as e:
            # Check for rate limit errors
            if "429" in str(e) or "rate_limit" in str(e).lower():
                logger.warning(f"Rate limit hit for {llm_provider}/{llm_model}, skipping memory extraction")
            else:
                logger.error(f"Error adding memory for user_id {user_id}: {e}")
            return None
    
    def search_memory(
        self, 
        query: str, 
        user_id: str, 
        agent_id: Optional[str] = None, 
        top_k: int = 5,
        llm_provider: str = "groq",
        llm_model: str = "llama-3.1-8b-instant"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Search for memories using Mem0
        
        Args:
            query: Search query
            user_id: User identifier
            agent_id: Optional agent identifier to filter results
            top_k: Number of results to return
            
        Returns:
            List of memory results or None if service is disabled
        """
        if not self.is_enabled():
            logger.debug("Memory service not enabled, skipping search_memory")
            return None
        
        # Get memory instance for this agent's LLM config
        memory = self._get_memory_instance(llm_provider, llm_model)
        if not memory:
            logger.debug(f"Could not get memory instance for search, memory features disabled")
            return None
            
        try:
            logger.debug(f"Searching memory for user_id: {user_id}, agent_id: {agent_id}, query: {query}")
            
            # Build filters
            filters = {}
            if agent_id:
                filters["agent_id"] = agent_id
            
            # Use Mem0's search method
            results = memory.search(query, user_id=user_id, limit=top_k, filters=filters if filters else None)
            
            # Normalize results to match expected format
            formatted_results = []
            if isinstance(results, dict) and "results" in results:
                items = results["results"]
            else:
                items = results if isinstance(results, list) else []
            
            for item in items:
                if isinstance(item, dict):
                    formatted_results.append({
                        "id": item.get("id"),
                        "score": item.get("score"),
                        "memory": item.get("memory", ""),
                        "messages": item.get("messages", []),
                        "metadata": item
                    })
            
            logger.info(f"Found {len(formatted_results)} memories for user_id: {user_id}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching memory for user_id {user_id}: {e}")
            return None
    
    def get_user_memories(
        self, 
        user_id: str, 
        agent_id: Optional[str] = None,
        llm_provider: str = "groq",
        llm_model: str = "llama-3.1-8b-instant"
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get all memories for a user using Mem0
        
        Args:
            user_id: User identifier
            agent_id: Optional agent identifier to filter results
            llm_provider: LLM provider (for getting memory instance)
            llm_model: LLM model (for getting memory instance)
            
        Returns:
            List of user memories or None if service is disabled
        """
        if not self.is_enabled():
            logger.debug("Memory service not enabled, skipping get_user_memories")
            return None
        
        # Get memory instance (use default or specified config)
        memory = self._get_memory_instance(llm_provider, llm_model)
        if not memory:
            logger.warning("Could not get memory instance for retrieving user memories")
            return None
            
        try:
            logger.debug(f"Retrieving all memories for user_id: {user_id}, agent_id: {agent_id}")
            
            # Build filters
            filters = {}
            if agent_id:
                filters["agent_id"] = agent_id
            
            # Use Mem0's get_all method
            results = memory.get_all(user_id=user_id, filters=filters if filters else None)
            
            # Normalize results
            formatted_results = []
            if isinstance(results, dict) and "results" in results:
                items = results["results"]
            else:
                items = results if isinstance(results, list) else []
            
            for item in items:
                if isinstance(item, dict):
                    formatted_results.append({
                        "id": item.get("id"),
                        "memory": item.get("memory", ""),
                        "messages": item.get("messages", []),
                        "metadata": item
                    })
            
            logger.info(f"Retrieved {len(formatted_results)} memories for user_id: {user_id}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error retrieving user memories for user_id {user_id}: {e}")
            return None
    
    def delete_session_memories(
        self, 
        session_id: str,
        llm_provider: str = "groq",
        llm_model: str = "llama-3.1-8b-instant"
    ) -> bool:
        """
        Delete all memories for a session (for cleanup on refresh/end)
        
        Args:
            session_id: Session identifier (thread_id)
            llm_provider: LLM provider (for getting memory instance)
            llm_model: LLM model (for getting memory instance)
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not self.is_enabled():
            logger.debug("Memory service not enabled, skipping delete_session_memories")
            return False
        
        # Get memory instance
        memory = self._get_memory_instance(llm_provider, llm_model)
        if not memory:
            logger.debug("Could not get memory instance for deleting session memories, skipping")
            return False
            
        try:
            logger.info(f"Deleting all memories for session_id: {session_id}")
            
            # Get all memories for this session
            memories = self.get_user_memories(user_id=session_id, llm_provider=llm_provider, llm_model=llm_model)
            
            if not memories:
                logger.debug(f"No memories found for session_id: {session_id}")
                return True
            
            # Delete each memory by ID
            deleted_count = 0
            for mem in memories:
                memory_id = mem.get("id")
                if memory_id:
                    try:
                        memory.delete(memory_id=memory_id)
                        deleted_count += 1
                    except Exception as e:
                        logger.error(f"Error deleting memory {memory_id}: {e}")
            
            logger.info(f"Deleted {deleted_count} memories for session_id: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting session memories for session_id {session_id}: {e}")
            return False