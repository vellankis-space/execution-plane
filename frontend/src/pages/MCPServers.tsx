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
  Globe,
  Terminal,
  AlertCircle,
  Search,
  FolderOpen,
  MoreVertical,
  ExternalLink
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
  DialogFooter,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from '@/hooks/use-toast';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MCPServerModal } from '@/components/MCPServerModal';
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

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
  const [viewingServer, setViewingServer] = useState<MCPServer | null>(null);
  const [serverTools, setServerTools] = useState<Record<string, MCPTool[]>>({});
  const [loadingTools, setLoadingTools] = useState<Record<string, boolean>>({});
  const [connectingServerId, setConnectingServerId] = useState<string | null>(null);
  const [disconnectingServerId, setDisconnectingServerId] = useState<string | null>(null);
  const [deletingServerId, setDeletingServerId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const { toast } = useToast();

  // Form state for Edit
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
        if (viewingServer?.server_id === server.server_id) {
          // Refresh tools for viewing server if it's the one we just connected
          // We need to fetch tools immediately for the UI to update
          fetchServerTools(server.server_id);
          // And update the viewingServer status locally so the UI reflects active state immediately without wait for fetchServers
          setViewingServer({ ...viewingServer, status: 'active' });
        }
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
        if (viewingServer?.server_id === server.server_id) {
          setViewingServer({ ...viewingServer, status: 'inactive' });
          setServerTools(prev => {
            const newTools = { ...prev };
            delete newTools[server.server_id];
            return newTools;
          });
        }
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
        if (viewingServer?.server_id === server.server_id) {
          setViewingServer(null);
        }
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

  const handleViewDetails = async (server: MCPServer) => {
    setViewingServer(server);
    if (server.status === 'active') {
      await fetchServerTools(server.server_id);
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
      active: { color: 'bg-green-100/10 text-green-600 dark:text-green-400 border-green-200/20', icon: CheckCircle },
      inactive: { color: 'bg-gray-100/10 text-gray-600 dark:text-gray-400 border-gray-200/20', icon: StopCircle },
      error: { color: 'bg-red-100/10 text-red-600 dark:text-red-400 border-red-200/20', icon: XCircle },
      connecting: { color: 'bg-yellow-100/10 text-yellow-600 dark:text-yellow-400 border-yellow-200/20', icon: Loader2 },
    };

    const config = variants[status] || variants.inactive;
    const Icon = config.icon;

    return (
      <Badge variant="outline" className={`${config.color} border gap-1.5 py-1`}>
        <Icon className={`w-3.5 h-3.5 ${status === 'connecting' ? 'animate-spin' : ''}`} />
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

  const filteredServers = servers.filter(server =>
    server.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    server.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    server.transport_type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-muted/40 p-8">
      {/* Header Section */}
      <div className="flex flex-col gap-6 mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight mb-1">MCP Servers</h1>
            <p className="text-muted-foreground">
              Manage your Model Context Protocol servers and connected tools
            </p>
          </div>
          <div className="flex gap-3">
            <MCPServerModal onServerAdded={fetchServers} />

            <Dialog open={showAddModal && editingServer !== null} onOpenChange={(open) => {
              if (!open) {
                setShowAddModal(false);
                resetForm();
              }
            }}>
              <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Edit MCP Server</DialogTitle>
                  <DialogDescription>
                    Update the configuration for this MCP server
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
                        <SelectItem value="stdio">STDIO (Local Process)</SelectItem>
                        <SelectItem value="http">HTTP</SelectItem>
                        <SelectItem value="sse">SSE (Server-Sent Events)</SelectItem>
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
                        <Label htmlFor="auth_token">API Key / Token (optional)</Label>
                        <Input
                          id="auth_token"
                          type="password"
                          value={formData.auth_token}
                          onChange={(e) => setFormData({ ...formData, auth_token: e.target.value })}
                          placeholder="Enter authentication token"
                        />
                      </div>
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
                          placeholder="e.g., bunx, npx, python, node, uvx"
                          required
                        />
                      </div>

                      <div>
                        <Label htmlFor="args">Arguments (JSON array)</Label>
                        <Textarea
                          id="args"
                          value={formData.args}
                          onChange={(e) => setFormData({ ...formData, args: e.target.value })}
                          placeholder='["--arg", "value"]'
                          rows={3}
                          className="font-mono text-xs"
                        />
                      </div>

                      <div>
                        <Label htmlFor="env">Environment Variables (JSON object)</Label>
                        <Textarea
                          id="env"
                          value={formData.env}
                          onChange={(e) => setFormData({ ...formData, env: e.target.value })}
                          placeholder='{"KEY": "VALUE"}'
                          rows={3}
                          className="font-mono text-xs"
                        />
                      </div>

                      <div>
                        <Label htmlFor="cwd">Working Directory (optional)</Label>
                        <Input
                          id="cwd"
                          value={formData.cwd}
                          onChange={(e) => setFormData({ ...formData, cwd: e.target.value })}
                          placeholder="/path/to/working/directory"
                        />
                      </div>
                    </>
                  )}

                  <div className="flex gap-3 pt-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setShowAddModal(false);
                        resetForm();
                      }}
                      className="flex-1"
                    >
                      Cancel
                    </Button>
                    <Button type="submit" className="flex-1">
                      Update Server
                    </Button>
                  </div>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Search Filter */}
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            className="pl-9"
            placeholder="Search servers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Grid Content */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
        </div>
      ) : filteredServers.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed rounded-lg">
          <Server className="w-12 h-12 text-muted-foreground mb-4" />
          <p className="text-lg font-medium text-muted-foreground">No servers found</p>
          <p className="text-sm text-muted-foreground">
            {searchQuery ? 'Try adjusting your search terms' : 'Add a new server to get started'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredServers.map((server) => (
            <Card
              key={server.server_id}
              className="group flex flex-col h-full hover:shadow-lg hover:border-primary/50 transition-all duration-300"
            >
              <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg bg-primary/5 text-primary`}>
                    {getTransportIcon(server.transport_type)}
                  </div>
                  <div>
                    <CardTitle className="text-base font-semibold leading-none mb-1">
                      {server.name}
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-[10px] h-5 px-1.5 font-normal">
                        {server.transport_type.toUpperCase()}
                      </Badge>
                      {server.name.includes('Docker') && (
                        <Badge variant="outline" className="text-[10px] h-5 px-1.5 font-normal border-blue-200 text-blue-600 bg-blue-50 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-800">
                          Docker
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
                {getStatusBadge(server.status)}
              </CardHeader>

              <CardContent className="flex-1 pb-4">
                <p className="text-sm text-muted-foreground line-clamp-2 mb-4 h-10">
                  {server.description || 'No description provided for this server.'}
                </p>

                <div className="grid grid-cols-3 gap-2 py-3 border-t border-b bg-muted/20 -mx-6 px-6">
                  <div className="flex flex-col items-center justify-center gap-1">
                    <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Tools</span>
                    <div className="flex items-center gap-1.5">
                      <Wrench className="w-3.5 h-3.5 text-primary" />
                      <span className="font-semibold">{server.tools_count}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-center justify-center gap-1 border-l border-r border-border/50">
                    <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Resources</span>
                    <div className="flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5 text-primary" />
                      <span className="font-semibold">{server.resources_count}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-center justify-center gap-1">
                    <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Prompts</span>
                    <div className="flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5 text-primary" />
                      <span className="font-semibold">{server.prompts_count}</span>
                    </div>
                  </div>
                </div>

                {server.last_error && (
                  <div className="mt-4 p-2.5 bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-900/50 rounded text-xs text-red-600 dark:text-red-400 flex gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span className="line-clamp-2">{server.last_error}</span>
                  </div>
                )}
              </CardContent>

              <CardFooter className="pt-2 gap-2">
                {server.status === 'active' ? (
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 h-8 text-xs hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20 dark:hover:text-red-400 border-dashed"
                    onClick={() => handleDisconnect(server)}
                    disabled={disconnectingServerId === server.server_id}
                  >
                    {disconnectingServerId === server.server_id ? (
                      <Loader2 className="w-3 h-3 mr-1.5 animate-spin" />
                    ) : (
                      <StopCircle className="w-3 h-3 mr-1.5" />
                    )}
                    Disconnect
                  </Button>
                ) : (
                  <Button
                    variant="default"
                    size="sm"
                    className="flex-1 h-8 text-xs"
                    onClick={() => handleConnect(server)}
                    disabled={connectingServerId === server.server_id}
                  >
                    {connectingServerId === server.server_id ? (
                      <Loader2 className="w-3 h-3 mr-1.5 animate-spin" />
                    ) : (
                      <Play className="w-3 h-3 mr-1.5" />
                    )}
                    Connect
                  </Button>
                )}

                <div className="flex gap-1 ml-auto">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => handleViewDetails(server)}
                    title="View Details"
                  >
                    <ExternalLink className="w-4 h-4 text-muted-foreground" />
                  </Button>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreVertical className="w-4 h-4 text-muted-foreground" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => handleEdit(server)}>
                        <Edit className="w-4 h-4 mr-2" />
                        Edit Configuration
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        className="text-red-600 focus:text-red-600"
                        onClick={() => handleDelete(server)}
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete Server
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {/* Server Details Dialog */}
      <Dialog open={!!viewingServer} onOpenChange={(open) => !open && setViewingServer(null)}>
        <DialogContent className="max-w-3xl max-h-[80vh] flex flex-col p-0 gap-0">
          <DialogHeader className="p-6 pb-2">
            <div className="flex items-center gap-3 mb-2">
              <div className={`p-2 rounded-lg bg-primary/10 text-primary`}>
                {viewingServer && getTransportIcon(viewingServer.transport_type)}
              </div>
              <div>
                <DialogTitle className="text-xl">
                  {viewingServer?.name}
                </DialogTitle>
                <DialogDescription>
                  {viewingServer?.description || 'No description provided'}
                </DialogDescription>
              </div>
              <div className="ml-auto">
                {viewingServer && getStatusBadge(viewingServer.status)}
              </div>
            </div>
          </DialogHeader>

          <div className="flex-1 overflow-hidden flex flex-col min-h-0">
            <Tabs defaultValue="tools" className="flex-1 flex flex-col min-h-0">
              <div className="px-6 border-b flex-none">
                <TabsList className="bg-transparent h-auto p-0 gap-6">
                  <TabsTrigger
                    value="tools"
                    className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none py-3 px-1"
                  >
                    Tools ({viewingServer?.tools_count || 0})
                  </TabsTrigger>
                  <TabsTrigger
                    value="config"
                    className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none py-3 px-1"
                  >
                    Configuration
                  </TabsTrigger>
                </TabsList>
              </div>

              <TabsContent value="tools" className="flex-1 overflow-y-auto m-0 p-0 min-h-0 outline-none focus:ring-0 ring-0">
                <div className="p-6 space-y-4">
                  {viewingServer && loadingTools[viewingServer.server_id] ? (
                    <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                      <Loader2 className="w-8 h-8 animate-spin mb-2" />
                      <p>Loading tools...</p>
                    </div>
                  ) : viewingServer?.status !== 'active' ? (
                    <div className="flex flex-col items-center justify-center py-12 text-muted-foreground bg-muted/30 rounded-lg mx-6 border border-dashed">
                      <StopCircle className="w-8 h-8 mb-2 opacity-50" />
                      <p>Server is not connected</p>
                      <Button
                        variant="outline"
                        size="sm"
                        className="mt-4"
                        onClick={() => handleConnect(viewingServer!)}
                      >
                        Connect to view tools
                      </Button>
                    </div>
                  ) : serverTools[viewingServer?.server_id || '']?.length > 0 ? (
                    serverTools[viewingServer!.server_id].map((tool, idx) => (
                      <Card key={idx} className="bg-card/50 border-border/50">
                        <CardHeader className="py-3">
                          <div className="flex items-center justify-between">
                            <div className="font-mono text-sm font-semibold text-primary">
                              {tool.name}
                            </div>
                          </div>
                        </CardHeader>
                        <CardContent className="py-3 pt-0 text-sm text-muted-foreground">
                          {tool.description}
                          {tool.inputSchema && (
                            <div className="mt-3 p-3 bg-muted/50 rounded-md">
                              <p className="text-xs font-medium uppercase mb-2 text-muted-foreground">Input Schema</p>
                              <pre className="text-xs font-mono overflow-auto max-h-32">
                                {JSON.stringify(tool.inputSchema, null, 2)}
                              </pre>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))
                  ) : (
                    <div className="text-center py-12 text-muted-foreground">
                      <Wrench className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p>No tools available</p>
                    </div>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="config" className="flex-1 overflow-y-auto m-0 p-0 min-h-0 outline-none focus:ring-0 ring-0">
                <div className="p-6">
                  <div className="space-y-4">
                    <div className="grid gap-1">
                      <span className="text-sm font-medium text-muted-foreground">Transport Type</span>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline">{viewingServer?.transport_type.toUpperCase()}</Badge>
                      </div>
                    </div>

                    {viewingServer?.url && (
                      <div className="grid gap-1">
                        <span className="text-sm font-medium text-muted-foreground">URL</span>
                        <code className="text-sm bg-muted px-2 py-1 rounded font-mono break-all">
                          {viewingServer.url}
                        </code>
                      </div>
                    )}

                    {viewingServer?.command && (
                      <div className="grid gap-1">
                        <span className="text-sm font-medium text-muted-foreground">Command</span>
                        <code className="text-sm bg-muted px-2 py-1 rounded font-mono break-all">
                          {viewingServer.command}
                        </code>
                      </div>
                    )}

                    <div className="grid gap-1">
                      <span className="text-sm font-medium text-muted-foreground">Created At</span>
                      <span className="text-sm">
                        {viewingServer && new Date(viewingServer.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          <DialogFooter className="p-4 border-t bg-muted/10">
            <Button variant="outline" onClick={() => setViewingServer(null)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default MCPServers;