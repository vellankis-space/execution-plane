import { useState, useCallback, useRef, useEffect } from "react";
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  ReactFlowInstance,
} from "reactflow";
import "reactflow/dist/style.css";
import { toast } from "@/hooks/use-toast";
import { useNavigate } from "react-router-dom";

import { nodeTypes } from "./CustomNodes";
import { NodePalette } from "./NodePalette";
import { WorkflowExecutionEngine, WorkflowExecutionResult } from "./WorkflowExecutionEngine";
import { CredentialsManager } from "./CredentialsManager";
import { ExecutionHistory } from "./ExecutionHistory";
import { WorkflowTriggers, WorkflowTrigger } from "./WorkflowTriggers";
import { transformWorkflowForBackend, validateWorkflow as validateWorkflowStructure } from "./workflowTransformers";

import { WorkflowCanvas } from "./WorkflowCanvas";
import { WorkflowToolbar } from "./WorkflowToolbar";
import { NodeConfigPanel } from "./NodeConfigPanel";
import { PerformancePanel } from "./PerformancePanel";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageSquare, Layers, Zap, Key, Clock, ChevronLeft, ChevronRight } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export function WorkflowBuilder() {
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
  const [showChatInputDialog, setShowChatInputDialog] = useState(false);
  const [chatInputMessage, setChatInputMessage] = useState("");
  const [chatInputWelcome, setChatInputWelcome] = useState("");
  const [chatInputResolver, setChatInputResolver] = useState<((value: string) => void) | null>(null);

  // UI State
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true);
  const [activeSidebarTab, setActiveSidebarTab] = useState<"nodes" | "triggers" | "credentials" | "history">("nodes");
  const [showPerformance, setShowPerformance] = useState(false);

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

  // Update agent node labels when agents are loaded
  useEffect(() => {
    if (agents.length === 0 || nodes.length === 0) return;

    setNodes((currentNodes) =>
      currentNodes.map((node) => {
        if (node.type === "agentNode" && node.data.agent_id) {
          // Check if label is generic/default
          if (node.data.label === "Agent Task" || node.data.label === "AI Agent") {
            const agent = agents.find(a => a.agent_id === node.data.agent_id);
            if (agent) {
              return {
                ...node,
                data: {
                  ...node.data,
                  label: agent.name
                }
              };
            }
          }
        }
        return node;
      })
    );
  }, [agents, nodes.length]); // Only run when agents load or node count changes (initial load)

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
      case "startNode": return { label: "Start" };
      case "endNode": return { label: "End" };
      case "agentNode": return { label: "Agent Task", agent_id: "", description: "", parameters: {} };
      case "conditionNode": return { label: "If Condition", condition: "" };
      case "loopNode": return { label: "Loop", iterations: 10, description: "" };
      case "actionNode": return { label: "Custom Action", action_type: "", description: "", config: {} };
      case "errorHandlerNode": return { label: "Error Handler", error_type: "all", description: "" };
      case "chatNode": return { label: "Chat / Manual", description: "Interactive manual trigger", welcomeMessage: "Hello! How can I help you?" };
      case "displayNode": return { label: "Display Output", description: "Shows execution results", previewData: {} };
      default: return { label: "Node" };
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
    (workflowData.definition as any).visualization = {
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
    await executeWorkflowWithInput();
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

    // Auto-save workflow if it hasn't been saved yet (temporary ID)
    if (workflowId.startsWith('workflow-')) {
      if (!workflowName.trim()) {
        toast({
          title: "Save Required",
          description: "Please save the workflow before executing",
          variant: "destructive",
        });
        return;
      }

      // Save the workflow first
      await handleSaveWorkflow();

      // Small delay to ensure state is updated
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    setIsExecuting(true);
    setIsPaused(false);

    try {
      // Use default message for workflow execution
      const variables = {
        message: "Execute workflow"
      };

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

      // Save execution to backend for history
      console.log("[Execution History] Attempting to save execution:", {
        workflowId,
        executionId: result.executionId,
        status: result.status,
        nodeResultsCount: result.nodeResults?.length || 0
      });

      try {
        const saveResponse = await fetch(`http://localhost:8000/api/v1/workflows/save-execution`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ...result,
            workflowId
          }),
        });

        console.log("[Execution History] Save response status:", saveResponse.status);

        if (saveResponse.ok) {
          const savedData = await saveResponse.json();
          console.log("[Execution History] Successfully saved execution:", savedData);
        } else {
          const errorText = await saveResponse.text();
          console.error("[Execution History] Failed to save execution:", errorText);
        }
      } catch (error) {
        console.error("[Execution History] Error saving execution to backend:", error);
      }

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

  const handleNodeUpdate = (nodeId: string, status: string, output?: any, executionTime?: number) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId
          ? {
            ...node,
            data: {
              ...node.data,
              status,
              lastOutput: output,
              executionTime: executionTime !== undefined ? executionTime : node.data.executionTime
            }
          }
          : node
      )
    );

    // Update edge animations based on execution flow
    if (status === "running") {
      setEdges((eds) =>
        eds.map((edge) => {
          if (edge.target === nodeId) {
            return {
              ...edge,
              animated: true,
              style: { ...edge.style, stroke: '#10b981', strokeWidth: 3, opacity: 1 },
            };
          }
          return edge;
        })
      );
    } else if (status === "completed" || status === "failed") {
      // Reset edges coming into this node to completed state (solid line, no animation)
      setEdges((eds) =>
        eds.map((edge) => {
          if (edge.target === nodeId) {
            return {
              ...edge,
              animated: false,
              style: { ...edge.style, stroke: status === "completed" ? '#10b981' : '#ef4444', strokeWidth: 2, opacity: 0.5 },
            };
          }
          return edge;
        })
      );
    }
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
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      <WorkflowToolbar
        workflowName={workflowName}
        setWorkflowName={setWorkflowName}
        workflowId={workflowId}
        isExecuting={isExecuting}
        isPaused={isPaused}
        testMode={testMode}
        setTestMode={setTestMode}
        executionStatus={currentExecution?.status}
        onExecute={handleExecuteWorkflow}
        onPause={handlePauseWorkflow}
        onStop={handleStopWorkflow}
        onSave={handleSaveWorkflow}
        onExport={exportWorkflow}
        onImport={importWorkflow}
        onClear={clearWorkflow}
        showPerformance={showPerformance}
        onTogglePerformance={() => setShowPerformance(!showPerformance)}
      />

      <div className="flex-1 flex overflow-hidden relative">
        {showPerformance && (
          <PerformancePanel
            nodes={nodes}
            executionResult={currentExecution}
            onClose={() => setShowPerformance(false)}
          />
        )}
        {/* Activity Bar (Fixed Left Strip) */}
        <div className="w-14 border-r bg-muted/40 flex flex-col items-center py-4 gap-4 z-20">
          <Button
            variant={activeSidebarTab === "nodes" && leftSidebarOpen ? "secondary" : "ghost"}
            size="icon"
            className="h-10 w-10 rounded-xl"
            onClick={() => {
              if (activeSidebarTab === "nodes" && leftSidebarOpen) {
                setLeftSidebarOpen(false);
              } else {
                setActiveSidebarTab("nodes");
                setLeftSidebarOpen(true);
              }
            }}
            title="Components"
          >
            <Layers className="w-5 h-5" />
          </Button>
          <Button
            variant={activeSidebarTab === "triggers" && leftSidebarOpen ? "secondary" : "ghost"}
            size="icon"
            className="h-10 w-10 rounded-xl"
            onClick={() => {
              if (activeSidebarTab === "triggers" && leftSidebarOpen) {
                setLeftSidebarOpen(false);
              } else {
                setActiveSidebarTab("triggers");
                setLeftSidebarOpen(true);
              }
            }}
            title="Triggers"
          >
            <Zap className="w-5 h-5" />
          </Button>
          <Button
            variant={activeSidebarTab === "credentials" && leftSidebarOpen ? "secondary" : "ghost"}
            size="icon"
            className="h-10 w-10 rounded-xl"
            onClick={() => {
              if (activeSidebarTab === "credentials" && leftSidebarOpen) {
                setLeftSidebarOpen(false);
              } else {
                setActiveSidebarTab("credentials");
                setLeftSidebarOpen(true);
              }
            }}
            title="Credentials"
          >
            <Key className="w-5 h-5" />
          </Button>
          <Button
            variant={activeSidebarTab === "history" && leftSidebarOpen ? "secondary" : "ghost"}
            size="icon"
            className="h-10 w-10 rounded-xl"
            onClick={() => {
              if (activeSidebarTab === "history" && leftSidebarOpen) {
                setLeftSidebarOpen(false);
              } else {
                setActiveSidebarTab("history");
                setLeftSidebarOpen(true);
              }
            }}
            title="History"
          >
            <Clock className="w-5 h-5" />
          </Button>
        </div>

        {/* Side Panel (Collapsible Content) */}
        <div
          className={`
             border-r bg-card flex flex-col transition-all duration-300 ease-in-out z-10 overflow-hidden
             ${leftSidebarOpen ? "w-72 opacity-100" : "w-0 opacity-0"}
           `}
        >
          {activeSidebarTab === "nodes" && <NodePalette />}

          {activeSidebarTab === "triggers" && (
            <div className="flex flex-col h-full">
              <div className="p-4 border-b border-border/50">
                <h2 className="font-semibold text-sm">Triggers</h2>
                <p className="text-xs text-muted-foreground mt-1">Configure when workflows run</p>
              </div>
              <ScrollArea className="flex-1">
                <div className="p-4">
                  <WorkflowTriggers
                    workflowId={workflowId}
                    triggers={triggers}
                    onTriggersChange={setTriggers}
                  />
                </div>
              </ScrollArea>
            </div>
          )}

          {activeSidebarTab === "credentials" && (
            <div className="flex flex-col h-full">
              <div className="p-4 border-b border-border/50">
                <h2 className="font-semibold text-sm">Credentials</h2>
                <p className="text-xs text-muted-foreground mt-1">Manage API keys & tokens</p>
              </div>
              <ScrollArea className="flex-1">
                <div className="p-4">
                  <CredentialsManager />
                </div>
              </ScrollArea>
            </div>
          )}

          {activeSidebarTab === "history" && (
            <div className="flex flex-col h-full">
              <div className="p-4 border-b border-border/50">
                <h2 className="font-semibold text-sm">Execution History</h2>
                <p className="text-xs text-muted-foreground mt-1">Past workflow runs</p>
              </div>
              <ScrollArea className="flex-1">
                <div className="p-4">
                  <ExecutionHistory workflowId={workflowId} />
                </div>
              </ScrollArea>
            </div>
          )}
        </div>

        {/* Canvas Area */}
        <div className="flex-1 h-full relative" ref={reactFlowWrapper}>
          <WorkflowCanvas
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={handleNodeClick}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            showMinimap={true}
          />
        </div>
      </div>

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

      {/* Enhanced Node Configuration Sheet */}
      <NodeConfigPanel
        isOpen={isNodeDialogOpen}
        onOpenChange={setIsNodeDialogOpen}
        selectedNode={selectedNode}
        updateNode={updateNode}
        handleSaveNode={handleSaveNode}
        handleDeleteNode={handleDeleteNode}
        agents={agents}
        credentials={credentials}
      />
    </div>
  );
}
