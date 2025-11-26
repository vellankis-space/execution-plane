import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Switch } from "@/components/ui/switch";
import { Webhook, Clock, Play, Zap, Calendar, Plus, Copy, Trash2 } from "lucide-react";
import { toast } from "@/hooks/use-toast";

export interface WorkflowTrigger {
  id: string;
  type: "webhook" | "schedule" | "manual" | "event";
  name: string;
  enabled: boolean;
  config: Record<string, any>;
}

interface WorkflowTriggersProps {
  workflowId: string;
  triggers: WorkflowTrigger[];
  onTriggersChange: (triggers: WorkflowTrigger[]) => void;
}

export function WorkflowTriggers({
  workflowId,
  triggers,
  onTriggersChange,
}: WorkflowTriggersProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingTrigger, setEditingTrigger] = useState<WorkflowTrigger | null>(null);
  const [triggerType, setTriggerType] = useState<WorkflowTrigger["type"]>("webhook");
  const [triggerName, setTriggerName] = useState("");
  const [triggerConfig, setTriggerConfig] = useState<Record<string, any>>({});

  const handleSaveTrigger = () => {
    if (!triggerName) {
      toast({
        title: "Validation Error",
        description: "Please provide a trigger name",
        variant: "destructive",
      });
      return;
    }

    const trigger: WorkflowTrigger = {
      id: editingTrigger?.id || `trigger-${Date.now()}`,
      type: triggerType,
      name: triggerName,
      enabled: true,
      config: triggerConfig,
    };

    let newTriggers: WorkflowTrigger[];
    if (editingTrigger) {
      newTriggers = triggers.map((t) => (t.id === editingTrigger.id ? trigger : t));
    } else {
      newTriggers = [...triggers, trigger];
    }

    onTriggersChange(newTriggers);
    setIsDialogOpen(false);
    resetForm();
    toast({
      title: "Success",
      description: "Trigger saved successfully",
    });
  };

  const handleDeleteTrigger = (id: string) => {
    if (!confirm("Are you sure you want to delete this trigger?")) return;

    const newTriggers = triggers.filter((t) => t.id !== id);
    onTriggersChange(newTriggers);
    toast({ title: "Success", description: "Trigger deleted" });
  };

  const handleToggleTrigger = (id: string, enabled: boolean) => {
    const newTriggers = triggers.map((t) =>
      t.id === id ? { ...t, enabled } : t
    );
    onTriggersChange(newTriggers);
  };

  const handleEditTrigger = (trigger: WorkflowTrigger) => {
    setEditingTrigger(trigger);
    setTriggerName(trigger.name);
    setTriggerType(trigger.type);
    setTriggerConfig(trigger.config);
    setIsDialogOpen(true);
  };

  const resetForm = () => {
    setEditingTrigger(null);
    setTriggerName("");
    setTriggerType("webhook");
    setTriggerConfig({});
  };

  const getWebhookUrl = (triggerId: string) => {
    return `${window.location.origin}/api/v1/webhooks/${workflowId}/${triggerId}`;
  };

  const copyWebhookUrl = (triggerId: string) => {
    const url = getWebhookUrl(triggerId);
    navigator.clipboard.writeText(url);
    toast({ title: "Copied", description: "Webhook URL copied to clipboard" });
  };

  const getTriggerIcon = (type: string) => {
    switch (type) {
      case "webhook":
        return <Webhook className="w-5 h-5" />;
      case "schedule":
        return <Clock className="w-5 h-5" />;
      case "manual":
        return <Play className="w-5 h-5" />;
      case "event":
        return <Zap className="w-5 h-5" />;
      default:
        return <Play className="w-5 h-5" />;
    }
  };

  return (
    <div className="space-y-4">
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogTrigger asChild>
          <Button onClick={resetForm} size="sm" className="w-full">
            <Plus className="w-4 h-4 mr-2" />
            Add Trigger
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>
              {editingTrigger ? "Edit" : "Add"} Trigger
            </DialogTitle>
            <DialogDescription>
              Configure when and how this workflow should execute
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 mt-4">
            <div>
              <Label>Trigger Name</Label>
              <Input
                value={triggerName}
                onChange={(e) => setTriggerName(e.target.value)}
                placeholder="e.g., On New Order"
                className="mt-1"
              />
            </div>

            <div>
              <Label>Trigger Type</Label>
              <Select value={triggerType} onValueChange={(v: any) => setTriggerType(v)}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="webhook">Webhook</SelectItem>
                  <SelectItem value="schedule">Schedule</SelectItem>
                  <SelectItem value="manual">Manual</SelectItem>
                  <SelectItem value="event">Event</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Webhook Configuration */}
            {triggerType === "webhook" && (
              <Card className="p-4 bg-muted/50">
                <div className="flex items-start gap-2">
                  <Webhook className="w-5 h-5 text-primary mt-0.5" />
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm">Webhook Configuration</h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      Workflow will trigger when a POST request is sent to the webhook URL
                    </p>
                    <div className="mt-3">
                      <Label className="text-xs">HTTP Method</Label>
                      <Select
                        value={triggerConfig.method || "POST"}
                        onValueChange={(v) =>
                          setTriggerConfig({ ...triggerConfig, method: v })
                        }
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="POST">POST</SelectItem>
                          <SelectItem value="GET">GET</SelectItem>
                          <SelectItem value="PUT">PUT</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="mt-3">
                      <Label className="text-xs">Authentication</Label>
                      <Select
                        value={triggerConfig.auth || "none"}
                        onValueChange={(v) =>
                          setTriggerConfig({ ...triggerConfig, auth: v })
                        }
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="none">None</SelectItem>
                          <SelectItem value="api_key">API Key</SelectItem>
                          <SelectItem value="bearer">Bearer Token</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>
              </Card>
            )}

            {/* Schedule Configuration */}
            {triggerType === "schedule" && (
              <Card className="p-4 bg-muted/50">
                <div className="flex items-start gap-2">
                  <Clock className="w-5 h-5 text-primary mt-0.5" />
                  <div className="flex-1">
                    <h4 className="font-semibold text-sm">Schedule Configuration</h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      Run workflow on a recurring schedule
                    </p>
                    <div className="mt-3">
                      <Label className="text-xs">Cron Expression</Label>
                      <Input
                        value={triggerConfig.cron || ""}
                        onChange={(e) =>
                          setTriggerConfig({ ...triggerConfig, cron: e.target.value })
                        }
                        placeholder="0 0 * * *"
                        className="mt-1 font-mono text-sm"
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        Example: "0 0 * * *" runs daily at midnight
                      </p>
                    </div>
                    <div className="mt-3">
                      <Label className="text-xs">Timezone</Label>
                      <Select
                        value={triggerConfig.timezone || "UTC"}
                        onValueChange={(v) =>
                          setTriggerConfig({ ...triggerConfig, timezone: v })
                        }
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="UTC">UTC</SelectItem>
                          <SelectItem value="America/New_York">Eastern</SelectItem>
                          <SelectItem value="America/Los_Angeles">Pacific</SelectItem>
                          <SelectItem value="Europe/London">London</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </div>
              </Card>
            )}

            {/* Manual Configuration */}
            {triggerType === "manual" && (
              <Card className="p-4 bg-muted/50">
                <div className="flex items-start gap-2">
                  <Play className="w-5 h-5 text-primary mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-sm">Manual Trigger</h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      Workflow runs only when manually triggered from the UI
                    </p>
                  </div>
                </div>
              </Card>
            )}

            <div className="flex justify-end gap-2 pt-4 border-t">
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSaveTrigger}>
                {editingTrigger ? "Update" : "Create"} Trigger
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <div className="space-y-2">
        {triggers.length === 0 ? (
          <Card className="p-8 text-center">
            <Calendar className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h4 className="font-semibold mb-2">No triggers configured</h4>
            <p className="text-sm text-muted-foreground mb-4">
              Add a trigger to define when this workflow should run
            </p>
          </Card>
        ) : (
          triggers.map((trigger) => (
            <Card key={trigger.id} className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <div className="p-2 rounded-md bg-primary/10 text-primary">
                    {getTriggerIcon(trigger.type)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold">{trigger.name}</h4>
                      <Badge variant="outline" className="capitalize">
                        {trigger.type}
                      </Badge>
                      {!trigger.enabled && (
                        <Badge variant="secondary">Disabled</Badge>
                      )}
                    </div>
                    {trigger.type === "webhook" && (
                      <div className="flex items-center gap-2 mt-1">
                        <code className="text-xs bg-muted px-2 py-1 rounded">
                          {getWebhookUrl(trigger.id)}
                        </code>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          onClick={() => copyWebhookUrl(trigger.id)}
                        >
                          <Copy className="w-3 h-3" />
                        </Button>
                      </div>
                    )}
                    {trigger.type === "schedule" && trigger.config.cron && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Schedule: <code className="bg-muted px-1 py-0.5 rounded">{trigger.config.cron}</code>
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Switch
                    checked={trigger.enabled}
                    onCheckedChange={(checked) =>
                      handleToggleTrigger(trigger.id, checked)
                    }
                  />
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => handleEditTrigger(trigger)}
                  >
                    <Play className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => handleDeleteTrigger(trigger.id)}
                  >
                    <Trash2 className="w-4 h-4 text-destructive" />
                  </Button>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div >
  );
}
