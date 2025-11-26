import { Handle, Position, NodeProps } from "reactflow";
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
}

const categoryStyles = {
  trigger: {
    border: "border-emerald-500/40",
    header: "bg-emerald-500/10",
    iconColor: "text-emerald-600 dark:text-emerald-400",
    handle: "!bg-emerald-500",
    glow: "shadow-emerald-500/20",
  },
  agent: {
    border: "border-blue-500/40",
    header: "bg-blue-500/10",
    iconColor: "text-blue-600 dark:text-blue-400",
    handle: "!bg-blue-500",
    glow: "shadow-blue-500/20",
  },
  logic: {
    border: "border-purple-500/40",
    header: "bg-purple-500/10",
    iconColor: "text-purple-600 dark:text-purple-400",
    handle: "!bg-purple-500",
    glow: "shadow-purple-500/20",
  },
  tool: {
    border: "border-orange-500/40",
    header: "bg-orange-500/10",
    iconColor: "text-orange-600 dark:text-orange-400",
    handle: "!bg-orange-500",
    glow: "shadow-orange-500/20",
  },
  human: {
    border: "border-cyan-500/40",
    header: "bg-cyan-500/10",
    iconColor: "text-cyan-600 dark:text-cyan-400",
    handle: "!bg-cyan-500",
    glow: "shadow-cyan-500/20",
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
              relative w-[300px] rounded-lg border bg-card shadow-md transition-all duration-200 group
              ${selected ? `ring-2 ring-primary ${styles.border} ${styles.glow}` : `border-border hover:${styles.border} hover:shadow-lg`}
            `}
          >
            {/* Drag Handle */}
            <div className="absolute -left-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity cursor-grab active:cursor-grabbing">
              <div className="bg-muted border border-border rounded p-0.5">
                <GripVertical className="w-3 h-3 text-muted-foreground" />
              </div>
            </div>

            {/* Header */}
            <div className={`flex items-center justify-between px-3 py-2 border-b border-border/50 ${styles.header}`}>
              <div className="flex items-center gap-2">
                <Icon className={`w-4 h-4 ${styles.iconColor}`} />
                <span className="font-semibold text-xs tracking-wide uppercase">{title}</span>
              </div>
              <div className="flex items-center gap-2">
                {StatusIcon && (
                  <Tooltip>
                    <TooltipTrigger>
                      <div className={statusInfo.color}>
                        <StatusIcon className={`w-3.5 h-3.5 ${statusInfo.animate ? "animate-spin" : ""}`} />
                      </div>
                    </TooltipTrigger>
                    <TooltipContent side="top" className="text-xs">
                      {statusInfo.label}
                    </TooltipContent>
                  </Tooltip>
                )}
                {errorCount > 0 && (
                  <Tooltip>
                    <TooltipTrigger>
                      <Badge variant="destructive" className="h-4 px-1 text-[10px]">
                        {errorCount}
                      </Badge>
                    </TooltipTrigger>
                    <TooltipContent side="top" className="text-xs">
                      {errorCount} error{errorCount > 1 ? "s" : ""}
                    </TooltipContent>
                  </Tooltip>
                )}
                <span className="text-[10px] text-muted-foreground font-mono opacity-50">
                  #{id.split("-")[1]?.slice(0, 4) || id.slice(0, 4)}
                </span>
              </div>
            </div>

            {/* Body */}
            <div className="p-3">{children}</div>

            {/* Footer with Metrics */}
            <div className="px-3 py-1.5 border-t border-border/50 bg-muted/20 flex items-center justify-between">
              <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                {executionTime !== undefined && (
                  <Tooltip>
                    <TooltipTrigger className="flex items-center gap-1">
                      <Activity className="w-3 h-3" />
                      <span className="font-mono">{executionTime}ms</span>
                    </TooltipTrigger>
                    <TooltipContent side="bottom" className="text-xs">
                      Last execution time
                    </TooltipContent>
                  </Tooltip>
                )}
                {lastRun && (
                  <Tooltip>
                    <TooltipTrigger className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      <span>{new Date(lastRun).toLocaleTimeString()}</span>
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
                        className="h-5 w-5 rounded"
                        onClick={(e) => {
                          e.stopPropagation();
                          onRun();
                        }}
                      >
                        <Play className="w-3 h-3" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent side="bottom" className="text-xs">
                      Test run this node
                    </TooltipContent>
                  </Tooltip>
                )}
              </div>
            </div>

            {/* Handles */}
            <Handle type="target" position={Position.Left} className={`w-3 h-3 border-2 border-background ${styles.handle}`} />
            <Handle type="source" position={Position.Right} className={`w-3 h-3 border-2 border-background ${styles.handle}`} />
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
            relative w-[220px] rounded-xl border-2 bg-card shadow-md p-3 transition-all
            ${selected ? "border-emerald-500 ring-2 ring-emerald-500/30 shadow-emerald-500/20" : "border-emerald-500/50 hover:border-emerald-500 hover:shadow-lg"}
          `}
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-emerald-500/10 flex items-center justify-center border-2 border-emerald-500/30 shrink-0">
              <Play className="w-6 h-6 text-emerald-600 dark:text-emerald-400 ml-0.5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-bold text-sm">Start</div>
              <div className="text-[10px] text-muted-foreground uppercase tracking-wide">{triggerType}</div>
              {triggerType === "webhook" && triggerConfig.method && (
                <Badge variant="outline" className="mt-1 h-4 text-[9px] px-1">
                  {triggerConfig.method}
                </Badge>
              )}
              {triggerType === "schedule" && triggerConfig.cron && (
                <code className="block mt-1 text-[9px] bg-muted px-1 rounded truncate">{triggerConfig.cron}</code>
              )}
            </div>
          </div>
          <Handle type="source" position={Position.Right} className="w-3 h-3 !bg-emerald-500 border-2 border-background" />
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
        relative w-[200px] rounded-xl border-2 bg-card shadow-md p-3 transition-all
        ${selected ? "border-red-500 ring-2 ring-red-500/30 shadow-red-500/20" : "border-red-500/50 hover:border-red-500 hover:shadow-lg"}
      `}
    >
      <Handle type="target" position={Position.Left} className="w-3 h-3 !bg-red-500 border-2 border-background" />
      <div className="flex items-center gap-3">
        <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center border-2 border-red-500/30">
          <Square className="w-6 h-6 text-red-600 dark:text-red-400" />
        </div>
        <div>
          <div className="font-bold text-sm">End</div>
          <div className="text-[10px] text-muted-foreground">Workflow Complete</div>
        </div>
      </div>
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
    >
      <div className="space-y-3">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500/20 to-blue-600/10 flex items-center justify-center shrink-0 border border-blue-500/20">
            <Bot className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-sm truncate">{data.label || "AI Agent"}</div>
            <div className="text-xs text-muted-foreground truncate">{data.agent_id || "Not configured"}</div>
          </div>
        </div>

        {data.description && (
          <div className="p-2 bg-muted/30 rounded-md text-xs text-muted-foreground line-clamp-2 border border-border/30">
            {data.description}
          </div>
        )}

        <div className="flex flex-wrap gap-1.5">
          <Badge variant="secondary" className="text-[10px] h-5 px-2 font-mono">
            {model}
          </Badge>
          <Badge variant="outline" className="text-[10px] h-5 px-2">
            temp: {temperature}
          </Badge>
          {tools.length > 0 && (
            <Badge variant="outline" className="text-[10px] h-5 px-2">
              {tools.length} tool{tools.length > 1 ? "s" : ""}
            </Badge>
          )}
        </div>

        {data.cost && (
          <div className="flex items-center justify-between text-[10px] text-muted-foreground pt-2 border-t border-border/30">
            <span>Est. Cost</span>
            <span className="font-mono font-medium">${data.cost.toFixed(4)}</span>
          </div>
        )}
      </div>
    </BaseNode>
  );
};

export const ConditionNode = ({ data, selected, id }: NodeProps) => {
  const trueCount = data.metrics?.trueCount || 0;
  const falseCount = data.metrics?.falseCount || 0;
  const total = trueCount + falseCount;
  const truePercent = total > 0 ? Math.round((trueCount / total) * 100) : 50;

  return (
    <ContextMenu>
      <ContextMenuTrigger>
        <div
          className={`
            relative w-[260px] rounded-lg border bg-card shadow-md transition-all
            ${selected ? "border-yellow-500 ring-2 ring-yellow-500/30" : "border-border hover:border-yellow-500/50"}
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
      lastRun={data.lastRun}
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

        <div className="relative h-28 bg-slate-950 rounded-lg border border-slate-800 p-2.5 overflow-hidden group">
          {hasData ? (
            <>
              <pre className="text-[10px] font-mono text-slate-300 leading-relaxed">
                {JSON.stringify(displayData, null, 2)}
              </pre>
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent pointer-events-none" />
              <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button size="icon" variant="secondary" className="h-6 w-6 bg-slate-800 hover:bg-slate-700">
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
};
