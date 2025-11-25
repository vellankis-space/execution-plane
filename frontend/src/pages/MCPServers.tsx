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
  Radio
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
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';

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
  const [serverTools, setServerTools] = useState<MCPTool[]>([]);
  const [showToolsModal, setShowToolsModal] = useState(false);
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
        throw new Error('Connection failed');
      }
    } catch (error: any) {
      toast({
        title: 'Connection Failed',
        description: error.message,
        variant: 'destructive',
      });
    }
  };

  const handleDisconnect = async (server: MCPServer) => {
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
    }
  };

  const handleDelete = async (server: MCPServer) => {
    if (!confirm(`Are you sure you want to delete "${server.name}"?`)) {
      return;
    }

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
        fetchServers();
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete server',
        variant: 'destructive',
      });
    }
  };

  const handleViewTools = async (server: MCPServer) => {
    try {
      setSelectedServer(server);
      setShowToolsModal(true);
      const response = await fetch(
        `http://localhost:8000/api/v1/mcp-servers/${server.server_id}/tools`
      );

      if (response.ok) {
        const data = await response.json();
        setServerTools(data.tools || []);
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to fetch tools',
        variant: 'destructive',
      });
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
                <h1 className="text-2xl font-bold">MCP Servers</h1>
                <p className="text-sm text-muted-foreground">
                  Manage Model Context Protocol servers and external tool integrations
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
                  <Label htmlFor="transport">Transport Type *</Label>
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
                      <SelectItem value="stdio">STDIO (Local Process)</SelectItem>
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
                      <p className="text-xs text-muted-foreground mt-1">
                        The executable command to run the MCP server
                      </p>
                    </div>

                    <div>
                      <Label htmlFor="args">Arguments (JSON array)</Label>
                      <Textarea
                        id="args"
                        value={formData.args}
                        onChange={(e) => setFormData({ ...formData, args: e.target.value })}
                        placeholder='["-y", "@upstash/context7-mcp", "--api-key", "YOUR_API_KEY"]'
                        rows={3}
                        className="font-mono text-xs"
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        Command-line arguments as a JSON array. Example: ["-y", "package-name", "--flag", "value"]
                      </p>
                    </div>

                    <div>
                      <Label htmlFor="env">Environment Variables (JSON object)</Label>
                      <Textarea
                        id="env"
                        value={formData.env}
                        onChange={(e) => setFormData({ ...formData, env: e.target.value })}
                        placeholder='{"API_KEY": "your-api-key-here", "DEBUG": "true"}'
                        rows={3}
                        className="font-mono text-xs"
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        Environment variables as a JSON object (optional)
                      </p>
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

                <div className="flex justify-end gap-2 pt-4">
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

      {/* Content Section */}
      <div className="container mx-auto px-8 py-8">
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
        </div>
      ) : servers.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center h-64">
            <Server className="w-12 h-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No MCP Servers</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Get started by adding your first MCP server
            </p>
            <Button onClick={() => setShowAddModal(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add MCP Server
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {servers.map((server) => (
            <Card key={server.server_id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    {getTransportIcon(server.transport_type)}
                    <CardTitle className="text-lg">{server.name}</CardTitle>
                  </div>
                  {getStatusBadge(server.status)}
                </div>
                <CardDescription className="line-clamp-2">
                  {server.description || 'No description'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Transport:</span>
                    <Badge variant="outline">{server.transport_type.toUpperCase()}</Badge>
                  </div>

                  {server.url && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Endpoint:</span>
                      <span className="text-xs font-mono truncate max-w-[180px]">
                        {server.url}
                      </span>
                    </div>
                  )}

                  <div className="grid grid-cols-3 gap-2 pt-2 border-t">
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 text-sm font-medium">
                        <Wrench className="w-3 h-3" />
                        {server.tools_count}
                      </div>
                      <div className="text-xs text-muted-foreground">Tools</div>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 text-sm font-medium">
                        <FileText className="w-3 h-3" />
                        {server.resources_count}
                      </div>
                      <div className="text-xs text-muted-foreground">Resources</div>
                    </div>
                    <div className="text-center">
                      <div className="flex items-center justify-center gap-1 text-sm font-medium">
                        <Zap className="w-3 h-3" />
                        {server.prompts_count}
                      </div>
                      <div className="text-xs text-muted-foreground">Prompts</div>
                    </div>
                  </div>

                  {server.last_error && (
                    <div className="text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-2 rounded">
                      {server.last_error}
                    </div>
                  )}

                  <div className="flex gap-2 pt-2">
                    {server.status === 'active' ? (
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex-1"
                        onClick={() => handleDisconnect(server)}
                      >
                        <StopCircle className="w-3 h-3 mr-1" />
                        Disconnect
                      </Button>
                    ) : (
                      <Button
                        size="sm"
                        variant="outline"
                        className="flex-1"
                        onClick={() => handleConnect(server)}
                      >
                        <Play className="w-3 h-3 mr-1" />
                        Connect
                      </Button>
                    )}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleViewTools(server)}
                      disabled={server.status !== 'active'}
                    >
                      <Wrench className="w-3 h-3" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleEdit(server)}
                    >
                      <Edit className="w-3 h-3" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDelete(server)}
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Tools Viewer Modal */}
      <Dialog open={showToolsModal} onOpenChange={setShowToolsModal}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {selectedServer?.name} - Available Tools
            </DialogTitle>
            <DialogDescription>
              {serverTools.length} tool(s) discovered from this MCP server
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-3">
            {serverTools.map((tool, index) => (
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

            {serverTools.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                No tools available from this server
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
