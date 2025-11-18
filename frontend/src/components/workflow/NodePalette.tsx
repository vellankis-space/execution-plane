import { Card } from "@/components/ui/card";
import { Bot, GitBranch, Repeat, Play, Square, Settings, AlertCircle, MessageSquare, Monitor } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface NodeTypeConfig {
  type: string;
  label: string;
  icon: React.ElementType;
  description: string;
  color: string;
  bgColor: string;
}

const nodeTypeConfigs: NodeTypeConfig[] = [
  {
    type: "startNode",
    label: "Start",
    icon: Play,
    description: "Entry point of the workflow",
    color: "text-green-600",
    bgColor: "bg-green-50 hover:bg-green-100 border-green-300",
  },
  {
    type: "endNode",
    label: "End",
    icon: Square,
    description: "Exit point of the workflow",
    color: "text-red-600",
    bgColor: "bg-red-50 hover:bg-red-100 border-red-300",
  },
  {
    type: "agentNode",
    label: "Agent",
    icon: Bot,
    description: "Execute an AI agent",
    color: "text-blue-600",
    bgColor: "bg-blue-50 hover:bg-blue-100 border-blue-300",
  },
  {
    type: "conditionNode",
    label: "Condition",
    icon: GitBranch,
    description: "Branch based on a condition",
    color: "text-yellow-600",
    bgColor: "bg-yellow-50 hover:bg-yellow-100 border-yellow-300",
  },
  {
    type: "loopNode",
    label: "Loop",
    icon: Repeat,
    description: "Repeat actions multiple times",
    color: "text-purple-600",
    bgColor: "bg-purple-50 hover:bg-purple-100 border-purple-300",
  },
  {
    type: "actionNode",
    label: "Action",
    icon: Settings,
    description: "Execute a custom action",
    color: "text-indigo-600",
    bgColor: "bg-indigo-50 hover:bg-indigo-100 border-indigo-300",
  },
  {
    type: "errorHandlerNode",
    label: "Error Handler",
    icon: AlertCircle,
    description: "Handle errors and exceptions",
    color: "text-orange-600",
    bgColor: "bg-orange-50 hover:bg-orange-100 border-orange-300",
  },
  {
    type: "chatNode",
    label: "Chat / Manual",
    icon: MessageSquare,
    description: "Manual trigger with chat interface",
    color: "text-cyan-600",
    bgColor: "bg-cyan-50 hover:bg-cyan-100 border-cyan-300",
  },
  {
    type: "displayNode",
    label: "Display Output",
    icon: Monitor,
    description: "Display and preview data beautifully",
    color: "text-emerald-600",
    bgColor: "bg-emerald-50 hover:bg-emerald-100 border-emerald-300",
  },
];

export function NodePalette() {
  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData("application/reactflow", nodeType);
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <Card className="w-64 h-full flex flex-col overflow-hidden border-r bg-muted/20 shadow-sm">
      <div className="p-4 border-b flex-shrink-0 bg-background/80">
        <h3 className="font-semibold text-sm tracking-wide uppercase text-muted-foreground">
          Node Library
        </h3>
        <p className="text-xs text-muted-foreground mt-1">
          Drag nodes onto the canvas to build your flow
        </p>
      </div>

      <ScrollArea className="flex-1 overflow-auto">
        <div className="space-y-4 p-3">
          <div>
            <p className="text-[10px] font-semibold tracking-wide text-muted-foreground uppercase mb-1.5">
              Flow
            </p>
            <div className="space-y-2">
              {nodeTypeConfigs
                .filter((n) => n.type === "startNode" || n.type === "endNode" || n.type === "chatNode" || n.type === "displayNode")
                .map((config) => {
                  const Icon = config.icon;
                  return (
                    <div
                      key={config.type}
                      className={`p-3 rounded-lg border cursor-move text-xs shadow-sm hover:shadow-md transition-all ${config.bgColor} dark:bg-gray-900/60 dark:border-gray-700`}
                      draggable
                      onDragStart={(e) => onDragStart(e, config.type)}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-md ${config.color} bg-white dark:bg-gray-800 shadow-sm`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-xs leading-tight">{config.label}</div>
                          <div className="text-[11px] text-muted-foreground mt-1 line-clamp-2">
                            {config.description}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>

          <div>
            <p className="text-[10px] font-semibold tracking-wide text-muted-foreground uppercase mb-1.5">
              Logic & Control
            </p>
            <div className="space-y-2">
              {nodeTypeConfigs
                .filter((n) => n.type === "conditionNode" || n.type === "loopNode" || n.type === "errorHandlerNode")
                .map((config) => {
                  const Icon = config.icon;
                  return (
                    <div
                      key={config.type}
                      className={`p-3 rounded-lg border cursor-move text-xs shadow-sm hover:shadow-md transition-all ${config.bgColor} dark:bg-gray-900/60 dark:border-gray-700`}
                      draggable
                      onDragStart={(e) => onDragStart(e, config.type)}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-md ${config.color} bg-white dark:bg-gray-800 shadow-sm`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-xs leading-tight">{config.label}</div>
                          <div className="text-[11px] text-muted-foreground mt-1 line-clamp-2">
                            {config.description}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>

          <div>
            <p className="text-[10px] font-semibold tracking-wide text-muted-foreground uppercase mb-1.5">
              Actions
            </p>
            <div className="space-y-2">
              {nodeTypeConfigs
                .filter((n) => n.type === "agentNode" || n.type === "actionNode")
                .map((config) => {
                  const Icon = config.icon;
                  return (
                    <div
                      key={config.type}
                      className={`p-3 rounded-lg border cursor-move text-xs shadow-sm hover:shadow-md transition-all ${config.bgColor} dark:bg-gray-900/60 dark:border-gray-700`}
                      draggable
                      onDragStart={(e) => onDragStart(e, config.type)}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-md ${config.color} bg-white dark:bg-gray-800 shadow-sm`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-xs leading-tight">{config.label}</div>
                          <div className="text-[11px] text-muted-foreground mt-1 line-clamp-2">
                            {config.description}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        </div>
      </ScrollArea>

      <div className="p-3 border-t bg-muted/60">
        <p className="text-[11px] text-muted-foreground text-center">
          Tip: Drag from a node handle to create connections
        </p>
      </div>
    </Card>
  );
}
