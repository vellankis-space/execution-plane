import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useQuery } from "@tanstack/react-query";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from "recharts";
import { format, subDays } from "date-fns";

export function MetricsChart() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>("all");
  const [metricType, setMetricType] = useState<"execution_time" | "resource_usage" | "success_rate">("execution_time");
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

  // Fetch metrics
  const { data: metricsData, isLoading } = useQuery({
    queryKey: ["metrics", selectedWorkflow, metricType],
    queryFn: async () => {
      const url = selectedWorkflow === "all"
        ? "http://localhost:8000/api/v1/enhanced-monitoring/enhanced-metrics/workflow-executions"
        : `http://localhost:8000/api/v1/enhanced-monitoring/enhanced-metrics/workflow-executions?workflow_id=${selectedWorkflow}`;
      
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to fetch metrics");
      const data = await response.json();
      
      if (data.executions && Array.isArray(data.executions)) {
        return data.executions
          .slice(0, 50) // Limit to last 50 executions
          .map((exec: any) => {
            const date = new Date(exec.created_at || exec.started_at);
            return {
              date: format(date, "MM/dd HH:mm"),
              execution_time: exec.execution_time || 0,
              memory_usage: exec.resource_usage?.memory_change_mb || 0,
              cpu_usage: exec.resource_usage?.cpu_change_percent || 0,
              success: exec.status === "completed" ? 1 : 0,
              failure: exec.status === "failed" ? 1 : 0,
            };
          })
          .reverse(); // Show oldest to newest
      }
      return [];
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const getChartData = () => {
    if (!metricsData) return [];
    
    switch (metricType) {
      case "execution_time":
        return metricsData.map((d: any) => ({
          date: d.date,
          value: d.execution_time,
        }));
      case "resource_usage":
        return metricsData.map((d: any) => ({
          date: d.date,
          memory: d.memory_usage,
          cpu: d.cpu_usage,
        }));
      case "success_rate":
        return metricsData.map((d: any) => ({
          date: d.date,
          success: d.success,
          failure: d.failure,
        }));
      default:
        return [];
    }
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold">Performance Metrics</h3>
          <div className="flex gap-4">
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
            <Select value={metricType} onValueChange={(v: any) => setMetricType(v)}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Select metric" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="execution_time">Execution Time</SelectItem>
                <SelectItem value="resource_usage">Resource Usage</SelectItem>
                <SelectItem value="success_rate">Success Rate</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-8 text-muted-foreground">Loading metrics...</div>
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            {metricType === "resource_usage" ? (
              <AreaChart data={getChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="memory"
                  stackId="1"
                  stroke="#8884d8"
                  fill="#8884d8"
                  name="Memory (MB)"
                />
                <Area
                  type="monotone"
                  dataKey="cpu"
                  stackId="2"
                  stroke="#82ca9d"
                  fill="#82ca9d"
                  name="CPU (%)"
                />
              </AreaChart>
            ) : (
              <LineChart data={getChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#8884d8"
                  name={metricType === "execution_time" ? "Time (s)" : "Rate"}
                />
              </LineChart>
            )}
          </ResponsiveContainer>
        )}
      </Card>
    </div>
  );
}

