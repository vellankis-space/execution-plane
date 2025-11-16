# Orchestration Platform - AI Agent & Workflow Management

Enterprise-grade orchestration platform for managing AI agents and workflows. Build, deploy, monitor, and scale intelligent automation with advanced LangGraph capabilities.

## Features

- **Orchestration at Scale**: Coordinate multiple AI agents and complex workflows
- **Multi-Provider Support**: OpenAI, Anthropic, Groq, and more
- **Agent Architectures**: ReAct, Plan & Execute, Reflection, and Custom Graphs
- **Workflow Builder**: Visual no-code workflow design and execution
- **Tool Integration**: Tavily Search, Python REPL, Wikipedia, and more
- **Real-time Monitoring**: Comprehensive observability and metrics tracking
- **Persistent Memory**: SQLite, PostgreSQL, Redis, and Qdrant vector storage
- **Enterprise Ready**: Authentication, audit logs, and cost tracking

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- npm or yarn
- Ollama (for local embeddings)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd execution-plane
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

3. Install backend dependencies:
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the backend directory with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   GROQ_API_KEY=your_groq_api_key
   SECRET_KEY=your_secret_key_for_encryption
   ```

5. Install and set up Ollama for local embeddings:
   ```bash
   # Install Ollama from https://ollama.com/
   # Pull the qwen3-embedding model
   ollama pull qwen3-embedding:0.6b
   ```

### Running the Application

Start both frontend and backend concurrently:
```bash
npm run dev
```

Or run them separately:

**Frontend:**
```bash
cd frontend
npm run dev
```

**Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Supported LLM Providers

- **OpenAI**: GPT-4, GPT-3.5, and newer models
- **Anthropic**: Claude Sonnet, Opus, and Haiku models
- **Groq**: Llama 3, Mixtral, and other fast inference models
- **Google**: Gemini models
- **OpenRouter**: Access to multiple providers through a single API
- **Together AI**: Llama, Mistral, and other models
- And more...

## Usage

1. Navigate to the agent builder interface
2. Configure your agent:
   - Select an LLM provider and model
   - Choose an agent architecture
   - Set system prompt and temperature
   - Select tools to include
   - Configure memory and streaming options
3. Provide your API key for the selected provider
4. Create and test your agent

## API Endpoints

- `POST /api/v1/agents` - Create a new agent
- `GET /api/v1/agents` - List all agents
- `GET /api/v1/agents/{agent_id}` - Get agent details
- `DELETE /api/v1/agents/{agent_id}` - Delete an agent
- `POST /api/v1/agents/{agent_id}/execute` - Execute an agent
- `POST /api/v1/agents/{agent_id}/chat` - Chat with an agent
- `WebSocket /api/v1/agents/{agent_id}/stream` - Stream agent responses

## Architecture

### Frontend

Built with React, TypeScript, Vite, and shadcn/ui components. Features a modern UI with:
- Agent management and configuration
- Visual workflow builder with ReactFlow
- Real-time monitoring dashboard
- Chat interface for agent interaction
- Audit logging and cost tracking

### Backend

Built with FastAPI, LangGraph, and SQLAlchemy. Provides:
- RESTful API for agent and workflow management
- WebSocket support for real-time streaming
- Vector memory integration with Qdrant
- Multi-provider LLM support
- Workflow orchestration engine

## Qdrant Memory Integration

This platform now includes enhanced memory capabilities powered by Qdrant vector database with local embeddings. With Qdrant integration:

- Conversations are automatically stored and retrieved for context using vector similarity search
- Agents remember past interactions for more personalized responses
- Memory is organized by user and agent for precise retrieval
- All data is stored locally using Qdrant's embedded storage

To enable Qdrant integration:

1. Install Ollama from [https://ollama.com/](https://ollama.com/)
2. Pull the qwen3-embedding model: `ollama pull qwen3-embedding:0.6b`
3. Install the required Python packages: `pip install -r requirements.txt`
4. Restart the backend service

Refer to `backend/README_MEM0.md` for detailed setup instructions and API usage.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.