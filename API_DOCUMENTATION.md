# API Documentation - Mech Agent Application

## Overview

The Mech Agent application is a comprehensive AI agent building platform that allows users to create, configure, and manage LangGraph-based agents with various tools and knowledge bases. The application consists of a FastAPI backend and a React/TypeScript frontend.

## Backend API

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication & Security
The application currently implements the following security measures:

- **API Key Management**: User-provided LLM API keys are encrypted and stored securely in the database
- **PII Filtering**: Configurable PII detection and filtering middleware with multiple strategies (redact, mask, hash, block)
- **CORS**: Configured for frontend communication (localhost:8080, localhost:5173)
- **Input Validation**: Pydantic models for request/response validation

**Note**: The application does not currently implement user authentication or session management. All operations are performed without user-specific authentication.

### Agent Management Endpoints

#### Create Agent
```http
POST /api/v1/agents/
```

**Request Body:**
```json
{
  "name": "string",
  "agent_type": "react|plan-execute|reflection|custom",
  "llm_provider": "openai|anthropic|google|groq|openrouter|together|fireworks|cohere|meta|mistral",
  "llm_model": "string",
  "api_key": "string",
  "temperature": 0.0,
  "system_prompt": "string",
  "tools": ["string"],
  "tool_configs": {"key": "value"},
  "max_iterations": 10,
  "memory_type": "string",
  "streaming_enabled": true,
  "human_in_loop": false,
  "recursion_limit": 25,
  "pii_config": {
    "blocked_pii_types": ["pii_email", "pii_phone"],
    "custom_pii_categories": [],
    "strategy": "redact",
    "apply_to_output": true,
    "apply_to_tool_results": false
  }
}
```

**Response (201):**
```json
{
  "agent_id": "string",
  "name": "string",
  "agent_type": "string",
  "llm_provider": "string",
  "llm_model": "string",
  "temperature": 0.0,
  "system_prompt": "string",
  "tools": ["string"],
  "tool_configs": {},
  "max_iterations": 10,
  "streaming_enabled": true,
  "human_in_loop": false,
  "recursion_limit": 25,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### Get Agent
```http
GET /api/v1/agents/{agent_id}
```

**Response (200):**
Returns agent configuration (same as create response)

#### Get All Agents
```http
GET /api/v1/agents/
```

**Response (200):**
```json
[
  {
    "agent_id": "string",
    "name": "string",
    // ... agent fields
  }
]
```

#### Delete Agent
```http
DELETE /api/v1/agents/{agent_id}
```

**Response (200):**
```json
{
  "message": "Agent deleted successfully"
}
```

#### Execute Agent
```http
POST /api/v1/agents/{agent_id}/execute
```

**Request Body:**
```json
{
  "input": "string"
}
```

**Response (200):**
```json
{
  "response": "string"
}
```

#### Chat with Agent
```http
POST /api/v1/agents/{agent_id}/chat/
```

**Request Body:**
```json
{
  "message": "string",
  "thread_id": "string (optional)"
}
```

**Response (200):**
```json
{
  "response": "string"
}
```

#### Stream Agent Response
```http
WebSocket /api/v1/agents/{agent_id}/stream
```

WebSocket endpoint for real-time streaming responses.

### Memory Management Endpoints

#### Add Memory
```http
POST /api/v1/agents/memory/add
```

**Request Body:**
```json
{
  "messages": [{"role": "user", "content": "message"}],
  "user_id": "string",
  "agent_id": "string (optional)"
}
```

#### Search Memory
```http
POST /api/v1/agents/memory/search
```

**Request Body:**
```json
{
  "query": "string",
  "user_id": "string",
  "agent_id": "string (optional)",
  "top_k": 5
}
```

#### Get User Memories
```http
GET /api/v1/agents/memory/user/{user_id}?agent_id=string
```

#### Delete Session Memories
```http
POST /api/v1/agents/memory/session/{session_id}
DELETE /api/v1/agents/memory/session/{session_id}
```

### Tools Endpoint

#### Get Available Tools
```http
GET /api/v1/agents/tools/available
```

**Response (200):**
```json
{
  "duckduckgo_search": {
    "name": "DuckDuckGo Search",
    "description": "Web search using DuckDuckGo (no API key required)",
    "requires_api_key": false,
    "config_fields": {
      "max_results": {"type": "int", "default": 5},
      "timeout": {"type": "int", "default": 10}
    }
  },
  "brave_search": {
    "name": "Brave Search",
    "description": "Web search using Brave Search API",
    "requires_api_key": true,
    "config_fields": {
      "api_key": {"type": "string", "required": true},
      "search_count": {"type": "int", "default": 3}
    }
  },
  // ... other tools
}
```

## Knowledge Base Management Endpoints

### Create Knowledge Base
```http
POST /api/v1/knowledge-bases/
```

**Request Body:**
```json
{
  "agent_id": "string",
  "name": "string",
  "description": "string (optional)",
  "embedding_model": "qwen3-embedding:0.6b",
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

**Response (201):**
```json
{
  "kb_id": "string",
  "agent_id": "string",
  "name": "string",
  "description": "string",
  "collection_name": "string",
  "embedding_model": "string",
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Get Knowledge Base
```http
GET /api/v1/knowledge-bases/{kb_id}
```

**Response (200):**
```json
{
  "kb_id": "string",
  // ... kb fields
  "documents": [
    {
      "doc_id": "string",
      "kb_id": "string",
      "source_type": "text|url|file",
      "source_content": "string",
      "source_url": "string",
      "file_name": "string",
      "file_path": "string",
      "chunk_count": 5,
      "status": "pending|processing|completed|failed",
      "error_message": "string",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ]
}
```

### Get Agent Knowledge Bases
```http
GET /api/v1/knowledge-bases/agent/{agent_id}
```

### Delete Knowledge Base
```http
DELETE /api/v1/knowledge-bases/{kb_id}
```

### Add Document (Text)
```http
POST /api/v1/knowledge-bases/{kb_id}/documents/text
```

**Request Body (Form Data):**
```
text: "document content here"
```

### Add Document (URL)
```http
POST /api/v1/knowledge-bases/{kb_id}/documents/url
```

**Request Body (Form Data):**
```
url: "https://example.com"
```

### Add Document (File)
```http
POST /api/v1/knowledge-bases/{kb_id}/documents/file
```

**Request Body (Form Data):**
```
file: [uploaded file]
```
**Supported file types:** PDF, DOCX, TXT, MD, HTML, HTM

### Query Knowledge Base
```http
POST /api/v1/knowledge-bases/{kb_id}/query
```

**Request Body:**
```json
{
  "query": "string",
  "top_k": 5
}
```

**Response (200):**
```json
[
  {
    "content": "relevant content chunk",
    "score": 0.85,
    "metadata": {
      "source": "document_name",
      "chunk_index": 1
    }
  }
]
```

### Delete Document
```http
DELETE /api/v1/knowledge-bases/documents/{doc_id}
```

### Get Knowledge Base Documents
```http
GET /api/v1/knowledge-bases/{kb_id}/documents
```

## Database Models

### Agent Model
```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    agent_id VARCHAR UNIQUE,
    name VARCHAR,
    agent_type VARCHAR,
    llm_provider VARCHAR,
    llm_model VARCHAR,
    temperature FLOAT,
    system_prompt TEXT,
    tools JSON,
    tool_configs JSON,
    max_iterations INTEGER,
    memory_type VARCHAR,
    streaming_enabled BOOLEAN,
    human_in_loop BOOLEAN,
    recursion_limit INTEGER,
    api_key_encrypted VARCHAR,
    pii_config JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Knowledge Base Models
```sql
CREATE TABLE knowledge_bases (
    id INTEGER PRIMARY KEY,
    kb_id VARCHAR UNIQUE,
    agent_id VARCHAR,
    name VARCHAR,
    description TEXT,
    collection_name VARCHAR UNIQUE,
    embedding_model VARCHAR,
    chunk_size INTEGER,
    chunk_overlap INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE knowledge_documents (
    id INTEGER PRIMARY KEY,
    doc_id VARCHAR UNIQUE,
    kb_id VARCHAR,
    source_type VARCHAR,
    source_content TEXT,
    source_url VARCHAR,
    file_name VARCHAR,
    file_path VARCHAR,
    chunk_count INTEGER,
    status VARCHAR,
    error_message TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Available Tools

The application supports the following tools:

1. **DuckDuckGo Search** - Web search (no API key)
2. **Brave Search** - Web search via Brave API
3. **GitHub Toolkit** - GitHub repository operations
4. **Gmail Toolkit** - Email operations
5. **PlayWright Browser** - Web automation
6. **MCP Database** - Database operations via MCP
7. **FireCrawl** - Web scraping and crawling
8. **Arxiv** - Academic paper search
9. **Wikipedia** - Encyclopedia search

## Frontend API Integration

The React frontend communicates with the backend via:

- **Direct fetch() calls** to backend endpoints
- **Form submissions** for agent creation and knowledge base management
- **File uploads** using FormData for document uploads
- **WebSocket connections** for streaming responses

Key frontend components:
- `AgentBuilder`: Main form for creating/configuring agents
- `AgentChat`: Chat interface for interacting with agents
- `AgentList`: Display and management of created agents
- `ToolConfigDialog`: Configuration interface for tool settings

## Configuration & Environment

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///agents.db

# Security
SECRET_KEY=your_secret_key

# LLM API Keys (optional - can be provided per agent)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
GROQ_API_KEY=gsk_...

# Memory Service
MEM0_API_KEY=your_mem0_key

# CORS Origins
ALLOWED_ORIGINS=["http://localhost:8080", "http://localhost:5173"]
```

### Tool-specific Environment Variables
```bash
# Brave Search
BRAVE_API_KEY=your_brave_key

# GitHub
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY=your_private_key

# Gmail
GOOGLE_CREDENTIALS_FILE=credentials.json

# FireCrawl
FIRECRAWL_API_KEY=your_firecrawl_key

# MCP Database
MCP_SERVER_URL=http://127.0.0.1:5000
```

## Error Handling

The API returns standard HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `500`: Internal Server Error

Error responses include a `detail` field with error description.

## Dependencies

### Backend Dependencies
- **FastAPI**: Web framework
- **SQLAlchemy**: Database ORM
- **LangChain/LangGraph**: AI agent framework
- **Cryptography**: API key encryption
- **PII Middleware**: Privacy filtering
- **Various tool libraries**: DuckDuckGo, PlayWright, etc.

### Frontend Dependencies
- **React**: UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Radix UI**: Component library
- **React Query**: Data fetching
- **React Router**: Navigation

## Getting Started

1. **Backend Setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m uvicorn main:app --reload
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs (FastAPI auto-generated)

## PII Filtering

The application includes comprehensive PII (Personally Identifiable Information) filtering capabilities:

### Supported PII Types
- Email addresses
- Phone numbers
- Social Security Numbers (SSN)
- Credit card numbers
- IP addresses
- MAC addresses
- URLs
- API keys
- Names (simplified detection)
- Addresses (simplified detection)
- Medical record numbers
- Financial account numbers

### PII Strategies
- **Redact**: Replace with `[REDACTED_TYPE]`
- **Mask**: Show last 4 characters (e.g., `****-****-****-1234`)
- **Hash**: Replace with deterministic hash
- **Block**: Prevent request if PII detected

### Custom PII Categories
Users can define custom PII patterns with regex expressions for organization-specific identifiers.

This documentation covers the complete API surface and configuration options for the Mech Agent application. The system provides a comprehensive platform for building and managing AI agents with various tools and knowledge sources.
