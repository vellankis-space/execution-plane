# LangChain Tools Implementation Guide

## Overview

This guide explains the implementation of 6 new LangChain tools integrated into the mech-agent application:

1. **DuckDuckGo Search** - Free web search (no API key required)
2. **Brave Search** - Privacy-focused search with API
3. **GitHub Toolkit** - Interact with GitHub repositories
4. **Gmail Toolkit** - Send, read, and draft Gmail messages
5. **PlayWright Browser Toolkit** - Automate web browser interactions
6. **MCP Database Toolbox** - Database operations via MCP server

## Installation

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs all required packages including:
- `duckduckgo-search` - DuckDuckGo search functionality
- `playwright` - Browser automation
- `lxml` - HTML parsing for PlayWright
- `pygithub` - GitHub API integration
- `langchain-google-community[gmail]` - Gmail toolkit
- `google-auth-oauthlib` - Google OAuth2 authentication
- `toolbox-langchain` - MCP Toolbox integration
- `nest-asyncio` - Async event loop support

### 2. Install PlayWright Browsers

For the PlayWright Browser Toolkit to work, you need to install browser binaries:

```bash
playwright install
```

This downloads Chromium, Firefox, and WebKit browsers.

### 3. Run Database Migration

Add the `tool_configs` column to the agents table:

```bash
cd backend
python migrations/add_tool_configs.py
```

Expected output:
```
============================================================
Tool Configs Migration
============================================================
Adding tool_configs column to agents table...
✓ Successfully added tool_configs column to agents table
✓ Migration verified: tool_configs column exists

============================================================
Migration completed successfully!
============================================================
```

## Tool Configuration

### DuckDuckGo Search 🦆

**Requires API Key:** No

**Configuration:**
- `max_results`: Number of search results (default: 5)

**Example:**
```json
{
  "max_results": 5
}
```

**Usage:** No setup required. Just select the tool when creating an agent.

---

### Brave Search 🦁

**Requires API Key:** Yes

**Setup:**
1. Visit [Brave Search API](https://brave.com/search/api/)
2. Sign up for a free account
3. Get your API key (starts with "BSA...")

**Configuration:**
- `api_key`: Your Brave Search API key (required)
- `search_count`: Number of results per query (default: 3)

**Example:**
```json
{
  "api_key": "BSA***************",
  "search_count": 3
}
```

**Usage in UI:**
1. Select "Brave Search" tool
2. Click the settings icon ⚙️
3. Enter your API key
4. Configure search count (optional)
5. Click "Save Configuration"

---

### GitHub Toolkit 🐙

**Requires API Key:** Yes (GitHub App credentials)

**Setup:**
1. Go to [GitHub Apps Settings](https://github.com/settings/apps)
2. Click "New GitHub App"
3. Fill in app details:
   - Name: YourAppName
   - Homepage URL: http://localhost:8000
   - Webhook: Disable
4. Set repository permissions:
   - Contents: Read & Write
   - Issues: Read & Write
   - Pull requests: Read & Write
   - Metadata: Read only
5. Click "Create GitHub App"
6. Note your App ID
7. Generate a private key and download it
8. Install the app on your repositories

**Configuration:**
- `app_id`: GitHub App ID (required)
- `private_key`: Full private key content (required)
- `repository`: Repository in format "owner/repo" (required)
- `branch`: Working branch (optional, defaults to main)
- `base_branch`: Base branch for PRs (optional)

**Example:**
```json
{
  "app_id": "123456",
  "private_key": "-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n-----END RSA PRIVATE KEY-----",
  "repository": "username/my-repo",
  "branch": "develop"
}
```

**Available Tools:**
- Get Issues
- Get Issue
- Comment on Issue
- Create Pull Request
- Create/Read/Update/Delete Files
- List branches
- Search code and issues

---

### Gmail Toolkit 📧

**Requires API Key:** Yes (OAuth2 credentials)

**Setup:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Application type: Desktop app
6. Download the credentials as `credentials.json`
7. Place `credentials.json` in your backend directory

**Configuration:**
- `credentials_file`: Path to credentials.json (default: "credentials.json")
- `token_file`: Path to store token (default: "token.json")
- `scopes`: Gmail API scopes (default: ["https://mail.google.com/"])

**Example:**
```json
{
  "credentials_file": "credentials.json",
  "token_file": "token.json"
}
```

**First Run:**
The first time you use Gmail toolkit, it will open a browser window for OAuth authentication. After granting permissions, a `token.json` file will be created for future use.

**Available Tools:**
- GmailCreateDraft
- GmailSendMessage
- GmailSearch
- GmailGetMessage
- GmailGetThread

---

### PlayWright Browser Toolkit 🎭

**Requires API Key:** No

**Setup:**
Make sure PlayWright browsers are installed (see Installation section).

**Configuration:** None required

**Available Tools:**
- NavigateTool - Navigate to a URL
- ClickTool - Click on elements
- ExtractTextTool - Extract text from pages
- ExtractHyperlinksTool - Extract links
- GetElementsTool - Select elements by CSS
- CurrentPageTool - Get current URL

**Usage Example:**
The agent can:
- Navigate to websites
- Click buttons and links
- Fill forms
- Extract information
- Take screenshots (programmatically)

---

### MCP Database Toolbox 🗄️

**Requires API Key:** No (requires MCP server)

**Setup:**

1. **Install MCP Toolbox:**
   ```bash
   # macOS (Homebrew)
   brew install mcp-toolbox
   
   # Other platforms: download from
   # https://github.com/googleapis/genai-toolbox/releases
   ```

2. **Create `tools.yaml` configuration:**
   ```yaml
   sources:
     my-pg-source:
       kind: postgres
       host: 127.0.0.1
       port: 5432
       database: your_db
       user: your_user
       password: your_password
   
   tools:
     search-data:
       kind: postgres-sql
       source: my-pg-source
       description: Search data in the database
       parameters:
         - name: query
           type: string
           description: Search query
       statement: SELECT * FROM table WHERE column LIKE '%' || $1 || '%';
   
   toolsets:
     my_toolset:
       - search-data
   ```

3. **Start MCP Toolbox Server:**
   ```bash
   toolbox --tools-file tools.yaml
   ```
   Server runs on `http://127.0.0.1:5000` by default.

**Configuration:**
- `server_url`: MCP server URL (default: "http://127.0.0.1:5000")
- `toolset_name`: Name of toolset to load (optional)
- `tool_names`: Individual tool names array (optional)

**Example:**
```json
{
  "server_url": "http://127.0.0.1:5000",
  "toolset_name": "my_toolset"
}
```

**Or specify individual tools:**
```json
{
  "server_url": "http://127.0.0.1:5000",
  "tool_names": ["search-data", "insert-data"]
}
```

---

## Using Tools in the UI

### Creating an Agent with Tools

1. **Navigate to Playground**
2. **Select Model and Configure Agent**
3. **Scroll to the Tools Section**
4. **Select desired tools:**
   - Click on tool checkboxes
   - Tools with 🔑 icon require configuration
   - Tools with ⚙️ icon (when selected) allow editing configuration

5. **Configure tools that require API keys:**
   - Click the ⚙️ settings icon next to selected tools
   - Fill in required credentials
   - Click "Save Configuration"

6. **Complete agent setup:**
   - Add system prompt
   - Configure other settings
   - Click "Generate Agent"

### Tool Icons Reference

- 🦆 DuckDuckGo Search
- 🦁 Brave Search
- 🐙 GitHub Toolkit
- 📧 Gmail Toolkit
- 🎭 PlayWright Browser
- 🗄️ MCP Database Toolbox
- 🔑 Requires API key/configuration
- ⚙️ Edit configuration

## Backend Architecture

### New Files

1. **`backend/services/tools_service.py`**
   - Manages tool initialization
   - Handles tool-specific configurations
   - Returns initialized LangChain tool objects

2. **`backend/migrations/add_tool_configs.py`**
   - Database migration script
   - Adds `tool_configs` JSON column to agents table

3. **`frontend/src/components/ToolConfigDialog.tsx`**
   - Configuration dialog for tools requiring API keys
   - Tool-specific forms for each configurable tool

### Modified Files

1. **`backend/requirements.txt`**
   - Added dependencies for all 6 tools

2. **`backend/models/agent.py`**
   - Added `tool_configs` JSON column

3. **`backend/schemas/agent.py`**
   - Added `tool_configs` field to schemas

4. **`backend/services/agent_service.py`**
   - Integrated ToolsService
   - Load external tools based on agent configuration

5. **`backend/api/v1/agents.py`**
   - Added `/tools/available` endpoint
   - Updated response models

6. **`frontend/src/components/AgentBuilder.tsx`**
   - Added 6 new tools to TOOLS array
   - Implemented tool configuration UI
   - Added state management for tool configs

## API Endpoints

### Get Available Tools

```http
GET /api/v1/agents/tools/available
```

**Response:**
```json
{
  "duckduckgo_search": {
    "name": "DuckDuckGo Search",
    "description": "Web search using DuckDuckGo (no API key required)",
    "requires_api_key": false,
    "config_fields": {
      "max_results": {
        "type": "int",
        "default": 5,
        "description": "Maximum search results"
      }
    }
  },
  "brave_search": {
    "name": "Brave Search",
    "requires_api_key": true,
    ...
  }
}
```

## Environment Variables (Optional)

You can set tool API keys as environment variables instead of configuring them per agent:

```bash
# .env file
BRAVE_SEARCH_API_KEY=your_brave_api_key_here
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY=path/to/private-key.pem
GITHUB_REPOSITORY=owner/repo
```

When environment variables are set, agents can use them as fallback if no config is provided.

## Troubleshooting

### PlayWright Browser Issues

**Error:** "Executable doesn't exist"
```bash
# Solution: Install browsers
playwright install
```

### Gmail Authentication Issues

**Error:** "credentials.json not found"
```bash
# Solution: Download OAuth credentials from Google Cloud Console
# Place in backend/credentials.json
```

### GitHub App Issues

**Error:** "Authentication failed"
- Verify App ID is correct
- Check private key formatting (should include header/footer)
- Ensure app is installed on the target repository
- Confirm repository name format is "owner/repo"

### MCP Toolbox Issues

**Error:** "Connection refused"
```bash
# Solution: Start MCP server
toolbox --tools-file tools.yaml
```

**Error:** "Toolset not found"
- Check toolset name in tools.yaml
- Verify tools.yaml syntax
- Restart MCP server after config changes

## Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables for production**
3. **Encrypt sensitive configurations**
4. **Rotate API keys regularly**
5. **Use least-privilege permissions**
6. **Monitor API usage and costs**

## Examples

### Example 1: Research Agent with Web Search

```python
# Agent Configuration
{
  "name": "Research Assistant",
  "agent_type": "react",
  "tools": ["duckduckgo_search"],
  "tool_configs": {
    "duckduckgo_search": {
      "max_results": 10
    }
  }
}
```

### Example 2: GitHub Manager

```python
# Agent Configuration
{
  "name": "GitHub Manager",
  "agent_type": "react",
  "tools": ["github_toolkit"],
  "tool_configs": {
    "github_toolkit": {
      "app_id": "123456",
      "private_key": "...",
      "repository": "myorg/myrepo"
    }
  }
}
```

### Example 3: Multi-Tool Agent

```python
# Agent Configuration
{
  "name": "Full-Stack Assistant",
  "agent_type": "react",
  "tools": [
    "duckduckgo_search",
    "github_toolkit",
    "playwright_browser"
  ],
  "tool_configs": {
    "github_toolkit": {
      "app_id": "123456",
      "private_key": "...",
      "repository": "user/repo"
    }
  }
}
```

## Support

For issues or questions:
- Check tool-specific documentation links in configuration dialogs
- Review LangChain documentation: https://python.langchain.com/docs/
- Open an issue on GitHub

## Next Steps

1. Run the database migration
2. Install dependencies
3. Configure tools you need
4. Create an agent with tools
5. Test in the chat interface

Happy building! 🚀
