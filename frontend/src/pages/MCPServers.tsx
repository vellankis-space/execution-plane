import React, { useState, useEffect } from 'react';
import {
  Plus,
  Server,
  Trash2,
  Edit,
  Play,
  StopCircle,
  CheckCircle,
  XCircle,
  Loader2,
  Wrench,
  FileText,
  Zap,
  RefreshCw,
  Globe,
  Terminal,
  Radio,
  AlertCircle,
  Search,
  ChevronDown,
  ChevronRight,
  FolderOpen,
  Folder
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface MCPServer {
  server_id: string;
  name: string;
  description: string;
  transport_type: string;
  status: string;
  url?: string;
  command?: string;
  tools_count: number;
  resources_count: number;
  prompts_count: number;
  last_connected?: string;
  last_error?: string;
  created_at: string;
}

interface MCPTool {
  name: string;
  description: string;
  inputSchema: any;
}

const MCPServers = () => {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingServer, setEditingServer] = useState<MCPServer | null>(null);
  const [selectedServer, setSelectedServer] = useState<MCPServer | null>(null);
  const [serverTools, setServerTools] = useState<Record<string, MCPTool[]>>({});
  const [loadingTools, setLoadingTools] = useState<Record<string, boolean>>({});
  const [showToolsModal, setShowToolsModal] = useState(false);
  const [connectingServerId, setConnectingServerId] = useState<string | null>(null);
  const [disconnectingServerId, setDisconnectingServerId] = useState<string | null>(null);
  const [deletingServerId, setDeletingServerId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedServers, setExpandedServers] = useState<Record<string, boolean>>({});
  const { toast } = useToast();

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    transport_type: 'http',
    url: '',
    auth_type: '',
    auth_token: '',
    command: '',
    args: '[]',
    env: '{}',
    cwd: ''
  });

  useEffect(() => {
    fetchServers();
  }, []);

  const fetchServers = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/mcp-servers');
      if (response.ok) {
        const data = await response.json();
        setServers(data);
      }
    } catch (error) {
      console.error('Error fetching MCP servers:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch MCP servers',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const payload: any = {
        name: formData.name,
        description: formData.description,
        transport_type: formData.transport_type,
      };

      if (formData.transport_type === 'http' || formData.transport_type === 'sse') {
        payload.url = formData.url;
        if (formData.auth_token) {
          payload.auth_type = formData.auth_type || 'bearer';
          payload.auth_token = formData.auth_token;
        }
      } else if (formData.transport_type === 'stdio') {
        payload.command = formData.command;
        try {
          payload.args = JSON.parse(formData.args);
        } catch {
          payload.args = [];
        }
        try {
          payload.env = JSON.parse(formData.env);
        } catch {
          payload.env = {};
        }
        if (formData.cwd) {
          payload.cwd = formData.cwd;
        }
      }

      const url = editingServer
        ? `http://localhost:8000/api/v1/mcp-servers/${editingServer.server_id}`
        : 'http://localhost:8000/api/v1/mcp-servers';

      const method = editingServer ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        toast({
          title: 'Success',
          description: `MCP server ${editingServer ? 'updated' : 'created'} successfully`,
        });
        setShowAddModal(false);
        resetForm();
        fetchServers();
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to save server');
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    }
  };

  const handleConnect = async (server: MCPServer) => {
    setConnectingServerId(server.server_id);

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/mcp-servers/${server.server_id}/connect`,
        { method: 'POST' }
      );

      if (response.ok) {
        toast({
          title: 'Connected',
          description: `Successfully connected to ${server.name}`,
        });
        fetchServers();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || 'Connection failed');
      }
    } catch (error: any) {
      toast({
        title: 'Connection Failed',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setConnectingServerId(null);
    }
  };

  const handleDisconnect = async (server: MCPServer) => {
    setDisconnectingServerId(server.server_id);

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/mcp-servers/${server.server_id}/disconnect`,
        { method: 'POST' }
      );

      if (response.ok) {
        toast({
          title: 'Disconnected',
          description: `Disconnected from ${server.name}`,
        });
        fetchServers();
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message,
        variant: 'destructive',
      });
    } finally {
      setDisconnectingServerId(null);
    }
  };

  const handleDelete = async (server: MCPServer) => {
    if (!confirm(`Are you sure you want to delete "${server.name}"?`)) {
      return;
    }

    setDeletingServerId(server.server_id);

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/mcp-servers/${server.server_id}`,
        { method: 'DELETE' }
      );

      if (response.ok) {
        toast({
          title: 'Deleted',
          description: `${server.name} deleted successfully`,
        });
        // Remove tools from cache when server is deleted
        setServerTools(prev => {
          const newTools = { ...prev };
          delete newTools[server.server_id];
          return newTools;
        });
        fetchServers();
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete server',
        variant: 'destructive',
      });
    } finally {
      setDeletingServerId(null);
    }
  };

  const fetchServerTools = async (serverId: string) => {
    // If we already have tools for this server, don't fetch again
    if (serverTools[serverId] && serverTools[serverId].length > 0) {
      return;
    }

    setLoadingTools(prev => ({ ...prev, [serverId]: true }));

    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/mcp-servers/${serverId}/tools`
      );

      if (response.ok) {
        const data = await response.json();
        setServerTools(prev => ({
          ...prev,
          [serverId]: data.tools || []
        }));
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to fetch tools',
        variant: 'destructive',
      });
    } finally {
      setLoadingTools(prev => ({ ...prev, [serverId]: false }));
    }
  };

  const handleToggleServerExpansion = async (serverId: string) => {
    const newState = !expandedServers[serverId];
    setExpandedServers(prev => ({
      ...prev,
      [serverId]: newState
    }));

    // If expanding, fetch tools
    if (newState) {
      await fetchServerTools(serverId);
    }
  };

  const handleEdit = (server: MCPServer) => {
    setEditingServer(server);
    setFormData({
      name: server.name,
      description: server.description || '',
      transport_type: server.transport_type,
      url: server.url || '',
      auth_type: '',
      auth_token: '',
      command: server.command || '',
      args: '[]',
      env: '{}',
      cwd: ''
    });
    setShowAddModal(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      transport_type: 'http',
      url: '',
      auth_type: '',
      auth_token: '',
      command: '',
      args: '[]',
      env: '{}',
      cwd: ''
    });
    setEditingServer(null);
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { color: string; icon: any }> = {
      active: { color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200', icon: CheckCircle },
      inactive: { color: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200', icon: StopCircle },
      error: { color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200', icon: XCircle },
      connecting: { color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200', icon: Loader2 },
    };

    const config = variants[status] || variants.inactive;
    const Icon = config.icon;

    return (
      <Badge className={config.color}>
        <Icon className="w-3 h-3 mr-1" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const getTransportIcon = (transportType: string) => {
    switch (transportType) {
      case 'http':
      case 'sse':
        return <Globe className="w-4 h-4" />;
      case 'stdio':
        return <Terminal className="w-4 h-4" />;
      default:
        return <Server className="w-4 h-4" />;
    }
  };

  // Filter servers based on search query
  const filteredServers = servers.filter(server =>
    server.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    server.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    server.transport_type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Header Section */}
      <div className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-30">
        <div className="container mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/25">
                <Server className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">MCP Servers & Tools Catalog</h1>
                <p className="text-sm text-muted-foreground">
                  Collection-wise view of servers and their available tools
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <Dialog open={showAddModal} onOpenChange={(open) => {
                setShowAddModal(open);
                if (!open) resetForm();
              }}>
                <DialogTrigger asChild>
                  <Button className="shine-effect bg-gradient-to-r from-primary to-primary/90">
                    <Plus className="w-4 h-4 mr-2" />
                    Add MCP Server
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>
                      {editingServer ? 'Edit MCP Server' : 'Add New MCP Server'}
                    </DialogTitle>
                    <DialogDescription>
                      Configure a Model Context Protocol server to extend agent capabilities
                    </DialogDescription>
                  </DialogHeader>

                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                      <Label htmlFor="name">Server Name *</Label>
                      <Input
                        id="name"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        placeholder="e.g., Weather API"
                        required
                      />
                    </div>

                    <div>
                      <Label htmlFor="description">Description</Label>
                      <Textarea
                        id="description"
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        placeholder="Describe what this server provides..."
                        rows={2}
                      />
                    </div>

                    <div>
                      <Label htmlFor="transport_type">Transport Type *</Label>
                      <Select
                        value={formData.transport_type}
                        onValueChange={(value) => setFormData({ ...formData, transport_type: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="http">HTTP</SelectItem>
                          <SelectItem value="sse">SSE (Server-Sent Events)</SelectItem>
                          <SelectItem value="stdio">STDIO</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    {(formData.transport_type === 'http' || formData.transport_type === 'sse') && (
                      <>
                        <div>
                          <Label htmlFor="url">Server URL *</Label>
                          <Input
                            id="url"
                            value={formData.url}
                            onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                            placeholder="https://api.example.com/mcp"
                            required
                          />
                        </div>

                        <div>
                          <Label htmlFor="auth_type">Authentication Type</Label>
                          <Select
                            value={formData.auth_type}
                            onValueChange={(value) => setFormData({ ...formData, auth_type: value })}
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="Select auth type" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="bearer">Bearer Token</SelectItem>
                              <SelectItem value="oauth">OAuth</SelectItem>
                              <SelectItem value="apikey">API Key</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>

                        {formData.auth_type && (
                          <div>
                            <Label htmlFor="auth_token">Authentication Token/API Key</Label>
                            <Input
                              id="auth_token"
                              type="password"
                              value={formData.auth_token}
                              onChange={(e) => setFormData({ ...formData, auth_token: e.target.value })}
                              placeholder="Enter your authentication token"
                            />
                          </div>
                        )}
                      </>
                    )}

                    {formData.transport_type === 'stdio' && (
                      <>
                        <div>
                          <Label htmlFor="command">Command *</Label>
                          <Input
                            id="command"
                            value={formData.command}
                            onChange={(e) => setFormData({ ...formData, command: e.target.value })}
                            placeholder="e.g., python server.py"
                            required
                          />
                        </div>

                        <div>
                          <Label htmlFor="args">Arguments (JSON array)</Label>
                          <Textarea
                            id="args"
                            value={formData.args}
                            onChange={(e) => setFormData({ ...formData, args: e.target.value })}
                            placeholder='["--port", "8080"]'
                            rows={2}
                          />
                        </div>

                        <div>
                          <Label htmlFor="env">Environment Variables (JSON object)</Label>
                          <Textarea
                            id="env"
                            value={formData.env}
                            onChange={(e) => setFormData({ ...formData, env: e.target.value })}
                            placeholder='{"DEBUG": "true", "PORT": "8080"}'
                            rows={2}
                          />
                        </div>

                        <div>
                          <Label htmlFor="cwd">Working Directory</Label>
                          <Input
                            id="cwd"
                            value={formData.cwd}
                            onChange={(e) => setFormData({ ...formData, cwd: e.target.value })}
                            placeholder="e.g., /path/to/server"
                          />
                        </div>
                      </>
                    )}

                    <div className="flex justify-end gap-3 pt-4">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                          setShowAddModal(false);
                          resetForm();
                        }}
                      >
                        Cancel
                      </Button>
                      <Button type="submit">
                        {editingServer ? 'Update Server' : 'Add Server'}
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <div className="container mx-auto px-8 py-4">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search servers or tools..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Content Section */}
      <div className="container mx-auto px-8 py-8">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
          </div>
        ) : filteredServers.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center h-64">
              <Server className="w-12 h-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">
                {searchQuery ? 'No servers match your search' : 'No MCP Servers'}
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                {searchQuery ? 'Try adjusting your search terms' : 'Get started by adding your first MCP server'}
              </p>
              {!searchQuery && (
                <Button onClick={() => setShowAddModal(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add MCP Server
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            <div className="text-sm text-muted-foreground">
              Showing {filteredServers.length} server{filteredServers.length !== 1 ? 's' : ''} with their tools
            </div>
            
            <div className="space-y-4">
              {filteredServers.map((server) => (
                <Card key={server.server_id} className="overflow-hidden">
                  {/* Server Header */}
                  <div 
                    className="flex items-center justify-between p-4 bg-muted/50 cursor-pointer hover:bg-muted/70 transition-colors"
                    onClick={() => handleToggleServerExpansion(server.server_id)}
                  >
                    <div className="flex items-center gap-3">
                      {expandedServers[server.server_id] ? (
                        <ChevronDown className="w-5 h-5 text-muted-foreground" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-muted-foreground" />
                      )}
                      <div className="flex items-center gap-2">
                        {getTransportIcon(server.transport_type)}
                        <div>
                          <h3 className="font-semibold text-lg flex items-center gap-2">
                            {server.name}
                            {server.name.includes('Docker') && (
                              <Badge variant="secondary" className="text-xs">
                                Docker
                              </Badge>
                            )}
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            {server.description || 'No description provided'}
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-1">
                          <Wrench className="w-4 h-4 text-muted-foreground" />
                          <span>{server.tools_count}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <FileText className="w-4 h-4 text-muted-foreground" />
                          <span>{server.resources_count}</span>
                        </div>
                      </div>
                      {getStatusBadge(server.status)}
                    </div>
                  </div>
                  
                  {/* Server Details and Tools */}
                  {expandedServers[server.server_id] && (
                    <div className="border-t">
                      <div className="p-4 bg-background">
                        {/* Server Actions */}
                        <div className="flex flex-wrap gap-2 mb-4">
                          {server.status === 'active' ? (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDisconnect(server);
                              }}
                              disabled={disconnectingServerId === server.server_id}
                            >
                              {disconnectingServerId === server.server_id ? (
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              ) : (
                                <StopCircle className="w-4 h-4 mr-2" />
                              )}
                              {disconnectingServerId === server.server_id ? 'Disconnecting...' : 'Disconnect'}
                            </Button>
                          ) : (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleConnect(server);
                              }}
                              disabled={connectingServerId === server.server_id}
                            >
                              {connectingServerId === server.server_id ? (
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              ) : (
                                <Play className="w-4 h-4 mr-2" />
                              )}
                              {connectingServerId === server.server_id ? 'Connecting...' : 'Connect'}
                            </Button>
                          )}
                          
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEdit(server);
                            }}
                          >
                            <Edit className="w-4 h-4 mr-2" />
                            Edit
                          </Button>
                          
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDelete(server);
                            }}
                            disabled={deletingServerId === server.server_id}
                          >
                            {deletingServerId === server.server_id ? (
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            ) : (
                              <Trash2 className="w-4 h-4 mr-2" />
                            )}
                            Delete
                          </Button>
                        </div>
                        
                        {/* Server Info */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                          <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                            <span className="text-muted-foreground">Transport:</span>
                            <Badge variant="outline">{server.transport_type.toUpperCase()}</Badge>
                          </div>
                          
                          {server.url && (
                            <div className="flex items-center justify-between p-3 bg-muted/30 rounded-lg">
                              <span className="text-muted-foreground">Endpoint:</span>
                              <span className="text-sm font-mono truncate max-w-[70%]">
                                {server.url}
                              </span>
                            </div>
                          )}
                        </div>
                        
                        {server.last_error && (
                          <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800 mb-6">
                            <div className="flex items-start gap-2">
                              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                              <div>
                                <p className="text-sm font-medium text-red-800 dark:text-red-200">Connection Error</p>
                                <p className="text-sm text-red-700 dark:text-red-300 mt-1">
                                  {server.last_error}
                                </p>
                              </div>
                            </div>
                          </div>
                        )}
                        
                        {/* Tools Section */}
                        <div className="border-t pt-4">
                          <div className="flex items-center gap-2 mb-4">
                            <FolderOpen className="w-5 h-5 text-muted-foreground" />
                            <h4 className="font-medium text-lg">Available Tools</h4>
                            <Badge variant="secondary">{serverTools[server.server_id]?.length || 0} tools</Badge>
                          </div>
                          
                          {loadingTools[server.server_id] ? (
                            <div className="flex items-center justify-center py-8">
                              <Loader2 className="w-6 h-6 animate-spin text-muted-foreground mr-2" />
                              <span>Loading tools...</span>
                            </div>
                          ) : server.status !== 'active' ? (
                            <div className="text-center py-8 text-muted-foreground">
                              <p>Connect to the server to view and use its tools</p>
                              <Button 
                                variant="outline" 
                                className="mt-3"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleConnect(server);
                                }}
                                disabled={connectingServerId === server.server_id}
                              >
                                {connectingServerId === server.server_id ? (
                                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                ) : (
                                  <Play className="w-4 h-4 mr-2" />
                                )}
                                Connect Server
                              </Button>
                            </div>
                          ) : !serverTools[server.server_id] || serverTools[server.server_id].length === 0 ? (
                            <div className="text-center py-8 text-muted-foreground">
                              <p>No tools available from this server</p>
                              <Button 
                                variant="outline" 
                                className="mt-3"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  fetchServerTools(server.server_id);
                                }}
                              >
                                <RefreshCw className="w-4 h-4 mr-2" />
                                Refresh Tools
                              </Button>
                            </div>
                          ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                              {serverTools[server.server_id].map((tool, index) => (
                                <Card 
                                  key={index} 
                                  className="hover:shadow-md transition-shadow cursor-pointer"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    // Show tool details in modal
                                    setSelectedServer(server);
                                    setServerTools(prev => ({
                                      ...prev,
                                      temp: [tool]
                                    }));
                                    setShowToolsModal(true);
                                  }}
                                >
                                  <CardHeader className="pb-2">
                                    <CardTitle className="text-base flex items-center gap-2">
                                      <Wrench className="w-4 h-4 text-muted-foreground" />
                                      <span className="truncate">{tool.name}</span>
                                    </CardTitle>
                                  </CardHeader>
                                  <CardContent>
                                    <CardDescription className="line-clamp-2 text-xs">
                                      {tool.description || 'No description available'}
                                    </CardDescription>
                                    <div className="mt-3 text-xs text-muted-foreground">
                                      Click to view details
                                    </div>
                                  </CardContent>
                                </Card>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Tools Viewer Modal */}
        <Dialog open={showToolsModal} onOpenChange={(open) => {
          setShowToolsModal(open);
          if (!open) {
            // Clean up temp tools if they exist
            setServerTools(prev => {
              const newTools = { ...prev };
              delete newTools.temp;
              return newTools;
            });
          }
        }}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {selectedServer?.name} - Tool Details
              </DialogTitle>
              <DialogDescription>
                Detailed information about the selected tool
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-3">
              {(serverTools.temp || []).map((tool, index) => (
                <Card key={index}>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <Wrench className="w-4 h-4" />
                      {tool.name}
                    </CardTitle>
                    <CardDescription>{tool.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-sm">
                      <span className="font-medium">Input Schema:</span>
                      <pre className="mt-2 p-3 bg-muted rounded text-xs overflow-x-auto">
                        {JSON.stringify(tool.inputSchema, null, 2)}
                      </pre>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {(serverTools.temp || []).length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  No tool details available
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default MCPServers;