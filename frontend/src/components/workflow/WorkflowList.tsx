import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Plus, Network, Trash2, Edit, Play, Send } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { useNavigate } from "react-router-dom";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";

interface Workflow {
  workflow_id: string;
  name: string;
  description: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export function WorkflowList() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [executeDialogOpen, setExecuteDialogOpen] = useState(false);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [inputMessage, setInputMessage] = useState("");
  const [executing, setExecuting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/workflows');
      if (response.ok) {
        const data = await response.json();
        setWorkflows(data);
      } else {
        console.error("Failed to fetch workflows, status:", response.status);
        toast({
          title: "Error",
          description: `Failed to load workflows. Status: ${response.status}`,
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Error fetching workflows:", error);
      toast({
        title: "Error",
        description: "Failed to load workflows. Please check if the backend is running.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteWorkflow = async (workflowId: string, workflowName: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/workflows/${workflowId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setWorkflows(workflows.filter(workflow => workflow.workflow_id !== workflowId));
        toast({
          title: "Workflow Deleted",
          description: `${workflowName} has been successfully deleted.`,
        });
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete workflow');
      }
    } catch (error) {
      console.error("Error deleting workflow:", error);
      toast({
        title: "Error Deleting Workflow",
        description: error.message || "Failed to delete workflow. Please try again.",
        variant: "destructive",
      });
    }
  };

  const openExecuteDialog = (workflow: Workflow) => {
    setSelectedWorkflow(workflow);
    setInputMessage("");
    setExecuteDialogOpen(true);
  };

  const handleExecuteWorkflow = async () => {
    if (!selectedWorkflow) return;
    
    try {
      setExecuting(true);
      const response = await fetch(`http://localhost:8000/api/v1/workflows/${selectedWorkflow.workflow_id}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: selectedWorkflow.workflow_id,
          input_data: {
            message: inputMessage || "Hello" // Default message if empty
          }
        }),
      });

      if (response.ok) {
        toast({
          title: "Workflow Started",
          description: `"${selectedWorkflow.name}" has been started successfully.`,
        });
        setExecuteDialogOpen(false);
        setInputMessage("");
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to start workflow');
      }
    } catch (error) {
      console.error("Error executing workflow:", error);
      toast({
        title: "Error Executing Workflow",
        description: error.message || "Failed to execute workflow. Please try again.",
        variant: "destructive",
      });
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-4">
        <div>
          <p className="text-sm text-muted-foreground">
            {workflows.length} {workflows.length === 1 ? 'workflow' : 'workflows'} configured
          </p>
        </div>
      </div>
      {workflows.length === 0 ? (
        <Card className="border-dashed border-border/50 bg-card/50">
          <div className="p-12 text-center">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500/20 to-purple-600/20 mx-auto mb-4 flex items-center justify-center">
              <Network className="w-8 h-8 text-purple-500" />
            </div>
            <h3 className="font-semibold text-lg mb-2">No workflows yet</h3>
            <p className="text-muted-foreground text-sm mb-6">
              Create your first workflow to orchestrate multiple agents
            </p>
            <Button onClick={() => navigate('/production-workflow')} className="shine-effect">
              <Plus className="w-4 h-4 mr-2" />
              Create Workflow
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workflows.map((workflow) => (
            <Card 
              key={workflow.workflow_id} 
              className="group relative overflow-hidden border-border/50 bg-gradient-to-br from-card to-card/50 hover:shadow-2xl transition-all duration-300 hover:scale-[1.02] h-full"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="p-6 relative">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-purple-500/25 group-hover:scale-110 transition-transform">
                      <Network className="w-6 h-6 text-white" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="font-semibold text-lg group-hover:text-primary transition-colors truncate">
                        {workflow.name || "Unnamed Workflow"}
                      </h3>
                      <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                        {workflow.description || "No description"}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDeleteWorkflow(workflow.workflow_id, workflow.name)}
                    className="text-muted-foreground hover:text-destructive hover:bg-destructive/10 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 h-8 w-8"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
                
                {/* Workflow Status Badge */}
                <div className="mb-4">
                  <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted/50 text-xs">
                    <div className={`w-2 h-2 rounded-full ${workflow.is_active ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
                    <span className="font-medium">{workflow.is_active ? 'Active' : 'Inactive'}</span>
                  </div>
                </div>

                <div className="flex gap-2 pt-4 border-t border-border/50">
                  <Button 
                    size="sm" 
                    className="flex-1 gap-2 bg-gradient-to-r from-primary to-primary/90 shine-effect"
                    onClick={() => openExecuteDialog(workflow)}
                  >
                    <Play className="w-4 h-4" />
                    Run
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="flex-1 gap-2 hover:bg-primary/10 hover:border-primary/50"
                    onClick={() => navigate(`/workflow-builder?id=${workflow.workflow_id}`)}
                  >
                    <Edit className="w-4 h-4" />
                    Edit
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Execute Workflow Dialog */}
      <Dialog open={executeDialogOpen} onOpenChange={setExecuteDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Execute Workflow</DialogTitle>
            <DialogDescription>
              {selectedWorkflow?.name && `Provide an input message for "${selectedWorkflow.name}"`}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Input Message</label>
              <Textarea
                placeholder="Type your message here... (e.g., 'Analyze this data' or 'Generate a report')"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                rows={4}
                className="resize-none"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.ctrlKey && !executing) {
                    handleExecuteWorkflow();
                  }
                }}
              />
              <p className="text-xs text-muted-foreground">
                Press Ctrl+Enter to execute
              </p>
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setExecuteDialogOpen(false)}
                disabled={executing}
              >
                Cancel
              </Button>
              <Button
                onClick={handleExecuteWorkflow}
                disabled={executing}
                className="gap-2"
              >
                {executing ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-background border-t-transparent" />
                    Executing...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Execute
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}