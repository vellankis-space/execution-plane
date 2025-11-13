import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useQuery } from "@tanstack/react-query";
import { Activity, CheckCircle, XCircle, AlertTriangle } from "lucide-react";

interface HealthMetrics {
  total_agents: number;
  active_agents: number;
  total_workflows: number;
  active_workflows: number;
  total_executions: number;
  running_executions: number;
  completed_executions: number;
  failed_executions: number;
  success_rate: number;
  avg_execution_time: number;
}

export function SystemHealth() {
  const { data: health, isLoading } = useQuery<HealthMetrics>({
    queryKey: ["system-health"],
    queryFn: async () => {
      const response = await fetch("http://localhost:8000/api/v1/monitoring/health");
      if (!response.ok) throw new Error("Failed to fetch health metrics");
      return response.json();
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  const getHealthStatus = () => {
    if (!health) return "unknown";
    if (health.success_rate >= 95) return "healthy";
    if (health.success_rate >= 80) return "warning";
    return "critical";
  };

  const healthStatus = getHealthStatus();
  const statusColor = {
    healthy: "bg-green-500",
    warning: "bg-yellow-500",
    critical: "bg-red-500",
    unknown: "bg-gray-500",
  }[healthStatus];

  return (
    <div className="space-y-6">
      {/* Overall Health Status */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">System Health</h3>
          <Badge className={statusColor}>
            {healthStatus.toUpperCase()}
          </Badge>
        </div>
        {isLoading ? (
          <div className="text-center py-8 text-muted-foreground">Loading...</div>
        ) : health ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold">{health.success_rate.toFixed(1)}%</p>
              <p className="text-sm text-muted-foreground">Success Rate</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">{health.total_executions}</p>
              <p className="text-sm text-muted-foreground">Total Executions</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">{health.running_executions}</p>
              <p className="text-sm text-muted-foreground">Running</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">{health.avg_execution_time.toFixed(1)}s</p>
              <p className="text-sm text-muted-foreground">Avg Time</p>
            </div>
          </div>
        ) : null}
      </Card>

      {/* Agent Health */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Agent Health</h3>
        {isLoading ? (
          <div className="text-center py-8 text-muted-foreground">Loading...</div>
        ) : health ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-blue-500" />
                <span>Total Agents</span>
              </div>
              <span className="font-semibold">{health.total_agents}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Active Agents</span>
              </div>
              <span className="font-semibold">{health.active_agents}</span>
            </div>
          </div>
        ) : null}
      </Card>

      {/* Workflow Health */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Workflow Health</h3>
        {isLoading ? (
          <div className="text-center py-8 text-muted-foreground">Loading...</div>
        ) : health ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-blue-500" />
                <span>Total Workflows</span>
              </div>
              <span className="font-semibold">{health.total_workflows}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Active Workflows</span>
              </div>
              <span className="font-semibold">{health.active_workflows}</span>
            </div>
          </div>
        ) : null}
      </Card>

      {/* Execution Health */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Execution Health</h3>
        {isLoading ? (
          <div className="text-center py-8 text-muted-foreground">Loading...</div>
        ) : health ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <span>Completed</span>
              </div>
              <span className="font-semibold">{health.completed_executions}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <XCircle className="h-5 w-5 text-red-500" />
                <span>Failed</span>
              </div>
              <span className="font-semibold">{health.failed_executions}</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-yellow-500" />
                <span>Running</span>
              </div>
              <span className="font-semibold">{health.running_executions}</span>
            </div>
          </div>
        ) : null}
      </Card>
    </div>
  );
}

