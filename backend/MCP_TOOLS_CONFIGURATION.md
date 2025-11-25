# MCP Tools Configuration Guide

## Problem: Token Overflow with MCP Tools

When loading MCP servers with many tools (e.g., CoinGecko has 47 tools), the agent can fail with **413 Payload Too Large** errors. This happens because:

1. All tool schemas are included in the system prompt sent to the LLM
2. Each tool has a name, description, and parameter schema
3. With 47 tools, the token count can reach 26K-56K tokens
4. Most LLM providers have limits (Groq: 6K-12K tokens per minute)
5. This causes the request to be rejected

## Solution: Tool Limiting

The system now automatically limits the number of MCP tools loaded per agent to prevent token overflow.

### Default Configuration

- **Default limit**: 15 tools per agent
- **Configurable via**: `MAX_MCP_TOOLS_PER_AGENT` environment variable

### How to Configure

Add to your `.env` file:

```bash
# Limit MCP tools per agent (default: 15)
MAX_MCP_TOOLS_PER_AGENT=20
```

### Recommendations

1. **Use fewer tools**: Instead of loading all tools from an MCP server, consider:
   - Creating multiple specialized agents, each with a subset of tools
   - Using only the most relevant tools for your use case

2. **Optimal tool count**:
   - **1-10 tools**: Ideal for most use cases
   - **11-15 tools**: Good balance between capability and performance
   - **16-20 tools**: May cause issues with smaller models
   - **20+ tools**: High risk of token overflow, especially with Groq

3. **Model considerations**:
   - Smaller models (e.g., `llama-3.1-8b-instant`): Use 5-10 tools max
   - Larger models (e.g., `llama-3.3-70b-versatile`): Can handle 10-15 tools
   - Very large models (e.g., `gpt-4`, `claude-3-opus`): Can handle 15-20 tools

### When Tools Are Trimmed

When an agent tries to load more tools than the limit, you'll see a warning:

```
⚠️  WARNING: Too many MCP tools (47)! Limiting to 15 tools to prevent API errors.
Consider selecting specific tools instead of loading all tools from MCP servers.
```

The system will automatically keep only the first N tools (based on the limit).

### Future Improvements

Planned features to improve tool management:

1. **Selective tool enabling**: Choose specific tools from an MCP server
2. **Tool prioritization**: Assign priority to tools for smarter selection
3. **Dynamic tool loading**: Load tools on-demand based on user query
4. **Tool groups**: Organize tools into categories for easier management

## Troubleshooting

### Still getting 413 errors?

1. **Reduce MAX_MCP_TOOLS_PER_AGENT**: Try setting it to 10 or even 5
2. **Check your model**: Some models have very low token limits
3. **Simplify system prompts**: Long system prompts add to token count
4. **Remove unused MCP servers**: Disconnect MCP servers you're not using

### Tools not working as expected?

1. **Check which tools are loaded**: Look at the server logs to see which tools were kept
2. **Increase the limit**: If you need more tools and have a model that supports it
3. **Create multiple agents**: Specialize agents for different tasks

## Example Configuration

For a CoinGecko agent with specific needs:

```bash
# .env file
MAX_MCP_TOOLS_PER_AGENT=10  # Limit to 10 most important tools
GROQ_API_KEY=your_groq_key
```

Then in your agent configuration, only connect the CoinGecko MCP server and the first 10 tools will be loaded automatically.
