# Knowledge Base Troubleshooting Guide

## Issue: Agent Timeout with Knowledge Base

If you're getting the error:
```
Error communicating with the agent: An unexpected error occurred while processing your request: 
Agent response timed out. The LLM provider may be slow or unreachable. Please try again.
```

This is typically caused by one of the following issues:

## Common Causes & Solutions

### 1. Ollama Server Not Running (Most Common)

**Problem**: The knowledge base uses Ollama for generating embeddings, which requires the Ollama server to be running.

**Solution**:
```bash
# Start Ollama server
ollama serve
```

Keep this terminal window open while using knowledge bases.

### 2. Embedding Model Not Installed

**Problem**: The default embedding model `qwen3-embedding:0.6b` is not pulled.

**Solution**:
```bash
# Pull the embedding model
ollama pull qwen3-embedding:0.6b
```

### 3. Slow LLM Provider Response

**Problem**: Your LLM provider (OpenAI, Anthropic, etc.) is responding slowly.

**Solutions**:
- Check your API key is valid and has quota
- Try a faster model (e.g., `gpt-4o-mini` instead of `gpt-4o`)
- Check your internet connection
- Wait a moment and try again (temporary rate limiting)

### 4. Large Knowledge Base Files

**Problem**: Processing very large files or many documents can be slow.

**Solutions**:
- Split large files into smaller chunks before uploading
- Upload files one at a time and wait for processing to complete
- Use text or links instead of large file uploads when possible

## Recent Improvements

The following improvements have been made to handle these issues better:

1. **Increased Timeouts**:
   - Knowledge base query timeout: 10s → 30s
   - Agent execution timeout with KB: 90s → 180s

2. **Better Error Messages**:
   - Clear error if Ollama is not running
   - Clear error if embedding model is not installed
   - KB errors no longer crash the agent (continues without KB context)

3. **JSON File Support**:
   - Added support for `.json` files in knowledge base uploads
   - JSON is converted to readable text format for embedding

## Quick Start Checklist

Before using agents with knowledge bases:

- [ ] Start Ollama: `ollama serve`
- [ ] Pull embedding model: `ollama pull qwen3-embedding:0.6b`
- [ ] Verify your LLM API key is valid
- [ ] Start backend: `cd backend && uvicorn main:app --reload`
- [ ] Start frontend: `cd frontend && npm run dev`

## Supported File Types

Knowledge bases now support:
- **PDF** (.pdf)
- **Word Documents** (.docx)
- **Text Files** (.txt, .md)
- **HTML** (.html, .htm)
- **JSON** (.json) - NEW!
- **Web URLs** (any valid HTTP/HTTPS URL)
- **Plain Text** (direct text input)

## Testing Your Setup

Run this command to verify Ollama is working:
```bash
# Test embedding generation
ollama run qwen3-embedding:0.6b "test"
```

If you see output without errors, your setup is correct!

## Still Having Issues?

Check the backend logs for detailed error messages:
1. Look at the terminal where you're running `uvicorn`
2. Check for specific error messages about:
   - Connection refused (Ollama not running)
   - Model not found (need to pull model)
   - API key errors (invalid LLM credentials)
   - Timeout errors (slow provider or large files)

## Alternative: Use Without Knowledge Base

If you need to use your agent urgently without knowledge base:
1. Create a new agent without uploading knowledge
2. Or edit your existing agent and remove the knowledge base
3. Use the system prompt to provide context instead
