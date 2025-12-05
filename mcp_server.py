#!/usr/bin/env python3
"""
Simple MCP Server Implementation
This server provides a calculator tool as an example.
"""

import json
import sys
from typing import Any, Dict

# MCP Protocol constants
PROTOCOL_VERSION = "2024-06-12"

def send_message(message: Dict[str, Any]) -> None:
    """Send a message to stdout"""
    print(json.dumps(message))
    sys.stdout.flush()

def handle_initialize() -> None:
    """Handle initialization request"""
    response = {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {
            "tools": {
                "listTools": True
            }
        }
    }
    send_message(response)

def handle_list_tools(request: Dict[str, Any]) -> None:
    """Handle list tools request"""
    tools = [
        {
            "name": "calculate",
            "description": "Performs basic arithmetic calculations",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate (e.g., '2+2', 'sqrt(16)', etc.)"
                    }
                },
                "required": ["expression"]
            }
        },
        {
            "name": "echo",
            "description": "Echoes back the provided text",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to echo back"
                    }
                },
                "required": ["text"]
            }
        }
    ]
    
    response = {
        "id": request.get("id"),
        "result": {
            "tools": tools
        }
    }
    send_message(response)

def handle_call_tool(request: Dict[str, Any]) -> None:
    """Handle call tool request"""
    try:
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "calculate":
            expression = arguments.get("expression", "")
            try:
                # Note: In a real implementation, you should use a safer evaluation method
                result = eval(expression, {"__builtins__": {}}, {})
                response = {
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": str(result)
                            }
                        ]
                    }
                }
            except Exception as e:
                response = {
                    "id": request.get("id"),
                    "error": {
                        "code": -32603,
                        "message": f"Calculation error: {str(e)}"
                    }
                }
                
        elif tool_name == "echo":
            text = arguments.get("text", "")
            response = {
                "id": request.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": text
                        }
                    ]
                }
            }
            
        else:
            response = {
                "id": request.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Tool '{tool_name}' not found"
                }
            }
            
        send_message(response)
        
    except Exception as e:
        response = {
            "id": request.get("id"),
            "error": {
                "code": -32603,
                "message": f"Error processing tool call: {str(e)}"
            }
        }
        send_message(response)

def main():
    """Main server loop"""
    # Send initialization message
    handle_initialize()
    
    # Main message loop
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line.strip())
            
            method = request.get("method")
            if method == "tools/list":
                handle_list_tools(request)
            elif method == "tools/call":
                handle_call_tool(request)
            else:
                response = {
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found"
                    }
                }
                send_message(response)
                
        except json.JSONDecodeError as e:
            response = {
                "id": 0,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            send_message(response)
        except Exception as e:
            response = {
                "id": 0,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            send_message(response)

if __name__ == "__main__":
    main()