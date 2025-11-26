import json
import logging
import asyncio
from typing import List, Dict, Any, Union
from langchain_core.messages import ToolMessage, AIMessage
from langchain_core.tools import Tool

logger = logging.getLogger(__name__)

class ToolExecutor:
    """Executes tools requested by the LLM."""
    
    def __init__(self, external_tools: List[Tool] = None, tool_call_delay: float = 0.5):
        """
        Initialize ToolExecutor.
        
        Args:
            external_tools: List of LangChain tools
            tool_call_delay: Delay in seconds between tool calls to prevent rate limiting (default: 0.5s)
        """
        self.external_tools = {t.name: t for t in external_tools} if external_tools else {}
        self.tool_call_delay = tool_call_delay

    async def execute_tools(self, tool_calls: List[Dict[str, Any]]) -> List[ToolMessage]:
        """
        Execute a list of tool calls with rate limiting protection.
        
        Args:
            tool_calls: List of tool call dicts from the LLM message.
                        [{'name': '...', 'args': {...}, 'id': '...'}]
        
        Returns:
            List of ToolMessages containing the results.
        """
        # Lazy import to avoid circular dependency
        from services.fastmcp_manager import fastmcp_manager
        
        results = []
        
        for i, tool_call in enumerate(tool_calls):
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]
            
            try:
                content = ""
                # Check if it's an external LangChain tool
                if tool_name in self.external_tools:
                    logger.info(f"Executing external tool {tool_name}")
                    tool = self.external_tools[tool_name]
                    # Handle async invocation
                    if hasattr(tool, 'ainvoke'):
                        result = await tool.ainvoke(tool_args)
                    else:
                        result = tool.invoke(tool_args)
                    content = str(result)
                else:
                    # Check if it's an MCP tool
                    # ... (existing MCP logic)
                
                    # Search in cached tools to find which server this tool belongs to
                    # This is a bit inefficient but safe. 
                    # Ideally, we should pass the tool mapping to the executor.
                    server_id = None
                    original_tool_name = tool_name
                    
                    for sid, tools in fastmcp_manager.cached_tools.items():
                        # Check for direct match or prefixed match
                        for t in tools:
                            if t["name"] == tool_name:
                                server_id = sid
                                original_tool_name = t["name"]
                                break
                            if f"{sid}_{t['name']}" == tool_name:
                                server_id = sid
                                original_tool_name = t["name"]
                                break
                        if server_id:
                            break
                    
                    if server_id:
                        logger.info(f"Executing MCP tool {original_tool_name} on server {server_id}")
                        result = await fastmcp_manager.call_tool(server_id, original_tool_name, tool_args)
                        
                        # Handle MCP content types
                        if isinstance(result, list):
                            # Extract text from TextContent objects
                            content_parts = []
                            for item in result:
                                if hasattr(item, 'text'):
                                    content_parts.append(item.text)
                                elif isinstance(item, dict) and 'text' in item:
                                    content_parts.append(item['text'])
                                else:
                                    content_parts.append(str(item))
                            content = "\n".join(content_parts)
                        elif hasattr(result, 'content') and isinstance(result.content, list):
                             # Handle CallToolResult object
                            content_parts = []
                            for item in result.content:
                                if hasattr(item, 'text'):
                                    content_parts.append(item.text)
                                elif isinstance(item, dict) and 'text' in item:
                                    content_parts.append(item['text'])
                                else:
                                    content_parts.append(str(item))
                            content = "\n".join(content_parts)
                        else:
                            content = str(result)
                        
                        if not content or content == "None":
                            content = "Tool executed successfully."
                    else:
                        # Fallback for non-MCP tools (if any)
                        content = f"Error: Tool {tool_name} not found or not associated with an active MCP server."
                        logger.error(content)

            except Exception as e:
                content = f"Error executing tool {tool_name}: {str(e)}"
                logger.error(content)
            
            results.append(ToolMessage(content=content, tool_call_id=tool_call_id, name=tool_name))
            
            # Add delay between tool calls to prevent rate limiting (except for the last call)
            if i < len(tool_calls) - 1 and self.tool_call_delay > 0:
                logger.debug(f"Cooldown delay: {self.tool_call_delay}s before next tool call")
                await asyncio.sleep(self.tool_call_delay)
            
        return results
