import { X, Activity, Clock, AlertCircle, CheckCircle2 } from "lucide-react";
import { Node } from "reactflow";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { WorkflowExecutionResult } from "./WorkflowExecutionEngine";

interface PerformancePanelProps {
    nodes: Node[];
    executionResult?: WorkflowExecutionResult | null;
    onClose: () => void;
}

export function PerformancePanel({ nodes, executionResult, onClose }: PerformancePanelProps) {
    // Calculate metrics based on execution result if available, otherwise fallback to nodes
    const totalTime = executionResult?.totalExecutionTime ||
        nodes.reduce((acc, node) => acc + (node.data.executionTime || 0), 0);

    const successCount = executionResult
        ? executionResult.nodeResults.filter(n => n.status === "success").length
        : nodes.filter(n => n.data.status === "completed").length;

    const failureCount = executionResult
        ? executionResult.nodeResults.filter(n => n.status === "error").length
        : nodes.filter(n => n.data.status === "failed").length;

    const runningCount = executionResult
        ? (executionResult.status === "running" ? 1 : 0) // Simplified for workflow level
        : nodes.filter(n => n.data.status === "running").length;

    // Sort by execution time (descending)
    // If we have execution result, use that for more accurate timing
    const sortedNodes = executionResult
        ? [...executionResult.nodeResults]
            .sort((a, b) => b.executionTime - a.executionTime)
            .map(result => {
                const node = nodes.find(n => n.id === result.nodeId);
                return {
                    id: result.nodeId,
                    label: node?.data.label || node?.type || result.nodeId,
                    executionTime: result.executionTime,
                    status: result.status === "success" ? "completed" : result.status === "error" ? "failed" : "running",
                    type: node?.type
                };
            })
        : [...nodes]
            .filter(node => node.data.executionTime !== undefined || node.data.status === "running" || node.data.status === "failed")
            .sort((a, b) => (b.data.executionTime || 0) - (a.data.executionTime || 0))
            .map(node => ({
                id: node.id,
                label: node.data.label || node.type,
                executionTime: node.data.executionTime || 0,
                status: node.data.status,
                type: node.type
            }));

    return (
        <div className="absolute bottom-4 right-4 w-96 bg-background/95 backdrop-blur-md border rounded-xl shadow-2xl z-50 flex flex-col max-h-[500px] animate-in slide-in-from-bottom-5 fade-in duration-300">
            <div className="flex items-center justify-between p-4 border-b">
                <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-blue-500" />
                    <h3 className="font-semibold text-sm">Performance Profile</h3>
                </div>
                <Button variant="ghost" size="icon" className="h-6 w-6" onClick={onClose}>
                    <X className="w-4 h-4" />
                </Button>
            </div>

            <div className="p-4 border-b bg-muted/30">
                <div className="flex justify-between items-end mb-2">
                    <span className="text-xs text-muted-foreground">Total Execution Time</span>
                    <span className="text-lg font-mono font-bold text-foreground">
                        {totalTime < 1000 ? `${totalTime}ms` : `${(totalTime / 1000).toFixed(2)}s`}
                    </span>
                </div>
                <div className="flex gap-2 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-green-500" />
                        {successCount}
                    </div>
                    <div className="flex items-center gap-1">
                        <AlertCircle className="w-3 h-3 text-red-500" />
                        {failureCount}
                    </div>
                    <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-blue-500" />
                        {runningCount}
                    </div>
                </div>
            </div>

            <ScrollArea className="flex-1">
                <div className="p-2 space-y-1">
                    {sortedNodes.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                            <Activity className="w-8 h-8 mb-2 opacity-20" />
                            <p className="text-xs">No execution data available</p>
                        </div>
                    ) : (
                        sortedNodes.map((node) => {
                            const percentage = totalTime > 0 ? (node.executionTime / totalTime) * 100 : 0;

                            return (
                                <div key={node.id} className="p-2 rounded-lg hover:bg-muted/50 transition-colors group">
                                    <div className="flex justify-between items-start mb-1">
                                        <div className="flex items-center gap-2 min-w-0">
                                            <Badge variant="outline" className="text-[10px] px-1 h-4 font-mono text-muted-foreground">
                                                {node.id.slice(0, 4)}
                                            </Badge>
                                            <span className="text-xs font-medium truncate max-w-[120px]">
                                                {node.label}
                                            </span>
                                        </div>
                                        <span className="text-xs font-mono text-muted-foreground">
                                            {node.executionTime}ms
                                        </span>
                                    </div>

                                    <div className="relative h-1.5 bg-muted rounded-full overflow-hidden">
                                        <div
                                            className={`absolute top-0 left-0 h-full rounded-full transition-all duration-500 ${node.status === "failed" ? "bg-red-500" :
                                                node.status === "running" ? "bg-blue-500 animate-pulse" :
                                                    "bg-emerald-500"
                                                }`}
                                            style={{ width: `${percentage}%` }}
                                        />
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>
            </ScrollArea>
        </div>
    );
}
