
import asyncio
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.agent_service import AgentService
from schemas.agent import AgentCreate
from models.mcp_server import MCPServer
from langchain_core.messages import HumanMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DB Setup
DATABASE_URL = "sqlite:///agents.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# User provided API Key (New OpenRouter Key)
OPENROUTER_API_KEY = "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"

# Free OpenRouter models - Testing Results for Tool Calling:
# ✅ google/gemini-2.0-flash-exp:free - WORKS but may hit rate limits (retry after wait)
# 🔍 openai/gpt-oss-20b:free - Testing now (21B params, designed for tool calling)
# 🔍 x-ai/grok-4.1-fast:free - Alternative (xAI's best agentic tool-calling model)
# ❌ deepseek/deepseek-r1:free - 404: No endpoints found that support tool use
# ❌ qwen/qwen-2.5-72b-instruct:free - 404: No endpoints found that support tool use  
# ❌ meta-llama/llama-3.3-70b-instruct:free - 400: Tools not supported in streaming mode

MODEL = "openai/gpt-oss-20b:free"  # OpenAI 21B model optimized for tool calling

async def main():
    print(f"Starting Extraction Test with OpenRouter model {MODEL}...")
    
    db = SessionLocal()
    agent_service = AgentService(db)
    
    # 1. Find Puppeteer Server
    server = db.query(MCPServer).filter(MCPServer.name.like("%Puppeteer%")).first()
    if not server:
        print("Puppeteer server not found!")
        return
    print(f"Found Puppeteer server: {server.server_id}")

    # 2. Create Agent
    print(f"Creating agent with model {MODEL}...")
    agent_data = AgentCreate(
        name="Extraction Test Agent - Puppeteer + GPT-OSS-20B",
        agent_type="react",
        llm_provider="OpenRouter",
        llm_model=MODEL,
        api_key=OPENROUTER_API_KEY,
        system_prompt=(
            "You are a helpful assistant with browser tools. "
            "IMPORTANT: The tool names have prefixes. You must use the EXACT name."
            "STEP 1: Use tool 'Puppeteer_Mcp_puppeteer_navigate' to open 'https://cognitbotz.com'. "
            "STEP 2: Use tool 'Puppeteer_Mcp_puppeteer_screenshot' to take a screenshot if needed. "
            "STEP 3: Use tool 'Puppeteer_Mcp_puppeteer_evaluate' with 'document.body.innerText' to read the page content. "
            "STEP 4: Extract the email address and phone number from the content. "
            "Be systematic and use the tools in order."
        ),
        mcp_servers=[server.server_id], # Bind Puppeteer server
        temperature=0.7,
        max_iterations=10,
        streaming_enabled=False,  # Disabled: Tools not supported in streaming mode
        human_in_loop=False,
        recursion_limit=50
    )
    
    try:
        agent = await agent_service.create_agent(agent_data)
        print(f"Agent created: {agent.agent_id}")
        
        # 3. Run Agent
        task = "Navigate to https://cognitbotz.com and find the email address and phone number on the page."
        print(f"Running agent with task: '{task}'...")
        
        session_id = "test-session-extraction-or-new-1"
        response = await agent_service.execute_agent(agent.agent_id, task, session_id)
        print(f"Agent Response: {response}")

    except Exception as e:
        print(f"Error running agent: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
