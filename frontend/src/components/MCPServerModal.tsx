import React, { useState } from 'react';
import { Plus, Loader2 } from 'lucide-react';
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

interface MCPServerModalProps {
  onServerAdded?: () => void;
}

export const MCPServerModal: React.FC<MCPServerModalProps> = ({ onServerAdded }) => {
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const { toast } = useToast();

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
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      // Check if server with same name already exists
      const checkResponse = await fetch('http://localhost:8000/api/v1/mcp-servers');
      if (checkResponse.ok) {
        const existingServers = await checkResponse.json();
        const duplicateName = existingServers.find(
          (server: any) => server.name.toLowerCase() === formData.name.toLowerCase()
        );
        
        if (duplicateName) {
          toast({
            title: 'Duplicate Server Name',
            description: `A server named "${formData.name}" already exists. Please choose a different name.`,
            variant: 'destructive',
          });
          setSubmitting(false);
          return;
        }
      }

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

      const response = await fetch('http://localhost:8000/api/v1/mcp-servers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const createdServer = await response.json();
        
        // Try to connect the server automatically
        try {
          const connectResponse = await fetch(
            `http://localhost:8000/api/v1/mcp-servers/${createdServer.server_id}/connect`,
            { method: 'POST' }
          );
          
          if (connectResponse.ok) {
            const connectData = await connectResponse.json();
            toast({
              title: 'Success',
              description: `MCP server connected! Found ${connectData.tools_count || 0} tools, ${connectData.resources_count || 0} resources, ${connectData.prompts_count || 0} prompts.`,
            });
          } else {
            // Get detailed error message from response
            let errorMessage = 'Connection failed. You can try connecting manually.';
            try {
              const errorData = await connectResponse.json();
              if (errorData.detail) {
                errorMessage = `Connection failed: ${errorData.detail}`;
              }
            } catch (parseError) {
              console.error('Could not parse error response:', parseError);
            }
            
            toast({
              title: 'Server Added',
              description: errorMessage,
              variant: 'destructive',
            });
          }
        } catch (connectError: any) {
          console.error('Error connecting server:', connectError);
          toast({
            title: 'Server Added',
            description: `Connection failed: ${connectError.message || 'Network error'}. You can try connecting manually.`,
            variant: 'destructive',
          });
        }
        
        setShowModal(false);
        resetForm();
        if (onServerAdded) {
          onServerAdded();
        }
      } else {
        const error = await response.json();
        toast({
          title: 'Error',
          description: error.detail || 'Failed to add MCP server',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Error adding MCP server:', error);
      toast({
        title: 'Error',
        description: 'Failed to add MCP server',
        variant: 'destructive',
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={showModal} onOpenChange={(open) => {
      setShowModal(open);
      if (!open) resetForm();
    }}>
      <DialogTrigger asChild>
        <Button
          type="button"
          size="sm"
          variant="outline"
        >
          <Plus className="w-3.5 h-3.5 mr-1.5" />
          Add MCP Server
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add New MCP Server</DialogTitle>
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

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setShowModal(false);
                resetForm();
              }}
              disabled={submitting}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button 
              type="submit" 
              disabled={submitting}
              className="flex-1"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Adding...
                </>
              ) : (
                'Add Server'
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};
