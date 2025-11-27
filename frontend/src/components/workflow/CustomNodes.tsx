import { Handle, Position, NodeProps, NodeResizer } from "reactflow";
import {
  Bot,
  GitBranch,
  Repeat,
  Play,
  Square,
  AlertCircle,
  MessageSquare,
  Monitor,
  Zap,
  ArrowRight,
  MoreHorizontal,
  Clock,
  Database,
  Code2,
  CheckCircle2,
  XCircle,
  Loader2,
  Copy,
  Trash2,
  Eye,
  Activity,
  TrendingUp,
  FileText,
  GripVertical,
  Plus,
  Layers,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
  ContextMenuSeparator,
} from "@/components/ui/context-menu";

// --- Enhanced Base Node Component ---

interface BaseNodeProps {
  children?: React.ReactNode;
  selected?: boolean;
  title: string;
  icon: React.ElementType;
  id: string;
  status?: "idle" | "queued" | "running" | "completed" | "failed" | "paused";
  category?: "trigger" | "agent" | "logic" | "tool" | "human";
  executionTime?: number;
  lastRun?: string;
  errorCount?: number;
  onRun?: () => void;
  onDelete?: () => void;
  onDuplicate?: () => void;
  onViewLogs?: () => void;
  notes?: string;
}

// Enhanced gradient and styling system for modern design
const categoryStyles = {
  trigger: {
    border: "border-emerald-500/50",
    gradient: "from-emerald-400 via-teal-500 to-green-500",
    glassEffect: "bg-gradient-to-br from-emerald-500/10 to-teal-500/5 backdrop-blur-sm",
    header: "bg-gradient-to-r from-emerald-500/20 to-teal-500/10 border-b border-emerald-500/30",
    iconColor: "text-emerald-600 dark:text-emerald-400",
    iconBg: "bg-gradient-to-br from-emerald-500/20 to-emerald-600/10",
    handle: "!bg-gradient-to-r !from-emerald-400 !to-emerald-600",
    glow: "shadow-lg shadow-emerald-500/30",
    hoverGlow: "hover:shadow-xl hover:shadow-emerald-500/50",
  },
  agent: {
    border: "border-blue-500/50",
    gradient: "from-blue-500 via-purple-500 to-indigo-600",
    glassEffect: "bg-gradient-to-br from-blue-500/10 to-purple-500/5 backdrop-blur-sm",
    header: "bg-gradient-to-r from-blue-500/20 to-purple-500/10 border-b border-blue-500/30",
    iconColor: "text-blue-600 dark:text-blue-400",
    iconBg: "bg-gradient-to-br from-blue-500/20 to-purple-500/10",
    handle: "!bg-gradient-to-r !from-blue-400 !to-purple-600",
    glow: "shadow-lg shadow-blue-500/30",
    hoverGlow: "hover:shadow-xl hover:shadow-blue-500/50",
  },
  logic: {
    border: "border-purple-500/50",
    gradient: "from-purple-500 via-pink-500 to-rose-500",
    glassEffect: "bg-gradient-to-br from-purple-500/10 to-pink-500/5 backdrop-blur-sm",
    header: "bg-gradient-to-r from-purple-500/20 to-pink-500/10 border-b border-purple-500/30",
    iconColor: "text-purple-600 dark:text-purple-400",
    iconBg: "bg-gradient-to-br from-purple-500/20 to-pink-500/10",
    handle: "!bg-gradient-to-r !from-purple-400 !to-pink-600",
    glow: "shadow-lg shadow-purple-500/30",
    hoverGlow: "hover:shadow-xl hover:shadow-purple-500/50",
  },
  tool: {
    border: "border-orange-500/50",
    gradient: "from-orange-400 via-amber-500 to-yellow-600",
    glassEffect: "bg-gradient-to-br from-orange-500/10 to-amber-500/5 backdrop-blur-sm",
    header: "bg-gradient-to-r from-orange-500/20 to-amber-500/10 border-b border-orange-500/30",
    iconColor: "text-orange-600 dark:text-orange-400",
    iconBg: "bg-gradient-to-br from-orange-500/20 to-amber-500/10",
    handle: "!bg-gradient-to-r !from-orange-400 !to-amber-600",
    glow: "shadow-lg shadow-orange-500/30",
    hoverGlow: "hover:shadow-xl hover:shadow-orange-500/50",
  },
  human: {
    border: "border-cyan-500/50",
    gradient: "from-cyan-400 via-blue-500 to-indigo-500",
    glassEffect: "bg-gradient-to-br from-cyan-500/10 to-blue-500/5 backdrop-blur-sm",
    header: "bg-gradient-to-r from-cyan-500/20 to-blue-500/10 border-b border-cyan-500/30",
    iconColor: "text-cyan-600 dark:text-cyan-400",
    iconBg: "bg-gradient-to-br from-cyan-500/20 to-blue-500/10",
    handle: "!bg-gradient-to-r !from-cyan-400 !to-blue-600",
    glow: "shadow-lg shadow-cyan-500/30",
    hoverGlow: "hover:shadow-xl hover:shadow-cyan-500/50",
  },
};

const statusConfig = {
  idle: { icon: null, color: "text-muted-foreground", label: "Idle" },
  queued: { icon: Clock, color: "text-yellow-500", label: "Queued" },
  running: { icon: Loader2, color: "text-blue-500", label: "Running", animate: true },
  completed: { icon: CheckCircle2, color: "text-green-500", label: "Completed" },
  failed: { icon: XCircle, color: "text-red-500", label: "Failed" },
  paused: { icon: Clock, color: "text-orange-500", label: "Paused" },
};

const BaseNode = ({
  children,
  selected,
  title,
  icon: Icon,
  id,
  status = "idle",
  category = "tool",
  executionTime,
  lastRun,
  errorCount = 0,
  onRun,
  onDelete,
  onDuplicate,
  onViewLogs,
  notes,
}: BaseNodeProps) => {
  const styles = categoryStyles[category];
  const statusInfo = statusConfig[status];
  const StatusIcon = statusInfo.icon;

  return (
    <ContextMenu>
      <ContextMenuTrigger>
        <TooltipProvider>
          <div
            className={`
              relative w-[300px] rounded-2xl border-2 transition-all duration-300 group
              ${styles.glassEffect}
              ${selected
                ? `ring-2 ring-offset-2 ring-offset-background ${styles.border} ${styles.glow} scale-105`
                : `${styles.border} hover:scale-[1.02] ${styles.hoverGlow}`
              }
              hover:-translate-y-0.5
            `}
          >
            {/* Gradient overlay for depth */}
            <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${styles.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300 pointer-events-none`} />

            {/* Drag Handle with enhanced styling */}
            <div className="absolute -left-3 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-all duration-200 cursor-grab active:cursor-grabbing z-10">
              <div className={`${styles.iconBg} border-2 ${styles.border} rounded-lg p-1 shadow-md`}>
                <GripVertical className={`w-4 h-4 ${styles.iconColor}`} />
              </div>
            </div>

            {/* Animated status ring for running state */}
            {status === "running" && (
              <div className={`absolute -inset-1 rounded-2xl bg-gradient-to-r ${styles.gradient} opacity-20 animate-pulse`} />
            )}

            {/* Header with gradient */}
            <div className={`flex items-center justify-between px-4 py-2.5 ${styles.header} rounded-t-2xl`}>
              <div className="flex items-center gap-2.5">
                <div className={`p-1.5 rounded-lg ${styles.iconBg} border ${styles.border} shadow-sm`}>
                  <Icon className={`w-4 h-4 ${styles.iconColor}`} />
                </div>
                <span className="font-bold text-xs tracking-wider uppercase">{title}</span>
              </div>
              <div className="flex items-center gap-2">
                {StatusIcon && (
                  <Tooltip>
                    <TooltipTrigger>
                      <div className={`${statusInfo.color} relative`}>
                        <StatusIcon className={`w-4 h-4 ${statusInfo.animate ? "animate-spin" : ""}`} />
                        {status === "running" && (
                          <span className="absolute inset-0 rounded-full animate-ping opacity-50">
                            <StatusIcon className="w-4 h-4" />
                          </span>
                        )}
                      </div>
                    </TooltipTrigger>
                    <TooltipContent side="top" className="text-xs font-medium">
                      {statusInfo.label}
                    </TooltipContent>
                  </Tooltip>
                )}
                {errorCount > 0 && (
                  <Tooltip>
                    <TooltipTrigger>
                      <Badge variant="destructive" className="h-5 px-1.5 text-[10px] font-bold shadow-lg">
                        {errorCount}
                      </Badge>
                    </TooltipTrigger>
                    <TooltipContent side="top" className="text-xs">
                      {errorCount} error{errorCount > 1 ? "s" : ""}
                    </TooltipContent>
                  </Tooltip>
                )}
                <span className="text-[10px] text-muted-foreground font-mono opacity-60 bg-muted/50 px-1.5 py-0.5 rounded">
                  #{id.split("-")[1]?.slice(0, 4) || id.slice(0, 4)}
                </span>
                {notes && (
                  <Tooltip>
                    <TooltipTrigger>
                      <div className="bg-yellow-500/20 text-yellow-600 dark:text-yellow-400 p-1 rounded-md border border-yellow-500/30">
                        <MessageSquare className="w-3.5 h-3.5" />
                      </div>
                    </TooltipTrigger>
                    <TooltipContent side="top" className="max-w-[200px] text-xs">
                      <div className="font-semibold mb-1">Note:</div>
                      {notes}
                    </TooltipContent>
                  </Tooltip>
                )}
              </div>
            </div>

            {/* Body with enhanced padding */}
            <div className="p-4">{children}</div>

            {/* Footer with enhanced metrics display */}
            <div className={`px-4 py-2 border-t ${styles.border} ${styles.glassEffect} flex items-center justify-between rounded-b-2xl`}>
              <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                {executionTime !== undefined && (
                  <Tooltip>
                    <TooltipTrigger className="flex items-center gap-1.5 bg-muted/50 px-2 py-1 rounded-md">
                      <Activity className="w-3.5 h-3.5" />
                      <span className="font-mono font-medium">{executionTime}ms</span>
                    </TooltipTrigger>
                    <TooltipContent side="bottom" className="text-xs">
                      Last execution time
                    </TooltipContent>
                  </Tooltip>
                )}
                {lastRun && (
                  <Tooltip>
                    <TooltipTrigger className="flex items-center gap-1.5 bg-muted/50 px-2 py-1 rounded-md">
                      <Clock className="w-3.5 h-3.5" />
                      <span className="font-medium">{new Date(lastRun).toLocaleTimeString()}</span>
                    </TooltipTrigger>
                    <TooltipContent side="bottom" className="text-xs">
                      Last run: {new Date(lastRun).toLocaleString()}
                    </TooltipContent>
                  </Tooltip>
                )}
              </div>
              <div className="flex gap-1">
                {onRun && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        className={`h-6 w-6 rounded-md ${styles.iconColor} hover:${styles.iconBg}`}
                        onClick={(e) => {
                          e.stopPropagation();
                          onRun();
                        }}
                      >
                        <Play className="w-3.5 h-3.5 fill-current" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent side="bottom" className="text-xs">
                      Test run this node
                    </TooltipContent>
                  </Tooltip>
                )}
              </div>
            </div>

            {/* Enhanced gradient handles */}
            <Handle
              type="target"
              position={Position.Left}
              className={`w-3.5 h-3.5 border-2 border-background shadow-lg ${styles.handle} transition-transform hover:scale-125`}
            />
            <Handle
              type="source"
              position={Position.Right}
              className={`w-3.5 h-3.5 border-2 border-background shadow-lg ${styles.handle} transition-transform hover:scale-125`}
            />
          </div>
        </TooltipProvider>
      </ContextMenuTrigger>

      <ContextMenuContent className="w-48">
        {onRun && (
          <ContextMenuItem onClick={onRun}>
            <Play className="w-4 h-4 mr-2" />
            Test Run
          </ContextMenuItem>
        )}
        {onViewLogs && (
          <ContextMenuItem onClick={onViewLogs}>
            <FileText className="w-4 h-4 mr-2" />
            View Logs
          </ContextMenuItem>
        )}
        {onDuplicate && (
          <ContextMenuItem onClick={onDuplicate}>
            <Copy className="w-4 h-4 mr-2" />
            Duplicate
          </ContextMenuItem>
        )}
        <ContextMenuSeparator />
        {onDelete && (
          <ContextMenuItem onClick={onDelete} className="text-destructive focus:text-destructive">
            <Trash2 className="w-4 h-4 mr-2" />
            Delete
          </ContextMenuItem>
        )}
      </ContextMenuContent>
    </ContextMenu>
  );
};

// --- Specific Node Implementations ---

export const StartNode = ({ data, selected, id }: NodeProps) => {
  const triggerType = data.triggerType || "manual";
  const triggerConfig = data.triggerConfig || {};

  return (
    <ContextMenu>
      <ContextMenuTrigger>
        <div
          className={`
            relative w-[240px] rounded-3xl border-2 shadow-lg transition-all duration-300 group overflow-hidden
            bg-gradient-to-br from-emerald-500/10 via-teal-500/5 to-transparent backdrop-blur-sm
            ${selected
              ? "border-emerald-500 ring-4 ring-emerald-500/30 shadow-emerald-500/40 scale-105"
              : "border-emerald-500/60 hover:border-emerald-500 hover:shadow-emerald-500/30 hover:scale-[1.02]"
            }
            hover:-translate-y-0.5
          `}
        >
          {/* Animated gradient background */}
          <div className="absolute inset-0 bg-gradient-to-r from-emerald-400/0 via-emerald-500/10 to-emerald-400/0 animate-pulse opacity-50" />

          {/* Pulsing ring for running state */}
          {data.status === "running" && (
            <div className="absolute -inset-1 rounded-3xl bg-gradient-to-r from-emerald-400 to-teal-500 opacity-20 animate-pulse" />
          )}

          <div className="relative flex items-center gap-4 px-4 py-3">
            {/* Large icon with pulsing glow */}
            <div className="relative">
              <div className="absolute inset-0 bg-emerald-500/30 rounded-full blur-xl group-hover:blur-2xl transition-all duration-300" />
              <div className="relative w-14 h-14 rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 flex items-center justify-center border-2 border-emerald-300/50 shadow-lg group-hover:scale-110 transition-transform duration-300">
                <Play className="w-7 h-7 text-white ml-0.5 drop-shadow-lg fill-white" />
              </div>
              {/* Animated pulse ring */}
              <div className="absolute inset-0 rounded-full border-2 border-emerald-400 animate-ping opacity-20" />
            </div>

            <div className="flex-1 min-w-0">
              <div className="font-bold text-base bg-gradient-to-r from-emerald-600 to-teal-600 dark:from-emerald-400 dark:to-teal-400 bg-clip-text text-transparent">
                Start Trigger
              </div>
              <div className="flex items-center gap-2 mt-1">
                <Badge className="text-[10px] h-5 px-2 bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border-emerald-500/30 font-semibold uppercase">
                  {triggerType}
                </Badge>
                {triggerType === "webhook" && triggerConfig.method && (
                  <Badge variant="outline" className="text-[9px] h-4 px-1.5 border-emerald-500/30">
                    {triggerConfig.method}
                  </Badge>
                )}
                {triggerType === "schedule" && triggerConfig.cron && (
                  <code className="text-[9px] bg-emerald-950/50 text-emerald-300 px-1.5 py-0.5 rounded border border-emerald-500/20 font-mono">
                    {triggerConfig.cron}
                  </code>
                )}
              </div>
            </div>
          </div>

          {/* Enhanced handle with glow */}
          <Handle
            type="source"
            position={Position.Right}
            className="w-4 h-4 !bg-gradient-to-r !from-emerald-400 !to-emerald-600 border-2 border-background shadow-lg shadow-emerald-500/50 transition-transform hover:scale-125"
          />

          {data.notes && (
            <Tooltip>
              <TooltipTrigger>
                <div className="absolute top-2 right-2 bg-yellow-500/20 text-yellow-600 dark:text-yellow-400 p-1.5 rounded-lg border border-yellow-500/30 backdrop-blur-sm z-10">
                  <MessageSquare className="w-3.5 h-3.5" />
                </div>
              </TooltipTrigger>
              <TooltipContent side="top" className="max-w-[200px] text-xs">
                <div className="font-semibold mb-1">Note:</div>
                {data.notes}
              </TooltipContent>
            </Tooltip>
          )}
        </div>
      </ContextMenuTrigger>
      <ContextMenuContent>
        <ContextMenuItem>
          <Play className="w-4 h-4 mr-2" />
          Trigger Workflow
        </ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  );
};

export const EndNode = ({ data, selected, id }: NodeProps) => {
  return (
    <div
      className={`
        relative w-[220px] rounded-3xl border-2 shadow-lg transition-all duration-300 group overflow-hidden
        bg-gradient-to-br from-red-500/10 via-rose-500/5 to-transparent backdrop-blur-sm
        ${selected
          ? "border-red-500 ring-4 ring-red-500/30 shadow-red-500/40 scale-105"
          : "border-red-500/60 hover:border-red-500 hover:shadow-red-500/30 hover:scale-[1.02]"
        }
        hover:-translate-y-0.5
      `}
    >
      {/* Animated gradient background */}
      <div className="absolute inset-0 bg-gradient-to-r from-red-400/0 via-rose-500/10 to-red-400/0 animate-pulse opacity-50" />

      {/* Success completion glow */}
      {data.status === "completed" && (
        <div className="absolute inset-0 bg-gradient-to-r from-green-400/20 to-emerald-500/20 animate-pulse" />
      )}

      <Handle type="target" position={Position.Left} className="w-4 h-4 !bg-gradient-to-r !from-red-400 !to-rose-600 border-2 border-background shadow-lg shadow-red-500/50 transition-transform hover:scale-125" />

      <div className="relative flex items-center gap-4 px-4 py-3">
        {/* Large icon with glow */}
        <div className="relative">
          <div className="absolute inset-0 bg-red-500/30 rounded-full blur-xl group-hover:blur-2xl transition-all duration-300" />
          <div className="relative w-14 h-14 rounded-full bg-gradient-to-br from-red-400 to-rose-600 flex items-center justify-center border-2 border-red-300/50 shadow-lg group-hover:scale-110 transition-transform duration-300">
            <Square className="w-6 h-6 text-white fill-white drop-shadow-lg" />
          </div>
        </div>

        <div>
          <div className="font-bold text-base bg-gradient-to-r from-red-600 to-rose-600 dark:from-red-400 dark:to-rose-400 bg-clip-text text-transparent">
            End
          </div>
          <div className="text-xs text-muted-foreground font-medium mt-0.5">Workflow Complete</div>
        </div>
      </div>

      {data.notes && (
        <Tooltip>
          <TooltipTrigger>
            <div className="absolute top-2 right-2 bg-yellow-500/20 text-yellow-600 dark:text-yellow-400 p-1.5 rounded-lg border border-yellow-500/30 backdrop-blur-sm z-10">
              <MessageSquare className="w-3.5 h-3.5" />
            </div>
          </TooltipTrigger>
          <TooltipContent side="top" className="max-w-[200px] text-xs">
            <div className="font-semibold mb-1">Note:</div>
            {data.notes}
          </TooltipContent>
        </Tooltip>
      )}
    </div>
  );
};

export const AgentNode = ({ data, selected, id }: NodeProps) => {
  const model = data.model || data.agent_config?.model || "gpt-4";
  const temperature = data.temperature || data.agent_config?.temperature || 0.7;
  const tools = data.tools || [];

  return (
    <BaseNode
      selected={selected}
      title="AI Agent"
      icon={Bot}
      id={id}
      status={data.status}
      category="agent"
      executionTime={data.executionTime}
      lastRun={data.lastRun}
      errorCount={data.errorCount}
      notes={data.notes}
    >
      <div className="space-y-3">
        <div className="flex items-start gap-3">
          <div className="relative">
            {/* Holographic glow effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/30 to-purple-500/30 rounded-lg blur-md" />
            <div className="relative w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-600/10 flex items-center justify-center shrink-0 border border-blue-500/30 shadow-lg group-hover:scale-110 transition-transform duration-300">
              <Bot className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-bold text-sm truncate bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent">
              {data.label || "AI Agent"}
            </div>
            <div className="text-xs text-muted-foreground truncate mt-0.5">{data.agent_id || "Not configured"}</div>
          </div>
        </div>

        {data.description && (
          <div className="p-2.5 bg-gradient-to-br from-blue-500/5 to-purple-500/5 rounded-lg text-xs text-muted-foreground line-clamp-2 border border-blue-500/20 backdrop-blur-sm">
            {data.description}
          </div>
        )}

        <div className="flex flex-wrap gap-2">

          {tools.length > 0 && (
            <Badge variant="outline" className="text-[10px] h-6 px-2.5 border-blue-500/30">
              {tools.length} tool{tools.length > 1 ? "s" : ""}
            </Badge>
          )}
        </div>

        {data.cost && (
          <div className="flex items-center justify-between text-[10px] text-muted-foreground pt-2 border-t border-blue-500/20">
            <span className="font-medium">Est. Cost</span>
            <span className="font-mono font-bold text-blue-600 dark:text-blue-400">${data.cost.toFixed(4)}</span>
          </div>
        )}
      </div>
    </BaseNode>
  );
};

export const ConditionNode = ({ data, selected, id }: NodeProps) => {
  const trueCount = data.trueCount || 0;
  const falseCount = data.falseCount || 0;
  const total = trueCount + falseCount;
  const truePercent = total > 0 ? Math.round((trueCount / total) * 100) : 50;

  // Multi-branch mode support
  const isMultiBranch = data.mode === "multi" || (data.branches && data.branches.length > 0);
  const branches = data.branches || [];

  if (isMultiBranch) {
    // Multi-branch (Switch-case) mode
    return (
      <ContextMenu>
        <ContextMenuTrigger>
          <div
            className={`
              relative w-[280px] rounded-xl border-2 bg-card shadow-md transition-all
              ${selected ? "border-yellow-500 ring-2 ring-yellow-500/30 shadow-yellow-500/20" : "border-yellow-500/50 hover:border-yellow-500 hover:shadow-lg"}
            `}
          >
            <div className="flex items-center gap-2 px-3 py-2 bg-yellow-500/10 border-b border-yellow-500/20 rounded-t-lg">
              <GitBranch className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
              <span className="font-semibold text-xs uppercase text-yellow-600 dark:text-yellow-400">Switch</span>
              <Badge variant="secondary" className="ml-auto text-[9px] h-4 px-1">
                {branches.length} cases
              </Badge>
              {data.notes && (
                <Tooltip>
                  <TooltipTrigger>
                    <div className="ml-1 bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 p-1 rounded-sm">
                      <MessageSquare className="w-3 h-3" />
                    </div>
                  </TooltipTrigger>
                  <TooltipContent side="top" className="max-w-[200px] text-xs">
                    <div className="font-semibold mb-1">Note:</div>
                    {data.notes}
                  </TooltipContent>
                </Tooltip>
              )}
            </div>

            <div className="p-3 space-y-2">
              <div className="text-xs font-mono bg-slate-950 text-slate-50 p-2 rounded border border-slate-800">
                {data.condition || "switch (value)"}
              </div>

              {/* Branch handles */}
              <div className="space-y-1">
                {branches.map((branch: any, index: number) => (
                  <div key={index} className="flex items-center justify-between text-[10px] px-2 py-1 bg-muted/30 rounded">
                    <span className="font-mono truncate">{branch.label || `Case ${index + 1}`}</span>
                    <code className="text-muted-foreground truncate ml-2">{branch.value || "default"}</code>
                  </div>
                ))}
              </div>
            </div>

            <Handle type="target" position={Position.Left} className="w-3 h-3 !bg-yellow-500 border-2 border-background" />

            {/* Dynamic handles for each branch */}
            {branches.map((branch: any, index: number) => {
              const totalBranches = branches.length;
              const spacing = 60 / (totalBranches + 1);
              const topPercent = spacing * (index + 1) + 20;

              return (
                <div
                  key={branch.id || index}
                  className="absolute -right-3 flex items-center"
                  style={{ top: `${topPercent}%` }}
                >
                  <div className="bg-card text-[10px] font-bold text-blue-600 dark:text-blue-400 px-1.5 py-0.5 border border-border rounded shadow-sm mr-1 max-w-[60px] truncate">
                    {branch.label || `C${index + 1}`}
                  </div>
                  <Handle
                    type="source"
                    position={Position.Right}
                    id={branch.id || `case-${index}`}
                    className="w-3 h-3 !bg-blue-500 border-2 border-background !static"
                  />
                </div>
              );
            })}

            {/* Default/Else handle */}
            <div className="absolute -right-3 bottom-4 flex items-center">
              <div className="bg-card text-[10px] font-bold text-muted-foreground px-1.5 py-0.5 border border-border rounded shadow-sm mr-1">
                DEFAULT
              </div>
              <Handle
                type="source"
                position={Position.Right}
                id="default"
                className="w-3 h-3 !bg-slate-500 border-2 border-background !static"
              />
            </div>
          </div>
        </ContextMenuTrigger>
        <ContextMenuContent>
          <ContextMenuItem>
            <Eye className="w-4 h-4 mr-2" />
            Test Expression
          </ContextMenuItem>
          <ContextMenuItem>
            <Plus className="w-4 h-4 mr-2" />
            Add Branch
          </ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>
    );
  }

  // Binary (True/False) mode - original implementation
  return (
    <ContextMenu>
      <ContextMenuTrigger>
        <div
          className={`
            relative w-[260px] rounded-xl border-2 bg-card shadow-md transition-all
            ${selected ? "border-yellow-500 ring-2 ring-yellow-500/30 shadow-yellow-500/20" : "border-yellow-500/50 hover:border-yellow-500 hover:shadow-lg"}
          `}
        >
          <div className="flex items-center gap-2 px-3 py-2 bg-yellow-500/10 border-b border-yellow-500/20 rounded-t-lg">
            <GitBranch className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
            <span className="font-semibold text-xs uppercase text-yellow-600 dark:text-yellow-400">Condition</span>
            {total > 0 && (
              <Badge variant="secondary" className="ml-auto text-[9px] h-4 px-1">
                {truePercent}% / {100 - truePercent}%
              </Badge>
            )}
          </div>

          <div className="p-3 space-y-2">
            <div className="text-xs font-mono bg-slate-950 text-slate-50 p-2 rounded border border-slate-800 break-all">
              {data.condition || "condition == true"}
            </div>
            {total > 0 && (
              <div className="flex gap-0.5 h-1.5 rounded-full overflow-hidden bg-muted">
                <div className="bg-green-500" style={{ width: `${truePercent}%` }} />
                <div className="bg-red-500" style={{ width: `${100 - truePercent}%` }} />
              </div>
            )}
          </div>

          <Handle type="target" position={Position.Left} className="w-3 h-3 !bg-yellow-500 border-2 border-background" />

          <div className="absolute -right-3 top-1/3 flex items-center">
            <div className="bg-card text-[10px] font-bold text-green-600 px-1.5 py-0.5 border border-border rounded shadow-sm mr-1">
              TRUE
            </div>
            <Handle type="source" position={Position.Right} id="true" className="w-3 h-3 !bg-green-500 border-2 border-background !static" />
          </div>

          <div className="absolute -right-3 bottom-1/3 flex items-center">
            <div className="bg-card text-[10px] font-bold text-red-600 px-1.5 py-0.5 border border-border rounded shadow-sm mr-1">
              FALSE
            </div>
            <Handle type="source" position={Position.Right} id="false" className="w-3 h-3 !bg-red-500 border-2 border-background !static" />
          </div>
          {data.notes && (
            <Tooltip>
              <TooltipTrigger>
                <div className="absolute top-2 right-2 bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 p-1 rounded-sm z-10">
                  <MessageSquare className="w-3 h-3" />
                </div>
              </TooltipTrigger>
              <TooltipContent side="top" className="max-w-[200px] text-xs">
                <div className="font-semibold mb-1">Note:</div>
                {data.notes}
              </TooltipContent>
            </Tooltip>
          )}
        </div>
      </ContextMenuTrigger>
      <ContextMenuContent>
        <ContextMenuItem>
          <Eye className="w-4 h-4 mr-2" />
          Test Expression
        </ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  );
};

export const LoopNode = ({ data, selected, id }: NodeProps) => {
  const currentIteration = data.currentIteration || 0;
  const maxIterations = data.iterations || 10;
  const progress = maxIterations > 0 ? (currentIteration / maxIterations) * 100 : 0;

  return (
    <BaseNode
      selected={selected}
      title="Loop"
      icon={Repeat}
      id={id}
      status={data.status}
      category="logic"
      executionTime={data.executionTime}
      lastRun={data.lastRun}
      notes={data.notes}
    >
      <div className="space-y-3">
        <div className="flex justify-between items-center text-xs">
          <span className="text-muted-foreground">Iterations</span>
          <span className="font-mono font-semibold">
            {currentIteration} / {maxIterations}
          </span>
        </div>

        {data.status === "running" && (
          <div className="space-y-1">
            <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
              <div className="bg-purple-500 h-full transition-all duration-300" style={{ width: `${progress}%` }} />
            </div>
            <div className="text-[10px] text-muted-foreground text-right">{Math.round(progress)}%</div>
          </div>
        )}

        <div className="text-xs">
          <span className="text-muted-foreground">Collection:</span>
          <code className="ml-1.5 bg-muted px-1.5 py-0.5 rounded text-purple-600 dark:text-purple-400">
            {data.collection_path || "items"}
          </code>
        </div>

        {data.parallelMode && (
          <Badge variant="outline" className="text-[10px] h-5">
            <Zap className="w-3 h-3 mr-1" />
            Parallel
          </Badge>
        )}
      </div>
      <Handle type="source" position={Position.Left} id="loop-back" className="!bg-purple-500 border-2 border-background top-2/3" />
    </BaseNode>
  );
};

export const ActionNode = ({ data, selected, id }: NodeProps) => {
  const actionType = data.action_type || "custom";
  const actionConfig = data.action_config || {};

  return (
    <BaseNode
      selected={selected}
      title="Action"
      icon={Zap}
      id={id}
      status={data.status}
      category="tool"
      executionTime={data.executionTime}
      lastRun={data.lastRun}
      errorCount={data.errorCount}
      notes={data.notes}
    >
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-xs font-medium capitalize">
            {actionType.replace("_", " ")}
          </Badge>
          {actionConfig.method && (
            <Badge variant="outline" className="text-[10px] h-5 px-1.5">
              {actionConfig.method}
            </Badge>
          )}
        </div>

        {actionConfig.url && (
          <div className="p-2 bg-muted/30 rounded border border-border/30">
            <div className="text-[9px] text-muted-foreground uppercase mb-0.5">Endpoint</div>
            <code className="text-xs font-mono truncate block">{actionConfig.url}</code>
          </div>
        )}

        <p className="text-xs text-muted-foreground line-clamp-2">{data.description || "Executes a custom action or script."}</p>

        {data.retryPolicy && (
          <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
            <Repeat className="w-3 h-3" />
            <span>
              Retry: {data.retryPolicy.max_retries || 3}x
            </span>
          </div>
        )}
      </div>
    </BaseNode>
  );
};

export const ChatNode = ({ data, selected, id }: NodeProps) => {
  const inputType = data.inputType || "text";
  const hasValidation = data.validation && Object.keys(data.validation).length > 0;

  return (
    <BaseNode
      selected={selected}
      title="Human Input"
      icon={MessageSquare}
      id={id}
      status={data.status}
      category="human"
      executionTime={data.executionTime}
      lastRun={data.lastRun}
      notes={data.notes}
    >
      <div className="space-y-3">
        <div className="bg-cyan-500/5 border border-cyan-500/20 p-2.5 rounded-lg">
          <p className="text-xs italic text-cyan-900 dark:text-cyan-100 line-clamp-3">
            "{data.welcomeMessage || "Waiting for user input..."}"
          </p>
        </div>

        <div className="flex flex-wrap gap-1.5">
          <Badge variant="outline" className="text-[10px] h-5 capitalize">
            {inputType}
          </Badge>
          {hasValidation && (
            <Badge variant="secondary" className="text-[10px] h-5">
              <CheckCircle2 className="w-3 h-3 mr-1" />
              Validated
            </Badge>
          )}
          {data.timeout && (
            <Badge variant="outline" className="text-[10px] h-5">
              <Clock className="w-3 h-3 mr-1" />
              {data.timeout}s
            </Badge>
          )}
        </div>

        <div className="flex items-center gap-1.5 text-[10px] text-cyan-600 dark:text-cyan-400 font-medium pt-2 border-t border-border/30">
          <div className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse" />
          <span>Pauses Execution</span>
        </div>
      </div>
    </BaseNode>
  );
};

export const DisplayNode = ({ data, selected, id }: NodeProps) => {
  const displayData = data.lastOutput || data.previewData;
  const hasData = displayData && Object.keys(displayData).length > 0;
  const viewMode = data.viewMode || "json";

  return (
    <BaseNode
      selected={selected}
      title="Display"
      icon={Monitor}
      id={id}
      status={data.status}
      category="tool"
      executionTime={data.executionTime}
      notes={data.notes}
    >
      <div className="space-y-2">
        <div className="flex gap-1">
          <Badge variant={viewMode === "json" ? "default" : "outline"} className="text-[9px] h-5 px-2">
            JSON
          </Badge>
          <Badge variant={viewMode === "table" ? "default" : "outline"} className="text-[9px] h-5 px-2">
            Table
          </Badge>
          <Badge variant={viewMode === "raw" ? "default" : "outline"} className="text-[9px] h-5 px-2">
            Raw
          </Badge>
        </div>

        <div className="relative max-h-60 bg-slate-950 rounded-lg border border-slate-800 p-2.5 overflow-auto group custom-scrollbar">
          {hasData ? (
            <>
              <pre className="text-[10px] font-mono text-slate-300 leading-relaxed whitespace-pre-wrap break-all">
                {JSON.stringify(displayData, null, 2)}
              </pre>
              <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity sticky">
                <Button size="icon" variant="secondary" className="h-6 w-6 bg-slate-800 hover:bg-slate-700 shadow-md">
                  <Eye className="w-3 h-3" />
                </Button>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-slate-500">
              <Monitor className="w-8 h-8 mb-1 opacity-30" />
              <span className="text-xs">No data</span>
            </div>
          )}
        </div>
      </div>
    </BaseNode>
  );
};

export const ErrorHandlerNode = ({ data, selected, id }: NodeProps) => {
  const errorsCaught = data.errorsCaught || 0;
  const retryStrategy = data.retryStrategy || "exponential";

  return (
    <BaseNode
      selected={selected}
      title="Error Handler"
      icon={AlertCircle}
      id={id}
      status={data.status}
      category="logic"
      executionTime={data.executionTime}
      notes={data.notes}
    >
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs">
            <span className="font-semibold text-orange-600 dark:text-orange-400">Catch:</span>
            <Badge variant="outline" className="border-orange-500/30 text-orange-600 dark:text-orange-400 text-[10px] h-5">
              {data.error_type || "All"}
            </Badge>
          </div>
          {errorsCaught > 0 && (
            <Badge variant="secondary" className="text-[10px] h-5">
              {errorsCaught} caught
            </Badge>
          )}
        </div>

        <div className="p-2 bg-orange-500/5 border border-orange-500/20 rounded">
          <div className="text-[9px] text-muted-foreground uppercase mb-1">Retry Strategy</div>
          <div className="text-xs font-medium capitalize">
            {retryStrategy.replace("_", " ")}
          </div>
        </div>

        {data.fallbackAction && (
          <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
            <ArrowRight className="w-3 h-3" />
            <span>Then: {data.fallbackAction}</span>
          </div>
        )}
      </div>
    </BaseNode>
  );
};

// --- New Specialized Node Types (Phase 2) ---

export const HttpRequestNode = ({ data, selected, id }: NodeProps) => {
  const method = data.method || "GET";
  const url = data.url || "";

  return (
    <BaseNode
      selected={selected}
      title="HTTP Request"
      icon={Zap}
      id={id}
      status={data.status}
      category="tool"
      executionTime={data.executionTime}
      lastRun={data.lastRun}
      errorCount={data.errorCount}
      notes={data.notes}
    >
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Badge
            variant={method === "GET" ? "default" : method === "POST" ? "secondary" : "outline"}
            className="text-xs font-mono px-2"
          >
            {method}
          </Badge>
          {data.statusCode && (
            <Badge
              variant={data.statusCode < 300 ? "default" : "destructive"}
              className="text-[10px] h-5"
            >
              {data.statusCode}
            </Badge>
          )}
        </div>

        {url && (
          <div className="p-2 bg-muted/30 rounded border border-border/30">
            <div className="text-[9px] text-muted-foreground uppercase mb-0.5">Endpoint</div>
            <code className="text-xs font-mono truncate block">{url}</code>
          </div>
        )}

        <div className="flex flex-wrap gap-1.5">
          {data.headers && Object.keys(data.headers).length > 0 && (
            <Badge variant="outline" className="text-[10px] h-5">
              {Object.keys(data.headers).length} header{Object.keys(data.headers).length > 1 ? "s" : ""}
            </Badge>
          )}
          {data.auth && (
            <Badge variant="outline" className="text-[10px] h-5">
              🔒 {data.auth}
            </Badge>
          )}
        </div>
      </div>
    </BaseNode>
  );
};

export const DatabaseNode = ({ data, selected, id }: NodeProps) => {
  const operation = data.operation || "select";
  const table = data.table || "";

  return (
    <BaseNode
      selected={selected}
      title="Database"
      icon={Database}
      id={id}
      status={data.status}
      category="tool"
      executionTime={data.executionTime}
      lastRun={data.lastRun}
      errorCount={data.errorCount}
      notes={data.notes}
    >
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-xs uppercase">
            {operation}
          </Badge>
          {data.rowsAffected !== undefined && (
            <Badge variant="outline" className="text-[10px] h-5">
              {data.rowsAffected} rows
            </Badge>
          )}
        </div>

        {table && (
          <div className="p-2 bg-slate-950 rounded border border-slate-800">
            <div className="text-[9px] text-slate-500 uppercase mb-0.5">Table</div>
            <code className="text-xs font-mono text-slate-50">{table}</code>
          </div>
        )}

        {data.query && (
          <div className="text-xs font-mono bg-muted p-2 rounded border border-border/50 line-clamp-2">
            {data.query}
          </div>
        )}

        {data.connection && (
          <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
            <Database className="w-3 h-3" />
            <span>{data.connection}</span>
          </div>
        )}
      </div>
    </BaseNode>
  );
};

export const TransformNode = ({ data, selected, id }: NodeProps) => {
  const transformType = data.transformType || "map";
  const mappingsCount = data.mappings ? Object.keys(data.mappings).length : 0;

  return (
    <BaseNode
      selected={selected}
      title="Transform"
      icon={Code2}
      id={id}
      status={data.status}
      category="tool"
      executionTime={data.executionTime}
      lastRun={data.lastRun}
      notes={data.notes}
    >
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-xs capitalize">
            {transformType}
          </Badge>
          {mappingsCount > 0 && (
            <Badge variant="outline" className="text-[10px] h-5">
              {mappingsCount} field{mappingsCount > 1 ? "s" : ""}
            </Badge>
          )}
        </div>

        {data.expression && (
          <div className="p-2 bg-muted/30 rounded border border-border/30">
            <code className="text-xs font-mono text-purple-600 dark:text-purple-400 line-clamp-2">
              {data.expression}
            </code>
          </div>
        )}

        {data.mappings && (
          <div className="space-y-1">
            {Object.entries(data.mappings).slice(0, 2).map(([key, value]: [string, any]) => (
              <div key={key} className="flex items-center gap-2 text-[10px]">
                <code className="text-muted-foreground">{key}</code>
                <ArrowRight className="w-3 h-3 text-muted-foreground" />
                <code className="text-foreground truncate">{String(value)}</code>
              </div>
            ))}
            {Object.keys(data.mappings).length > 2 && (
              <div className="text-[10px] text-muted-foreground">
                +{Object.keys(data.mappings).length - 2} more
              </div>
            )}
          </div>
        )}
      </div>
    </BaseNode>
  );
};

export const FilterNode = ({ data, selected, id }: NodeProps) => {
  const rules = data.rules || [];
  const filterMode = data.filterMode || "keep";

  return (
    <BaseNode
      selected={selected}
      title="Filter"
      icon={GitBranch}
      id={id}
      status={data.status}
      category="logic"
      executionTime={data.executionTime}
      notes={data.notes}
    >
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Badge variant={filterMode === "keep" ? "default" : "secondary"} className="text-xs">
            {filterMode === "keep" ? "Keep matching" : "Remove matching"}
          </Badge>
          {rules.length > 0 && (
            <Badge variant="outline" className="text-[10px] h-5">
              {rules.length} rule{rules.length > 1 ? "s" : ""}
            </Badge>
          )}
        </div>

        {data.filterExpression && (
          <div className="text-xs font-mono bg-muted p-2 rounded border border-border/50 line-clamp-2">
            {data.filterExpression}
          </div>
        )}

        {data.itemsFiltered !== undefined && (
          <div className="flex justify-between text-[10px] text-muted-foreground pt-2 border-t border-border/30">
            <span>Items Filtered</span>
            <span className="font-mono font-medium">{data.itemsFiltered}</span>
          </div>
        )}
      </div>
    </BaseNode>
  );
};

export const MergeNode = ({ data, selected, id }: NodeProps) => {
  const mergeMode = data.mergeMode || "concatenate";
  const inputCount = data.inputCount || 2;

  return (
    <BaseNode
      selected={selected}
      title="Merge"
      icon={GitBranch}
      id={id}
      status={data.status}
      category="logic"
      executionTime={data.executionTime}
      notes={data.notes}
    >
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-xs capitalize">
            {mergeMode.replace("_", " ")}
          </Badge>
          <Badge variant="outline" className="text-[10px] h-5">
            {inputCount} inputs
          </Badge>
        </div>

        {data.mergeKey && (
          <div className="p-2 bg-muted/30 rounded border border-border/30">
            <div className="text-[9px] text-muted-foreground uppercase mb-0.5">Merge Key</div>
            <code className="text-xs font-mono">{data.mergeKey}</code>
          </div>
        )}

        <p className="text-xs text-muted-foreground line-clamp-2">
          {mergeMode === "concatenate" && "Combines all inputs into a single array"}
          {mergeMode === "merge" && "Merges objects by key"}
          {mergeMode === "zip" && "Creates pairs from inputs"}
          {mergeMode === "join" && "SQL-style join on key"}
        </p>
      </div>
    </BaseNode>
  );
};

export const DelayNode = ({ data, selected, id }: NodeProps) => {
  const delayType = data.delayType || "fixed";
  const duration = data.duration || 1000;

  return (
    <BaseNode
      selected={selected}
      title="Delay"
      icon={Clock}
      id={id}
      status={data.status}
      category="logic"
      executionTime={data.executionTime}
      notes={data.notes}
    >
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-xs capitalize">
            {delayType} delay
          </Badge>
          <Badge variant="outline" className="text-[10px] h-5 font-mono">
            {duration < 1000 ? `${duration}ms` : `${duration / 1000}s`}
          </Badge>
        </div>

        {data.waitUntil && (
          <div className="p-2 bg-muted/30 rounded border border-border/30">
            <div className="text-[9px] text-muted-foreground uppercase mb-0.5">Wait Until</div>
            <code className="text-xs">{new Date(data.waitUntil).toLocaleString()}</code>
          </div>
        )}

        {data.condition && (
          <div className="text-xs font-mono bg-muted p-2 rounded border border-border/50 line-clamp-2">
            Wait for: {data.condition}
          </div>
        )}

        <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
          <Clock className="w-3 h-3 animate-pulse" />
          <span>Pauses workflow execution</span>
        </div>
      </div>
    </BaseNode>
  );
};

export const GroupNode = ({ data, selected, id }: NodeProps) => {
  return (
    <>
      <NodeResizer
        minWidth={200}
        minHeight={100}
        isVisible={selected}
        lineClassName="border-blue-500"
        handleClassName="h-3 w-3 bg-blue-500 border-2 border-background rounded"
      />
      <div
        className={`
          h-full w-full rounded-xl border-2 transition-all bg-slate-100/50 dark:bg-slate-900/50 backdrop-blur-sm
          ${selected ? "border-blue-500 ring-2 ring-blue-500/20" : "border-slate-200 dark:border-slate-800 border-dashed"}
        `}
        style={{ backgroundColor: data.color || undefined }}
      >
        <div className="absolute -top-8 left-0 flex items-center gap-2 px-2 py-1">
          <Layers className="w-4 h-4 text-muted-foreground" />
          <span className="font-semibold text-sm text-foreground">{data.label || "Group"}</span>
        </div>
        {data.notes && (
          <div className="absolute top-2 right-2">
            <Tooltip>
              <TooltipTrigger>
                <div className="bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 p-1 rounded-sm">
                  <MessageSquare className="w-3 h-3" />
                </div>
              </TooltipTrigger>
              <TooltipContent side="top" className="max-w-[200px] text-xs">
                <div className="font-semibold mb-1">Note:</div>
                {data.notes}
              </TooltipContent>
            </Tooltip>
          </div>
        )}
      </div>
    </>
  );
};

export const nodeTypes = {
  startNode: StartNode,
  endNode: EndNode,
  agentNode: AgentNode,
  conditionNode: ConditionNode,
  loopNode: LoopNode,
  actionNode: ActionNode,
  errorHandlerNode: ErrorHandlerNode,
  chatNode: ChatNode,
  displayNode: DisplayNode,
  // Phase 2: New specialized nodes
  httpRequestNode: HttpRequestNode,
  databaseNode: DatabaseNode,
  transformNode: TransformNode,
  filterNode: FilterNode,
  mergeNode: MergeNode,
  delayNode: DelayNode,
  // Phase 4: Group node
  groupNode: GroupNode,
};
