import React, { useState, useEffect } from 'react';
import { Check, X, Search, Loader2, ChevronDown, ChevronRight, AlertCircle } from 'lucide-react';

interface Tool {
  name: string;
  description?: string;
}

interface MCPToolSelectorProps {
  serverId: string;
  serverName: string;
  initialSelectedTools?: string[] | null;
  onToolsChange: (selectedTools: string[] | null) => void;
}

const MCPToolSelector: React.FC<MCPToolSelectorProps> = ({
  serverId,
  serverName,
  initialSelectedTools,
  onToolsChange,
}) => {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTools, setSelectedTools] = useState<Set<string>>(
    new Set(initialSelectedTools || [])
  );
  const [searchQuery, setSearchQuery] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectAllTools, setSelectAllTools] = useState(
    initialSelectedTools === null || initialSelectedTools === undefined
  );

  // Fetch available tools for this MCP server
  useEffect(() => {
    const fetchTools = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetch(`http://localhost:8000/api/v1/mcp-servers/${serverId}/tools`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch tools');
        }
        
        const data = await response.json();
        setTools(data.tools || []);
        
        // If "all tools" mode and we now have the tools, set them all as selected
        if (selectAllTools && data.tools) {
          const allToolNames = data.tools.map((t: Tool) => t.name);
          setSelectedTools(new Set(allToolNames));
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load tools');
      } finally {
        setLoading(false);
      }
    };

    if (isExpanded && tools.length === 0) {
      fetchTools();
    }
  }, [serverId, isExpanded, selectAllTools]);

  // Filter tools based on search query
  const filteredTools = tools.filter(tool =>
    tool.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    tool.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleToolToggle = (toolName: string) => {
    const newSelected = new Set(selectedTools);
    
    if (newSelected.has(toolName)) {
      newSelected.delete(toolName);
    } else {
      newSelected.add(toolName);
    }
    
    setSelectedTools(newSelected);
    setSelectAllTools(false);
    
    // Notify parent of changes
    onToolsChange(Array.from(newSelected));
  };

  const handleSelectAll = () => {
    if (selectAllTools) {
      // Switch to manual selection mode
      setSelectAllTools(false);
      setSelectedTools(new Set());
      onToolsChange([]);
    } else {
      // Switch to "all tools" mode
      setSelectAllTools(true);
      const allToolNames = tools.map(t => t.name);
      setSelectedTools(new Set(allToolNames));
      onToolsChange(null); // null means "all tools"
    }
  };

  const handleSelectNone = () => {
    setSelectAllTools(false);
    setSelectedTools(new Set());
    onToolsChange([]);
  };

  return (
    <div className="bg-background">
      {/* Header */}
      <div
        className="flex items-center justify-between p-3 cursor-pointer hover:bg-muted/50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="w-4 h-4 text-muted-foreground" />
          )}
          <span className="text-sm font-medium">Tool Selection</span>
        </div>
        
        <div className="flex items-center gap-2">
          {selectAllTools ? (
            <span className="text-xs text-blue-600 dark:text-blue-400 font-medium">
              All tools ({tools.length})
            </span>
          ) : (
            <span className="text-xs text-muted-foreground">
              {selectedTools.size} / {tools.length} selected
            </span>
          )}
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-border">
          {loading ? (
            <div className="p-8 flex items-center justify-center">
              <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
              <span className="ml-2 text-gray-600 dark:text-gray-400">Loading tools...</span>
            </div>
          ) : error ? (
            <div className="p-4 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mr-2" />
                <span className="text-sm text-red-700 dark:text-red-300">{error}</span>
              </div>
            </div>
          ) : (
            <>
              {/* Controls */}
              <div className="p-3 bg-muted/50 space-y-2">
                {/* Search */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search tools..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 text-sm border border-input rounded-lg focus:ring-2 focus:ring-ring focus:border-transparent bg-background"
                  />
                </div>

                {/* Bulk Actions */}
                <div className="flex gap-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelectAll();
                    }}
                    className="flex-1 px-3 py-1.5 text-xs font-medium rounded-lg border border-input hover:bg-muted transition-colors"
                  >
                    {selectAllTools ? 'Manual Selection' : 'Select All'}
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelectNone();
                    }}
                    className="flex-1 px-3 py-1.5 text-xs font-medium rounded-lg border border-input hover:bg-muted transition-colors"
                  >
                    Deselect All
                  </button>
                </div>

                {selectAllTools && (
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      <strong>All tools mode:</strong> All tools from this MCP server will be loaded,
                      including any new tools added in the future.
                    </p>
                  </div>
                )}
              </div>

              {/* Tools List */}
              <div className="max-h-80 overflow-y-auto">
                {filteredTools.length === 0 ? (
                  <div className="p-8 text-center text-muted-foreground text-sm">
                    {searchQuery ? 'No tools match your search' : 'No tools available'}
                  </div>
                ) : (
                  <div className="divide-y divide-border">
                    {filteredTools.map((tool) => (
                      <div
                        key={tool.name}
                        className={`p-3 hover:bg-muted/50 cursor-pointer transition-colors ${
                          selectedTools.has(tool.name) ? 'bg-blue-50 dark:bg-blue-900/10' : ''
                        }`}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleToolToggle(tool.name);
                        }}
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className={`flex-shrink-0 w-4 h-4 rounded border-2 flex items-center justify-center mt-0.5 ${
                              selectedTools.has(tool.name)
                                ? 'bg-blue-600 border-blue-600'
                                : 'border-input'
                            }`}
                          >
                            {selectedTools.has(tool.name) && (
                              <Check className="w-3 h-3 text-white" />
                            )}
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium break-words">
                              {tool.name}
                            </p>
                            {tool.description && (
                              <p className="text-xs text-muted-foreground mt-0.5 break-words line-clamp-2">
                                {tool.description}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default MCPToolSelector;
