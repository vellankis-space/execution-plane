import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot, User, Loader2, Trash2, RefreshCw, Sparkles, ArrowUp } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { ToolCallLog } from "@/components/ToolCallLog";
import { cn } from "@/lib/utils";

interface ToolCall {
  id: string;
  name: string;
  args: any;
  result?: string;
  duration?: number;
  status: 'running' | 'complete' | 'error';
}

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  toolCalls?: ToolCall[];
  isStreaming?: boolean;
  isThinking?: boolean;
}

interface Agent {
  agent_id: string;
  name: string;
  agent_type: string;
  llm_provider: string;
  llm_model: string;
  temperature: number;
  system_prompt: string;
  tools: string[];
  max_iterations: number;
  memory_type: string;
  streaming_enabled: boolean;
  human_in_loop: boolean;
  recursion_limit: number;
  created_at: string;
  updated_at: string;
}

export function AgentChat() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [threadId, setThreadId] = useState<string>("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const sessionKeyRef = useRef<string>("");
  const inFlightControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    fetchAgents();
    // Generate a unique thread ID for this conversation session
    const newThreadId = `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setThreadId(newThreadId);

    // Cleanup function to delete session memories on unmount or refresh
    const cleanupSession = async () => {
      if (newThreadId) {
        try {
          await fetch(`http://localhost:8000/api/v1/agents/memory/session/${newThreadId}`, {
            method: 'DELETE',
          });
          console.log(`Session ${newThreadId} cleaned up`);
        } catch (error) {
          console.error("Error cleaning up session:", error);
        }
      }
    };

    // Cleanup on page unload (refresh/close)
    const handleBeforeUnload = () => {
      // Use sendBeacon for reliable cleanup on page unload
      if (newThreadId) {
        navigator.sendBeacon(
          `http://localhost:8000/api/v1/agents/memory/session/${newThreadId}`,
        );
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    // Cleanup on component unmount
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      cleanupSession();
    };
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      const scrollElement = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight;
      }
    }
  }, [messages]);

  useEffect(() => {
    if (!selectedAgentId) return;

    const prevThreadId = threadId;

    const cleanupPrevSession = async () => {
      if (prevThreadId) {
        try {
          await fetch(`http://localhost:8000/api/v1/agents/memory/session/${prevThreadId}`, {
            method: 'POST',
          });
          console.log(`Previous session ${prevThreadId} cleaned up on agent switch`);
        } catch (error) {
          console.error("Error cleaning up previous session on agent switch:", error);
        }
      }
    };

    const newThreadId = `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setThreadId(newThreadId);

    setMessages([]);
    setInput("");
    setIsLoading(false);

    cleanupPrevSession();
  }, [selectedAgentId]);

  useEffect(() => {
    sessionKeyRef.current = `${selectedAgentId}|${threadId}`;
    if (inFlightControllerRef.current) {
      try { inFlightControllerRef.current.abort(); } catch { }
      inFlightControllerRef.current = null;
    }
  }, [selectedAgentId, threadId]);

  const fetchAgents = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/agents/');
      if (response.ok) {
        const data = await response.json();
        setAgents(data);
        if (data.length > 0 && !selectedAgentId) {
          setSelectedAgentId(data[0].agent_id);
        }
      }
    } catch (error) {
      console.error("Error fetching agents:", error);
      toast({
        title: "Error",
        description: "Failed to load agents",
        variant: "destructive",
      });
    }
  };

  const handleDeleteAgent = async (agentId: string, agentName: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/agents/${agentId}/`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // Remove the agent from the local state
        setAgents(agents.filter(agent => agent.agent_id !== agentId));
        // If the deleted agent was selected, clear the selection
        if (selectedAgentId === agentId) {
          setSelectedAgentId("");
          setMessages([]);
        }
        toast({
          title: "Agent Deleted",
          description: `${agentName} has been successfully deleted.`,
        });
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete agent');
      }
    } catch (error) {
      console.error("Error deleting agent:", error);
      toast({
        title: "Error Deleting Agent",
        description: error.message || "Failed to delete agent. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleClearConversation = async () => {
    setIsRefreshing(true);
    try {
      // Optional: Cleanup old session on backend
      if (threadId) {
        await fetch(`http://localhost:8000/api/v1/agents/memory/session/${threadId}`, {
          method: 'DELETE',
        }).catch(console.error);
      }
    } finally {
      const newThreadId = `thread_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      setThreadId(newThreadId);
      setMessages([]);
      setIsRefreshing(false);
      toast({
        title: "Conversation Cleared",
        description: "Started a new chat session.",
      });
    }
  };

  const handleSend = async () => {
    if (!input.trim() || !selectedAgentId) return;

    const messageToSend = input;
    setInput("");
    setIsLoading(true);

    const userMessage: Message = {
      role: "user",
      content: messageToSend,
      timestamp: new Date(),
    };

    // Initialize streaming assistant message
    const streamingMessage: Message = {
      role: "assistant",
      content: "",
      timestamp: new Date(),
      toolCalls: [],
      isStreaming: true,
      isThinking: false,
    };

    // Add both user message and streaming placeholder in one update
    setMessages((prev) => [...prev, userMessage, streamingMessage]);

    // Store the index of the streaming message to ensure we always update the same one
    const streamingMessageIndexRef = { current: -1 };

    try {
      // Connect to WebSocket
      const ws = new WebSocket(`ws://localhost:8000/api/v1/agents/${selectedAgentId}/stream`);

      ws.onopen = () => {
        console.log("WebSocket connected");
        // Send message to backend
        ws.send(JSON.stringify({
          message: messageToSend,
          thread_id: threadId
        }));
      };

      ws.onmessage = (event) => {
        try {
          const streamEvent = JSON.parse(event.data);

          setMessages((prev) => {
            const updated = [...prev];

            // Find the streaming assistant message index (last assistant message)
            let msgIndex = streamingMessageIndexRef.current;
            if (msgIndex === -1) {
              // First time - find the last assistant message
              for (let i = updated.length - 1; i >= 0; i--) {
                if (updated[i].role === "assistant") {
                  msgIndex = i;
                  streamingMessageIndexRef.current = i;
                  break;
                }
              }
            }

            if (msgIndex === -1 || !updated[msgIndex] || updated[msgIndex].role !== "assistant") {
              console.warn("⚠️ No assistant message found at index", msgIndex);
              return prev;
            }

            const currentMsg = { ...updated[msgIndex] };

            switch (streamEvent.type) {
              case 'agent_thinking':
                console.log(`[${msgIndex}] Setting thinking indicator`);
                currentMsg.isThinking = true;
                break;

              case 'tool_call_start':
                console.log(`[${msgIndex}] Adding tool call: ${streamEvent.tool_name}`);
                const newToolCall: ToolCall = {
                  id: streamEvent.tool_id,
                  name: streamEvent.tool_name,
                  args: streamEvent.arguments,
                  status: 'running'
                };
                currentMsg.toolCalls = [...(currentMsg.toolCalls || []), newToolCall];
                currentMsg.isThinking = false;
                break;

              case 'tool_call_end':
                console.log(`[${msgIndex}] Tool call completed: ${streamEvent.tool_id}`);
                console.log(`[${msgIndex}] Current tool calls:`, currentMsg.toolCalls);

                // Create new array with updated tool - ensures React detects the change
                currentMsg.toolCalls = (currentMsg.toolCalls || []).map(tc => {
                  if (tc.id === streamEvent.tool_id) {
                    console.log(`[${msgIndex}] ✅ Updating tool ${tc.name} status: running → complete`);
                    // Create new object to ensure React detects change
                    return {
                      ...tc,
                      result: streamEvent.result,
                      duration: streamEvent.duration_ms,
                      status: 'complete' as const
                    };
                  }
                  return tc;
                });
                console.log(`[${msgIndex}] Updated tool calls:`, currentMsg.toolCalls);
                break;

              case 'llm_token':
                console.log(`[${msgIndex}] Adding content token (total: ${currentMsg.content.length + (streamEvent.content || '').length} chars)`);
                currentMsg.content += streamEvent.content || '';
                currentMsg.isThinking = false;
                break;

              case 'agent_complete':
                console.log(`[${msgIndex}] Agent complete - tool calls: ${currentMsg.toolCalls?.length || 0}, content: ${currentMsg.content.length} chars`);
                currentMsg.isStreaming = false;
                currentMsg.isThinking = false;
                break;

              case 'error':
                console.log(`[${msgIndex}] Error received`);
                currentMsg.content = `Error: ${streamEvent.error}`;
                currentMsg.isStreaming = false;
                currentMsg.isThinking = false;
                break;
            }

            updated[msgIndex] = currentMsg;
            return updated;
          });
        } catch (error) {
          console.error("Error parsing stream event:", error);
        }
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        toast({
          title: "Connection Error",
          description: "Failed to connect to agent stream",
          variant: "destructive",
        });
        setIsLoading(false);
      };

      ws.onclose = () => {
        console.log("WebSocket closed");
        setIsLoading(false);
      };

    } catch (error: any) {
      console.error("Error sending message:", error);
      toast({
        title: "Error",
        description: error?.message || "Failed to send message",
        variant: "destructive",
      });
      setIsLoading(false);
      // Remove the streaming placeholder on error
      setMessages((prev) => prev.slice(0, -1));
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const selectedAgent = agents.find((a) => a.agent_id === selectedAgentId);

  return (
    <div className="flex flex-col h-[calc(100vh-theme(spacing.16))] bg-background relative">
      {/* Minimal Header with Agent Selector */}
      <div className="w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 z-10 sticky top-0">
        <div className="max-w-3xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Select value={selectedAgentId} onValueChange={setSelectedAgentId}>
              <SelectTrigger className="w-auto min-w-[200px] max-w-none h-auto py-2 [&>span]:line-clamp-none border-none shadow-none bg-transparent hover:bg-muted/50 focus:ring-0 font-medium text-lg px-2 transition-colors">
                <SelectValue placeholder="Select Agent" />
              </SelectTrigger>
              <SelectContent>
                {agents.length === 0 ? (
                  <SelectItem value="none" disabled>No agents available</SelectItem>
                ) : (
                  agents.map((agent) => (
                    <SelectItem key={agent.agent_id} value={agent.agent_id}>
                      <div className="flex items-center gap-2">
                        <span>{agent.name}</span>
                        <span className="text-xs text-muted-foreground ml-2">({agent.agent_type})</span>
                      </div>
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
            {selectedAgent && (
              <span className="text-xs text-muted-foreground border px-2 py-0.5 rounded-full bg-muted/30">
                {selectedAgent.llm_model}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={handleClearConversation} title="Clear Conversation" className="text-muted-foreground hover:text-foreground">
              <RefreshCw className={cn("w-4 h-4", isRefreshing && "animate-spin")} />
            </Button>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <ScrollArea className="flex-1" ref={scrollRef}>
        <div className="max-w-3xl mx-auto px-4 py-8 min-h-full flex flex-col">
          {messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center space-y-6 opacity-0 animate-in fade-in duration-500 slide-in-from-bottom-4 fill-mode-forwards" style={{ animationDelay: '0.2s' }}>
              <div className="w-24 h-24 rounded-3xl bg-primary/5 flex items-center justify-center shadow-inner">
                <Sparkles className="w-10 h-10 text-primary/40" />
              </div>
              <div className="space-y-2 max-w-md">
                <h2 className="text-2xl font-semibold tracking-tight text-foreground">
                  {selectedAgent ? `Chat with ${selectedAgent.name}` : "Select an Agent"}
                </h2>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {selectedAgent
                    ? "I'm ready to help you with your tasks. Ask me anything!"
                    : "Choose an agent from the top menu to start a conversation."}
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-8 pb-32">
              {messages.map((message, index) => (
                <div key={index} className={cn(
                  "flex gap-4 w-full group",
                  message.role === "user" ? "justify-end" : "justify-start"
                )}>
                  {/* Avatar for Assistant */}
                  {message.role === "assistant" && (
                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
                      <Bot className="w-5 h-5 text-primary" />
                    </div>
                  )}

                  <div className={cn(
                    "flex flex-col max-w-[85%]",
                    message.role === "user" ? "items-end" : "items-start"
                  )}>
                    {/* Tool Logs */}
                    {(message.toolCalls || message.isThinking) && (
                      <div className="mb-3 ml-1 w-full">
                        <ToolCallLog toolCalls={message.toolCalls || []} isThinking={message.isThinking} />
                      </div>
                    )}

                    {/* Content */}
                    {(message.content || message.role === "user") && (
                      <div className={cn(
                        "relative px-5 py-3.5 text-sm leading-relaxed shadow-sm transition-all",
                        message.role === "user"
                          ? "bg-primary text-primary-foreground rounded-2xl rounded-tr-sm"
                          : "bg-muted/50 text-foreground rounded-2xl rounded-tl-sm border border-border/50 hover:bg-muted/70"
                      )}>
                        <div className="whitespace-pre-wrap">{message.content}</div>
                        {message.isStreaming && (
                          <span className="inline-block w-1.5 h-4 bg-current animate-pulse ml-1 align-middle" />
                        )}
                      </div>
                    )}

                    {/* Timestamp */}
                    <span className={cn(
                      "text-[10px] text-muted-foreground/40 mt-1 px-1 opacity-0 group-hover:opacity-100 transition-opacity",
                      message.role === "user" ? "text-right" : "text-left"
                    )}>
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>

                  {/* Avatar for User */}
                  {message.role === "user" && (
                    <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center flex-shrink-0 mt-1 shadow-sm">
                      <User className="w-4 h-4 text-secondary-foreground" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Floating Input Area */}
      <div className="absolute bottom-6 left-0 right-0 px-4 z-20 pointer-events-none">
        <div className="max-w-3xl mx-auto pointer-events-auto">
          <div className="relative flex items-center gap-2 p-2 rounded-full border bg-background/80 backdrop-blur-xl shadow-2xl ring-1 ring-black/5 dark:ring-white/10 transition-all focus-within:ring-2 focus-within:ring-primary/20">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={selectedAgentId ? "Type a message..." : "Select an agent to start..."}
              className="flex-1 border-none shadow-none bg-transparent focus-visible:ring-0 px-4 py-6 h-12 text-base placeholder:text-muted-foreground/50"
              disabled={!selectedAgentId || isLoading}
            />
            <Button
              size="icon"
              className={cn(
                "rounded-full h-10 w-10 shrink-0 mr-1 transition-all duration-200",
                input.trim() ? "opacity-100 scale-100" : "opacity-50 scale-95"
              )}
              onClick={handleSend}
              disabled={!selectedAgentId || !input.trim() || isLoading}
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowUp className="w-5 h-5" />}
            </Button>
          </div>
          <div className="text-center mt-3">
            <p className="text-[10px] text-muted-foreground/40 font-medium">
              AI can make mistakes. Check important info.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}