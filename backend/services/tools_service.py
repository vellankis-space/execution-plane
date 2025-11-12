"""
Tools Service for managing external LangChain tools
Supports: DuckDuckGo Search, Brave Search, GitHub Toolkit, Gmail Toolkit, 
          PlayWright Browser Toolkit, FireCrawl, MCP Toolbox for Databases, and Arxiv
"""

from typing import List, Optional, Dict, Any
import os
import logging
from langchain_core.tools import BaseTool, tool, StructuredTool
from pydantic import BaseModel, Field
from urllib.parse import urlparse
from functools import partial
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError


class ToolsService:
    """Service for initializing and managing external tools"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available_tools = {
            "duckduckgo_search": self._init_duckduckgo,
            "brave_search": self._init_brave_search,
            "github_toolkit": self._init_github_toolkit,
            "gmail_toolkit": self._init_gmail_toolkit,
            "playwright_browser": self._init_playwright_browser,
            "mcp_database": self._init_mcp_database,
            "firecrawl": self._init_firecrawl,
            "arxiv": self._init_arxiv,
        }
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format and accessibility"""
        if not url or not isinstance(url, str):
            return False
        
        try:
            result = urlparse(url)
            return all([
                result.scheme in ('http', 'https'),
                result.netloc
            ])
        except Exception:
            return False
    
    def get_tools(self, tool_names: List[str], tool_configs: Optional[Dict[str, Any]] = None) -> List[BaseTool]:
        """
        Get initialized tools based on tool names and configurations
        
        Args:
            tool_names: List of tool identifiers to initialize
            tool_configs: Optional dictionary of tool-specific configurations
        
        Returns:
            List of initialized LangChain tools
        """
        self.logger.debug(f"get_tools called with tool_names: {tool_names}")
        self.logger.debug(f"get_tools called with tool_configs: {tool_configs}")
        
        tools = []
        configs = tool_configs or {}
        
        for tool_name in tool_names:
            self.logger.debug(f"Processing tool: {tool_name}")
            if tool_name in self.available_tools:
                try:
                    tool_list = self.available_tools[tool_name](configs.get(tool_name, {}))
                    self.logger.debug(f"Tool {tool_name} initialized with {len(tool_list)} tools: {[t.name if hasattr(t, 'name') else str(t) for t in tool_list]}")
                    if tool_list:
                        tools.extend(tool_list)
                except Exception as e:
                    self.logger.error(f"Error initializing tool {tool_name}: {e}", exc_info=True)
            else:
                self.logger.warning(f"Tool {tool_name} not found in available_tools")
        
        self.logger.info(f"Returning {len(tools)} total tools: {[t.name for t in tools]}")
        return tools
    
    def _init_duckduckgo(self, config: Dict[str, Any]) -> List[BaseTool]:
        """Initialize DuckDuckGo Search tool (no API key required)"""
        try:
            from langchain_community.tools import DuckDuckGoSearchRun
            from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
            import time
            
            max_results = config.get("max_results", 5)
            timeout = config.get("timeout", 10)
            
            wrapper = DuckDuckGoSearchAPIWrapper(max_results=max_results)
            
            class RateLimitHandledDuckDuckGoSearchRun(DuckDuckGoSearchRun):
                def _run(self, query: str) -> str:
                    max_retries = 3
                    base_delay = 2
                    
                    for attempt in range(max_retries):
                        try:
                            return super()._run(query)
                        except Exception as e:
                            error_msg = str(e).lower()
                            
                            # Check for rate limiting
                            if any(keyword in error_msg for keyword in [
                                "ratelimit", "rate limit", "too many requests",
                                "429", "blocked", "forbidden", "access denied"
                            ]):
                                if attempt < max_retries - 1:
                                    delay = base_delay * (2 ** attempt)
                                    self.logger.warning(f"DuckDuckGo rate limited (attempt {attempt + 1}/{max_retries}). Waiting {delay}s...")
                                    time.sleep(delay)
                                    continue
                                else:
                                    return "DuckDuckGo search is temporarily unavailable due to rate limiting. Please try again later."
                            
                            # Check for timeout
                            elif any(keyword in error_msg for keyword in [
                                "timeout", "timed out", "connection timeout"
                            ]):
                                if attempt < max_retries - 1:
                                    delay = base_delay * (2 ** attempt)
                                    self.logger.warning(f"DuckDuckGo timeout (attempt {attempt + 1}/{max_retries}). Waiting {delay}s...")
                                    time.sleep(delay)
                                    continue
                                else:
                                    return f"Search timed out after {max_retries} attempts."
                            
                            # Other errors
                            else:
                                self.logger.error(f"DuckDuckGo search error: {str(e)}")
                                return f"Search failed: {str(e)}"
                    
                    return "Search failed after multiple attempts."
            
            search_tool = RateLimitHandledDuckDuckGoSearchRun(api_wrapper=wrapper)
            self.logger.info("DuckDuckGo search tool initialized successfully")
            return [search_tool]
            
        except ImportError as e:
            self.logger.error(f"DuckDuckGo dependencies not installed: {e}")
            return self._create_placeholder_tool(
                "duckduckgo_search",
                "Search the web using DuckDuckGo",
                "DuckDuckGo dependencies not installed. Install: pip install langchain-community duckduckgo-search"
            )
        except Exception as e:
            self.logger.error(f"Error initializing DuckDuckGo: {e}", exc_info=True)
            return self._create_placeholder_tool(
                "duckduckgo_search",
                "Search the web using DuckDuckGo",
                f"DuckDuckGo initialization failed: {str(e)}"
            )
    
    def _init_brave_search(self, config: Dict[str, Any]) -> List[BaseTool]:
        """Initialize Brave Search tool (requires API key)"""
        try:
            from langchain_community.tools import BraveSearch
            
            api_key = config.get("api_key") or os.getenv("BRAVE_SEARCH_API_KEY")
            
            if not api_key:
                self.logger.warning("Brave Search API key not provided")
                return self._create_placeholder_tool(
                    "brave_search",
                    "Search the web using Brave Search API",
                    "Brave Search requires an API key. Configure BRAVE_SEARCH_API_KEY."
                )
            
            search_count = config.get("search_count", 3)
            brave_tool = BraveSearch.from_api_key(
                api_key=api_key, 
                search_kwargs={"count": search_count}
            )
            
            self.logger.info("Brave Search tool initialized successfully")
            return [brave_tool]
            
        except ImportError as e:
            self.logger.error(f"Brave Search dependencies not installed: {e}")
            return self._create_placeholder_tool(
                "brave_search",
                "Search the web using Brave Search",
                "Brave Search dependencies not installed. Install: pip install langchain-community"
            )
        except Exception as e:
            self.logger.error(f"Error initializing Brave Search: {e}", exc_info=True)
            return self._create_placeholder_tool(
                "brave_search",
                "Search the web using Brave Search",
                f"Brave Search initialization failed: {str(e)}"
            )
    
    def _init_github_toolkit(self, config: Dict[str, Any]) -> List[BaseTool]:
        """Initialize GitHub Toolkit (requires GitHub App credentials)"""
        try:
            from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
            from langchain_community.utilities.github import GitHubAPIWrapper
            
            app_id = config.get("app_id") or os.getenv("GITHUB_APP_ID")
            private_key = config.get("private_key") or os.getenv("GITHUB_APP_PRIVATE_KEY")
            repository = config.get("repository") or os.getenv("GITHUB_REPOSITORY")
            
            if not all([app_id, private_key, repository]):
                self.logger.warning("GitHub credentials incomplete")
                return self._create_placeholder_tools([
                    ("github_search", "Search GitHub repositories"),
                    ("github_get_issue", "Get GitHub issue details")
                ], "GitHub Toolkit requires App ID, private key, and repository name.")
            
            # Set environment variables
            os.environ["GITHUB_APP_ID"] = app_id
            os.environ["GITHUB_APP_PRIVATE_KEY"] = private_key
            os.environ["GITHUB_REPOSITORY"] = repository
            
            if config.get("branch"):
                os.environ["GITHUB_BRANCH"] = config["branch"]
            if config.get("base_branch"):
                os.environ["GITHUB_BASE_BRANCH"] = config["base_branch"]
            
            github = GitHubAPIWrapper()
            toolkit = GitHubToolkit.from_github_api_wrapper(github)
            
            self.logger.info("GitHub Toolkit initialized successfully")
            return toolkit.get_tools()
            
        except ImportError as e:
            self.logger.error(f"GitHub toolkit dependencies not installed: {e}")
            return self._create_placeholder_tools([
                ("github_search", "Search GitHub repositories"),
                ("github_get_issue", "Get GitHub issue details")
            ], "GitHub dependencies not installed. Install: pip install langchain-community")
        except Exception as e:
            self.logger.error(f"Error initializing GitHub toolkit: {e}", exc_info=True)
            return self._create_placeholder_tools([
                ("github_search", "Search GitHub repositories"),
                ("github_get_issue", "Get GitHub issue details")
            ], f"GitHub initialization failed: {str(e)}")
    
    def _init_gmail_toolkit(self, config: Dict[str, Any]) -> List[BaseTool]:
        """Initialize Gmail Toolkit (requires OAuth2 credentials)"""
        try:
            from langchain_google_community import GmailToolkit
            from langchain_google_community.gmail.utils import (
                build_resource_service,
                get_gmail_credentials,
            )
            
            credentials_file = config.get("credentials_file", "credentials.json")
            token_file = config.get("token_file", "token.json")
            scopes = config.get("scopes", ["https://mail.google.com/"])
            
            if not os.path.exists(credentials_file):
                self.logger.warning(f"Gmail credentials file not found: {credentials_file}")
                return self._create_placeholder_tools([
                    ("gmail_search", "Search Gmail messages"),
                    ("gmail_send", "Send Gmail messages")
                ], "Gmail requires OAuth2 credentials.json file.")
            
            credentials = get_gmail_credentials(
                token_file=token_file,
                scopes=scopes,
                client_secrets_file=credentials_file,
            )
            
            api_resource = build_resource_service(credentials=credentials)
            toolkit = GmailToolkit(api_resource=api_resource)
            
            self.logger.info("Gmail Toolkit initialized successfully")
            return toolkit.get_tools()
            
        except ImportError as e:
            self.logger.error(f"Gmail toolkit dependencies not installed: {e}")
            return self._create_placeholder_tools([
                ("gmail_search", "Search Gmail messages"),
                ("gmail_send", "Send Gmail messages")
            ], "Gmail dependencies not installed. Install: pip install langchain-google-community")
        except Exception as e:
            self.logger.error(f"Error initializing Gmail toolkit: {e}", exc_info=True)
            return self._create_placeholder_tools([
                ("gmail_search", "Search Gmail messages"),
                ("gmail_send", "Send Gmail messages")
            ], f"Gmail initialization failed: {str(e)}")
    
    def _init_playwright_browser(self, config: Dict[str, Any]) -> List[BaseTool]:
        """Initialize PlayWright Browser Toolkit"""
        try:
            from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
            from langchain_community.tools.playwright.utils import create_async_playwright_browser
            import nest_asyncio
            import asyncio

            try:
                loop = asyncio.get_running_loop()
                loop_type = type(loop).__name__
                self.logger.info(f"Current event loop type: {loop_type}")

                if 'uvloop' in loop_type.lower():
                    self.logger.warning("Detected uvloop - PlayWright may not be compatible")
                    return self._create_playwright_placeholders(
                        "PlayWright is not compatible with uvloop event loops."
                    )

                nest_asyncio.apply()
                self.logger.debug("Applied nest_asyncio")

            except RuntimeError:
                self.logger.warning("No running event loop - PlayWright requires async context")
                return self._create_playwright_placeholders(
                    "PlayWright requires an async event loop context."
                )

            async_browser = create_async_playwright_browser()
            toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
            tools = toolkit.get_tools()
            
            self.logger.info(f"PlayWright initialized successfully with {len(tools)} tools")
            return tools

        except ImportError as e:
            self.logger.error(f"PlayWright dependencies not installed: {e}")
            return self._create_playwright_placeholders(
                "PlayWright dependencies not installed. Install: pip install playwright && playwright install"
            )
        except Exception as e:
            self.logger.error(f"Error initializing PlayWright: {e}", exc_info=True)
            return self._create_playwright_placeholders(
                f"PlayWright initialization failed: {str(e)}"
            )

    def _create_playwright_placeholders(self, error_msg: str) -> List[BaseTool]:
        """Create placeholder tools for PlayWright"""
        return self._create_placeholder_tools([
            ("navigate_browser", "Navigate to a URL"),
            ("click_element", "Click an element"),
            ("extract_text", "Extract text from page")
        ], error_msg)
    
    def _init_mcp_database(self, config: Dict[str, Any]) -> List[BaseTool]:
        """Initialize MCP Toolbox for Databases"""
        try:
            from toolbox_langchain import ToolboxClient
            
            server_url = config.get("server_url", "http://127.0.0.1:5000")
            
            self.logger.info(f"MCP Toolbox requires async initialization. Server: {server_url}")
            return self._create_placeholder_tool(
                "mcp_database",
                "Database operations via MCP Toolbox",
                f"MCP Toolbox requires async initialization. Use get_mcp_tools_async() method. Server: {server_url}"
            )
            
        except ImportError as e:
            self.logger.error(f"MCP Toolbox dependencies not installed: {e}")
            return self._create_placeholder_tool(
                "mcp_database",
                "Database operations via MCP Toolbox",
                "MCP Toolbox dependencies not installed. Install: pip install toolbox-langchain"
            )
        except Exception as e:
            self.logger.error(f"Error with MCP database toolkit: {e}", exc_info=True)
            return self._create_placeholder_tool(
                "mcp_database",
                "Database operations via MCP Toolbox",
                f"MCP initialization failed: {str(e)}"
            )
    
    async def get_mcp_tools_async(self, config: Dict[str, Any]) -> List[BaseTool]:
        """Async method to initialize MCP Toolbox tools"""
        try:
            from toolbox_langchain import ToolboxClient
            
            server_url = config.get("server_url", "http://127.0.0.1:5000")
            toolset_name = config.get("toolset_name")
            tool_names = config.get("tool_names", [])
            
            async with ToolboxClient(server_url) as client:
                if toolset_name:
                    tools = await client.aload_toolset(toolset_name)
                elif tool_names:
                    tools = []
                    for tool_name in tool_names:
                        tool = await client.aload_tool(tool_name)
                        tools.append(tool)
                else:
                    self.logger.warning("MCP config needs either toolset_name or tool_names")
                    return []
                
                self.logger.info(f"MCP tools loaded successfully: {len(tools)} tools")
                return tools
                
        except Exception as e:
            self.logger.error(f"Error loading MCP tools: {e}", exc_info=True)
            return []
    
    def _init_firecrawl(self, config: Dict[str, Any]) -> List[BaseTool]:
        """Initialize FireCrawl tools using LangChain FireCrawlLoader as per documentation"""
        try:
            from langchain_community.document_loaders.firecrawl import FireCrawlLoader
            from concurrent.futures import ThreadPoolExecutor, TimeoutError

            api_key = config.get("api_key") or os.getenv("FIRECRAWL_API_KEY")

            if not api_key:
                self.logger.warning("FireCrawl API key not provided")
                return self._create_firecrawl_placeholders("missing_api_key")

            if api_key and not api_key.startswith('fc-'):
                self.logger.warning(f"FireCrawl API key format unexpected (should start with 'fc-')")

            # Get default timeout settings
            scrape_timeout = config.get("scrape_timeout", 30)
            crawl_timeout = config.get("crawl_timeout", 45)
            map_timeout = config.get("map_timeout", 20)

            tools = []

            # Input schemas
            class URLInput(BaseModel):
                url: str = Field(description="URL to process")

            # Scrape tool - single URL scraping
            def firecrawl_scrape(url: str) -> str:
                """Scrape a single webpage using FireCrawl."""
                if not self._validate_url(url):
                    return f"Invalid URL format: {url}"

                try:
                    # Run in thread with timeout
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(
                            lambda: FireCrawlLoader(
                                api_key=api_key,
                                url=url,
                                mode="scrape"
                            ).load()
                        )
                        docs = future.result(timeout=scrape_timeout)
                    
                    if docs and len(docs) > 0:
                        return docs[0].page_content
                    return "No content found at the specified URL."
                except TimeoutError:
                    return f"Scraping timed out after {scrape_timeout} seconds"
                except Exception as e:
                    self.logger.error(f"Error scraping {url}: {e}")
                    return f"Error scraping URL: {str(e)}"

            # Crawl tool - website crawling
            def firecrawl_crawl(url: str) -> str:
                """Crawl a website and all accessible subpages using FireCrawl."""
                if not self._validate_url(url):
                    return f"Invalid URL format: {url}"

                try:
                    # Run in thread with timeout
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(
                            lambda: FireCrawlLoader(
                                api_key=api_key,
                                url=url,
                                mode="crawl"
                            ).load()
                        )
                        docs = future.result(timeout=crawl_timeout)
                    
                    if docs and len(docs) > 0:
                        # Limit to first 5 pages to avoid overwhelming response
                        limited_docs = docs[:5]
                        formatted_pages = []
                        for i, doc in enumerate(limited_docs):
                            url_info = doc.metadata.get('sourceURL', doc.metadata.get('ogUrl', f'Page {i+1}'))
                            content = doc.page_content[:500]
                            if len(doc.page_content) > 500:
                                content += "..."
                            formatted_pages.append(f"Page {i+1} ({url_info}):\n{content}")
                        return "\n\n".join(formatted_pages)
                    return "No pages found to crawl."
                except TimeoutError:
                    return f"Crawling timed out after {crawl_timeout} seconds"
                except Exception as e:
                    self.logger.error(f"Error crawling {url}: {e}")
                    return f"Error crawling website: {str(e)}"

            # Map tool - find related pages
            def firecrawl_map(url: str) -> str:
                """Map a URL and return semantically related pages using FireCrawl."""
                if not self._validate_url(url):
                    return f"Invalid URL format: {url}"

                try:
                    # Run in thread with timeout
                    with ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(
                            lambda: FireCrawlLoader(
                                api_key=api_key,
                                url=url,
                                mode="map"
                            ).load()
                        )
                        docs = future.result(timeout=map_timeout)
                    
                    if docs and len(docs) > 0:
                        # Extract links from the map results
                        links = []
                        for doc in docs[:10]:  # Limit to 10 links
                            if 'links' in doc.metadata:
                                links.extend(doc.metadata['links'][:10])
                            elif 'sourceURL' in doc.metadata:
                                links.append(doc.metadata['sourceURL'])

                        if links:
                            return "Semantically related pages:\n" + "\n".join(links[:10])
                    return "No related pages found."
                except TimeoutError:
                    return f"Mapping timed out after {map_timeout} seconds"
                except Exception as e:
                    self.logger.error(f"Error mapping {url}: {e}")
                    return f"Error mapping URL: {str(e)}"

            # Create StructuredTools using LangChain pattern
            firecrawl_scrape_tool = StructuredTool.from_function(
                func=firecrawl_scrape,
                name="firecrawl_scrape",
                description=f"Scrape a single webpage using FireCrawl (returns markdown content)",
                args_schema=URLInput
            )

            firecrawl_crawl_tool = StructuredTool.from_function(
                func=firecrawl_crawl,
                name="firecrawl_crawl",
                description=f"Crawl entire website using FireCrawl (returns content from multiple pages)",
                args_schema=URLInput
            )

            firecrawl_map_tool = StructuredTool.from_function(
                func=firecrawl_map,
                name="firecrawl_map",
                description=f"Map URL for semantically related pages using FireCrawl (returns related URLs)",
                args_schema=URLInput
            )

            tools = [firecrawl_scrape_tool, firecrawl_crawl_tool, firecrawl_map_tool]
            self.logger.info(f"FireCrawl initialized successfully with {len(tools)} tools using LangChain FireCrawlLoader")
            return tools

        except ImportError as e:
            self.logger.error(f"FireCrawl LangChain dependencies not installed: {e}")
            return self._create_firecrawl_placeholders("dependencies_missing")
        except Exception as e:
            self.logger.error(f"Error initializing FireCrawl: {e}", exc_info=True)
            return self._create_firecrawl_placeholders("initialization_failed")
    
    def _init_arxiv(self, config: Dict[str, Any]) -> List[BaseTool]:
        """Initialize Arxiv tool for searching academic papers"""
        try:
            from langchain_community.utilities import ArxivAPIWrapper
            from langchain_community.tools import ArxivQueryRun
            
            arxiv_tool = ArxivQueryRun(api_wrapper=ArxivAPIWrapper())
            self.logger.info("Arxiv tool initialized successfully")
            return [arxiv_tool]
        except ImportError as e:
            self.logger.error(f"Arxiv dependencies not installed: {e}")
            return self._create_placeholder_tool(
                "arxiv",
                "Search for academic papers on Arxiv",
                "Arxiv dependencies not installed. Install: pip install arxiv"
            )
        except Exception as e:
            self.logger.error(f"Error initializing Arxiv tool: {e}", exc_info=True)
            return self._create_placeholder_tool(
                "arxiv",
                "Search for academic papers on Arxiv",
                f"Arxiv initialization failed: {str(e)}"
            )

    def _create_firecrawl_placeholders(self, error_type: str) -> List[BaseTool]:
        """Create placeholder tools for FireCrawl"""
        error_messages = {
            "missing_api_key": "FireCrawl requires an API key. Configure FIRECRAWL_API_KEY.",
            "invalid_api_key": "FireCrawl API key is invalid or initialization failed.",
            "dependencies_missing": "FireCrawl dependencies not installed. Install: pip install firecrawl-py",
            "initialization_failed": "FireCrawl initialization failed. Check configuration and API key."
        }
        
        message = error_messages.get(error_type, "FireCrawl is not available.")
        
        return self._create_placeholder_tools([
            ("firecrawl_scrape", "Scrape a webpage"),
            ("firecrawl_crawl", "Crawl a website"),
            ("firecrawl_map", "Map URL for related pages")
        ], message)
    
    def _create_placeholder_tool(self, name: str, description: str, error_msg: str) -> List[BaseTool]:
        """Helper to create a single placeholder tool"""
        @tool
        def placeholder_func(query: str) -> str:
            return error_msg
        
        placeholder_func.name = name
        placeholder_func.description = f"{description} (Not configured: {error_msg})"
        return [placeholder_func]
    
    def _create_placeholder_tools(self, tool_definitions: List[tuple], error_msg: str) -> List[BaseTool]:
        """Helper to create multiple placeholder tools"""
        tools = []
        for name, description in tool_definitions:
            @tool
            def placeholder_func(query: str, error_message=error_msg) -> str:
                return error_message
            
            placeholder_func.name = name
            placeholder_func.description = f"{description} (Not configured: {error_msg})"
            tools.append(placeholder_func)
        
        return tools
    
    @staticmethod
    def get_available_tools_info() -> Dict[str, Dict[str, Any]]:
        """Get information about available tools and their requirements"""
        return {
            "duckduckgo_search": {
                "name": "DuckDuckGo Search",
                "description": "Web search using DuckDuckGo (no API key required)",
                "requires_api_key": False,
                "config_fields": {
                    "max_results": {"type": "int", "default": 5},
                    "timeout": {"type": "int", "default": 10}
                }
            },
            "brave_search": {
                "name": "Brave Search",
                "description": "Web search using Brave Search API",
                "requires_api_key": True,
                "config_fields": {
                    "api_key": {"type": "string", "required": True},
                    "search_count": {"type": "int", "default": 3}
                }
            },
            "github_toolkit": {
                "name": "GitHub Toolkit",
                "description": "Interact with GitHub repositories",
                "requires_api_key": True,
                "config_fields": {
                    "app_id": {"type": "string", "required": True},
                    "private_key": {"type": "string", "required": True},
                    "repository": {"type": "string", "required": True}
                }
            },
            "gmail_toolkit": {
                "name": "Gmail Toolkit",
                "description": "Read, draft, and send Gmail messages",
                "requires_api_key": True,
                "config_fields": {
                    "credentials_file": {"type": "string", "default": "credentials.json"}
                }
            },
            "playwright_browser": {
                "name": "PlayWright Browser",
                "description": "Automate web browser interactions",
                "requires_api_key": False,
                "notes": "Requires async context, not compatible with uvloop"
            },
            "mcp_database": {
                "name": "MCP Database Toolbox",
                "description": "Database operations via MCP Toolbox",
                "requires_api_key": False,
                "config_fields": {
                    "server_url": {"type": "string", "default": "http://127.0.0.1:5000"}
                }
            },
            "firecrawl": {
                "name": "FireCrawl",
                "description": "Web scraping and crawling using FireCrawl API",
                "requires_api_key": True,
                "config_fields": {
                    "api_key": {"type": "string", "required": True},
                    "scrape_timeout": {"type": "int", "default": 30},
                    "crawl_timeout": {"type": "int", "default": 45},
                    "map_timeout": {"type": "int", "default": 20}
                }
            },
            "arxiv": {
                "name": "Arxiv",
                "description": "Search for academic papers on Arxiv",
                "requires_api_key": False,
                "config_fields": {}
            }
        }