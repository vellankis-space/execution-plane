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
  AreaChart,
  Area,
  BarChart,
  Bar,
  Legend
} from 'recharts';
import {
  Activity,
  Clock,
  AlertTriangle,
  DollarSign,
  Users,
  Zap,
  Server,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { useAgents } from '@/services/agentService';
import { useAgentMetrics, AgentMetrics } from '@/services/observabilityService';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function MonitoringAgentView() {
  const { data: agents, isLoading: isLoadingAgents } = useAgents();
  const [selectedAgentId, setSelectedAgentId] = useState<string>("");

  // Auto-select first agent when loaded
  useEffect(() => {
    if (agents && agents.length > 0 && !selectedAgentId) {
      setSelectedAgentId(agents[0].agent_id);
    }
  }, [agents, selectedAgentId]);

  const { data: metrics, isLoading: isLoadingMetrics, error } = useAgentMetrics(selectedAgentId);

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
          Please create an agent first to view monitoring metrics.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      {/* Agent Selector */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold tracking-tight">Agent Monitoring</h2>
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

      {isLoadingMetrics ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      ) : error ? (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            Failed to load metrics for this agent. Please try again later.
          </AlertDescription>
        </Alert>
      ) : metrics && metrics.traffic ? (
        <>
          {/* Traffic Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-500" />
              Traffic Metrics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricCard
                title="Total Requests"
                value={metrics.traffic.total_requests.toLocaleString()}
                icon={<Server className="w-4 h-4" />}
                description="Total requests in selected period"
              />
              <MetricCard
                title="Active Users"
                value={metrics.traffic.active_users.toLocaleString()}
                icon={<Users className="w-4 h-4" />}
                description="Unique users"
              />
              <MetricCard
                title="LLM Calls"
                value={metrics.traffic.llm_calls.toLocaleString()}
                icon={<Zap className="w-4 h-4" />}
                description="Total LLM inferences"
              />
              <MetricCard
                title="Tool Calls"
                value={metrics.traffic.tool_calls.toLocaleString()}
                icon={<Zap className="w-4 h-4" />}
                description="External tool executions"
              />
            </div>
          </div>

          {/* Latency Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Clock className="w-5 h-5 text-amber-500" />
              Latency Metrics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <MetricCard title="Avg Latency" value={`${Math.round(metrics.latency.avg)}ms`} icon={<Clock className="w-4 h-4" />} />
              <MetricCard title="P99 Latency" value={`${Math.round(metrics.latency.p99)}ms`} icon={<AlertCircle className="w-4 h-4" />} trendColor="text-red-500" />
              <MetricCard title="TTFT" value={`${Math.round(metrics.latency.ttft)}ms`} icon={<Zap className="w-4 h-4" />} description="Time to First Token" />
            </div>
          </div>

          {/* Error & Cost */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-red-500" />
                Reliability
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <MetricCard
                  title="Error Rate"
                  value={`${(metrics.errors.rate * 100).toFixed(2)}%`}
                  icon={<AlertTriangle className="w-4 h-4" />}
                  trendColor={metrics.errors.rate > 0.05 ? "text-red-500" : "text-green-500"}
                />
                <MetricCard
                  title="Error Count"
                  value={metrics.errors.count.toString()}
                  icon={<AlertCircle className="w-4 h-4" />}
                />
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-green-500" />
                Cost & Tokens
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <MetricCard
                  title="Total Cost"
                  value={`$${metrics.cost.total.toFixed(4)}`}
                  icon={<DollarSign className="w-4 h-4" />}
                />
                <MetricCard
                  title="Total Tokens"
                  value={metrics.cost.tokens.toLocaleString()}
                  icon={<Zap className="w-4 h-4" />}
                />
              </div>
            </div>
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-card/50 backdrop-blur-sm border-border/50">
              <CardHeader>
                <CardTitle className="text-lg font-medium">Requests Over Time</CardTitle>
                <CardDescription>Request volume trend</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={metrics.charts?.requests_over_time || []}>
                      <defs>
                        <linearGradient id="colorRequests" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
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
                        dataKey="requests"
                        stroke="#3b82f6"
                        fillOpacity={1}
                        fill="url(#colorRequests)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-card/50 backdrop-blur-sm border-border/50">
              <CardHeader>
                <CardTitle className="text-lg font-medium">Success vs Failure</CardTitle>
                <CardDescription>Request outcome breakdown</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[300px] w-full flex items-center justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={[
                      { name: 'Success', value: metrics.traffic.total_requests - metrics.errors.count, fill: '#22c55e' },
                      { name: 'Failed', value: metrics.errors.count, fill: '#ef4444' }
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

          {/* Advanced Metrics: Token & Cost Breakdown */}
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
                        prompt: metrics.cost.token_breakdown?.prompt || 0,
                        completion: metrics.cost.token_breakdown?.completion || 0
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
                <CardDescription>Cost distribution across models</CardDescription>
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
      ) : null}
    </div >
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


