import { useState, useCallback, useRef, useEffect } from "react";
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
  Panel,
} from "reactflow";
import "reactflow/dist/style.css";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
import {
  Save,
  Play,
  Pause,
  Square,
  Download,
  Upload,
  Home,
  Settings,
  Bug,
  Zap,
  Key,
  Clock,
  CheckCircle2,
  AlertCircle,
  Trash2,
} from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { useNavigate } from "react-router-dom";

import { nodeTypes } from "./CustomNodes";
import { NodePalette } from "./NodePalette";
import { WorkflowExecutionEngine, WorkflowExecutionResult } from "./WorkflowExecutionEngine";
import { CredentialsManager } from "./CredentialsManager";
import { ExecutionHistory } from "./ExecutionHistory";
import { WorkflowTriggers, WorkflowTrigger } from "./WorkflowTriggers";
import { ExpressionEditor, ParameterMapper } from "./ExpressionEditor";

export function ProductionWorkflowBuilder() {
  const navigate = useNavigate();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null);

  const [workflowId, setWorkflowId] = useState<string>(`workflow-${Date.now()}`);
  const [workflowName, setWorkflowName] = useState("");
  const [workflowDescription, setWorkflowDescription] = useState("");
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [isNodeDialogOpen, setIsNodeDialogOpen] = useState(false);
  const [agents, setAgents] = useState<Array<{ agent_id: string; name: string }>>([]);
  const [triggers, setTriggers] = useState<WorkflowTrigger[]>([]);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Execution state
  const [isExecuting, setIsExecuting] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [executionEngine, setExecutionEngine] = useState<WorkflowExecutionEngine | null>(null);
  const [currentExecution, setCurrentExecution] = useState<WorkflowExecutionResult | null>(null);
  const [testMode, setTestMode] = useState(false);
  const [testData, setTestData] = useState("{}");

  // Settings
  const [activeTab, setActiveTab] = useState("canvas");
  const [showMinimap, setShowMinimap] = useState(true);
  const [autoSave, setAutoSave] = useState(false);

  // Load agents
  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/agents/");
      if (response.ok) {
        const data = await response.json();
        setAgents(data || []);
      }
    } catch (error) {
      console.error("Error loading agents:", error);
    }
  };

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
      if (!type || !reactFlowInstance) return;

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
        return { label: "Agent Task", agent_id: "", description: "", parameters: {} };
      case "conditionNode":
        return { label: "If Condition", condition: "" };
      case "loopNode":
        return { label: "Loop", iterations: 10, description: "" };
      case "actionNode":
        return { label: "Custom Action", action_type: "", description: "", config: {} };
      case "errorHandlerNode":
        return { label: "Error Handler", error_type: "all", description: "" };
      default:
        return { label: "Node" };
    }
  };

  const updateNode = (nodeId: string, updates: Partial<Node["data"]>) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...updates } } : node
      )
    );
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

    const steps = nodes.map((node) => ({
      id: node.id,
      type: node.type || "agentNode",
      name: node.data.label || "Unnamed Step",
      agent_id: node.data.agent_id || "",
      description: node.data.description || "",
      position: node.position,
      data: node.data,
    }));

    const dependencies: Record<string, string[]> = {};
    edges.forEach((edge) => {
      if (!dependencies[edge.target]) {
        dependencies[edge.target] = [];
      }
      dependencies[edge.target].push(edge.source);
    });

    const workflowData = {
      name: workflowName,
      description: workflowDescription,
      definition: { steps, dependencies, conditions: {} },
      triggers,
    };

    try {
      const response = await fetch("http://localhost:8000/api/v1/workflows", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(workflowData),
      });

      if (response.ok) {
        const savedWorkflow = await response.json();
        setWorkflowId(savedWorkflow.id || workflowId);
        toast({
          title: "Workflow Saved",
          description: "Your workflow has been saved successfully.",
        });
      } else {
        const error = await response.json();
        throw new Error(error.detail || "Failed to save workflow");
      }
    } catch (error: any) {
      toast({
        title: "Error Saving Workflow",
        description: error.message,
        variant: "destructive",
      });
    }
  };

  const handleExecuteWorkflow = async () => {
    // Validate workflow structure
    const validation = validateWorkflow();
    if (!validation.valid) {
      toast({
        title: "Validation Error",
        description: validation.error,
        variant: "destructive",
      });
      return;
    }

    setIsExecuting(true);
    setIsPaused(false);

    try {
      // Parse test data safely
      let variables = {};
      if (testMode) {
        try {
          variables = JSON.parse(testData);
        } catch (error) {
          throw new Error("Invalid JSON in test data");
        }
      }

      const engine = new WorkflowExecutionEngine(
        nodes,
        edges,
        {
          workflowId,
          executionId: `exec-${Date.now()}`,
          variables,
          credentials: {},
        },
        handleNodeUpdate,
        handleExecutionUpdate
      );

      setExecutionEngine(engine);
      const result = await engine.execute();
      setCurrentExecution(result);

      toast({
        title: "Execution Complete",
        description: `Workflow executed in ${result.totalExecutionTime}ms`,
      });
    } catch (error: any) {
      toast({
        title: "Execution Failed",
        description: error.message,
        variant: "destructive",
      });
    } finally {
      setIsExecuting(false);
      setExecutionEngine(null);
    }
  };

  const handlePauseWorkflow = () => {
    if (executionEngine) {
      if (isPaused) {
        executionEngine.resume();
        setIsPaused(false);
        toast({ title: "Resumed", description: "Workflow execution resumed" });
      } else {
        executionEngine.pause();
        setIsPaused(true);
        toast({ title: "Paused", description: "Workflow execution paused" });
      }
    }
  };

  const handleStopWorkflow = () => {
    if (executionEngine) {
      executionEngine.stop();
      setIsExecuting(false);
      setIsPaused(false);
      toast({ title: "Stopped", description: "Workflow execution stopped" });
    }
  };

  const handleNodeUpdate = (nodeId: string, status: string, output?: any) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, status, lastOutput: output } }
          : node
      )
    );
  };

  const handleExecutionUpdate = (result: WorkflowExecutionResult) => {
    setCurrentExecution(result);
  };

  const validateWorkflow = (): { valid: boolean; error?: string } => {
    if (nodes.length === 0) {
      return { valid: false, error: "Add nodes to the workflow before executing" };
    }

    const hasStart = nodes.some((n) => n.type === "startNode");
    if (!hasStart) {
      return { valid: false, error: "Workflow must have a Start node" };
    }

    // Check for disconnected nodes
    const connectedNodeIds = new Set<string>();
    edges.forEach((e) => {
      connectedNodeIds.add(e.source);
      connectedNodeIds.add(e.target);
    });

    const disconnectedNodes = nodes.filter(
      (n) => !connectedNodeIds.has(n.id) && n.type !== "startNode"
    );

    if (disconnectedNodes.length > 0) {
      return {
        valid: false,
        error: `${disconnectedNodes.length} node(s) are not connected`,
      };
    }

    return { valid: true };
  };

  const exportWorkflow = () => {
    const fileName = workflowName
      ? `workflow-${workflowName.replace(/\s+/g, "-").toLowerCase()}.json`
      : `workflow-${Date.now()}.json`;

    const workflowData = { name: workflowName, description: workflowDescription, nodes, edges, triggers };
    const dataStr = JSON.stringify(workflowData, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    link.click();
    URL.revokeObjectURL(url);
    toast({ title: "Exported", description: "Workflow exported successfully" });
  };

  const importWorkflow = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.onchange = async (e: any) => {
      const file = e.target.files[0];
      if (!file) return;

      try {
        const text = await file.text();
        const data = JSON.parse(text);

        if (data.name) setWorkflowName(data.name);
        if (data.description) setWorkflowDescription(data.description);
        if (data.nodes) setNodes(data.nodes);
        if (data.edges) setEdges(data.edges);
        if (data.triggers) setTriggers(data.triggers);

        toast({
          title: "Imported",
          description: "Workflow imported successfully",
        });
      } catch (error: any) {
        toast({
          title: "Import Failed",
          description: error.message,
          variant: "destructive",
        });
      }
    };
    input.click();
  };

  const handleDeleteNode = () => {
    if (selectedNode) {
      setNodes((nds) => nds.filter((n) => n.id !== selectedNode.id));
      setEdges((eds) =>
        eds.filter((e) => e.source !== selectedNode.id && e.target !== selectedNode.id)
      );
      setIsNodeDialogOpen(false);
      setSelectedNode(null);
      toast({ title: "Deleted", description: "Node deleted successfully" });
    }
  };

  const clearWorkflow = () => {
    if (confirm("Are you sure you want to clear the entire workflow?")) {
      setNodes([]);
      setEdges([]);
      setWorkflowName("");
      setWorkflowDescription("");
      setTriggers([]);
      toast({ title: "Cleared", description: "Workflow cleared" });
    }
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <Card className="rounded-none border-x-0 border-t-0 p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex-1">
            <h1 className="text-2xl font-bold flex items-center gap-2">
              Production Workflow Builder
              {isExecuting && (
                <Badge variant="secondary" className="animate-pulse">
                  <Play className="w-3 h-3 mr-1" />
                  Running
                </Badge>
              )}
            </h1>
            <div className="grid grid-cols-2 gap-4 mt-3">
              <Input
                placeholder="Workflow name"
                value={workflowName}
                onChange={(e) => setWorkflowName(e.target.value)}
              />
              <Input
                placeholder="Description"
                value={workflowDescription}
                onChange={(e) => setWorkflowDescription(e.target.value)}
              />
            </div>
          </div>
          <div className="flex gap-2 ml-4">
            <Button variant="outline" onClick={() => navigate("/")}>
              <Home className="w-4 h-4 mr-2" />
              Home
            </Button>
          </div>
        </div>

        {/* Execution Controls */}
        <div className="flex items-center justify-between pt-3 border-t">
          <div className="flex gap-2">
            <Button
              onClick={handleExecuteWorkflow}
              disabled={isExecuting}
              className="gap-2"
            >
              <Play className="w-4 h-4" />
              {testMode ? "Test Run" : "Execute"}
            </Button>
            {isExecuting && (
              <>
                <Button onClick={handlePauseWorkflow} variant="outline" className="gap-2">
                  <Pause className="w-4 h-4" />
                  {isPaused ? "Resume" : "Pause"}
                </Button>
                <Button
                  onClick={handleStopWorkflow}
                  variant="destructive"
                  className="gap-2"
                >
                  <Square className="w-4 h-4" />
                  Stop
                </Button>
              </>
            )}
            <Button onClick={handleSaveWorkflow} variant="outline" className="gap-2">
              <Save className="w-4 h-4" />
              Save
            </Button>
            <Button onClick={exportWorkflow} variant="outline" className="gap-2">
              <Download className="w-4 h-4" />
              Export
            </Button>
            <Button onClick={importWorkflow} variant="outline" className="gap-2">
              <Upload className="w-4 h-4" />
              Import
            </Button>
            <Button onClick={clearWorkflow} variant="outline" className="gap-2">
              <Trash2 className="w-4 h-4" />
              Clear
            </Button>
          </div>

          <div className="flex gap-2 items-center">
            <Label className="text-sm flex items-center gap-2">
              <input
                type="checkbox"
                checked={testMode}
                onChange={(e) => setTestMode(e.target.checked)}
                className="w-4 h-4"
              />
              Test Mode
            </Label>
            {currentExecution && (
              <Badge variant={currentExecution.status === "completed" ? "default" : "destructive"}>
                {currentExecution.status === "completed" ? (
                  <CheckCircle2 className="w-3 h-3 mr-1" />
                ) : (
                  <AlertCircle className="w-3 h-3 mr-1" />
                )}
                {currentExecution.status}
              </Badge>
            )}
          </div>
        </div>
      </Card>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <div className="w-80 border-r bg-muted/30 flex flex-col min-h-0">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col min-h-0">
            <TabsList className="grid w-full grid-cols-4 m-2">
              <TabsTrigger value="canvas">Nodes</TabsTrigger>
              <TabsTrigger value="triggers">
                <Zap className="w-4 h-4" />
              </TabsTrigger>
              <TabsTrigger value="credentials">
                <Key className="w-4 h-4" />
              </TabsTrigger>
              <TabsTrigger value="history">
                <Clock className="w-4 h-4" />
              </TabsTrigger>
            </TabsList>

            <div className="flex-1 min-h-0 overflow-hidden">
              <TabsContent value="canvas" className="m-0 h-full">
                <NodePalette />
              </TabsContent>
              <TabsContent value="triggers" className="p-4 h-full overflow-auto">
                <WorkflowTriggers
                  workflowId={workflowId}
                  triggers={triggers}
                  onTriggersChange={setTriggers}
                />
              </TabsContent>
              <TabsContent value="credentials" className="p-4 h-full overflow-auto">
                <CredentialsManager />
              </TabsContent>
              <TabsContent value="history" className="p-4 h-full overflow-auto">
                <ExecutionHistory workflowId={workflowId} />
              </TabsContent>
            </div>
          </Tabs>
        </div>

        {/* Canvas */}
        <div className="flex-1 flex flex-col">
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
              className="bg-muted/10"
            >
              <Controls />
              {showMinimap && <MiniMap nodeStrokeWidth={3} zoomable pannable />}
              <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
              
              <Panel position="top-right" className="bg-background/80 backdrop-blur-sm p-2 rounded-lg border">
                <div className="text-xs space-y-1">
                  <div>Nodes: {nodes.length}</div>
                  <div>Edges: {edges.length}</div>
                </div>
              </Panel>
            </ReactFlow>
          </div>
        </div>
      </div>

      {/* Enhanced Node Configuration Dialog - continued in next message due to length */}
      {renderNodeConfigDialog()}
    </div>
  );

  function renderNodeConfigDialog() {
    if (!selectedNode) return null;

    return (
      <Dialog open={isNodeDialogOpen} onOpenChange={setIsNodeDialogOpen}>
        <DialogContent className="sm:max-w-[700px] max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Configure {selectedNode.type?.replace("Node", "") || "Node"}</DialogTitle>
            <DialogDescription>
              Configure node properties, parameters, and data mapping
            </DialogDescription>
          </DialogHeader>

          <Tabs defaultValue="general" className="mt-4">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="general">General</TabsTrigger>
              <TabsTrigger value="parameters">Parameters</TabsTrigger>
              <TabsTrigger value="output">Output</TabsTrigger>
            </TabsList>

            <TabsContent value="general" className="space-y-4">
              <div>
                <Label>Node Name</Label>
                <Input
                  value={selectedNode.data.label || ""}
                  onChange={(e) => updateNode(selectedNode.id, { label: e.target.value })}
                  className="mt-1"
                />
              </div>

              {selectedNode.type === "agentNode" && (
                <div>
                  <Label>Agent</Label>
                  <Select
                    value={selectedNode.data.agent_id || ""}
                    onValueChange={(value) => updateNode(selectedNode.id, { agent_id: value })}
                  >
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="Select agent" />
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
              )}

              {selectedNode.type === "conditionNode" && (
                <div>
                  <Label>Condition Expression</Label>
                  <Textarea
                    value={selectedNode.data.condition || ""}
                    onChange={(e) => updateNode(selectedNode.id, { condition: e.target.value })}
                    placeholder="{{ $json.value > 100 }}"
                    className="mt-1 font-mono text-sm"
                    rows={3}
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Enter a boolean expression. Use $json for current data.
                  </p>
                </div>
              )}

              {selectedNode.type === "loopNode" && (
                <div>
                  <Label>Iterations</Label>
                  <Input
                    type="number"
                    value={selectedNode.data.iterations || 10}
                    onChange={(e) => updateNode(selectedNode.id, { iterations: parseInt(e.target.value) || 10 })}
                    className="mt-1"
                    min="1"
                    max="1000"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Maximum number of loop iterations
                  </p>
                </div>
              )}

              {selectedNode.type === "actionNode" && (
                <div>
                  <Label>Action Type</Label>
                  <Select
                    value={selectedNode.data.action_type || ""}
                    onValueChange={(value) => updateNode(selectedNode.id, { action_type: value })}
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
              )}

              {selectedNode.type === "errorHandlerNode" && (
                <div>
                  <Label>Error Type</Label>
                  <Select
                    value={selectedNode.data.error_type || "all"}
                    onValueChange={(value) => updateNode(selectedNode.id, { error_type: value })}
                  >
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="Select error type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Errors</SelectItem>
                      <SelectItem value="timeout">Timeout</SelectItem>
                      <SelectItem value="validation">Validation</SelectItem>
                      <SelectItem value="network">Network</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}

              <div>
                <Label>Description</Label>
                <Textarea
                  value={selectedNode.data.description || ""}
                  onChange={(e) => updateNode(selectedNode.id, { description: e.target.value })}
                  className="mt-1"
                  rows={3}
                />
              </div>
            </TabsContent>

            <TabsContent value="parameters" className="space-y-4">
              <ParameterMapper
                parameters={selectedNode.data.parameters || {}}
                onChange={(params) => updateNode(selectedNode.id, { parameters: params })}
              />
            </TabsContent>

            <TabsContent value="output" className="space-y-4">
              {selectedNode.data.lastOutput && (
                <Card className="p-4 bg-muted">
                  <Label className="text-sm font-semibold">Last Output</Label>
                  <pre className="text-xs mt-2 overflow-auto max-h-60">
                    {JSON.stringify(selectedNode.data.lastOutput, null, 2)}
                  </pre>
                </Card>
              )}
              <p className="text-sm text-muted-foreground">
                Output will appear here after execution
              </p>
            </TabsContent>
          </Tabs>

          <div className="flex justify-between pt-4 border-t">
            <Button 
              variant="destructive" 
              onClick={handleDeleteNode}
              className="gap-2"
            >
              <Trash2 className="w-4 h-4" />
              Delete Node
            </Button>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setIsNodeDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSaveNode}>Save</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }
}
