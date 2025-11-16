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
  MessageSquare,
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
import { ActionNodeConfig } from "./ActionNodeConfig";
import { transformWorkflowForBackend, validateWorkflow as validateWorkflowStructure } from "./workflowTransformers";

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
  const [credentials, setCredentials] = useState<Array<{ id: string; name: string; type: string }>>([]);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Execution state
  const [isExecuting, setIsExecuting] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [executionEngine, setExecutionEngine] = useState<WorkflowExecutionEngine | null>(null);
  const [currentExecution, setCurrentExecution] = useState<WorkflowExecutionResult | null>(null);
  const [testMode, setTestMode] = useState(false);
  const [testData, setTestData] = useState("{}");
  const [showExecuteDialog, setShowExecuteDialog] = useState(false);
  const [executionInput, setExecutionInput] = useState("");  // Changed to simple message input
  
  // Chat node input during execution
  const [showChatInputDialog, setShowChatInputDialog] = useState(false);
  const [chatInputMessage, setChatInputMessage] = useState("");
  const [chatInputWelcome, setChatInputWelcome] = useState("");
  const [chatInputResolver, setChatInputResolver] = useState<((value: string) => void) | null>(null);

  // Settings
  const [activeTab, setActiveTab] = useState("canvas");
  const [showMinimap, setShowMinimap] = useState(true);
  const [autoSave, setAutoSave] = useState(false);

  // Load agents, credentials, and workflow
  useEffect(() => {
    const initializeBuilder = async () => {
      await loadAgents();
      await loadCredentials();
      
      // Load workflow from URL params if present
      const params = new URLSearchParams(window.location.search);
      const workflowIdParam = params.get('id');
      if (workflowIdParam) {
        await loadWorkflow(workflowIdParam);
      }
    };
    
    initializeBuilder();
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

  const loadCredentials = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/credentials");
      if (response.ok) {
        const data = await response.json();
        setCredentials(data || []);
      }
    } catch (error) {
      console.error("Error loading credentials:", error);
    }
  };

  const loadWorkflow = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/workflows/${id}`);
      if (response.ok) {
        const workflow = await response.json();
        
        // Set basic workflow info
        setWorkflowId(workflow.workflow_id || id);
        setWorkflowName(workflow.name || "");
        setWorkflowDescription(workflow.description || "");
        
        // Load visualization data if available (React Flow format)
        if (workflow.definition?.visualization) {
          const viz = workflow.definition.visualization;
          setNodes(viz.nodes || []);
          setEdges(viz.edges || []);
          
          toast({
            title: "Workflow Loaded",
            description: `Successfully loaded "${workflow.name}"`,
          });
        } else {
          // Fallback: Try to reconstruct from steps (legacy format)
          toast({
            title: "Legacy Format",
            description: "Workflow uses old format. Please re-save to update.",
            variant: "destructive",
          });
        }
      } else {
        throw new Error("Failed to load workflow");
      }
    } catch (error: any) {
      console.error("Error loading workflow:", error);
      toast({
        title: "Error Loading Workflow",
        description: error.message || "Failed to load workflow",
        variant: "destructive",
      });
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
      case "chatNode":
        return { label: "Chat / Manual", description: "Interactive manual trigger", welcomeMessage: "Hello! How can I help you?" };
      case "displayNode":
        return { label: "Display Output", description: "Shows execution results", previewData: {} };
      default:
        return { label: "Node" };
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
    const validation = validateWorkflowStructure(nodes, edges);
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
      workflowDescription,
      triggers
    );

    // Add visualization data to preserve React Flow format
    workflowData.definition.visualization = {
      nodes: nodes.map(node => ({
        id: node.id,
        type: node.type,
        position: node.position,
        data: node.data
      })),
      edges: edges.map(edge => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        sourceHandle: edge.sourceHandle,
        targetHandle: edge.targetHandle,
        type: edge.type
      }))
    };

    try {
      // Determine if this is a create or update operation
      const isUpdate = workflowId && !workflowId.startsWith('workflow-');
      const url = isUpdate 
        ? `http://localhost:8000/api/v1/workflows/${workflowId}`
        : "http://localhost:8000/api/v1/workflows";
      const method = isUpdate ? "PUT" : "POST";

      const response = await fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(workflowData),
      });

      if (response.ok) {
        const savedWorkflow = await response.json();
        setWorkflowId(savedWorkflow.workflow_id || savedWorkflow.id || workflowId);
        toast({
          title: isUpdate ? "Workflow Updated" : "Workflow Saved",
          description: isUpdate 
            ? "Your workflow has been updated successfully."
            : "Your workflow has been saved successfully.",
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
    // Show input dialog first
    setShowExecuteDialog(true);
  };

  const handleChatInputRequired = async (node: any, welcomeMessage: string): Promise<string> => {
    // Return a promise that resolves when user provides input
    return new Promise((resolve) => {
      setChatInputWelcome(welcomeMessage);
      setChatInputMessage("");
      setChatInputResolver(() => resolve);
      setShowChatInputDialog(true);
    });
  };

  const submitChatInput = () => {
    if (chatInputResolver) {
      chatInputResolver(chatInputMessage);
      setChatInputResolver(null);
      setShowChatInputDialog(false);
      setChatInputMessage("");
    }
  };

  const executeWorkflowWithInput = async () => {
    // Validate workflow structure
    const validation = validateWorkflowStructure(nodes, edges);
    if (!validation.valid) {
      toast({
        title: "Validation Error",
        description: validation.error,
        variant: "destructive",
      });
      return;
    }

    setShowExecuteDialog(false);
    setIsExecuting(true);
    setIsPaused(false);

    try {
      // Use simple message input instead of JSON
      const variables = {
        message: executionInput || "Hello, how can you help me?"
      };
      
      // Legacy handling for JSON input (kept for compatibility)
      try {
        if (executionInput.trim().startsWith('{')) {
          const parsed = JSON.parse(executionInput);
          Object.assign(variables, parsed);
        }
      } catch (error) {
        // If parsing fails, just use the message as-is
        toast({
          title: "Using Plain Text",
          description: "Please provide valid JSON input",
          variant: "destructive",
        });
        setIsExecuting(false);
        return;
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
        handleExecutionUpdate,
        handleChatInputRequired
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

  const handleDeleteNode = () => {
    if (selectedNode) {
      setNodes((nds) => nds.filter((node) => node.id !== selectedNode.id));
      setEdges((eds) =>
        eds.filter((edge) => edge.source !== selectedNode.id && edge.target !== selectedNode.id)
      );
      setIsNodeDialogOpen(false);
      setSelectedNode(null);
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

      {/* Workflow Execution Input Dialog */}
      <Dialog open={showExecuteDialog} onOpenChange={setShowExecuteDialog}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Execute Workflow</DialogTitle>
            <DialogDescription>
              Provide an input message for your workflow
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Input Message</Label>
              <Textarea
                value={executionInput}
                onChange={(e) => setExecutionInput(e.target.value)}
                placeholder="Type your message here... (e.g., 'Analyze this data' or 'Generate a report')"
                className="resize-none"
                rows={4}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.ctrlKey && !isExecuting) {
                    executeWorkflowWithInput();
                  }
                }}
              />
              <p className="text-xs text-muted-foreground">
                💡 Press Ctrl+Enter to execute • This message will be available as <code className="bg-muted px-1 py-0.5 rounded">{"{{ $json.message }}"}</code> in your nodes
              </p>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setShowExecuteDialog(false)} disabled={isExecuting}>
              Cancel
            </Button>
            <Button onClick={executeWorkflowWithInput} disabled={isExecuting} className="gap-2">
              {isExecuting ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-background border-t-transparent" />
                  Executing...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Execute
                </>
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Chat Node Input Dialog (During Execution) */}
      <Dialog open={showChatInputDialog} onOpenChange={(open) => !open && chatInputResolver && chatInputResolver("")}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-cyan-600" />
              Chat Input Required
            </DialogTitle>
            <DialogDescription>
              The workflow is waiting for your input
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {chatInputWelcome && (
              <div className="rounded-lg bg-cyan-50 dark:bg-cyan-950/30 p-4 border border-cyan-200 dark:border-cyan-800">
                <p className="text-sm text-cyan-900 dark:text-cyan-100 leading-relaxed">
                  {chatInputWelcome}
                </p>
              </div>
            )}
            
            <div className="space-y-2">
              <Label>Your Message</Label>
              <Textarea
                autoFocus
                placeholder="Type your message here..."
                value={chatInputMessage}
                onChange={(e) => setChatInputMessage(e.target.value)}
                className="resize-none"
                rows={4}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.ctrlKey && chatInputMessage.trim()) {
                    submitChatInput();
                  }
                }}
              />
              <p className="text-xs text-muted-foreground">
                Press Ctrl+Enter to submit
              </p>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button
              onClick={submitChatInput}
              disabled={!chatInputMessage.trim()}
              className="gap-2"
            >
              <MessageSquare className="w-4 h-4" />
              Submit
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Enhanced Node Configuration Dialog */}
      {selectedNode && (
      <Dialog open={isNodeDialogOpen} onOpenChange={setIsNodeDialogOpen}>
        <DialogContent className="sm:max-w-[700px] max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Configure {selectedNode.type?.replace("Node", "") || "Node"}</DialogTitle>
            <DialogDescription>
              Configure node properties, parameters, and data mapping
            </DialogDescription>
          </DialogHeader>

          <Tabs defaultValue="general" className="mt-4">
            <TabsList className={`grid w-full ${selectedNode.type === "agentNode" ? "grid-cols-3" : "grid-cols-4"}`}>
              <TabsTrigger value="general">General</TabsTrigger>
              <TabsTrigger value="parameters">Parameters</TabsTrigger>
              {selectedNode.type !== "agentNode" && (
                <TabsTrigger value="advanced">Advanced</TabsTrigger>
              )}
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
                <>
                  <div>
                    <Label>Collection Path</Label>
                    <Input
                      placeholder="{{ $json.items }}" 
                      value={selectedNode.data.collection_path || ""}
                      onChange={(e) => updateNode(selectedNode.id, { collection_path: e.target.value })}
                      className="mt-1 font-mono text-sm"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Path to array (e.g., {`{{ $node.previousStep.json.items }}`})
                    </p>
                  </div>
                  
                  <div>
                    <Label>Max Iterations</Label>
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
                </>
              )}

              {selectedNode.type === "actionNode" && (
                <>
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
                        <SelectItem value="http_request">HTTP Request</SelectItem>
                        <SelectItem value="data_transform">Data Transform</SelectItem>
                        <SelectItem value="webhook">Webhook</SelectItem>
                        <SelectItem value="wait">Wait/Delay</SelectItem>
                        <SelectItem value="custom">Custom Script</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  {selectedNode.data.action_type && (
                    <ActionNodeConfig
                      actionType={selectedNode.data.action_type}
                      config={selectedNode.data.action_config || {}}
                      onChange={(config) => updateNode(selectedNode.id, { action_config: config })}
                    />
                  )}
                </>
              )}

              {selectedNode.type === "errorHandlerNode" && (
                <>
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
                  
                  <div>
                    <Label>Recovery Action</Label>
                    <Select
                      value={selectedNode.data.recovery_action || "continue"}
                      onValueChange={(value) => updateNode(selectedNode.id, { recovery_action: value })}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select recovery action" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="continue">Continue Workflow</SelectItem>
                        <SelectItem value="retry">Retry Step</SelectItem>
                        <SelectItem value="fallback">Use Fallback Value</SelectItem>
                        <SelectItem value="stop">Stop Workflow</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  {selectedNode.data.recovery_action === "fallback" && (
                    <div>
                      <Label>Fallback Value</Label>
                      <Input
                        placeholder="Default value on error"
                        value={selectedNode.data.fallback_value || ""}
                        onChange={(e) => updateNode(selectedNode.id, { fallback_value: e.target.value })}
                        className="mt-1"
                      />
                    </div>
                  )}
                </>
              )}

              {selectedNode.type === "chatNode" && (
                <>
                  <div className="space-y-2">
                    <Label className="flex items-center gap-2">
                      <MessageSquare className="w-4 h-4 text-cyan-600" />
                      Welcome Message
                    </Label>
                    <Textarea
                      placeholder="Enter the message that will be displayed when workflow starts... (e.g., 'Hello! I'm ready to help you.')"
                      value={selectedNode.data.welcomeMessage || ""}
                      onChange={(e) => updateNode(selectedNode.id, { welcomeMessage: e.target.value })}
                      className="mt-1 min-h-[100px]"
                      rows={4}
                    />
                    <p className="text-xs text-muted-foreground">
                      💡 This message will be shown at the start of workflow execution. Users will provide their input after seeing this message.
                    </p>
                  </div>

                  <div className="rounded-lg bg-cyan-50 dark:bg-cyan-950/30 p-4 border border-cyan-200 dark:border-cyan-800">
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-cyan-500 flex items-center justify-center">
                        <MessageSquare className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex-1 space-y-2">
                        <h4 className="text-sm font-semibold text-cyan-900 dark:text-cyan-100">
                          How Chat Input Works
                        </h4>
                        <ul className="text-xs text-cyan-800 dark:text-cyan-200 space-y-1.5">
                          <li className="flex items-start gap-2">
                            <span className="text-cyan-600 dark:text-cyan-400 font-bold">1.</span>
                            <span>Your welcome message is displayed to the user</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-cyan-600 dark:text-cyan-400 font-bold">2.</span>
                            <span>User provides input through the execution dialog</span>
                          </li>
                          <li className="flex items-start gap-2">
                            <span className="text-cyan-600 dark:text-cyan-400 font-bold">3.</span>
                            <span>Input is available as <code className="bg-cyan-100 dark:bg-cyan-900 px-1.5 py-0.5 rounded text-xs">{"{{ $json.message }}"}</code></span>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-lg bg-blue-50 dark:bg-blue-950/30 p-3 border border-blue-200 dark:border-blue-800">
                    <p className="text-xs text-blue-800 dark:text-blue-200">
                      <strong>Example:</strong> If you set "Hello! How can I help you today?" as the welcome message, 
                      users will see this prompt when executing the workflow, then they can type their request.
                    </p>
                  </div>
                </>
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

            <TabsContent value="advanced" className="space-y-4">
              {/* Credentials Selector */}
              {(selectedNode.type === "agentNode" || selectedNode.type === "actionNode") && (
                <div>
                  <Label>Credentials</Label>
                  <Select
                    value={selectedNode.data.credential_id || ""}
                    onValueChange={(value) => updateNode(selectedNode.id, { credential_id: value })}
                  >
                    <SelectTrigger className="mt-1">
                      <SelectValue placeholder="Select credential (optional)" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">None</SelectItem>
                      {credentials.map((cred) => (
                        <SelectItem key={cred.id} value={cred.id}>
                          {cred.name} ({cred.type})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground mt-1">
                    Use {`{{ $credentials.field_name }}`} to access in expressions
                  </p>
                </div>
              )}

              {/* Retry Policy */}
              <div className="space-y-3">
                <Label className="text-base font-semibold">Retry Policy</Label>
                
                <div>
                  <Label>Max Retries</Label>
                  <Input
                    type="number"
                    value={selectedNode.data.retry_policy?.max_retries ?? 3}
                    onChange={(e) => updateNode(selectedNode.id, {
                      retry_policy: {
                        ...selectedNode.data.retry_policy,
                        max_retries: parseInt(e.target.value) || 0
                      }
                    })}
                    className="mt-1"
                    min="0"
                    max="10"
                  />
                </div>
                
                <div>
                  <Label>Initial Delay (seconds)</Label>
                  <Input
                    type="number"
                    value={selectedNode.data.retry_policy?.initial_delay ?? 1}
                    onChange={(e) => updateNode(selectedNode.id, {
                      retry_policy: {
                        ...selectedNode.data.retry_policy,
                        initial_delay: parseFloat(e.target.value) || 1
                      }
                    })}
                    className="mt-1"
                    min="0.1"
                    max="60"
                    step="0.1"
                  />
                </div>
                
                <div>
                  <Label>Max Delay (seconds)</Label>
                  <Input
                    type="number"
                    value={selectedNode.data.retry_policy?.max_delay ?? 30}
                    onChange={(e) => updateNode(selectedNode.id, {
                      retry_policy: {
                        ...selectedNode.data.retry_policy,
                        max_delay: parseFloat(e.target.value) || 30
                      }
                    })}
                    className="mt-1"
                    min="1"
                    max="300"
                  />
                </div>
                
                <div>
                  <Label>Exponential Base</Label>
                  <Input
                    type="number"
                    value={selectedNode.data.retry_policy?.exponential_base ?? 2}
                    onChange={(e) => updateNode(selectedNode.id, {
                      retry_policy: {
                        ...selectedNode.data.retry_policy,
                        exponential_base: parseFloat(e.target.value) || 2
                      }
                    })}
                    className="mt-1"
                    min="1"
                    max="10"
                    step="0.1"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Multiplier for exponential backoff (2 = double each retry)
                  </p>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="output" className="space-y-4">
              {selectedNode.data.lastOutput ? (
                <Card className="p-4 bg-muted">
                  <Label className="text-sm font-semibold">Last Output</Label>
                  <pre className="text-xs mt-2 overflow-auto max-h-60 font-mono">
                    {JSON.stringify(selectedNode.data.lastOutput, null, 2)}
                  </pre>
                </Card>
              ) : (
                <div className="text-center py-8">
                  <p className="text-sm text-muted-foreground">
                    Output will appear here after execution
                  </p>
                </div>
              )}
              
              {selectedNode.data.executionTime && (
                <div className="text-xs text-muted-foreground">
                  <p>Execution time: {selectedNode.data.executionTime}ms</p>
                  <p>Status: {selectedNode.data.status || 'pending'}</p>
                </div>
              )}
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
      )}
    </div>
  );
}
