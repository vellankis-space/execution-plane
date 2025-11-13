import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Bell, CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { format } from "date-fns";

interface AlertRule {
  rule_id: string;
  name: string;
  description?: string;
  workflow_id?: string;
  condition_type: string;
  condition_config: any;
  notification_channels: any[];
  enabled: boolean;
  severity: string;
  created_at: string;
}

interface Alert {
  alert_id: string;
  rule_id: string;
  workflow_id?: string;
  execution_id?: string;
  severity: string;
  message: string;
  status: string;
  created_at: string;
}

export function AlertManagement() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const queryClient = useQueryClient();

  // Fetch alert rules
  const { data: rules } = useQuery<AlertRule[]>({
    queryKey: ["alert-rules"],
    queryFn: async () => {
      const response = await fetch("http://localhost:8000/api/v1/alerting/rules");
      if (!response.ok) throw new Error("Failed to fetch alert rules");
      return response.json();
    },
  });

  // Fetch alerts
  const { data: alerts } = useQuery<Alert[]>({
    queryKey: ["alerts"],
    queryFn: async () => {
      const response = await fetch("http://localhost:8000/api/v1/alerting/alerts?limit=50");
      if (!response.ok) throw new Error("Failed to fetch alerts");
      return response.json();
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  // Fetch workflows for selection
  const { data: workflows = [] } = useQuery({
    queryKey: ["workflows-for-alerts"],
    queryFn: async () => {
      const response = await fetch("http://localhost:8000/api/v1/workflows");
      if (!response.ok) throw new Error("Failed to fetch workflows");
      return response.json();
    },
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-500";
      case "high":
        return "bg-orange-500";
      case "medium":
        return "bg-yellow-500";
      case "low":
        return "bg-blue-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "resolved":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "acknowledged":
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      default:
        return <Bell className="h-4 w-4 text-red-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Alert Rules */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Alert Rules</h3>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create Alert Rule
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
              <DialogHeader>
                <DialogTitle>Create Alert Rule</DialogTitle>
                <DialogDescription>
                  Configure an alert rule to monitor workflow executions
                </DialogDescription>
              </DialogHeader>
              <AlertRuleForm
                onSuccess={() => {
                  setIsCreateDialogOpen(false);
                  queryClient.invalidateQueries({ queryKey: ["alert-rules"] });
                }}
              />
            </DialogContent>
          </Dialog>
        </div>

        <div className="space-y-2">
          {rules && rules.length > 0 ? (
            rules.map((rule) => (
              <div
                key={rule.rule_id}
                className="flex items-center justify-between p-3 border rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <Badge
                    className={getSeverityColor(rule.severity)}
                    variant={rule.enabled ? "default" : "secondary"}
                  >
                    {rule.severity}
                  </Badge>
                  <div>
                    <p className="font-medium">{rule.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {rule.condition_type} • {rule.workflow_id || "All workflows"}
                    </p>
                  </div>
                </div>
                <Switch
                  checked={rule.enabled}
                  onCheckedChange={async (checked) => {
                    try {
                      const response = await fetch(
                        `http://localhost:8000/api/v1/alerting/rules/${rule.rule_id}`,
                        {
                          method: "PUT",
                          headers: { "Content-Type": "application/json" },
                          body: JSON.stringify({ enabled: checked }),
                        }
                      );
                      if (response.ok) {
                        queryClient.invalidateQueries({ queryKey: ["alert-rules"] });
                        toast({
                          title: "Alert rule updated",
                          description: `Alert rule ${checked ? "enabled" : "disabled"}`,
                        });
                      }
                    } catch (error) {
                      toast({
                        title: "Error",
                        description: "Failed to update alert rule",
                        variant: "destructive",
                      });
                    }
                  }}
                />
              </div>
            ))
          ) : (
            <p className="text-center text-muted-foreground py-8">
              No alert rules configured
            </p>
          )}
        </div>
      </Card>

      {/* Active Alerts */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Active Alerts</h3>
        <div className="space-y-2">
          {alerts && alerts.length > 0 ? (
            alerts
              .filter((alert) => alert.status === "active")
              .map((alert) => (
                <div
                  key={alert.alert_id}
                  className="flex items-start justify-between p-4 border rounded-lg"
                >
                  <div className="flex items-start gap-3 flex-1">
                    {getStatusIcon(alert.status)}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={getSeverityColor(alert.severity)}>
                          {alert.severity}
                        </Badge>
                        <p className="font-medium">{alert.message}</p>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {format(new Date(alert.created_at), "PPpp")}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={async () => {
                        try {
                          const response = await fetch(
                            `http://localhost:8000/api/v1/alerting/alerts/${alert.alert_id}/acknowledge`,
                            {
                              method: "POST",
                              headers: { "Content-Type": "application/json" },
                              body: JSON.stringify({ acknowledged_by: "user" }),
                            }
                          );
                          if (response.ok) {
                            queryClient.invalidateQueries({ queryKey: ["alerts"] });
                            toast({
                              title: "Alert acknowledged",
                            });
                          }
                        } catch (error) {
                          toast({
                            title: "Error",
                            description: "Failed to acknowledge alert",
                            variant: "destructive",
                          });
                        }
                      }}
                    >
                      Acknowledge
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={async () => {
                        try {
                          const response = await fetch(
                            `http://localhost:8000/api/v1/alerting/alerts/${alert.alert_id}/resolve`,
                            {
                              method: "POST",
                            }
                          );
                          if (response.ok) {
                            queryClient.invalidateQueries({ queryKey: ["alerts"] });
                            toast({
                              title: "Alert resolved",
                            });
                          }
                        } catch (error) {
                          toast({
                            title: "Error",
                            description: "Failed to resolve alert",
                            variant: "destructive",
                          });
                        }
                      }}
                    >
                      Resolve
                    </Button>
                  </div>
                </div>
              ))
          ) : (
            <p className="text-center text-muted-foreground py-8">No active alerts</p>
          )}
        </div>
      </Card>
    </div>
  );
}

function AlertRuleForm({ onSuccess }: { onSuccess: () => void }) {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    workflow_id: "",
    condition_type: "execution_failure",
    condition_config: {},
    notification_channels: [{ channel_id: "in_app", type: "in_app" }],
    severity: "medium",
    enabled: true,
  });

  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await fetch("http://localhost:8000/api/v1/alerting/rules", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error("Failed to create alert rule");
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Alert rule created",
        description: "Your alert rule has been created successfully.",
      });
      onSuccess();
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to create alert rule",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="name">Rule Name</Label>
        <Input
          id="name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />
      </div>

      <div>
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        />
      </div>

      <div>
        <Label htmlFor="workflow_id">Workflow (Optional)</Label>
        <Select
          value={formData.workflow_id}
          onValueChange={(value) => setFormData({ ...formData, workflow_id: value })}
        >
          <SelectTrigger>
            <SelectValue placeholder="All workflows" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All workflows</SelectItem>
            {workflows.map((wf: any) => (
              <SelectItem key={wf.workflow_id} value={wf.workflow_id}>
                {wf.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label htmlFor="condition_type">Condition Type</Label>
        <Select
          value={formData.condition_type}
          onValueChange={(value) =>
            setFormData({ ...formData, condition_type: value })
          }
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="execution_failure">Execution Failure</SelectItem>
            <SelectItem value="performance_degradation">
              Performance Degradation
            </SelectItem>
            <SelectItem value="resource_threshold">Resource Threshold</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label htmlFor="severity">Severity</Label>
        <Select
          value={formData.severity}
          onValueChange={(value) => setFormData({ ...formData, severity: value })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="low">Low</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex justify-end gap-2 pt-4">
        <Button type="submit" disabled={createMutation.isPending}>
          Create Rule
        </Button>
      </div>
    </form>
  );
}

