import { useState } from "react";
import {
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  XCircle,
  Loader2,
  Terminal,
  Clock
} from "lucide-react";
import { cn } from "@/lib/utils";

export interface ToolCall {
  id: string;
  name: string;
  args: any;
  result?: string;
  duration?: number;
  status: 'running' | 'complete' | 'error';
}

interface ToolCallLogProps {
  toolCalls: ToolCall[];
  isThinking?: boolean;
}

export function ToolCallLog({ toolCalls, isThinking }: ToolCallLogProps) {
  const [isOpen, setIsOpen] = useState(true);

  // Check if any tools are currently running
  const hasRunningTools = toolCalls.some(call => call.status === 'running');
  // Show working indicator if tools are running OR if thinking with no tools yet
  const showWorking = hasRunningTools || (isThinking && toolCalls.length === 0);

  if (!toolCalls.length && !isThinking) return null;

  return (
    <div className="border border-border rounded-md bg-card/50 my-2 overflow-hidden shadow-sm">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-2 p-2 text-xs font-medium text-muted-foreground hover:bg-muted/50 transition-colors bg-muted/20"
      >
        {isOpen ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
        <Terminal className="w-3 h-3" />
        <span>Agent Process</span>
        {showWorking && (
          <div className="flex items-center gap-1.5 ml-auto text-primary">
            <Loader2 className="w-3 h-3 animate-spin" />
            <span className="text-[10px] font-normal">Working...</span>
          </div>
        )}
      </button>

      {isOpen && (
        <div className="p-2 space-y-2 bg-background/50">
          {toolCalls.map((call) => (
            <div key={call.id} className="text-sm group">
              {/* Tool Header */}
              <div className="flex items-center gap-2 py-1">
                {call.status === 'running' ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-500 flex-shrink-0" />
                ) : call.status === 'complete' ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-green-500 flex-shrink-0" />
                ) : (
                  <XCircle className="w-3.5 h-3.5 text-red-500 flex-shrink-0" />
                )}

                <span className="font-mono text-xs font-medium text-foreground/90">
                  {call.name}
                </span>

                {call.duration && (
                  <span className="flex items-center gap-1 text-[10px] text-muted-foreground ml-auto">
                    <Clock className="w-3 h-3" />
                    {(call.duration / 1000).toFixed(2)}s
                  </span>
                )}
              </div>

              {/* Tool Details (Args & Result) */}
              <div className="pl-5.5 space-y-1.5">
                {/* Arguments */}
                <div className="text-xs">
                  <span className="text-muted-foreground mr-1">Input:</span>
                  <span className="font-mono text-muted-foreground/80 break-all">
                    {JSON.stringify(call.args)}
                  </span>
                </div>

                {/* Result */}
                {call.result && (
                  <div className="text-xs">
                    <span className="text-muted-foreground mr-1">Output:</span>
                    <span className="text-muted-foreground/80 line-clamp-2 group-hover:line-clamp-none transition-all">
                      {call.result}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Thinking Indicator (Bottom of list) - only show if thinking and NO tools yet */}
          {isThinking && toolCalls.length === 0 && (
            <div className="flex items-center gap-2 py-1 pl-0.5 animate-pulse">
              <div className="w-3.5 h-3.5 flex items-center justify-center">
                <div className="w-1.5 h-1.5 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              </div>
              <span className="text-xs text-muted-foreground italic">Thinking...</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
