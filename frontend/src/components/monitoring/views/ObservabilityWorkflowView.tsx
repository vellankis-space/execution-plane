import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from "@/components/ui/table";
import {
    GitBranch,
    CheckCircle2,
    XCircle,
    Search,
    Activity,
    Loader2,
    AlertCircle,
    Clock,
    DollarSign,
    Zap,
    TrendingUp,
    PlayCircle
} from 'lucide-react';
import { Button } from "@/components/ui/button";
import { useWorkflows } from '@/services/workflowService';
import { useTraces, useWorkflowMetrics } from '@/services/observabilityService';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { TraceDetailView } from './TraceDetailView';

export function ObservabilityWorkflowView() {
    const { data: workflows, isLoading: isLoadingWorkflows } = useWorkflows();
    const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>("");
    const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
    const [timeRange, setTimeRange] = useState<string>("24h");

    // Auto-select first workflow when loaded
    useEffect(() => {
        if (workflows && workflows.length > 0 && !selectedWorkflowId) {
            setSelectedWorkflowId(workflows[0].workflow_id);
        }
    }, [workflows, selectedWorkflowId]);

    const { data: traces, isLoading: isLoadingTraces } = useTraces({
        workflowId: selectedWorkflowId,
        limit: 10
    });

    // Fetch comprehensive workflow metrics from OpenLLMetry
    const { data: workflowMetrics, isLoading: isLoadingMetrics } = useWorkflowMetrics(selectedWorkflowId, timeRange);

    if (isLoadingWorkflows) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    if (!workflows || workflows.length === 0) {
        return (
            <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>No Workflows Found</AlertTitle>
                <AlertDescription>
                    Please create a workflow first to view observability data.
                </AlertDescription>
            </Alert>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Workflow Selector */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold tracking-tight">Workflow Observability</h2>
                <div className="w-[250px]">
                    <Select value={selectedWorkflowId} onValueChange={setSelectedWorkflowId}>
                        <SelectTrigger>
                            <SelectValue placeholder="Select a workflow" />
                        </SelectTrigger>
                        <SelectContent>
                            {workflows.map((workflow) => (
                                <SelectItem key={workflow.workflow_id} value={workflow.workflow_id}>
                                    {workflow.name || "Unnamed Workflow"}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* Execution Summary - Real OpenLLMetry Data */}
            {workflowMetrics && !isLoadingMetrics && (
                <div className="space-y-4">
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                        <Activity className="w-5 h-5 text-purple-500" />
                        Execution Summary
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                            <CardContent className="p-6 flex flex-col items-center justify-center text-center space-y-2">
                                <div className="text-3xl font-bold text-primary">{workflowMetrics.executions.total.toLocaleString()}</div>
                                <div className="text-xs font-medium text-muted-foreground">Total Runs</div>
                            </CardContent>
                        </Card>
                        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                            <CardContent className="p-6 flex flex-col items-center justify-center text-center space-y-2">
                                <div className="text-3xl font-bold text-green-500">{(workflowMetrics.executions.success_rate * 100).toFixed(1)}%</div>
                                <div className="text-xs font-medium text-muted-foreground">Success Rate</div>
                            </CardContent>
                        </Card>
                        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                            <CardContent className="p-6 flex flex-col items-center justify-center text-center space-y-2">
                                <div className="text-3xl font-bold text-red-500">{(workflowMetrics.executions.failure_rate * 100).toFixed(1)}%</div>
                                <div className="text-xs font-medium text-muted-foreground">Failure Rate</div>
                            </CardContent>
                        </Card>
                        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                            <CardContent className="p-6 flex flex-col items-center justify-center text-center space-y-2">
                                <div className="text-3xl font-bold text-amber-500">{Math.round(workflowMetrics.latency.avg_duration)}ms</div>
                                <div className="text-xs font-medium text-muted-foreground">Avg Duration</div>
                            </CardContent>
                        </Card>
                        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                            <CardContent className="p-6 flex flex-col items-center justify-center text-center space-y-2">
                                <div className="text-3xl font-bold text-cyan-500">${workflowMetrics.cost.total.toFixed(4)}</div>
                                <div className="text-xs font-medium text-muted-foreground">Total Cost</div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            )}

            {isLoadingMetrics && (
                <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                    <CardContent className="p-12">
                        <div className="flex flex-col items-center justify-center gap-4">
                            <Loader2 className="w-8 h-8 animate-spin text-primary" />
                            <p className="text-sm text-muted-foreground">Loading workflow metrics...</p>
                        </div>
                    </CardContent>
                </Card>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Workflow Traces */}
                <div className="lg:col-span-2 space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold flex items-center gap-2">
                            <GitBranch className="w-5 h-5 text-purple-500" />
                            Workflow Traces
                        </h3>
                        <Button variant="outline" size="sm">View All</Button>
                    </div>
                    <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                        <CardContent className="p-0">
                            {isLoadingTraces ? (
                                <div className="flex items-center justify-center h-32">
                                    <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
                                </div>
                            ) : traces && traces.length > 0 ? (
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Trace ID</TableHead>
                                            <TableHead>Status</TableHead>
                                            <TableHead>Duration</TableHead>
                                            <TableHead>Tokens</TableHead>
                                            <TableHead>Time</TableHead>
                                            <TableHead></TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {traces.map((trace) => (
                                            <TableRow 
                                                key={trace.id || Math.random().toString()} 
                                                className="cursor-pointer hover:bg-muted/50"
                                                onClick={() => setSelectedTraceId(trace.id)}
                                            >
                                                <TableCell className="font-mono text-xs">{(trace.id || "").substring(0, 8)}...</TableCell>
                                                <TableCell>
                                                    <Badge variant={trace.status === 'success' ? 'outline' : 'destructive'} className="capitalize">
                                                        {trace.status === 'success' ? <CheckCircle2 className="w-3 h-3 mr-1" /> : <XCircle className="w-3 h-3 mr-1" />}
                                                        {trace.status}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell>{trace.latency}</TableCell>
                                                <TableCell>{trace.tokens}</TableCell>
                                                <TableCell className="text-muted-foreground text-xs">{new Date(trace.timestamp).toLocaleTimeString()}</TableCell>
                                                <TableCell>
                                                    <Button variant="ghost" size="icon" className="h-8 w-8">
                                                        <Search className="w-4 h-4" />
                                                    </Button>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            ) : (
                                <div className="p-8 text-center text-muted-foreground">
                                    No traces found for this workflow. Execute the workflow to generate traces.
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>

                {/* Cost & Performance Insights - Real OpenLLMetry Data */}
                <div className="space-y-4">
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-green-500" />
                        Cost & Performance
                    </h3>

                    <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium">Cost Breakdown</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            {workflowMetrics ? (
                                <>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Total Cost</span>
                                        <span className="text-lg font-bold text-green-500">${workflowMetrics.cost.total.toFixed(4)}</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Avg Cost/Run</span>
                                        <span className="text-sm font-medium">
                                            ${workflowMetrics.executions.total > 0 
                                                ? (workflowMetrics.cost.total / workflowMetrics.executions.total).toFixed(6) 
                                                : '0.00'}
                                        </span>
                                    </div>
                                    {workflowMetrics.cost.by_model && workflowMetrics.cost.by_model.length > 0 && (
                                        <div className="pt-2 border-t border-border/50">
                                            <p className="text-xs text-muted-foreground mb-2">By Model</p>
                                            {workflowMetrics.cost.by_model.slice(0, 3).map((model) => (
                                                <div key={model.name} className="flex items-center justify-between text-xs py-1">
                                                    <span className="text-muted-foreground truncate max-w-[120px]">{model.name}</span>
                                                    <span className="font-medium">${model.cost.toFixed(4)}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </>
                            ) : (
                                <div className="text-sm text-muted-foreground text-center py-4">
                                    No cost data available yet.
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium">Performance Stats</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            {workflowMetrics ? (
                                <>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Success Rate</span>
                                        <Badge variant={workflowMetrics.executions.success_rate >= 0.9 ? "outline" : "destructive"}>
                                            {(workflowMetrics.executions.success_rate * 100).toFixed(1)}%
                                        </Badge>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Avg Duration</span>
                                        <span className="text-sm font-medium">{Math.round(workflowMetrics.latency.avg_duration)}ms</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">P95 Duration</span>
                                        <span className="text-sm font-medium">{Math.round(workflowMetrics.latency.p95)}ms</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Total Runs</span>
                                        <span className="text-sm font-medium">{workflowMetrics.executions.total.toLocaleString()}</span>
                                    </div>
                                </>
                            ) : (
                                <div className="text-sm text-muted-foreground text-center py-4">
                                    No performance data available yet.
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium">Token Usage</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            {workflowMetrics && workflowMetrics.tokens ? (
                                <>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Total Tokens</span>
                                        <span className="text-sm font-medium">{workflowMetrics.tokens.total.toLocaleString()}</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Prompt Tokens</span>
                                        <span className="text-sm font-medium">{workflowMetrics.tokens.prompt.toLocaleString()}</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Completion Tokens</span>
                                        <span className="text-sm font-medium">{workflowMetrics.tokens.completion.toLocaleString()}</span>
                                    </div>
                                </>
                            ) : (
                                <div className="text-sm text-muted-foreground text-center py-4">
                                    No token data available yet.
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>

            {/* Trace Detail Sheet */}
            <Sheet open={!!selectedTraceId} onOpenChange={(open) => !open && setSelectedTraceId(null)}>
                <SheetContent className="w-full sm:w-[540px] md:w-[700px] lg:w-[900px] sm:max-w-full overflow-y-auto">
                    <SheetHeader className="mb-4">
                        <SheetTitle>Trace Details</SheetTitle>
                        <SheetDescription>
                            Detailed execution flow and metadata for trace {selectedTraceId?.substring(0, 8)}...
                        </SheetDescription>
                    </SheetHeader>
                    {selectedTraceId && <TraceDetailView traceId={selectedTraceId} />}
                </SheetContent>
            </Sheet>
        </div>
    );
}
