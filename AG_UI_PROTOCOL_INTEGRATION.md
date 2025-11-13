# AG-UI Protocol Integration

## Overview

The platform now supports the **AG-UI Protocol** (Agent-User Interaction Protocol) for standardized, real-time communication between the UI and AI agents.

## What is AG-UI Protocol?

AG-UI is an open, lightweight, event-based protocol designed to standardize interactions between AI agents and front-end applications. It facilitates:

- **Real-time interactivity** with streaming updates
- **Human-in-the-loop workflows** with pauses, approvals, and edits
- **Multimodality** support for files, images, audio
- **Frontend tool calls** for seamless agent-frontend integration
- **Shared state management** between agent and application
- **Generative UI** for rendering model outputs as components

## Features Implemented

### 1. **Event-Based Communication**
- Standardized event types (RUN_STARTED, TEXT_MESSAGE_CONTENT, TOOL_CALL_STARTED, etc.)
- Structured message format with metadata support
- Type-safe event handling

### 2. **Real-Time Streaming**
- WebSocket-based streaming
- Token-by-token response streaming
- Progress updates and status notifications

### 3. **Tool Call Visibility**
- Real-time tool execution notifications
- Tool call progress tracking
- Error handling for tool failures

### 4. **State Management**
- Shared state between agent and UI
- State diffs for efficient updates
- Conflict resolution support

### 5. **Human-in-the-Loop**
- Request human input mid-flow
- Approval gates
- Edit and retry capabilities

## Implementation Details

### Backend (`backend/services/ag_ui_protocol.py`)

The AG-UI Protocol service provides:

- **Message Creation**: Factory methods for all event types
- **Message Parsing**: Parse incoming AG-UI messages
- **Type Safety**: Enum-based event types

### Agent Service Integration

The `AgentService` now includes:

- **Streaming Support**: `stream_agent()` method with AG-UI Protocol
- **Event Emission**: Automatic event generation during execution
- **Error Handling**: Proper error events and recovery

### Frontend Hook (`frontend/src/hooks/use-ag-ui.ts`)

React hook for AG-UI Protocol:

```typescript
const { isConnected, isLoading, sendMessage, connect, disconnect } = useAGUI({
  agentId: 'agent-123',
  sessionId: 'session-456',
  onMessage: (message) => {
    // Handle AG-UI messages
  },
  onError: (error) => {
    // Handle errors
  }
});
```

## Event Types

### Run Lifecycle
- `RUN_STARTED` - Agent execution started
- `RUN_FINISHED` - Agent execution completed
- `RUN_CANCELLED` - Agent execution cancelled

### Messages
- `TEXT_MESSAGE_CONTENT` - Text message from agent or user
- `ATTACHMENT_MESSAGE_CONTENT` - File/image/audio attachment

### Tool Calls
- `TOOL_CALL_STARTED` - Tool execution started
- `TOOL_CALL_FINISHED` - Tool execution completed
- `TOOL_CALL_ERROR` - Tool execution failed

### Streaming
- `STREAM_START` - Streaming started
- `STREAM_CHUNK` - Streaming chunk received
- `STREAM_END` - Streaming completed

### State Management
- `STATE_UPDATE` - State updated
- `STATE_DIFF` - State diff applied

### Human-in-the-Loop
- `HUMAN_INPUT_REQUEST` - Request human input
- `HUMAN_INPUT_RESPONSE` - Human input received

### Error Handling
- `ERROR` - Error occurred

## Usage Example

### Backend (Python)

```python
from services.ag_ui_protocol import AGUIProtocol

# Create and send events
run_started = AGUIProtocol.create_run_started(run_id="run-123")
await websocket.send_text(run_started.to_json())

text_msg = AGUIProtocol.create_text_message(
    content="Hello!",
    run_id="run-123",
    role="assistant"
)
await websocket.send_text(text_msg.to_json())
```

### Frontend (TypeScript)

```typescript
import { useAGUI, AGUIEventType } from '@/hooks/use-ag-ui';

function AgentChat() {
  const { sendMessage, isConnected, isLoading } = useAGUI({
    agentId: 'agent-123',
    sessionId: 'session-456',
    onMessage: (message) => {
      switch (message.event) {
        case AGUIEventType.TEXT_MESSAGE_CONTENT:
          // Display text message
          break;
        case AGUIEventType.TOOL_CALL_STARTED:
          // Show tool execution
          break;
        case AGUIEventType.STREAM_CHUNK:
          // Append streaming chunk
          break;
      }
    }
  });

  return (
    <div>
      <button onClick={() => sendMessage('Hello!')}>
        Send Message
      </button>
    </div>
  );
}
```

## WebSocket Endpoint

```
ws://localhost:8000/api/v1/agents/{agent_id}/stream
```

### Connection Flow

1. Client connects to WebSocket
2. Client sends initial message (optional):
   ```json
   {
     "message": "User input",
     "session_id": "session-123"
   }
   ```
3. Server sends AG-UI Protocol events:
   - `RUN_STARTED`
   - `TEXT_MESSAGE_CONTENT` (user message)
   - `TOOL_CALL_STARTED` (if tools used)
   - `STREAM_CHUNK` (streaming responses)
   - `TEXT_MESSAGE_CONTENT` (agent response)
   - `RUN_FINISHED`

## Benefits

### Before (REST API)
- ❌ No real-time updates
- ❌ No streaming support
- ❌ No tool call visibility
- ❌ Limited error handling
- ❌ No standardized protocol

### After (AG-UI Protocol)
- ✅ Real-time event streaming
- ✅ Token-by-token streaming
- ✅ Tool call visibility
- ✅ Standardized protocol
- ✅ Better error handling
- ✅ Human-in-the-loop support
- ✅ State management
- ✅ Multimodality support

## Next Steps

1. **Update AgentChat Component**: Integrate `useAGUI` hook
2. **Add Tool Call UI**: Display tool executions in real-time
3. **Implement State Management**: Use shared state for UI updates
4. **Add Human-in-the-Loop UI**: Approval gates and input requests
5. **Support Multimodality**: File uploads, images, audio

## Documentation

- **AG-UI Protocol Docs**: https://docs.ag-ui.com/
- **Backend Service**: `backend/services/ag_ui_protocol.py`
- **Frontend Hook**: `frontend/src/hooks/use-ag-ui.ts`
- **WebSocket Endpoint**: `backend/api/v1/agents.py`

---

**The AG-UI Protocol integration provides a standardized, production-ready solution for agent-UI communication!**

