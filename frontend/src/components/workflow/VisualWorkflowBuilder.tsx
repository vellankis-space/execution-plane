import { useState, useCallback, useMemo, useEffect } from "react";
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
  NodeTypes,
  BackgroundVariant,
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
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, Save, Play, Trash2, Settings } from "lucide-react";
import { toast } from "@/hooks/use-toast";

// Custom Node Component
const WorkflowNode = ({ data, selected }: any) => {
  return (
    <div
      className={`px-4 py-3 shadow-md rounded-md bg-white border-2 ${
        selected ? "border-blue-500" : "border-gray-300"
      }`}
      style={{ minWidth: "200px" }}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="font-semibold text-sm">{data.label}</div>
        {data.status && (
          <span
            className={`text-xs px-2 py-1 rounded ${
              data.status === "completed"
                ? "bg-green-100 text-green-800"
                : data.status === "running"
                ? "bg-blue-100 text-blue-800"
                : data.status === "failed"
                ? "bg-red-100 text-red-800"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            {data.status}
          </span>
        )}
      </div>
      <div className="text-xs text-gray-600">
        Agent: {data.agent_id || "Not set"}
      </div>
      {data.description && (
        <div className="text-xs text-gray-500 mt-1 truncate">
          {data.description}
        </div>
      )}
    </div>
  );
};

const nodeTypes: NodeTypes = {
  workflowNode: WorkflowNode,
};

interface WorkflowStep {
  id: string;
  name: string;
  agent_id: string;
  description: string;
  position?: { x: number; y: number };
}

interface VisualWorkflowBuilderProps {
  workflowName?: string;
  workflowDescription?: string;
  initialSteps?: WorkflowStep[];
  initialDependencies?: Record<string, string[]>;
  onSave?: (workflow: any) => void;
}

export function VisualWorkflowBuilder({
  workflowName: initialName = "",
  workflowDescription: initialDescription = "",
  initialSteps = [],
  initialDependencies = {},
  onSave,
}: VisualWorkflowBuilderProps) {
  const [workflowName, setWorkflowName] = useState(initialName);
  const [workflowDescription, setWorkflowDescription] = useState(
    initialDescription
  );
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [isNodeDialogOpen, setIsNodeDialogOpen] = useState(false);
  const [agents, setAgents] = useState<Array<{ agent_id: string; name: string }>>([]);

  // Convert initial steps to React Flow nodes
  const initialNodes: Node[] = useMemo(() => {
    if (initialSteps.length > 0) {
      return initialSteps.map((step, index) => ({
        id: step.id,
        type: "workflowNode",
        position: step.position || { x: 250 * (index % 3), y: 150 * Math.floor(index / 3) },
        data: {
          label: step.name,
          agent_id: step.agent_id,
          description: step.description,
        },
      }));
    }
    return [];
  }, [initialSteps]);

  // Convert initial dependencies to React Flow edges
  const initialEdges: Edge[] = useMemo(() => {
    const edges: Edge[] = [];
    Object.entries(initialDependencies).forEach(([targetId, sourceIds]) => {
      sourceIds.forEach((sourceId) => {
        edges.push({
          id: `e${sourceId}-${targetId}`,
          source: sourceId,
          target: targetId,
          type: "smoothstep",
          animated: false,
        });
      });
    });
    return edges;
  }, [initialDependencies]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Load agents on mount
  useEffect(() => {
    fetch("http://localhost:8000/api/v1/agents/")
      .then((res) => res.json())
      .then((data) => {
        setAgents(data || []);
      })
      .catch((err) => {
        console.error("Error loading agents:", err);
      });
  }, []);

  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => addEdge(params, eds));
    },
    [setEdges]
  );

  const addNode = () => {
    const newNode: Node = {
      id: `step-${Date.now()}`,
      type: "workflowNode",
      position: { x: Math.random() * 400, y: Math.random() * 400 },
      data: {
        label: "New Step",
        agent_id: "",
        description: "",
      },
    };
    setNodes((nds) => [...nds, newNode]);
    setSelectedNode(newNode);
    setIsNodeDialogOpen(true);
  };

  const deleteNode = (nodeId: string) => {
    setNodes((nds) => nds.filter((node) => node.id !== nodeId));
    setEdges((eds) =>
      eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId)
    );
  };

  const updateNode = (nodeId: string, updates: Partial<Node["data"]>) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, ...updates } }
          : node
      )
    );
  };

  const handleNodeClick = (event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
    setIsNodeDialogOpen(true);
  };

  const handleSaveNode = () => {
    if (selectedNode) {
      // Node is already updated via updateNode
      setIsNodeDialogOpen(false);
      setSelectedNode(null);
    }
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

    // Convert React Flow nodes and edges to workflow definition
    const steps = nodes.map((node) => ({
      id: node.id,
      name: node.data.label || "Unnamed Step",
      agent_id: node.data.agent_id || "",
      description: node.data.description || "",
      position: node.position,
    }));

    const dependencies: Record<string, string[]> = {};
    edges.forEach((edge) => {
      if (!dependencies[edge.target]) {
        dependencies[edge.target] = [];
      }
      dependencies[edge.target].push(edge.source);
    });

    const workflowDefinition = {
      steps,
      dependencies,
      conditions: {}, // Can be added later
    };

    const workflowData = {
      name: workflowName,
      description: workflowDescription,
      definition: workflowDefinition,
    };

    if (onSave) {
      onSave(workflowData);
    } else {
      // Default save behavior
      try {
        const response = await fetch("http://localhost:8000/api/v1/workflows", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(workflowData),
        });

        if (response.ok) {
          toast({
            title: "Workflow Saved",
            description: "Your workflow has been saved successfully.",
          });
        } else {
          const error = await response.json();
          throw new Error(error.detail || "Failed to save workflow");
        }
      } catch (error: any) {
        console.error("Error saving workflow:", error);
        toast({
          title: "Error Saving Workflow",
          description: error.message || "Failed to save workflow. Please try again.",
          variant: "destructive",
        });
      }
    }
  };

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <Card className="rounded-none border-x-0 border-t-0 border-b bg-gradient-to-r from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-950/80 p-4 mb-2">
        <div className="space-y-3">
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
            <Textarea
              id="workflow-description"
              placeholder="Describe what this workflow does"
              value={workflowDescription}
              onChange={(e) => setWorkflowDescription(e.target.value)}
              className="mt-1 text-sm"
              rows={3}
            />
          </div>
        </div>
      </Card>

      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 border-b bg-muted/30">
        <div className="flex gap-2">
          <Button onClick={addNode} variant="outline" size="sm">
            <Plus className="w-4 h-4 mr-2" />
            Add Step
          </Button>
          {selectedNode && (
            <Button
              onClick={() => deleteNode(selectedNode.id)}
              variant="outline"
              size="sm"
              className="text-destructive"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete Step
            </Button>
          )}
        </div>
        <Button onClick={handleSaveWorkflow} variant="outline" className="gap-2">
          <Save className="w-4 h-4" />
          Save Workflow
        </Button>
      </div>

      {/* React Flow Canvas */}
      <div className="flex-1 border-t bg-slate-50 dark:bg-slate-950/60">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={handleNodeClick}
          nodeTypes={nodeTypes}
          fitView
          className="bg-slate-50 dark:bg-slate-950/60"
        >
          <Controls />
          <MiniMap />
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        </ReactFlow>
      </div>

      {/* Node Configuration Dialog */}
      <Dialog open={isNodeDialogOpen} onOpenChange={setIsNodeDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Configure Step</DialogTitle>
            <DialogDescription>
              Configure the step details and select an agent
            </DialogDescription>
          </DialogHeader>
          {selectedNode && (
            <div className="space-y-4 mt-4">
              <div>
                <Label htmlFor="step-name">Step Name</Label>
                <Input
                  id="step-name"
                  placeholder="Enter step name"
                  value={selectedNode.data.label || ""}
                  onChange={(e) =>
                    updateNode(selectedNode.id, { label: e.target.value })
                  }
                  className="mt-1"
                />
              </div>
              <div>
                <Label htmlFor="step-agent">Agent</Label>
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
                <Label htmlFor="step-description">Description</Label>
                <Textarea
                  id="step-description"
                  placeholder="Describe what this step does"
                  value={selectedNode.data.description || ""}
                  onChange={(e) =>
                    updateNode(selectedNode.id, { description: e.target.value })
                  }
                  className="mt-1"
                />
              </div>
              <div className="flex justify-end gap-2 pt-4">
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

