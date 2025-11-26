import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot, User, Loader2, Trash2, RefreshCw } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { ToolCallLog } from "@/components/ToolCallLog";

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
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
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

  const handleRefreshAgents = async () => {
    setIsRefreshing(true);
    await fetchAgents();
    setIsRefreshing(false);
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
    <div className="min-h-screen w-full bg-background">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="flex flex-col gap-6">
          {/* Header */}
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Agent Chat</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Interact with your agents in real-time
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Panel - Agent List */}
            <div className="lg:col-span-1">
              <Card className="p-5">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">Your Agents</h2>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleRefreshAgents}
                    disabled={isRefreshing}
                  >
                    <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
                  </Button>
                </div>

                {agents.length === 0 ? (
                  <div className="text-center py-8">
                    <Bot className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground text-sm">
                      No agents created yet
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-[500px] overflow-y-auto">
                    {agents.map((agent) => (
                      <div
                        key={agent.agent_id}
                        className={`p-4 rounded-lg border cursor-pointer transition-all ${selectedAgentId === agent.agent_id
                          ? "border-primary bg-primary/5"
                          : "border-border hover:bg-muted/50"
                          }`}
                        onClick={() => setSelectedAgentId(agent.agent_id)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            <h3 className="font-medium text-base truncate">
                              {agent.name}
                            </h3>
                            <p className="text-xs text-muted-foreground capitalize mt-1 truncate">
                              {agent.agent_type}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1 truncate">
                              {agent.llm_provider} / {agent.llm_model}
                            </p>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteAgent(agent.agent_id, agent.name);
                            }}
                            className="text-muted-foreground hover:text-destructive hover:bg-destructive/10 h-8 w-8 ml-2 flex-shrink-0"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            </div>

            {/* Right Panel - Chat Interface */}
            <div className="lg:col-span-2 flex flex-col gap-6">
              {/* Agent Selection - Mobile View */}
              <Card className="p-4 lg:hidden">
                <div className="flex items-center gap-4">
                  <div className="flex-1">
                    <label className="text-xs text-muted-foreground mb-2 block">
                      Select Agent
                    </label>
                    <Select value={selectedAgentId} onValueChange={setSelectedAgentId}>
                      <SelectTrigger className="h-10 bg-background">
                        <SelectValue placeholder="Choose an agent" />
                      </SelectTrigger>
                      <SelectContent>
                        {agents.length === 0 ? (
                          <SelectItem value="none" disabled>
                            No agents available
                          </SelectItem>
                        ) : (
                          agents.map((agent) => (
                            <SelectItem key={agent.agent_id} value={agent.agent_id}>
                              {agent.name} ({agent.agent_type})
                            </SelectItem>
                          ))
                        )}
                      </SelectContent>
                    </Select>
                  </div>
                  {selectedAgent && (
                    <div className="text-xs text-muted-foreground pt-6">
                      Model: {selectedAgent.llm_model}
                    </div>
                  )}
                </div>
              </Card>

              {/* Chat Interface */}
              <Card className="flex flex-col h-[600px]">
                {/* Messages */}
                <ScrollArea className="flex-1 p-4" ref={scrollRef}>
                  {messages.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center">
                      <Bot className="w-12 h-12 text-muted-foreground mb-4" />
                      <p className="text-muted-foreground">
                        {selectedAgentId
                          ? "Start a conversation with your agent"
                          : "Select an agent to begin"}
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {messages.map((message, index) => (
                        <div
                          key={index}
                          className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"
                            }`}
                        >
                          {message.role === "assistant" && (
                            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                              <Bot className="w-4 h-4 text-primary-foreground" />
                            </div>
                          )}
                          <div className={`max-w-[80%] space-y-2 ${message.role === "user" ? "flex flex-col items-end" : ""}`}>
                            {/* Tool Call Log */}
                            {(message.toolCalls || message.isThinking) && (
                              <ToolCallLog
                                toolCalls={message.toolCalls || []}
                                isThinking={message.isThinking}
                              />
                            )}

                            {/* Message Content */}
                            {(message.content || message.role === "user") && (
                              <div
                                className={`rounded-lg px-4 py-2 ${message.role === "user"
                                  ? "bg-primary text-primary-foreground"
                                  : "bg-muted text-foreground"
                                  }`}
                              >
                                <p className="text-sm whitespace-pre-wrap">
                                  {message.content}
                                  {message.isStreaming && (
                                    <span className="inline-block w-1.5 h-4 bg-current animate-pulse ml-1 align-middle"></span>
                                  )}
                                </p>
                                <p className="text-xs opacity-70 mt-1">
                                  {message.timestamp.toLocaleTimeString()}
                                </p>
                              </div>
                            )}
                          </div>
                          {message.role === "user" && (
                            <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
                              <User className="w-4 h-4 text-secondary-foreground" />
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>

                {/* Input */}
                <div className="border-t border-border p-4">
                  <div className="flex gap-2">
                    <Input
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder={
                        selectedAgentId
                          ? "Type your message..."
                          : "Select an agent first"
                      }
                      disabled={!selectedAgentId || isLoading}
                      className="flex-1"
                    />
                    <Button
                      onClick={handleSend}
                      disabled={!selectedAgentId || !input.trim() || isLoading}
                      size="icon"
                    >
                      <Send className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}