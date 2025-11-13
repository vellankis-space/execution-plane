import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useQuery } from "@tanstack/react-query";
import { format } from "date-fns";
import { Search, Filter } from "lucide-react";

interface AuditLog {
  log_id: string;
  user_id?: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  resource_name?: string;
  tenant_id?: string;
  ip_address?: string;
  request_method?: string;
  request_path?: string;
  status_code?: number;
  success: number;
  error_message?: string;
  changes: Record<string, any>;
  metadata: Record<string, any>;
  created_at: string;
}

export function AuditLogViewer() {
  const [filters, setFilters] = useState({
    action: "",
    resource_type: "",
    user_id: "",
    search: "",
  });
  const [limit, setLimit] = useState(100);

  const { data: logs, isLoading } = useQuery<AuditLog[]>({
    queryKey: ["audit-logs", filters, limit],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.action) params.append("action", filters.action);
      if (filters.resource_type) params.append("resource_type", filters.resource_type);
      if (filters.user_id) params.append("user_id", filters.user_id);
      if (filters.search) params.append("q", filters.search);
      params.append("limit", limit.toString());

      const url = filters.search
        ? `http://localhost:8000/api/v1/audit/search?${params}`
        : `http://localhost:8000/api/v1/audit/logs?${params}`;

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      if (!response.ok) throw new Error("Failed to fetch audit logs");
      return response.json();
    },
  });

  const { data: summary } = useQuery({
    queryKey: ["audit-summary"],
    queryFn: async () => {
      const response = await fetch("http://localhost:8000/api/v1/audit/summary?days=30", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      if (!response.ok) throw new Error("Failed to fetch audit summary");
      return response.json();
    },
  });

  const getStatusColor = (success: number) => {
    return success === 1 ? "bg-green-500" : "bg-red-500";
  };

  const getActionColor = (action: string) => {
    switch (action) {
      case "create":
        return "bg-blue-500";
      case "update":
        return "bg-yellow-500";
      case "delete":
        return "bg-red-500";
      case "read":
        return "bg-green-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <p className="text-sm text-muted-foreground">Total Actions</p>
            <p className="text-2xl font-bold">{summary.total_actions}</p>
          </Card>
          <Card className="p-4">
            <p className="text-sm text-muted-foreground">Success Rate</p>
            <p className="text-2xl font-bold">{summary.success_rate?.toFixed(1)}%</p>
          </Card>
          <Card className="p-4">
            <p className="text-sm text-muted-foreground">Success</p>
            <p className="text-2xl font-bold text-green-600">{summary.success_count}</p>
          </Card>
          <Card className="p-4">
            <p className="text-sm text-muted-foreground">Failures</p>
            <p className="text-2xl font-bold text-red-600">{summary.failure_count}</p>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="p-6">
        <div className="flex items-center gap-4 mb-4">
          <Filter className="h-5 w-5" />
          <h3 className="text-lg font-semibold">Filters</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <Input
              placeholder="Search..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="w-full"
            />
          </div>
          <Select value={filters.action} onValueChange={(v) => setFilters({ ...filters, action: v })}>
            <SelectTrigger>
              <SelectValue placeholder="Action" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Actions</SelectItem>
              <SelectItem value="create">Create</SelectItem>
              <SelectItem value="update">Update</SelectItem>
              <SelectItem value="delete">Delete</SelectItem>
              <SelectItem value="read">Read</SelectItem>
              <SelectItem value="execute">Execute</SelectItem>
            </SelectContent>
          </Select>
          <Select
            value={filters.resource_type}
            onValueChange={(v) => setFilters({ ...filters, resource_type: v })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Resource Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Resources</SelectItem>
              <SelectItem value="agent">Agent</SelectItem>
              <SelectItem value="workflow">Workflow</SelectItem>
              <SelectItem value="user">User</SelectItem>
              <SelectItem value="schedule">Schedule</SelectItem>
            </SelectContent>
          </Select>
          <Input
            placeholder="User ID"
            value={filters.user_id}
            onChange={(e) => setFilters({ ...filters, user_id: e.target.value })}
          />
        </div>
      </Card>

      {/* Audit Logs Table */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Audit Logs</h3>
        {isLoading ? (
          <div className="text-center py-8 text-muted-foreground">Loading...</div>
        ) : logs && logs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Time</th>
                  <th className="text-left p-2">User</th>
                  <th className="text-left p-2">Action</th>
                  <th className="text-left p-2">Resource</th>
                  <th className="text-left p-2">Status</th>
                  <th className="text-left p-2">IP Address</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.log_id} className="border-b hover:bg-muted/50">
                    <td className="p-2 text-sm">
                      {format(new Date(log.created_at), "PPpp")}
                    </td>
                    <td className="p-2 text-sm">{log.user_id || "System"}</td>
                    <td className="p-2">
                      <Badge className={getActionColor(log.action)}>{log.action}</Badge>
                    </td>
                    <td className="p-2 text-sm">
                      {log.resource_type}
                      {log.resource_name && `: ${log.resource_name}`}
                    </td>
                    <td className="p-2">
                      <Badge className={getStatusColor(log.success)}>
                        {log.success === 1 ? "Success" : "Failed"}
                      </Badge>
                      {log.status_code && (
                        <span className="ml-2 text-xs text-muted-foreground">
                          {log.status_code}
                        </span>
                      )}
                    </td>
                    <td className="p-2 text-sm text-muted-foreground">{log.ip_address || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">No audit logs found</div>
        )}
      </Card>
    </div>
  );
}

