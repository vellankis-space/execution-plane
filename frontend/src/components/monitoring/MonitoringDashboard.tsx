import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { RefreshCw, Activity, CheckCircle, XCircle, Clock, TrendingUp } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from "recharts";

interface DashboardStats {
  total_executions: number;
  running_executions: number;
  completed_executions: number;
  failed_executions: number;
  success_rate: number;
  avg_execution_time: number;
  total_agents?: number;
  active_agents?: number;
  total_workflows?: number;
  active_workflows?: number;
}

interface ExecutionStatus {
  execution_id: string;
  workflow_id: string;
  workflow_name: string;
  status: string;
  started_at: string;
  execution_time?: number;
}

export function MonitoringDashboard() {
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000); // 5 seconds

  // Fetch dashboard stats
  const { data: stats, refetch: refetchStats } = useQuery<DashboardStats>({
    queryKey: ["dashboard-stats"],
    queryFn: async () => {
      const response = await fetch("http://localhost:8000/api/v1/monitoring/health");
      if (!response.ok) throw new Error("Failed to fetch stats");
      return response.json();
    },
    refetchInterval: autoRefresh ? refreshInterval : false,
  });

  // Fetch recent executions
  const { data: executions, refetch: refetchExecutions } = useQuery<ExecutionStatus[]>({
    queryKey: ["recent-executions"],
    queryFn: async () => {
      const response = await fetch("http://localhost:8000/api/v1/monitoring/recent-executions?limit=10");
      if (!response.ok) throw new Error("Failed to fetch executions");
      return response.json();
    },
    refetchInterval: autoRefresh ? refreshInterval : false,
  });

  // Fetch workflow metrics for chart
  const { data: metricsData } = useQuery({
    queryKey: ["workflow-metrics"],
    queryFn: async () => {
      const response = await fetch("http://localhost:8000/api/v1/monitoring/metrics/workflow-executions");
      if (!response.ok) throw new Error("Failed to fetch metrics");
      const data = await response.json();
      
      // Transform data for chart
      if (data.executions && Array.isArray(data.executions)) {
        return data.executions.slice(0, 20).map((exec: any) => ({
          time: new Date(exec.created_at).toLocaleTimeString(),
          execution_time: exec.execution_time || 0,
          status: exec.status === "completed" ? 1 : exec.status === "failed" ? -1 : 0,
        }));
      }
      return [];
    },
    refetchInterval: autoRefresh ? refreshInterval : false,
  });

  const handleRefresh = () => {
    refetchStats();
    refetchExecutions();
  };

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Executions</p>
              <p className="text-2xl font-bold mt-2">{stats?.total_executions || 0}</p>
            </div>
            <Activity className="h-8 w-8 text-blue-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Running</p>
              <p className="text-2xl font-bold mt-2">{stats?.running_executions || 0}</p>
            </div>
            <Clock className="h-8 w-8 text-yellow-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Success Rate</p>
              <p className="text-2xl font-bold mt-2">{stats?.success_rate?.toFixed(1) || 0}%</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Avg Execution Time</p>
              <p className="text-2xl font-bold mt-2">
                {stats?.avg_execution_time ? `${stats.avg_execution_time.toFixed(1)}s` : "0s"}
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-purple-500" />
          </div>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Execution Time Trend</h3>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metricsData || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="execution_time"
                stroke="#8884d8"
                name="Execution Time (s)"
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Execution Status</h3>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="mr-2"
              />
              <span className="text-sm text-muted-foreground">Auto-refresh</span>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={metricsData || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="status" fill="#82ca9d" name="Status" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Recent Executions */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Executions</h3>
        <div className="space-y-2">
          {executions && executions.length > 0 ? (
            executions.map((exec) => (
              <div
                key={exec.execution_id}
                className="flex items-center justify-between p-3 border rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <Badge
                    variant={
                      exec.status === "completed"
                        ? "default"
                        : exec.status === "failed"
                        ? "destructive"
                        : "secondary"
                    }
                  >
                    {exec.status}
                  </Badge>
                  <div>
                    <p className="font-medium">{exec.workflow_name}</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(exec.started_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                {exec.execution_time && (
                  <div className="text-sm text-muted-foreground">
                    {exec.execution_time.toFixed(2)}s
                  </div>
                )}
              </div>
            ))
          ) : (
            <p className="text-center text-muted-foreground py-8">
              No recent executions
            </p>
          )}
        </div>
      </Card>
    </div>
  );
}

