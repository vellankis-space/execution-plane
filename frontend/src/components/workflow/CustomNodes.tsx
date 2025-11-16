import { Handle, Position, NodeProps } from "reactflow";
import { Card } from "@/components/ui/card";
import { Bot, GitBranch, Repeat, Play, Square, Settings, AlertCircle, MessageSquare, Monitor } from "lucide-react";

// Start Node
export const StartNode = ({ data, selected }: NodeProps) => {
  return (
    <div
      className={`px-4 py-3 shadow-lg rounded-full bg-gradient-to-r from-green-400 to-green-600 border-2 ${
        selected ? "border-blue-500" : "border-green-700"
      } text-white min-w-[120px] text-center`}
    >
      <div className="flex items-center justify-center gap-2">
        <Play className="w-4 h-4" />
        <div className="font-semibold text-sm">Start</div>
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-green-700"
      />
    </div>
  );
};

// End Node
export const EndNode = ({ data, selected }: NodeProps) => {
  return (
    <div
      className={`px-4 py-3 shadow-lg rounded-full bg-gradient-to-r from-red-400 to-red-600 border-2 ${
        selected ? "border-blue-500" : "border-red-700"
      } text-white min-w-[120px] text-center`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-red-700"
      />
      <div className="flex items-center justify-center gap-2">
        <Square className="w-4 h-4" />
        <div className="font-semibold text-sm">End</div>
      </div>
    </div>
  );
};

// Agent Node
export const AgentNode = ({ data, selected }: NodeProps) => {
  return (
    <div
      className={`px-4 py-3 shadow-lg rounded-lg bg-white dark:bg-gray-800 border-2 ${
        selected ? "border-blue-500" : "border-gray-300 dark:border-gray-600"
      } min-w-[200px]`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-blue-500"
      />
      
      <div className="flex items-center gap-2 mb-2">
        <div className="p-1.5 rounded-md bg-blue-100 dark:bg-blue-900">
          <Bot className="w-4 h-4 text-blue-600 dark:text-blue-400" />
        </div>
        <div className="font-semibold text-sm">{data.label || "Agent"}</div>
      </div>
      
      {data.agent_id && (
        <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
          Agent: {data.agent_id}
        </div>
      )}
      
      {data.description && (
        <div className="text-xs text-gray-500 dark:text-gray-500 line-clamp-2">
          {data.description}
        </div>
      )}
      
      {data.status && (
        <div className="mt-2">
          <span
            className={`text-xs px-2 py-1 rounded-full ${
              data.status === "completed"
                ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                : data.status === "running"
                ? "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                : data.status === "failed"
                ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                : "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200"
            }`}
          >
            {data.status}
          </span>
        </div>
      )}
      
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-blue-500"
      />
    </div>
  );
};

// Condition Node
export const ConditionNode = ({ data, selected }: NodeProps) => {
  return (
    <div className="relative">
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-yellow-500"
      />
      
      <div
        className={`px-4 py-3 shadow-lg bg-white dark:bg-gray-800 border-2 ${
          selected ? "border-blue-500" : "border-yellow-400 dark:border-yellow-600"
        } transform rotate-45 w-32 h-32 flex items-center justify-center`}
      >
        <div className="transform -rotate-45 text-center">
          <div className="flex items-center justify-center gap-1 mb-1">
            <GitBranch className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
          </div>
          <div className="font-semibold text-xs">{data.label || "Condition"}</div>
          {data.condition && (
            <div className="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-1">
              {data.condition}
            </div>
          )}
        </div>
      </div>
      
      <Handle
        type="source"
        position={Position.Right}
        id="true"
        className="w-3 h-3 !bg-green-500"
        style={{ top: "50%", right: "-6px" }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="false"
        className="w-3 h-3 !bg-red-500"
        style={{ left: "50%", bottom: "-6px" }}
      />
    </div>
  );
};

// Loop Node
export const LoopNode = ({ data, selected }: NodeProps) => {
  return (
    <div
      className={`px-4 py-3 shadow-lg rounded-lg bg-white dark:bg-gray-800 border-2 border-dashed ${
        selected ? "border-blue-500" : "border-purple-400 dark:border-purple-600"
      } min-w-[200px]`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-purple-500"
      />
      
      <div className="flex items-center gap-2 mb-2">
        <div className="p-1.5 rounded-md bg-purple-100 dark:bg-purple-900">
          <Repeat className="w-4 h-4 text-purple-600 dark:text-purple-400" />
        </div>
        <div className="font-semibold text-sm">{data.label || "Loop"}</div>
      </div>
      
      {data.iterations && (
        <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
          Max iterations: {data.iterations}
        </div>
      )}
      
      {data.description && (
        <div className="text-xs text-gray-500 dark:text-gray-500 line-clamp-2">
          {data.description}
        </div>
      )}
      
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-purple-500"
      />
      <Handle
        type="source"
        position={Position.Left}
        id="loop"
        className="w-3 h-3 !bg-purple-500"
        style={{ top: "50%", left: "-6px" }}
      />
    </div>
  );
};

// Action Node
export const ActionNode = ({ data, selected }: NodeProps) => {
  return (
    <div
      className={`px-4 py-3 shadow-lg rounded-lg bg-white dark:bg-gray-800 border-2 ${
        selected ? "border-blue-500" : "border-indigo-300 dark:border-indigo-600"
      } min-w-[200px]`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-indigo-500"
      />
      
      <div className="flex items-center gap-2 mb-2">
        <div className="p-1.5 rounded-md bg-indigo-100 dark:bg-indigo-900">
          <Settings className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
        </div>
        <div className="font-semibold text-sm">{data.label || "Action"}</div>
      </div>
      
      {data.action_type && (
        <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
          Type: {data.action_type}
        </div>
      )}
      
      {data.description && (
        <div className="text-xs text-gray-500 dark:text-gray-500 line-clamp-2">
          {data.description}
        </div>
      )}
      
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-indigo-500"
      />
    </div>
  );
};

// Error Handler Node
export const ErrorHandlerNode = ({ data, selected }: NodeProps) => {
  return (
    <div
      className={`px-4 py-3 shadow-lg rounded-lg bg-white dark:bg-gray-800 border-2 ${
        selected ? "border-blue-500" : "border-orange-300 dark:border-orange-600"
      } min-w-[200px]`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-orange-500"
      />
      
      <div className="flex items-center gap-2 mb-2">
        <div className="p-1.5 rounded-md bg-orange-100 dark:bg-orange-900">
          <AlertCircle className="w-4 h-4 text-orange-600 dark:text-orange-400" />
        </div>
        <div className="font-semibold text-sm">{data.label || "Error Handler"}</div>
      </div>
      
      {data.error_type && (
        <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">
          Handles: {data.error_type}
        </div>
      )}
      
      {data.description && (
        <div className="text-xs text-gray-500 dark:text-gray-500 line-clamp-2">
          {data.description}
        </div>
      )}
      
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-orange-500"
      />
    </div>
  );
};

// Chat/Manual Trigger Node (n8n-inspired design)
export const ChatNode = ({ data, selected }: NodeProps) => {
  const hasMessage = data.welcomeMessage && data.welcomeMessage.trim().length > 0;
  
  return (
    <div
      className={`px-5 py-4 shadow-lg rounded-xl border-2 transition-all ${
        selected 
          ? "border-cyan-500 shadow-cyan-200 dark:shadow-cyan-900/50 scale-105" 
          : "border-cyan-300 dark:border-cyan-600 hover:border-cyan-400 dark:hover:border-cyan-500"
      } bg-gradient-to-br from-cyan-50 to-blue-50 dark:from-gray-800 dark:to-gray-900`}
      style={{ minWidth: '200px' }}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-cyan-500 border-2 border-white dark:border-gray-800"
      />
      
      {/* Header with icon and label */}
      <div className="flex items-center gap-2.5 mb-3">
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-cyan-500 dark:bg-cyan-600 flex items-center justify-center shadow-sm">
          <MessageSquare className="w-4.5 h-4.5 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-sm text-gray-800 dark:text-gray-100 truncate">
            {data.label || "Chat Input"}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-400">
            Manual Trigger
          </div>
        </div>
      </div>
      
      {/* Message preview or placeholder */}
      {hasMessage ? (
        <div className="mt-2 mb-2 p-2.5 rounded-lg bg-white/60 dark:bg-gray-900/40 border border-cyan-200 dark:border-cyan-800">
          <div className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 leading-relaxed">
            "{data.welcomeMessage}"
          </div>
        </div>
      ) : (
        <div className="mt-2 mb-2 p-2.5 rounded-lg bg-white/40 dark:bg-gray-900/30 border border-dashed border-cyan-300 dark:border-cyan-700">
          <div className="text-xs text-gray-400 dark:text-gray-500 italic">
            Click to configure message
          </div>
        </div>
      )}
      
      {/* Footer badge */}
      <div className="flex items-center gap-1.5 mt-2 pt-2 border-t border-cyan-200/50 dark:border-cyan-700/30">
        <div className="flex items-center gap-1 text-xs text-cyan-600 dark:text-cyan-400">
          <div className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse"></div>
          <span className="font-medium">Ready for input</span>
        </div>
      </div>
      
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-cyan-500 border-2 border-white dark:border-gray-800"
      />
    </div>
  );
};

// Display/Output Node
export const DisplayNode = ({ data, selected }: NodeProps) => {
  const displayData = data.lastOutput || data.previewData || {};
  const hasData = Object.keys(displayData).length > 0;

  return (
    <div
      className={`px-4 py-4 shadow-lg rounded-lg border-2 ${
        selected ? "border-blue-500 shadow-blue-300" : "border-emerald-400"
      } bg-white dark:bg-gray-800 min-w-[300px] max-w-[400px]`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-emerald-500"
      />
      
      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-emerald-200 dark:border-emerald-800">
        <Monitor className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
        <div className="font-semibold text-emerald-700 dark:text-emerald-300">
          {data.label || "Display Output"}
        </div>
      </div>
      
      {hasData ? (
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-3 max-h-[300px] overflow-auto">
          <pre className="text-xs font-mono text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words">
            {typeof displayData === 'string' 
              ? displayData 
              : JSON.stringify(displayData, null, 2)}
          </pre>
        </div>
      ) : (
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 text-center">
          <Monitor className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Connect to see output
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
            Data will appear here when the workflow runs
          </p>
        </div>
      )}
      
      {data.description && (
        <div className="text-xs text-gray-500 dark:text-gray-500 mt-2 pt-2 border-t">
          {data.description}
        </div>
      )}
      
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-emerald-500"
      />
    </div>
  );
};

// Export all node types
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
