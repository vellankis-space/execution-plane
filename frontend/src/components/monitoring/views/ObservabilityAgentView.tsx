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
    Search,
    CheckCircle,
    XCircle,
    Loader2,
    AlertCircle,
    Brain,
    Wrench,
    TrendingUp,
    Activity,
    DollarSign,
    Zap
} from 'lucide-react';
import { Button } from "@/components/ui/button";
import { useAgents } from '@/services/agentService';
import { useTraces, useAgentMetrics } from '@/services/observabilityService';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { TraceDetailView } from './TraceDetailView';

// Import chart components for OpenLLMetry data visualization
import { LLMMetricsGrid } from '../charts/LLMMetricsGrid';
import { TokenUsageChart } from '../charts/TokenUsageChart';
import { ModelCostTable } from '../charts/ModelCostTable';
import { FinishReasonsChart } from '../charts/FinishReasonsChart';
import { ToolAnalyticsTable } from '../charts/ToolAnalyticsTable';
import { PromptResponseInspector } from '../charts/PromptResponseInspector';

export function ObservabilityAgentView() {
    const { data: agents, isLoading: isLoadingAgents } = useAgents();
    const [selectedAgentId, setSelectedAgentId] = useState<string>("");
    const [selectedTraceId, setSelectedTraceId] = useState<string | null>(null);
    const [timeRange, setTimeRange] = useState<string>("24h");

    // Auto-select first agent when loaded
    useEffect(() => {
        if (agents && agents.length > 0 && !selectedAgentId) {
            setSelectedAgentId(agents[0].agent_id);
        }
    }, [agents, selectedAgentId]);

    const { data: traces, isLoading: isLoadingTraces } = useTraces({
        agentId: selectedAgentId,
        limit: 10
    });

    // Fetch comprehensive agent metrics
    const { data: agentMetrics, isLoading: isLoadingMetrics } = useAgentMetrics(selectedAgentId, timeRange);

    if (isLoadingAgents) {
        return (
            <div className="flex items-center justify-center h-64">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    if (!agents || agents.length === 0) {
        return (
            <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>No Agents Found</AlertTitle>
                <AlertDescription>
                    Please create an agent first to view observability data.
                </AlertDescription>
            </Alert>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Agent Selector */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold tracking-tight">Agent Observability</h2>
                <div className="w-[250px]">
                    <Select value={selectedAgentId} onValueChange={setSelectedAgentId}>
                        <SelectTrigger>
                            <SelectValue placeholder="Select an agent" />
                        </SelectTrigger>
                        <SelectContent>
                            {agents.map((agent) => (
                                <SelectItem key={agent.agent_id} value={agent.agent_id}>
                                    {agent.name || "Unnamed Agent"}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* Execution Summary - Real OpenLLMetry Data */}
            {agentMetrics && !isLoadingMetrics && (
                <div className="space-y-4">
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                        <Activity className="w-5 h-5 text-blue-500" />
                        Execution Summary
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                            <CardContent className="p-6 flex flex-col items-center justify-center text-center space-y-2">
                                <div className="text-3xl font-bold text-primary">{agentMetrics.traffic.total_requests.toLocaleString()}</div>
                                <div className="text-xs font-medium text-muted-foreground">Total Executions</div>
                            </CardContent>
                        </Card>
                        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                            <CardContent className="p-6 flex flex-col items-center justify-center text-center space-y-2">
                                <div className="text-3xl font-bold text-green-500">{((1 - agentMetrics.errors.rate) * 100).toFixed(1)}%</div>
                                <div className="text-xs font-medium text-muted-foreground">Success Rate</div>
                            </CardContent>
                        </Card>
                        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                            <CardContent className="p-6 flex flex-col items-center justify-center text-center space-y-2">
                                <div className="text-3xl font-bold text-purple-500">{agentMetrics.traffic.llm_calls.toLocaleString()}</div>
                                <div className="text-xs font-medium text-muted-foreground">LLM Calls</div>
                            </CardContent>
                        </Card>
                        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                            <CardContent className="p-6 flex flex-col items-center justify-center text-center space-y-2">
                                <div className="text-3xl font-bold text-amber-500">{agentMetrics.traffic.tool_calls.toLocaleString()}</div>
                                <div className="text-xs font-medium text-muted-foreground">Tool Calls</div>
                            </CardContent>
                        </Card>
                        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                            <CardContent className="p-6 flex flex-col items-center justify-center text-center space-y-2">
                                <div className="text-3xl font-bold text-cyan-500">{agentMetrics.traffic.active_users.toLocaleString()}</div>
                                <div className="text-xs font-medium text-muted-foreground">Active Users</div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            )}

            {/* LLM Performance Metrics */}
            {agentMetrics && !isLoadingMetrics && (
                <>
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold flex items-center gap-2">
                            <Brain className="w-5 h-5 text-purple-500" />
                            LLM Performance Metrics
                        </h3>
                        <LLMMetricsGrid metrics={agentMetrics} />
                    </div>

                    {/* Token Usage & Cost */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <TokenUsageChart
                            promptTokens={agentMetrics.cost.token_breakdown?.prompt || 0}
                            completionTokens={agentMetrics.cost.token_breakdown?.completion || 0}
                        />
                        <FinishReasonsChart reasons={agentMetrics.finish_reasons || {}} />
                    </div>

                    {/* Model Cost Breakdown */}
                    <ModelCostTable costs={agentMetrics.cost.by_model || []} />

                    {/* Tool Analytics */}
                    {agentMetrics.tool_usage && agentMetrics.tool_usage.length > 0 && (
                        <div className="space-y-4">
                            <h3 className="text-lg font-semibold flex items-center gap-2">
                                <Wrench className="w-5 h-5 text-orange-500" />
                                Tool Usage Analytics
                            </h3>
                            <ToolAnalyticsTable
                                toolUsage={agentMetrics.tool_usage}
                                mcpServersUsed={agentMetrics.mcp_servers_used || []}
                            />
                        </div>
                    )}

                    {/* Prompt & Response Inspector */}
                    <PromptResponseInspector metrics={agentMetrics} />
                </>
            )}

            {isLoadingMetrics && (
                <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                    <CardContent className="p-12">
                        <div className="flex flex-col items-center justify-center gap-4">
                            <Loader2 className="w-8 h-8 animate-spin text-primary" />
                            <p className="text-sm text-muted-foreground">Loading comprehensive metrics...</p>
                        </div>
                    </CardContent>
                </Card>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Tracing Section */}
                <div className="lg:col-span-2 space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold flex items-center gap-2">
                            <Search className="w-5 h-5 text-blue-500" />
                            Recent Traces
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
                                            <TableHead>Latency</TableHead>
                                            <TableHead>Tokens</TableHead>
                                            <TableHead>Cost</TableHead>
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
                                                        {trace.status === 'success' ? <CheckCircle className="w-3 h-3 mr-1" /> : <XCircle className="w-3 h-3 mr-1" />}
                                                        {trace.status}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell>{trace.latency}</TableCell>
                                                <TableCell>{trace.tokens}</TableCell>
                                                <TableCell>{trace.cost}</TableCell>
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
                                    No traces found for this agent. Execute the agent to generate traces.
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>

                {/* Cost & Efficiency Insights - Real OpenLLMetry Data */}
                <div className="space-y-4">
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-green-500" />
                        Cost & Efficiency
                    </h3>

                    <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm font-medium">Cost Breakdown</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            {agentMetrics ? (
                                <>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Total Cost</span>
                                        <span className="text-lg font-bold text-green-500">${agentMetrics.cost.total.toFixed(4)}</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Total Tokens</span>
                                        <span className="text-sm font-medium">{agentMetrics.cost.tokens.toLocaleString()}</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Avg Cost/Request</span>
                                        <span className="text-sm font-medium">
                                            ${agentMetrics.traffic.total_requests > 0 
                                                ? (agentMetrics.cost.total / agentMetrics.traffic.total_requests).toFixed(6) 
                                                : '0.00'}
                                        </span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Avg Tokens/Request</span>
                                        <span className="text-sm font-medium">
                                            {agentMetrics.traffic.total_requests > 0 
                                                ? Math.round(agentMetrics.cost.tokens / agentMetrics.traffic.total_requests).toLocaleString() 
                                                : '0'}
                                        </span>
                                    </div>
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
                            {agentMetrics ? (
                                <>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Error Rate</span>
                                        <Badge variant={agentMetrics.errors.rate > 0.05 ? "destructive" : "outline"}>
                                            {(agentMetrics.errors.rate * 100).toFixed(2)}%
                                        </Badge>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Avg Latency</span>
                                        <span className="text-sm font-medium">{Math.round(agentMetrics.latency.avg)}ms</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">P99 Latency</span>
                                        <span className="text-sm font-medium">{Math.round(agentMetrics.latency.p99)}ms</span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <span className="text-sm text-muted-foreground">Time to First Token</span>
                                        <span className="text-sm font-medium">{Math.round(agentMetrics.latency.ttft)}ms</span>
                                    </div>
                                </>
                            ) : (
                                <div className="text-sm text-muted-foreground text-center py-4">
                                    No performance data available yet.
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
