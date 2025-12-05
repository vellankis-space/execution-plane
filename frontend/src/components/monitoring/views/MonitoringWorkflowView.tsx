import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
    Legend,
    ComposedChart,
    Area,
    AreaChart
} from 'recharts';
import {
    GitBranch,
    Clock,
    AlertTriangle,
    DollarSign,
    PlayCircle,
    CheckCircle2,
    XCircle,
    Activity,
    Loader2,
    AlertCircle
} from 'lucide-react';
import { useWorkflows } from '@/services/workflowService';
import { useWorkflowMetrics } from '@/services/observabilityService';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function MonitoringWorkflowView() {
    const { data: workflows, isLoading: isLoadingWorkflows } = useWorkflows();
    const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>("");

    // Auto-select first workflow when loaded
    useEffect(() => {
        if (workflows && workflows.length > 0 && !selectedWorkflowId) {
            setSelectedWorkflowId(workflows[0].workflow_id);
        }
    }, [workflows, selectedWorkflowId]);

    const { data: metrics, isLoading: isLoadingMetrics, error } = useWorkflowMetrics(selectedWorkflowId);

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
                    Please create a workflow first to view monitoring metrics.
                </AlertDescription>
            </Alert>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Workflow Selector */}
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold tracking-tight">Workflow Monitoring</h2>
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

            {isLoadingMetrics ? (
                <div className="flex items-center justify-center h-64">
                    <Loader2 className="w-8 h-8 animate-spin text-primary" />
                </div>
            ) : error ? (
                <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Error Loading Metrics</AlertTitle>
                    <AlertDescription>
                        {(error as any)?.response?.status === 401 
                            ? "Authentication required. Please log in again."
                            : `Failed to load metrics: ${(error as any)?.message || 'Unknown error'}`}
                    </AlertDescription>
                </Alert>
            ) : metrics && metrics.executions ? (
                <>
                    {/* Traffic & Execution Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold flex items-center gap-2">
                            <GitBranch className="w-5 h-5 text-purple-500" />
                            Traffic & Execution Metrics
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <MetricCard
                                title="Total Runs"
                                value={metrics.executions.total.toLocaleString()}
                                icon={<PlayCircle className="w-4 h-4" />}
                                description="Total executions in selected period"
                            />
                            <MetricCard
                                title="Success Rate"
                                value={`${(metrics.executions.success_rate * 100).toFixed(1)}%`}
                                icon={<CheckCircle2 className="w-4 h-4" />}
                                trendColor={metrics.executions.success_rate > 0.9 ? "text-green-500" : "text-red-500"}
                            />
                            <MetricCard
                                title="Failure Rate"
                                value={`${(metrics.executions.failure_rate * 100).toFixed(1)}%`}
                                icon={<XCircle className="w-4 h-4" />}
                                trendColor={metrics.executions.failure_rate < 0.1 ? "text-green-500" : "text-red-500"}
                            />
                            <MetricCard
                                title="Avg Duration"
                                value={`${Math.round(metrics.latency.avg_duration)}ms`}
                                icon={<Activity className="w-4 h-4" />}
                            />
                        </div>
                    </div>

                    {/* Latency Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold flex items-center gap-2">
                            <Clock className="w-5 h-5 text-amber-500" />
                            Latency Metrics
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <MetricCard title="Avg Duration" value={`${Math.round(metrics.latency.avg_duration)}ms`} icon={<Clock className="w-4 h-4" />} />
                            <MetricCard title="P95 Latency" value={`${Math.round(metrics.latency.p95)}ms`} icon={<AlertTriangle className="w-4 h-4" />} trendColor="text-yellow-500" />
                        </div>
                    </div>

                    {/* Cost & Token Metrics */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold flex items-center gap-2">
                            <DollarSign className="w-5 h-5 text-green-500" />
                            Cost & Token Metrics
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <MetricCard
                                title="Total Cost"
                                value={`$${metrics.cost.total.toFixed(4)}`}
                                icon={<DollarSign className="w-4 h-4" />}
                            />
                            <MetricCard
                                title="Total Tokens"
                                value={metrics.tokens?.total?.toLocaleString() || '0'}
                                icon={<Activity className="w-4 h-4" />}
                                description="Total tokens used"
                            />
                            <MetricCard
                                title="Prompt Tokens"
                                value={metrics.tokens?.prompt?.toLocaleString() || '0'}
                                icon={<Activity className="w-4 h-4" />}
                                description="Input tokens"
                            />
                            <MetricCard
                                title="Completion Tokens"
                                value={metrics.tokens?.completion?.toLocaleString() || '0'}
                                icon={<Activity className="w-4 h-4" />}
                                description="Output tokens"
                            />
                        </div>
                    </div>
                    {/* Charts Section */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                            <CardHeader>
                                <CardTitle className="text-lg font-medium">Executions Over Time</CardTitle>
                                <CardDescription>Workflow execution trend</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="h-[300px] w-full">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <AreaChart data={metrics.charts?.executions_over_time || []}>
                                            <defs>
                                                <linearGradient id="colorExecutions" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                                                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                                                </linearGradient>
                                            </defs>
                                            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                                            <XAxis
                                                dataKey="time"
                                                tickFormatter={(value) => new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                className="text-xs text-muted-foreground"
                                            />
                                            <YAxis className="text-xs text-muted-foreground" />
                                            <Tooltip
                                                contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))' }}
                                                labelFormatter={(value) => new Date(value).toLocaleString()}
                                            />
                                            <Area
                                                type="monotone"
                                                dataKey="executions"
                                                stroke="#8b5cf6"
                                                fillOpacity={1}
                                                fill="url(#colorExecutions)"
                                            />
                                        </AreaChart>
                                    </ResponsiveContainer>
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                            <CardHeader>
                                <CardTitle className="text-lg font-medium">Status Breakdown</CardTitle>
                                <CardDescription>Execution outcomes</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="h-[300px] w-full flex items-center justify-center">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={[
                                            { name: 'Success', value: Math.round(metrics.executions.total * metrics.executions.success_rate), fill: '#22c55e' },
                                            { name: 'Failed', value: Math.round(metrics.executions.total * metrics.executions.failure_rate), fill: '#ef4444' }
                                        ]}>
                                            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                                            <XAxis dataKey="name" className="text-xs text-muted-foreground" />
                                            <YAxis className="text-xs text-muted-foreground" />
                                            <Tooltip
                                                contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))' }}
                                                cursor={{ fill: 'transparent' }}
                                            />
                                            <Bar dataKey="value" radius={[4, 4, 0, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Token & Cost Breakdown Charts */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                            <CardHeader>
                                <CardTitle className="text-lg font-medium">Token Usage Breakdown</CardTitle>
                                <CardDescription>Prompt vs Completion tokens</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="h-[300px] w-full flex items-center justify-center">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={[
                                            {
                                                name: 'Tokens',
                                                prompt: metrics.tokens?.prompt || 0,
                                                completion: metrics.tokens?.completion || 0
                                            }
                                        ]}>
                                            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                                            <XAxis dataKey="name" className="text-xs text-muted-foreground" />
                                            <YAxis className="text-xs text-muted-foreground" />
                                            <Tooltip
                                                contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))' }}
                                                cursor={{ fill: 'transparent' }}
                                            />
                                            <Legend />
                                            <Bar dataKey="prompt" name="Prompt" stackId="a" fill="#3b82f6" radius={[0, 0, 4, 4]} />
                                            <Bar dataKey="completion" name="Completion" stackId="a" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </CardContent>
                        </Card>

                        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                            <CardHeader>
                                <CardTitle className="text-lg font-medium">Cost by Model</CardTitle>
                                <CardDescription>Cost distribution across LLM models</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="h-[300px] w-full flex items-center justify-center">
                                    {metrics.cost.by_model && metrics.cost.by_model.length > 0 ? (
                                        <ResponsiveContainer width="100%" height="100%">
                                            <BarChart data={metrics.cost.by_model} layout="vertical">
                                                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                                                <XAxis type="number" className="text-xs text-muted-foreground" unit="$" />
                                                <YAxis dataKey="name" type="category" width={100} className="text-xs text-muted-foreground" />
                                                <Tooltip
                                                    contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))' }}
                                                    cursor={{ fill: 'transparent' }}
                                                    formatter={(value: number) => [`$${value.toFixed(4)}`, 'Cost']}
                                                />
                                                <Bar dataKey="cost" fill="#10b981" radius={[0, 4, 4, 0]} />
                                            </BarChart>
                                        </ResponsiveContainer>
                                    ) : (
                                        <div className="text-muted-foreground text-sm">No model cost data available</div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </>
            ) : (
                <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>No Metrics Available</AlertTitle>
                    <AlertDescription>
                        No monitoring data found for this workflow. Run the workflow to generate metrics.
                    </AlertDescription>
                </Alert>
            )}
        </div>
    );
}

function MetricCard({ title, value, trend, icon, description, trendColor = "text-green-500" }: {
    title: string;
    value: string;
    trend?: string;
    icon?: React.ReactNode;
    description?: string;
    trendColor?: string;
}) {
    return (
        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
            <CardContent className="p-6">
                <div className="flex items-center justify-between space-y-0 pb-2">
                    <p className="text-sm font-medium text-muted-foreground">{title}</p>
                    {icon && <div className="text-muted-foreground">{icon}</div>}
                </div>
                <div className="flex items-end justify-between">
                    <div>
                        <div className="text-2xl font-bold">{value}</div>
                        {description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}
                    </div>
                    {trend && (
                        <div className={`text-xs font-medium ${trendColor} flex items-center`}>
                            {trend}
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
