import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { X } from "lucide-react";

interface ToolConfigDialogProps {
  toolId: string;
  toolLabel: string;
  onSave: (toolId: string, config: any) => void;
  onClose: () => void;
  existingConfig?: any;
}

export function ToolConfigDialog({ toolId, toolLabel, onSave, onClose, existingConfig }: ToolConfigDialogProps) {
  const [config, setConfig] = useState(existingConfig || {});

  const handleSave = () => {
    onSave(toolId, config);
  };

  const renderConfigFields = () => {
    switch (toolId) {
      case "brave_search":
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="brave-api-key" className="text-sm">Brave Search API Key *</Label>
              <Input
                id="brave-api-key"
                type="password"
                placeholder="BSA..."
                value={config.api_key || ""}
                onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
                className="mt-2"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Get your API key from <a href="https://brave.com/search/api/" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Brave Search API</a>
              </p>
            </div>
            <div>
              <Label htmlFor="search-count" className="text-sm">Number of Results</Label>
              <Input
                id="search-count"
                type="number"
                min="1"
                max="10"
                value={config.search_count || 3}
                onChange={(e) => setConfig({ ...config, search_count: parseInt(e.target.value) })}
                className="mt-2"
              />
            </div>
          </div>
        );

      case "github_toolkit":
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="github-app-id" className="text-sm">GitHub App ID *</Label>
              <Input
                id="github-app-id"
                placeholder="123456"
                value={config.app_id || ""}
                onChange={(e) => setConfig({ ...config, app_id: e.target.value })}
                className="mt-2"
              />
            </div>
            <div>
              <Label htmlFor="github-private-key" className="text-sm">GitHub Private Key *</Label>
              <Textarea
                id="github-private-key"
                placeholder="-----BEGIN RSA PRIVATE KEY-----..."
                value={config.private_key || ""}
                onChange={(e) => setConfig({ ...config, private_key: e.target.value })}
                className="mt-2 min-h-[100px] font-mono text-xs"
              />
            </div>
            <div>
              <Label htmlFor="github-repo" className="text-sm">Repository (owner/repo) *</Label>
              <Input
                id="github-repo"
                placeholder="username/repository"
                value={config.repository || ""}
                onChange={(e) => setConfig({ ...config, repository: e.target.value })}
                className="mt-2"
              />
            </div>
            <div>
              <Label htmlFor="github-branch" className="text-sm">Working Branch (optional)</Label>
              <Input
                id="github-branch"
                placeholder="main"
                value={config.branch || ""}
                onChange={(e) => setConfig({ ...config, branch: e.target.value })}
                className="mt-2"
              />
            </div>
            <p className="text-xs text-muted-foreground">
              Create a GitHub App at <a href="https://github.com/settings/apps" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">GitHub Settings</a>
            </p>
          </div>
        );

      case "gmail_toolkit":
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="gmail-credentials" className="text-sm">Credentials File Path *</Label>
              <Input
                id="gmail-credentials"
                placeholder="credentials.json"
                value={config.credentials_file || "credentials.json"}
                onChange={(e) => setConfig({ ...config, credentials_file: e.target.value })}
                className="mt-2"
              />
            </div>
            <div>
              <Label htmlFor="gmail-token" className="text-sm">Token File Path</Label>
              <Input
                id="gmail-token"
                placeholder="token.json"
                value={config.token_file || "token.json"}
                onChange={(e) => setConfig({ ...config, token_file: e.target.value })}
                className="mt-2"
              />
            </div>
            <p className="text-xs text-muted-foreground">
              Set up OAuth2 credentials at <a href="https://console.cloud.google.com/apis/credentials" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Google Cloud Console</a>. 
              Download credentials.json and place it in your backend directory.
            </p>
          </div>
        );

      case "mcp_database":
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="mcp-server-url" className="text-sm">MCP Server URL *</Label>
              <Input
                id="mcp-server-url"
                placeholder="http://127.0.0.1:5000"
                value={config.server_url || "http://127.0.0.1:5000"}
                onChange={(e) => setConfig({ ...config, server_url: e.target.value })}
                className="mt-2"
              />
            </div>
            <div>
              <Label htmlFor="mcp-toolset" className="text-sm">Toolset Name</Label>
              <Input
                id="mcp-toolset"
                placeholder="hotel_toolset"
                value={config.toolset_name || ""}
                onChange={(e) => setConfig({ ...config, toolset_name: e.target.value })}
                className="mt-2"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Or specify individual tool names below (comma-separated)
              </p>
            </div>
            <div>
              <Label htmlFor="mcp-tools" className="text-sm">Individual Tool Names</Label>
              <Input
                id="mcp-tools"
                placeholder="search-hotels-by-location, book-hotel"
                value={config.tool_names_str || ""}
                onChange={(e) => {
                  const toolNames = e.target.value.split(',').map(t => t.trim()).filter(t => t);
                  setConfig({ ...config, tool_names_str: e.target.value, tool_names: toolNames });
                }}
                className="mt-2"
              />
            </div>
            <p className="text-xs text-muted-foreground">
              Install and run MCP Toolbox server. See <a href="https://github.com/googleapis/genai-toolbox" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">documentation</a>.
            </p>
          </div>
        );

      case "duckduckgo_search":
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="ddg-max-results" className="text-sm">Maximum Results</Label>
              <Input
                id="ddg-max-results"
                type="number"
                min="1"
                max="20"
                value={config.max_results || 5}
                onChange={(e) => setConfig({ ...config, max_results: parseInt(e.target.value) })}
                className="mt-2"
              />
            </div>
            <p className="text-xs text-muted-foreground">
              DuckDuckGo Search requires no API key. It's free and privacy-focused.
            </p>
          </div>
        );

      case "firecrawl":
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="firecrawl-api-key" className="text-sm">FireCrawl API Key *</Label>
              <Input
                id="firecrawl-api-key"
                type="password"
                placeholder="fc-..."
                value={config.api_key || ""}
                onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
                className="mt-2"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Get your API key from <a href="https://firecrawl.dev" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">FireCrawl Dashboard</a>
              </p>
            </div>
            <div className="bg-muted p-3 rounded-lg">
              <h4 className="text-sm font-medium mb-2">Available Tools:</h4>
              <ul className="text-xs space-y-1 text-muted-foreground">
                <li><strong>firecrawl_scrape:</strong> Scrape a single webpage (10-30 seconds)</li>
                <li><strong>firecrawl_crawl:</strong> Crawl entire website and subpages (20-45+ seconds)</li>
                <li><strong>firecrawl_map:</strong> Find semantically related pages (10-20 seconds)</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-2">
                ⚠️ FireCrawl operations can be slow. Please be patient when using these tools.
              </p>
            </div>
          </div>
        );

      default:
        return (
          <p className="text-sm text-muted-foreground">
            No configuration required for this tool.
          </p>
        );
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-card border border-border rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-card border-b border-border p-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold">Configure {toolLabel}</h3>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>
        
        <div className="p-6">
          {renderConfigFields()}
        </div>
        
        <div className="sticky bottom-0 bg-card border-t border-border p-4 flex gap-2 justify-end">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave}>
            Save Configuration
          </Button>
        </div>
      </div>
    </div>
  );
}
