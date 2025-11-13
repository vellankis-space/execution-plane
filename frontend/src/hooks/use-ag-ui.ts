/**
 * AG-UI Protocol Hook
 * Provides utilities for communicating with agents using AG-UI Protocol
 */
import { useState, useCallback, useRef, useEffect } from 'react';

export enum AGUIEventType {
  RUN_STARTED = 'run_started',
  RUN_FINISHED = 'run_finished',
  RUN_CANCELLED = 'run_cancelled',
  TEXT_MESSAGE_CONTENT = 'text_message_content',
  ATTACHMENT_MESSAGE_CONTENT = 'attachment_message_content',
  TOOL_CALL_STARTED = 'tool_call_started',
  TOOL_CALL_FINISHED = 'tool_call_finished',
  TOOL_CALL_ERROR = 'tool_call_error',
  STATE_UPDATE = 'state_update',
  FRONTEND_ACTION_REQUEST = 'frontend_action_request',
  HUMAN_INPUT_REQUEST = 'human_input_request',
  STREAM_START = 'stream_start',
  STREAM_CHUNK = 'stream_chunk',
  STREAM_END = 'stream_end',
  ERROR = 'error',
  METADATA = 'metadata',
}

export interface AGUIMessage {
  event: AGUIEventType;
  run_id?: string;
  session_id?: string;
  timestamp?: string;
  data?: any;
  metadata?: any;
}

export interface UseAGUIOptions {
  agentId: string;
  sessionId?: string;
  onMessage?: (message: AGUIMessage) => void;
  onError?: (error: Error) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

export function useAGUI(options: UseAGUIOptions) {
  const { agentId, sessionId, onMessage, onError, onConnect, onDisconnect } = options;
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentRunId, setCurrentRunId] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = `ws://localhost:8000/api/v1/agents/${agentId}/stream`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setIsConnected(true);
      reconnectAttempts.current = 0;
      onConnect?.();
      
      // Send initial message if sessionId provided
      if (sessionId) {
        ws.send(JSON.stringify({
          session_id: sessionId,
          message: ''
        }));
      }
    };

    ws.onmessage = (event) => {
      try {
        const message: AGUIMessage = JSON.parse(event.data);
        
        // Handle run lifecycle
        if (message.event === AGUIEventType.RUN_STARTED) {
          setCurrentRunId(message.run_id || null);
          setIsLoading(true);
        } else if (message.event === AGUIEventType.RUN_FINISHED) {
          setIsLoading(false);
        } else if (message.event === AGUIEventType.ERROR) {
          setIsLoading(false);
          onError?.(new Error(message.data?.error || 'Unknown error'));
        }
        
        onMessage?.(message);
      } catch (error) {
        console.error('Error parsing AG-UI message:', error);
        onError?.(error as Error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      onError?.(new Error('WebSocket connection error'));
    };

    ws.onclose = () => {
      setIsConnected(false);
      setIsLoading(false);
      onDisconnect?.();
      
      // Attempt to reconnect
      if (reconnectAttempts.current < maxReconnectAttempts) {
        reconnectAttempts.current++;
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 1000 * reconnectAttempts.current); // Exponential backoff
      }
    };

    wsRef.current = ws;
  }, [agentId, sessionId, onMessage, onError, onConnect, onDisconnect]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setIsLoading(false);
  }, []);

  const sendMessage = useCallback((message: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        message,
        session_id: sessionId,
      }));
    } else {
      // Connect first if not connected
      connect();
      // Wait a bit for connection, then send
      setTimeout(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({
            message,
            session_id: sessionId,
          }));
        }
      }, 500);
    }
  }, [sessionId, connect]);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    isLoading,
    currentRunId,
    connect,
    disconnect,
    sendMessage,
  };
}

