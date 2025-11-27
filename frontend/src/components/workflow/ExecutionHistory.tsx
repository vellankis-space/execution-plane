import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  PlayCircle,
  ChevronRight,
  Calendar,
  Timer,
} from "lucide-react";
import { WorkflowExecutionResult, NodeExecutionResult } from "./WorkflowExecutionEngine";

interface ExecutionHistoryProps {
  workflowId: string;
}

export function ExecutionHistory({ workflowId }: ExecutionHistoryProps) {
  const [executions, setExecutions] = useState<WorkflowExecutionResult[]>([]);
  const [selectedExecution, setSelectedExecution] = useState<WorkflowExecutionResult | null>(
    null
  );
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  useEffect(() => {
    loadExecutions();
    // Poll for updates every 5 seconds
    const interval = setInterval(loadExecutions, 5000);
    return () => clearInterval(interval);
  }, [workflowId]);

  const loadExecutions = async () => {
    console.log("[ExecutionHistory] Loading executions for workflow:", workflowId);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/workflows/${workflowId}/executions`
      );
      console.log("[ExecutionHistory] Response status:", response.status);

      if (response.ok) {
        const data = await response.json();
        console.log("[ExecutionHistory] Received data:", data);

        // Ensure data is an array and sort by startTime descending
        const validData = Array.isArray(data) ? data : [];
        const sortedData = validData.sort((a: WorkflowExecutionResult, b: WorkflowExecutionResult) =>
          new Date(b.startTime).getTime() - new Date(a.startTime).getTime()
        );
        console.log("[ExecutionHistory] Setting", sortedData.length, "executions");
        setExecutions(sortedData);
      }
    } catch (error) {
      console.error("[ExecutionHistory] Error loading executions:", error);
      setExecutions([]); // Fallback to empty array on error
    }
  };

  const handleViewExecution = (execution: WorkflowExecutionResult) => {
    setSelectedExecution(execution);
    setIsDialogOpen(true);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
      case "success":
        return <CheckCircle2 className="w-4 h-4 text-green-600" />;
      case "failed":
      case "error":
        return <XCircle className="w-4 h-4 text-red-600" />;
      case "running":
        return <PlayCircle className="w-4 h-4 text-blue-600 animate-pulse" />;
      case "paused":
        return <AlertCircle className="w-4 h-4 text-yellow-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusBadgeVariant = (status: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (status) {
      case "completed":
      case "success":
        return "default";
      case "failed":
      case "error":
        return "destructive";
      case "running":
        return "secondary";
      default:
        return "outline";
    }
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
    return `${(ms / 60000).toFixed(2)}m`;
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-semibold">Execution History</h3>
        <p className="text-sm text-muted-foreground">
          View past workflow executions and their results
        </p>
      </div>

      <ScrollArea className="h-[500px]">
        <div className="space-y-2">
          {executions.length === 0 ? (
            <Card className="p-8 text-center">
              <Clock className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <h4 className="font-semibold mb-2">No executions yet</h4>
              <p className="text-sm text-muted-foreground">
                Run your workflow to see execution history here
              </p>
            </Card>
          ) : (
            executions.map((execution, index) => (
              <Card
                key={`${execution.executionId}-${index}`}
                className="p-4 hover:bg-muted/50 cursor-pointer transition-colors"
                onClick={() => handleViewExecution(execution)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1">
                    {getStatusIcon(execution.status)}
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">
                          {new Date(execution.startTime).toLocaleString()}
                        </span>
                        <Badge variant={getStatusBadgeVariant(execution.status)}>
                          {execution.status}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 mt-1 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Timer className="w-3 h-3" />
                          {execution.totalExecutionTime
                            ? formatDuration(execution.totalExecutionTime)
                            : "In progress"}
                        </span>
                        <span>
                          {(execution.nodeResults || []).length} nodes executed
                        </span>
                        {(execution.nodeResults || []).filter((n) => n.status === "error")
                          .length > 0 && (
                            <span className="text-red-600">
                              {
                                (execution.nodeResults || []).filter((n) => n.status === "error")
                                  .length
                              }{" "}
                              errors
                            </span>
                          )}
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground" />
                </div>
              </Card>
            ))
          )}
        </div>
      </ScrollArea>

      {/* Execution Details Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="sm:max-w-[800px] max-h-[80vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              Execution Details
              {selectedExecution && (
                <Badge variant={getStatusBadgeVariant(selectedExecution.status)}>
                  {selectedExecution.status}
                </Badge>
              )}
            </DialogTitle>
            <DialogDescription>
              {selectedExecution && (
                <div className="flex items-center gap-4 text-sm mt-2">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {new Date(selectedExecution.startTime).toLocaleString()}
                  </span>
                  {selectedExecution.totalExecutionTime && (
                    <span className="flex items-center gap-1">
                      <Timer className="w-3 h-3" />
                      {formatDuration(selectedExecution.totalExecutionTime)}
                    </span>
                  )}
                </div>
              )}
            </DialogDescription>
          </DialogHeader>

          {selectedExecution && (
            <ScrollArea className="h-[500px] pr-4">
              <div className="space-y-4">
                {(selectedExecution.nodeResults || []).map((nodeResult, index) => (
                  <Card key={`${nodeResult.nodeId}-${index}`} className="p-4">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(nodeResult.status)}
                        <h4 className="font-semibold">{nodeResult.nodeId}</h4>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Timer className="w-3 h-3" />
                        {formatDuration(nodeResult.executionTime)}
                      </div>
                    </div>

                    {nodeResult.error && (
                      <div className="bg-destructive/10 border border-destructive/20 rounded-md p-3 mb-3">
                        <div className="flex items-start gap-2">
                          <XCircle className="w-4 h-4 text-destructive mt-0.5" />
                          <div className="flex-1">
                            <p className="text-sm font-semibold text-destructive">Error</p>
                            <p className="text-xs text-destructive/80 mt-1">
                              {nodeResult.error}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {nodeResult.output && (
                      <div className="bg-muted rounded-md p-3">
                        <p className="text-xs font-semibold mb-2">Output</p>
                        <pre className="text-xs overflow-auto max-h-40">
                          {JSON.stringify(nodeResult.output, null, 2)}
                        </pre>
                      </div>
                    )}

                    <p className="text-xs text-muted-foreground mt-2">
                      {new Date(nodeResult.timestamp).toLocaleString()}
                    </p>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          )}

          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
