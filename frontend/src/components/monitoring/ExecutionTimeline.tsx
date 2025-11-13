import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";

interface Execution {
  execution_id: string;
  workflow_id: string;
  workflow_name?: string;
  status: string;
  started_at: string;
  completed_at?: string;
  execution_time?: number;
  step_count?: number;
  success_count?: number;
  failure_count?: number;
}

export function ExecutionTimeline() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>("all");
  const [workflows, setWorkflows] = useState<Array<{ workflow_id: string; name: string }>>([]);

  // Fetch workflows
  useQuery({
    queryKey: ["workflows"],
    queryFn: async () => {
      const response = await fetch("http://localhost:8000/api/v1/workflows");
      if (!response.ok) throw new Error("Failed to fetch workflows");
      const data = await response.json();
      setWorkflows(data || []);
      return data;
    },
  });

  // Fetch executions
  const { data: executions, isLoading } = useQuery<Execution[]>({
    queryKey: ["executions", selectedWorkflow],
    queryFn: async () => {
      if (selectedWorkflow === "all") {
        // Use recent executions endpoint for all workflows
        const response = await fetch("http://localhost:8000/api/v1/monitoring/recent-executions?limit=50");
        if (!response.ok) throw new Error("Failed to fetch executions");
        const data = await response.json();
        return data.map((exec: any) => ({
          execution_id: exec.execution_id,
          workflow_id: exec.workflow_id,
          workflow_name: exec.workflow_name,
          status: exec.status,
          started_at: exec.started_at,
          completed_at: exec.completed_at,
          execution_time: exec.execution_time,
          step_count: exec.step_count,
          success_count: exec.success_count,
          failure_count: exec.failure_count,
        }));
      } else {
        // Use metrics endpoint for specific workflow
        const response = await fetch(`http://localhost:8000/api/v1/monitoring/metrics/workflow-executions?workflow_id=${selectedWorkflow}`);
        if (!response.ok) throw new Error("Failed to fetch executions");
        const data = await response.json();
        
        if (data.executions && Array.isArray(data.executions)) {
          return data.executions.map((exec: any) => ({
            execution_id: exec.execution_id,
            workflow_id: exec.workflow_id,
            workflow_name: workflows.find(w => w.workflow_id === exec.workflow_id)?.name || "Unknown",
            status: exec.status,
            started_at: exec.started_at || exec.created_at,
            completed_at: exec.completed_at,
            execution_time: exec.execution_time,
            step_count: exec.step_count,
            success_count: exec.success_count,
            failure_count: exec.failure_count,
          }));
        }
        return [];
      }
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500";
      case "failed":
        return "bg-red-500";
      case "running":
        return "bg-blue-500";
      case "pending":
        return "bg-gray-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Execution Timeline</h3>
          <Select value={selectedWorkflow} onValueChange={setSelectedWorkflow}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Select workflow" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Workflows</SelectItem>
              {workflows.map((wf) => (
                <SelectItem key={wf.workflow_id} value={wf.workflow_id}>
                  {wf.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {isLoading ? (
          <div className="text-center py-8 text-muted-foreground">Loading...</div>
        ) : executions && executions.length > 0 ? (
          <div className="space-y-4">
            {executions.map((exec) => (
              <div
                key={exec.execution_id}
                className="flex items-start gap-4 p-4 border rounded-lg hover:bg-muted/50 transition-colors"
              >
                <div className={`w-3 h-3 rounded-full mt-2 ${getStatusColor(exec.status)}`} />
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge variant={exec.status === "completed" ? "default" : exec.status === "failed" ? "destructive" : "secondary"}>
                        {exec.status}
                      </Badge>
                      <span className="text-sm font-mono text-muted-foreground">
                        {exec.execution_id.substring(0, 8)}...
                      </span>
                    </div>
                    {exec.execution_time && (
                      <span className="text-sm text-muted-foreground">
                        {exec.execution_time.toFixed(2)}s
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <p>
                      Started: {format(new Date(exec.started_at), "PPpp")}
                    </p>
                    {exec.completed_at && (
                      <p>
                        Completed: {format(new Date(exec.completed_at), "PPpp")}
                      </p>
                    )}
                    {exec.step_count !== undefined && (
                      <p>
                        Steps: {exec.success_count || 0} succeeded, {exec.failure_count || 0} failed
                        {exec.step_count !== undefined && ` (${exec.step_count} total)`}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No executions found
          </div>
        )}
      </Card>
    </div>
  );
}

