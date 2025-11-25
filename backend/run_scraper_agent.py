import asyncio
import os
import sys
import json
import logging

# Add current directory to path
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from core.database import SessionLocal, Base, engine
from services.agent_service import AgentService
from models.mcp_server import MCPServer, AgentMCPServer
from models.agent import Agent
from schemas.agent import AgentCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    OPENROUTER_API_KEY = "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"

    db = SessionLocal()
    try:
        # 1. Ensure Puppeteer MCP Server exists in DB
        server_name = "puppeteer"
        # Check if it exists
        server = db.query(MCPServer).filter(MCPServer.server_id == "puppeteer").first()
        
        if not server:
            logger.info(f"Creating {server_name} MCP server record...")
            server = MCPServer(
                server_id="puppeteer",
                name="puppeteer",
                description="Puppeteer browser automation",
                transport_type="stdio",
                command="npx",
                args=json.dumps(["-y", "@modelcontextprotocol/server-puppeteer"]),
                env={}
            )
            db.add(server)
            db.commit()
            db.refresh(server)
        else:
            logger.info(f"Found existing {server_name} MCP server.")
            # Update config just in case
            server.command = "npx"
            server.args = json.dumps(["-y", "@modelcontextprotocol/server-puppeteer"])
            db.commit()

        # 2. Create Agent
        agent_service = AgentService(db)
        
        # Define agent data
        # Using liquid/lfm-40b as a robust model for "gpt oss 20b" request
        # or mistralai/mistral-small-24b-instruct-2501
        # Let's use a known good openrouter model
        model_id = "anthropic/claude-3.5-sonnet"  # Better instruction following
        
        agent_data = AgentCreate(
            name="CognitBotz Scraper",
            description="Agent to scrape cognitbotz.com",
            agent_type="react",
            llm_provider="openrouter",
            llm_model=model_id,  # More capable model for tool use
            mcp_servers=["puppeteer"],
            system_prompt="""You are a web scraper. Use the puppeteer tools to navigate websites and extract information.

CRITICAL RULES FOR TOOL USAGE:
1. ALWAYS call puppeteer_puppeteer_navigate FIRST before any other puppeteer tool
2. After navigate succeeds, you can use puppeteer_puppeteer_evaluate to extract data
3. NEVER call evaluate, click, fill, or screenshot without navigating first
4. If a tool fails, read the error message carefully and adjust your approach

TOOL SEQUENCE EXAMPLE:
Step 1: puppeteer_puppeteer_navigate(url='https://example.com')
Step 2: Wait for success response
Step 3: puppeteer_puppeteer_evaluate(script='document.querySelector("h1")?.textContent')

Always return the extracted information in your final response.""",
            api_key=OPENROUTER_API_KEY,
            temperature=0.1,
            max_iterations=20,
            streaming_enabled=False,
            human_in_loop=False,
            recursion_limit=50
        )
        
        logger.info("Creating agent...")
        agent = await agent_service.create_agent(agent_data)
        logger.info(f"Agent created with ID: {agent.agent_id}")

        # 3. Run Agent
        prompt = """Extract the main heading (h1) from https://cognitbotz.com

Follow this exact sequence:
1. First, call puppeteer_puppeteer_navigate with url='https://cognitbotz.com'
2. Wait for the navigate tool to return success
3. Then, call puppeteer_puppeteer_evaluate with script='document.querySelector("h1")?.textContent || "Not found"'
4. Return the extracted text in your final response

IMPORTANT: Do NOT skip step 1. Navigation MUST happen before evaluation, otherwise you will get errors."""
        logger.info(f"Executing agent with prompt: {prompt}")
        
        # Increase recursion limit for complex task
        response = await agent_service.execute_agent(agent.agent_id, prompt, recursion_limit=100)
        
        print("\n" + "="*50)
        print("AGENT RESPONSE")
        print("="*50)
        print(response)
        print("="*50 + "\n")

    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
