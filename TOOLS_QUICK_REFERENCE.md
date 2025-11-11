# 🚀 LangChain Tools - Quick Reference

## Quick Setup (3 Steps)

```bash
# 1. Run setup script
bash setup_tools.sh

# 2. Start backend
cd backend && uvicorn main:app --reload

# 3. Start frontend (new terminal)
cd frontend && npm run dev
```

Open http://localhost:5173 and create agents with tools!

---

## 🛠️ Tools at a Glance

| Tool | Icon | API Key? | Setup Time | Use Case |
|------|------|----------|------------|----------|
| **DuckDuckGo Search** | 🦆 | No | 0 min | Free web search |
| **Brave Search** | 🦁 | Yes | 5 min | Privacy-focused search |
| **GitHub Toolkit** | 🐙 | Yes | 15 min | Repository management |
| **Gmail Toolkit** | 📧 | Yes | 10 min | Email operations |
| **PlayWright Browser** | 🎭 | No | 2 min | Web automation |
| **MCP Database** | 🗄️ | No* | 20 min | Database queries |
| **FireCrawl** | 🕷️ | Yes | 5 min | Web scraping & crawling |

*Requires MCP server (not API key)

---

## ⚡ Quick Start Guide

### DuckDuckGo Search (Easiest)
```bash
# No setup needed - just use it!
```
1. Select tool in UI ✅ Done!

### Brave Search
```bash
# Get API key: https://brave.com/search/api/
```
1. Sign up for Brave Search API (free tier available)
2. Get API key (starts with "BSA")
3. In UI: Select tool → Click ⚙️ → Enter API key

### GitHub Toolkit
```bash
# Create app: https://github.com/settings/apps
```
1. Create GitHub App
2. Set permissions (Contents, Issues, PRs)
3. Generate private key
4. In UI: Configure App ID, key, repo

### Gmail Toolkit
```bash
# Setup: https://console.cloud.google.com/
```
1. Enable Gmail API in Google Cloud
2. Create OAuth credentials
3. Download credentials.json → backend/
4. In UI: Configure (OAuth on first run)

### PlayWright Browser
```bash
playwright install  # Install browsers once
```
1. Run install command ✅ Done!

### MCP Database
```bash
brew install mcp-toolbox  # or download binary
toolbox --tools-file tools.yaml  # Start server
```
1. Install MCP Toolbox
2. Create tools.yaml config
3. Start server
4. In UI: Configure server URL

### FireCrawl
```bash
# No additional installation needed - uses langchain-community
```
1. Get API key from [FireCrawl Dashboard](https://firecrawl.dev/)
2. API key should start with "fc-"
3. In UI: Select tool → Click ⚙️ → Enter API key

---

## 💡 Common Use Cases

### Research & Search
```
Tools: DuckDuckGo + Brave Search + PlayWright
Use: "Research the latest trends in AI and summarize findings"
```

### Development
```
Tools: GitHub Toolkit + PlayWright
Use: "Check my repo issues and test the website"
```

### Communication
```
Tools: Gmail Toolkit
Use: "Check my unread emails and draft replies"
```

### Data Analysis
```
Tools: MCP Database + DuckDuckGo
Use: "Query sales data and research market trends"
```

---

## 🔑 API Keys & Credentials

### Where to Get Them

| Tool | Get Key Here | Type |
|------|-------------|------|
| Brave Search | https://brave.com/search/api/ | API Key |
| GitHub | https://github.com/settings/apps | App Credentials |
| Gmail | https://console.cloud.google.com/ | OAuth2 |
| FireCrawl | https://firecrawl.dev/ | API Key |

### How to Configure

**Option 1: Per Agent (Recommended)**
- Select tool in UI
- Click ⚙️ settings icon
- Enter credentials
- Save

**Option 2: Environment Variables**
```bash
# backend/.env
BRAVE_SEARCH_API_KEY=your_key
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY=...
FIRECRAWL_API_KEY=fc_your_key
```

---

## 🐛 Quick Troubleshooting

### "Module not found" Error
```bash
cd backend
pip install -r requirements.txt
```

### "Playwright executable doesn't exist"
```bash
playwright install
```

### "Gmail credentials not found"
```bash
# Download credentials.json from Google Cloud Console
# Place in: backend/credentials.json
```

### "GitHub authentication failed"
- Check App ID is correct
- Verify private key format (include headers)
- Ensure app installed on repository

### "MCP connection refused"
```bash
# Start MCP server in separate terminal
toolbox --tools-file tools.yaml
```

---

## 📝 Configuration Examples

### Brave Search
```json
{
  "api_key": "BSA1234567890abcdef",
  "search_count": 5
}
```

### GitHub
```json
{
  "app_id": "123456",
  "private_key": "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----",
  "repository": "username/repo-name"
}
```

### Gmail
```json
{
  "credentials_file": "credentials.json",
  "token_file": "token.json"
}
```

### MCP Database
```json
{
  "server_url": "http://127.0.0.1:5000",
  "toolset_name": "my_toolset"
}
```

### FireCrawl
```json
{
  "api_key": "fc1234567890abcdef",
  "scrape_timeout": 30,
  "crawl_timeout": 45
}
```

---

## 🎯 Tips & Best Practices

### Security
- ✅ Never commit API keys to git
- ✅ Use environment variables for production
- ✅ Rotate keys regularly
- ✅ Use least-privilege permissions

### Performance
- ✅ Start with free tools (DuckDuckGo, PlayWright)
- ✅ Test locally before production
- ✅ Monitor API usage and costs
- ✅ Cache results when possible

### Development
- ✅ Test each tool individually first
- ✅ Use descriptive agent names
- ✅ Start with simple prompts
- ✅ Review logs for debugging

---

## 📚 Documentation Links

- **Full Guide:** [TOOLS_IMPLEMENTATION_GUIDE.md](./TOOLS_IMPLEMENTATION_GUIDE.md)
- **Summary:** [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- **LangChain Docs:** https://python.langchain.com/docs/
- **Project README:** [README.md](./README.md)

---

## 🆘 Need Help?

1. Check TOOLS_IMPLEMENTATION_GUIDE.md
2. Review error messages carefully
3. Verify API keys/credentials
4. Check tool-specific documentation
5. Test tools individually

---

## ✅ Testing Checklist

- [ ] Setup script completed successfully
- [ ] Backend server running
- [ ] Frontend accessible at localhost:5173
- [ ] Can select tools in UI
- [ ] Configuration dialog opens for tools with 🔑
- [ ] Can save tool configurations
- [ ] Agent creation successful with tools
- [ ] Can chat with agent
- [ ] Tools execute correctly

---

## 🎉 You're Ready!

All tools are implemented and ready to use. Create your first agent with tools and start building! 🚀

**Happy Building!** ✨
