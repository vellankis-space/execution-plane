import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Plus, Play, Trash2, Edit } from "lucide-react";
import { toast } from "@/hooks/use-toast";

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

  const handleExecuteWorkflow = async (workflowId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/workflows/${workflowId}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_id: workflowId,
          input_data: {}
        }),
      });

      if (response.ok) {
        toast({
          title: "Workflow Started",
          description: "The workflow has been started successfully.",
        });
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
      <div className="flex items-center justify-between border-b pb-4">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">Workflows</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {workflows.length} {workflows.length === 1 ? 'workflow' : 'workflows'} configured
          </p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Create Workflow
        </Button>
      </div>
      {workflows.length === 0 ? (
        <Card className="border-dashed">
          <div className="p-12 text-center">
            <div className="mx-auto mb-4 flex items-center justify-center w-16 h-16 rounded-full bg-muted">
              <Play className="w-8 h-8 text-muted-foreground" />
            </div>
            <p className="text-muted-foreground text-sm">No workflows created yet. Create your first workflow!</p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workflows.map((workflow) => (
            <Card 
              key={workflow.workflow_id} 
              className="group hover:shadow-lg transition-all duration-200 hover:border-primary/50 overflow-hidden"
            >
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 min-w-0 flex-1">
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center flex-shrink-0 shadow-sm">
                      <Play className="w-6 h-6 text-primary-foreground" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="font-semibold text-lg group-hover:text-primary transition-colors truncate">
                        {workflow.name || "Unnamed Workflow"}
                      </h3>
                      <p className="text-sm text-muted-foreground mt-1 truncate">
                        {workflow.description || "No description"}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center justify-between mt-4">
                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="h-8 px-3"
                      onClick={() => handleExecuteWorkflow(workflow.workflow_id)}
                    >
                      <Play className="w-4 h-4 mr-1" />
                      Run
                    </Button>
                    <Button variant="outline" size="sm" className="h-8 px-3">
                      <Edit className="w-4 h-4 mr-1" />
                      Edit
                    </Button>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDeleteWorkflow(workflow.workflow_id, workflow.name)}
                    className="text-muted-foreground hover:text-destructive hover:bg-destructive/10"
                  >
                    <Trash2 className="w-5 h-5" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}