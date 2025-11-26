from typing import Dict, Any, List, Optional
from langchain_core.tools import Tool
from langchain_core.utils.function_calling import convert_to_openai_tool

def adapt_mcp_to_langchain(mcp_tool: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert an MCP tool definition to a LangChain/OpenAI tool definition.
    
    IMPORTANT: Only includes REQUIRED properties in the schema to prevent
    LLM providers (especially Groq) from passing null for optional parameters,
    which causes validation errors.
    
    MCP Tool format:
    {
        "name": "tool_name",
        "description": "tool description",
        "inputSchema": {
            "type": "object",
            "properties": { ... },
            "required": [...]
        }
    }
    
    Target OpenAI format:
    {
        "type": "function",
        "function": {
            "name": "tool_name",
            "description": "tool description",
            "parameters": { ... }  # filtered inputSchema (required only)
        }
    }
    """
    name = mcp_tool.get("name")
    description = mcp_tool.get("description", "")
    input_schema = mcp_tool.get("inputSchema", {})
    
    # Ensure input_schema is a valid JSON schema object
    if not input_schema:
        input_schema = {"type": "object", "properties": {}}
    
    # Extract required fields and all properties
    required = input_schema.get("required", [])
    all_properties = input_schema.get("properties", {})
    
    # Filter to only include required properties
    # This prevents LLMs from passing null for optional params, which causes validation errors
    filtered_properties = {
        k: v for k, v in all_properties.items() 
        if k in required
    }
    
    # Build filtered schema with only required properties
    filtered_schema = {
        "type": input_schema.get("type", "object"),
        "properties": filtered_properties,
        "required": required
    }
    
    # Include additionalProperties if present
    if "additionalProperties" in input_schema:
        filtered_schema["additionalProperties"] = input_schema["additionalProperties"]
        
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": filtered_schema
        }
    }
