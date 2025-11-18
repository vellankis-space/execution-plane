import { useState, useCallback, useMemo, useEffect, useRef } from "react";
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
  BackgroundVariant,
  ReactFlowInstance,
  NodeChange,
  EdgeChange,
} from "reactflow";
import "reactflow/dist/style.css";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Save, Play, Trash2, Download, Upload, ZoomIn, ZoomOut, Home } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { nodeTypes } from "./CustomNodes";
import { NodePalette } from "./NodePalette";
import { useNavigate, useSearchParams } from "react-router-dom";
import { transformWorkflowForBackend, validateWorkflow } from "./workflowTransformers";

interface Agent {
  agent_id: string;
  name: string;
}

export function NoCodeWorkflowBuilder() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const editWorkflowId = searchParams.get('id');
  const [isEditMode, setIsEditMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);
  
  const [workflowName, setWorkflowName] = useState("");
  const [workflowDescription, setWorkflowDescription] = useState("");
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [isNodeDialogOpen, setIsNodeDialogOpen] = useState(false);
  const [agents, setAgents] = useState<Agent[]>([]);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Load agents on mount
  useEffect(() => {
    fetch("http://localhost:8000/api/v1/agents/")
      .then((res) => res.json())
      .then((data) => {
        setAgents(data || []);
      })
      .catch((err) => {
        console.error("Error loading agents:", err);
        toast({
          title: "Warning",
          description: "Could not load agents. You can still build workflows.",
          variant: "default",
        });
      });
  }, []);

  // Fetch workflow data if in edit mode
  useEffect(() => {
    const fetchWorkflowData = async () => {
      if (editWorkflowId) {
        setLoading(true);
        try {
          const response = await fetch(`http://localhost:8000/api/v1/workflows/${editWorkflowId}`);
          if (response.ok) {
            const workflow = await response.json();
            setIsEditMode(true);
            setWorkflowName(workflow.name || "");
            setWorkflowDescription(workflow.description || "");
            
            // Load workflow definition if available
            if (workflow.definition) {
              const definition = typeof workflow.definition === 'string' 
                ? JSON.parse(workflow.definition) 
                : workflow.definition;
              
              if (definition.steps && Array.isArray(definition.steps)) {
                const loadedNodes = definition.steps.map((step: any) => ({
                  id: step.id,
                  type: step.type || "agentNode",
                  position: step.position || { x: 100, y: 100 },
                  data: step.data || { label: step.name, agent_id: step.agent_id, description: step.description },
                }));
                setNodes(loadedNodes);
              }
              
              if (definition.dependencies) {
                const loadedEdges: Edge[] = [];
                Object.entries(definition.dependencies).forEach(([target, sources]: [string, any]) => {
                  if (Array.isArray(sources)) {
                    sources.forEach((source) => {
                      loadedEdges.push({
                        id: `${source}-${target}`,
                        source,
                        target,
                        type: "smoothstep",
                        animated: true,
                      });
                    });
                  }
                });
                setEdges(loadedEdges);
              }
            }
          } else {
            toast({
              title: "Error",
              description: "Failed to load workflow data",
              variant: "destructive",
            });
          }
        } catch (error) {
          console.error("Error fetching workflow:", error);
          toast({
            title: "Error",
            description: "Failed to load workflow data",
            variant: "destructive",
          });
        } finally {
          setLoading(false);
        }
      }
    };
    fetchWorkflowData();
  }, [editWorkflowId, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => addEdge({ ...params, type: "smoothstep", animated: true }, eds));
    },
    [setEdges]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData("application/reactflow");
      if (!type || !reactFlowInstance) {
        return;
      }

      const reactFlowBounds = reactFlowWrapper.current?.getBoundingClientRect();
      if (!reactFlowBounds) return;

      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });

      const newNode: Node = {
        id: `${type}-${Date.now()}`,
        type,
        position,
        data: getDefaultNodeData(type),
      };

      setNodes((nds) => [...nds, newNode]);
    },
    [reactFlowInstance, setNodes]
  );

  const getDefaultNodeData = (type: string) => {
    switch (type) {
      case "startNode":
        return { label: "Start" };
      case "endNode":
        return { label: "End" };
      case "agentNode":
        return { label: "Agent Task", agent_id: "", description: "" };
      case "conditionNode":
        return { label: "If Condition", condition: "" };
      case "loopNode":
        return { label: "Loop", iterations: 10, description: "" };
      case "actionNode":
        return { label: "Custom Action", action_type: "", description: "" };
      case "errorHandlerNode":
        return { label: "Error Handler", error_type: "all", description: "" };
      default:
        return { label: "Node" };
    }
  };

  const deleteNode = () => {
    if (selectedNode) {
      setNodes((nds) => nds.filter((node) => node.id !== selectedNode.id));
      setEdges((eds) =>
        eds.filter((edge) => edge.source !== selectedNode.id && edge.target !== selectedNode.id)
      );
      setSelectedNode(null);
      setIsNodeDialogOpen(false);
    }
  };

  const updateNode = (nodeId: string, updates: Partial<Node["data"]>) => {
    setNodes((nds) => {
      const updatedNodes = nds.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...updates } } : node
      );
      // Update selectedNode to keep dialog in sync
      if (selectedNode && selectedNode.id === nodeId) {
        const updatedNode = updatedNodes.find(n => n.id === nodeId);
        if (updatedNode) {
          setSelectedNode(updatedNode);
        }
      }
      return updatedNodes;
    });
  };

  const handleNodeClick = (event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
    setIsNodeDialogOpen(true);
  };

  const handleSaveNode = () => {
    setIsNodeDialogOpen(false);
    setSelectedNode(null);
  };

  const handleSaveWorkflow = async () => {
    if (!workflowName.trim()) {
      toast({
        title: "Validation Error",
        description: "Please enter a workflow name",
        variant: "destructive",
      });
      return;
    }

    // Validate workflow structure
    const validation = validateWorkflow(nodes, edges);
    if (!validation.valid) {
      toast({
        title: "Validation Error",
        description: validation.error,
        variant: "destructive",
      });
      return;
    }

    // Transform workflow using proper transformation logic
    const workflowData = transformWorkflowForBackend(
      nodes,
      edges,
      workflowName,
      workflowDescription
    );

    try {
      const url = isEditMode
        ? `http://localhost:8000/api/v1/workflows/${editWorkflowId}`
        : "http://localhost:8000/api/v1/workflows";
      const method = isEditMode ? "PUT" : "POST";
      
      const response = await fetch(url, {
        method: method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(workflowData),
      });

      if (response.ok) {
        toast({
          title: isEditMode ? "Workflow Updated" : "Workflow Saved",
          description: isEditMode 
            ? "Your workflow has been updated successfully."
            : "Your workflow has been saved successfully.",
        });
        if (isEditMode) {
          navigate('/workflows');
        }
      } else {
        const error = await response.json();
        throw new Error(error.detail || (isEditMode ? "Failed to update workflow" : "Failed to save workflow"));
      }
    } catch (error: any) {
      console.error(isEditMode ? "Error updating workflow:" : "Error saving workflow:", error);
      toast({
        title: isEditMode ? "Error Updating Workflow" : "Error Saving Workflow",
        description: error.message || (isEditMode ? "Failed to update workflow. Please try again." : "Failed to save workflow. Please try again."),
        variant: "destructive",
      });
    }
  };

  const exportWorkflow = () => {
    const workflowData = {
      name: workflowName,
      description: workflowDescription,
      nodes,
      edges,
    };
    
    const dataStr = JSON.stringify(workflowData, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `workflow-${workflowName.replace(/\s+/g, "-").toLowerCase()}.json`;
    link.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: "Workflow Exported",
      description: "Workflow has been downloaded as JSON file.",
    });
  };

  const importWorkflow = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target?.result as string);
        setWorkflowName(data.name || "");
        setWorkflowDescription(data.description || "");
        setNodes(data.nodes || []);
        setEdges(data.edges || []);
        
        toast({
          title: "Workflow Imported",
          description: "Workflow has been loaded successfully.",
        });
      } catch (error) {
        toast({
          title: "Import Error",
          description: "Failed to import workflow. Invalid file format.",
          variant: "destructive",
        });
      }
    };
    reader.readAsText(file);
  };

  const clearWorkflow = () => {
    setNodes([]);
    setEdges([]);
    toast({
      title: "Canvas Cleared",
      description: "All nodes and connections have been removed.",
    });
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <Card className="rounded-none border-x-0 border-t-0 border-b bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-950/80 p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              {isEditMode ? 'Edit Workflow' : 'Workflow Orchestration Builder'}
            </h1>
            <p className="text-xs text-muted-foreground mt-1">
              {isEditMode
                ? 'Update your workflow orchestration visually'
                : 'Design and orchestrate workflows using nodes and connections'}
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => navigate("/")}>
              <Home className="w-4 h-4 mr-2" />
              Home
            </Button>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4 mt-2">
          <div>
            <Label htmlFor="workflow-name">Workflow Name</Label>
            <Input
              id="workflow-name"
              placeholder="Enter workflow name"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              className="mt-1 h-9 text-sm"
            />
          </div>
          <div>
            <Label htmlFor="workflow-description">Description</Label>
            <Input
              id="workflow-description"
              placeholder="Describe what this workflow does"
              value={workflowDescription}
              onChange={(e) => setWorkflowDescription(e.target.value)}
              className="mt-1 h-9 text-sm"
            />
          </div>
        </div>
      </Card>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Node Palette */}
        <NodePalette />

        {/* Canvas */}
        <div className="flex-1 flex flex-col">
          {/* Toolbar */}
          <div className="p-3 border-b flex items-center justify-between bg-muted/30">
            <div className="flex gap-2">
              <Button onClick={handleSaveWorkflow} size="sm" disabled={loading}>
                <Save className="w-4 h-4 mr-2" />
                {loading ? 'Loading...' : (isEditMode ? 'Update Workflow' : 'Save Workflow')}
              </Button>
              <Button onClick={exportWorkflow} variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm" asChild>
                <label>
                  <Upload className="w-4 h-4 mr-2" />
                  Import
                  <input
                    type="file"
                    accept=".json"
                    className="hidden"
                    onChange={importWorkflow}
                  />
                </label>
              </Button>
            </div>
            <div className="flex gap-2">
              {selectedNode && (
                <Button onClick={deleteNode} variant="destructive" size="sm">
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete Node
                </Button>
              )}
              <Button onClick={clearWorkflow} variant="outline" size="sm">
                Clear Canvas
              </Button>
            </div>
          </div>

          {/* React Flow Canvas */}
          <div className="flex-1" ref={reactFlowWrapper}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onNodeClick={handleNodeClick}
              onInit={setReactFlowInstance}
              onDrop={onDrop}
              onDragOver={onDragOver}
              nodeTypes={nodeTypes}
              fitView
              className="bg-slate-50 dark:bg-slate-950/60"
            >
              <Controls />
              <MiniMap
                nodeStrokeWidth={3}
                zoomable
                pannable
                className="bg-background"
              />
              <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
            </ReactFlow>
          </div>
        </div>
      </div>

      {/* Node Configuration Dialog */}
      <Dialog open={isNodeDialogOpen} onOpenChange={setIsNodeDialogOpen}>
        <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Configure {selectedNode?.type?.replace("Node", "") || "Node"}</DialogTitle>
            <DialogDescription>
              Configure the node properties and behavior
            </DialogDescription>
          </DialogHeader>
          {selectedNode && (
            <div className="space-y-4 mt-4">
              {/* Common fields */}
              <div>
                <Label htmlFor="node-label">Node Label</Label>
                <Input
                  id="node-label"
                  placeholder="Enter node label"
                  value={selectedNode.data.label || ""}
                  onChange={(e) =>
                    updateNode(selectedNode.id, { label: e.target.value })
                  }
                  className="mt-1"
                />
              </div>

              {/* Agent Node specific fields */}
              {selectedNode.type === "agentNode" && (
                <>
                  <div>
                    <Label htmlFor="node-agent">Agent</Label>
                    <Select
                      value={selectedNode.data.agent_id || ""}
                      onValueChange={(value) =>
                        updateNode(selectedNode.id, { agent_id: value })
                      }
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select an agent" />
                      </SelectTrigger>
                      <SelectContent>
                        {agents.map((agent) => (
                          <SelectItem key={agent.agent_id} value={agent.agent_id}>
                            {agent.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="node-description">Description</Label>
                    <Textarea
                      id="node-description"
                      placeholder="Describe what this agent does"
                      value={selectedNode.data.description || ""}
                      onChange={(e) =>
                        updateNode(selectedNode.id, { description: e.target.value })
                      }
                      className="mt-1"
                    />
                  </div>
                </>
              )}

              {/* Condition Node specific fields */}
              {selectedNode.type === "conditionNode" && (
                <div>
                  <Label htmlFor="node-condition">Condition Expression</Label>
                  <Input
                    id="node-condition"
                    placeholder="e.g., output.score > 0.8"
                    value={selectedNode.data.condition || ""}
                    onChange={(e) =>
                      updateNode(selectedNode.id, { condition: e.target.value })
                    }
                    className="mt-1"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Right output: condition is true, Bottom output: condition is false
                  </p>
                </div>
              )}

              {/* Loop Node specific fields */}
              {selectedNode.type === "loopNode" && (
                <>
                  <div>
                    <Label htmlFor="node-iterations">Max Iterations</Label>
                    <Input
                      id="node-iterations"
                      type="number"
                      placeholder="10"
                      value={selectedNode.data.iterations || 10}
                      onChange={(e) =>
                        updateNode(selectedNode.id, { iterations: parseInt(e.target.value) || 10 })
                      }
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="node-description">Description</Label>
                    <Textarea
                      id="node-description"
                      placeholder="Describe the loop behavior"
                      value={selectedNode.data.description || ""}
                      onChange={(e) =>
                        updateNode(selectedNode.id, { description: e.target.value })
                      }
                      className="mt-1"
                    />
                  </div>
                </>
              )}

              {/* Action Node specific fields */}
              {selectedNode.type === "actionNode" && (
                <>
                  <div>
                    <Label htmlFor="node-action-type">Action Type</Label>
                    <Select
                      value={selectedNode.data.action_type || ""}
                      onValueChange={(value) =>
                        updateNode(selectedNode.id, { action_type: value })
                      }
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select action type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="api_call">API Call</SelectItem>
                        <SelectItem value="data_transform">Data Transform</SelectItem>
                        <SelectItem value="webhook">Webhook</SelectItem>
                        <SelectItem value="custom">Custom Script</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="node-description">Description</Label>
                    <Textarea
                      id="node-description"
                      placeholder="Describe the action"
                      value={selectedNode.data.description || ""}
                      onChange={(e) =>
                        updateNode(selectedNode.id, { description: e.target.value })
                      }
                      className="mt-1"
                    />
                  </div>
                </>
              )}

              {/* Error Handler Node specific fields */}
              {selectedNode.type === "errorHandlerNode" && (
                <>
                  <div>
                    <Label htmlFor="node-error-type">Error Type to Handle</Label>
                    <Select
                      value={selectedNode.data.error_type || "all"}
                      onValueChange={(value) =>
                        updateNode(selectedNode.id, { error_type: value })
                      }
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select error type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Errors</SelectItem>
                        <SelectItem value="timeout">Timeout Errors</SelectItem>
                        <SelectItem value="validation">Validation Errors</SelectItem>
                        <SelectItem value="network">Network Errors</SelectItem>
                        <SelectItem value="custom">Custom Errors</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="node-description">Recovery Action</Label>
                    <Textarea
                      id="node-description"
                      placeholder="Describe the recovery action"
                      value={selectedNode.data.description || ""}
                      onChange={(e) =>
                        updateNode(selectedNode.id, { description: e.target.value })
                      }
                      className="mt-1"
                    />
                  </div>
                </>
              )}

              <div className="flex justify-end gap-2 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => setIsNodeDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button onClick={handleSaveNode}>
                  <Save className="w-4 h-4 mr-2" />
                  Save
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
