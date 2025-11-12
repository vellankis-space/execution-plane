import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Play, Pause, RotateCcw, Eye } from "lucide-react";
import { WorkflowVisualization } from "./WorkflowVisualization";
import { toast } from "@/hooks/use-toast";

interface WorkflowStep {
  id: string;
  name: string;
  agent_id: string;
  description: string;
  position?: { x: number; y: number };
}

interface StepExecution {
  id: number;
  step_id: string;
  execution_id: string;
  agent_id: string;
  status: "pending" | "running" | "completed" | "failed";
  input_data: Record<string, any> | null;
  output_data: Record<string, any> | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

interface WorkflowExecution {
  execution_id: string;
  workflow_id: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  input_data: Record<string, any> | null;
  output_data: Record<string, any> | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  step_executions: StepExecution[];
}

interface WorkflowExecutionMonitorProps {
  executionId: string;
}

export function WorkflowExecutionMonitor({ executionId }: WorkflowExecutionMonitorProps) {
  const [execution, setExecution] = useState<WorkflowExecution | null>(null);
  const [steps, setSteps] = useState<WorkflowStep[]>([]);
  const [dependencies, setDependencies] = useState<Record<string, string[]>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [polling, setPolling] = useState(true);

  // Fetch workflow execution data
  const fetchExecutionData = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/workflow-executions/${executionId}`);
      if (response.ok) {
        const data = await response.json();
        setExecution(data);
        
        // Extract steps from workflow definition if available
        if (data.workflow?.definition?.steps) {
          setSteps(data.workflow.definition.steps);
        }
        
        // Extract dependencies if available
        if (data.workflow?.definition?.dependencies) {
          setDependencies(data.workflow.definition.dependencies);
        }
      } else {
        throw new Error("Failed to fetch execution data");
      }
    } catch (error) {
      console.error("Error fetching execution data:", error);
      toast({
        title: "Error",
        description: "Failed to fetch workflow execution data",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Poll for updates
  useEffect(() => {
    if (!executionId) return;
    
    fetchExecutionData();
    
    if (polling) {
      const interval = setInterval(() => {
        fetchExecutionData();
      }, 3000); // Poll every 3 seconds
      
      return () => clearInterval(interval);
    }
  }, [executionId, polling]);

  // Get execution status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending": return "bg-gray-100 text-gray-800";
      case "running": return "bg-blue-100 text-blue-800";
      case "completed": return "bg-green-100 text-green-800";
      case "failed": return "bg-red-100 text-red-800";
      case "cancelled": return "bg-yellow-100 text-yellow-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  // Create execution status map for visualization
  const executionStatusMap = execution?.step_executions.reduce((acc, step) => {
    acc[step.step_id] = step.status;
    return acc;
  }, {} as Record<string, string>) || {};

  // Handle step click to show details
  const handleStepClick = (stepId: string) => {
    const stepExecution = execution?.step_executions.find(se => se.step_id === stepId);
    if (stepExecution) {
      // In a real implementation, you might open a modal with step details
      console.log("Step clicked:", stepExecution);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading workflow execution...</div>
      </div>
    );
  }

  if (!execution) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-red-500">Failed to load workflow execution</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Workflow Execution</h2>
          <p className="text-muted-foreground">
            Monitoring execution: {execution.execution_id}
          </p>
        </div>
        <div className="flex gap-2">
          <Badge className={getStatusColor(execution.status)}>
            {execution.status.charAt(0).toUpperCase() + execution.status.slice(1)}
          </Badge>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setPolling(!polling)}
          >
            {polling ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
            {polling ? "Pause" : "Resume"} Updates
          </Button>
          <Button variant="outline" size="sm" onClick={fetchExecutionData}>
            <RotateCcw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      <Card className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Started</h4>
            <p className="font-medium">
              {execution.started_at ? new Date(execution.started_at).toLocaleString() : "Not started"}
            </p>
          </div>
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Completed</h4>
            <p className="font-medium">
              {execution.completed_at ? new Date(execution.completed_at).toLocaleString() : "Not completed"}
            </p>
          </div>
          <div>
            <h4 className="text-sm font-medium text-muted-foreground">Duration</h4>
            <p className="font-medium">
              {execution.started_at && execution.completed_at ? 
                `${Math.round((new Date(execution.completed_at).getTime() - new Date(execution.started_at).getTime()) / 1000)}s` : 
                execution.started_at ? "In progress" : "Not started"}
            </p>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Execution Visualization</h3>
          <div className="h-96">
            <WorkflowVisualization 
              steps={steps}
              dependencies={dependencies}
              executionStatus={executionStatusMap}
              onStepClick={handleStepClick}
            />
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Step Executions</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {execution.step_executions.map((step) => (
              <Card key={step.id} className="p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium">{step.step_id}</h4>
                    <p className="text-sm text-muted-foreground">Agent: {step.agent_id}</p>
                  </div>
                  <Badge className={getStatusColor(step.status)}>
                    {step.status.charAt(0).toUpperCase() + step.status.slice(1)}
                  </Badge>
                </div>
                
                <div className="mt-2 text-sm">
                  {step.started_at && (
                    <p>Started: {new Date(step.started_at).toLocaleTimeString()}</p>
                  )}
                  {step.completed_at && (
                    <p>Completed: {new Date(step.completed_at).toLocaleTimeString()}</p>
                  )}
                  {step.error_message && (
                    <p className="text-red-500 mt-1">Error: {step.error_message}</p>
                  )}
                </div>
                
                <div className="mt-2 flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => handleStepClick(step.step_id)}>
                    <Eye className="w-4 h-4 mr-1" />
                    View Details
                  </Button>
                </div>
              </Card>
            ))}
            
            {execution.step_executions.length === 0 && (
              <p className="text-muted-foreground text-center py-4">
                No step executions found
              </p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}