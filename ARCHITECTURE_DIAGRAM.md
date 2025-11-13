# Architecture Diagrams

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                    │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    React Frontend (TypeScript)                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │ Agent        │  │ Workflow     │  │ Monitoring   │          │   │
│  │  │ Builder      │  │ Builder      │  │ Dashboard    │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │ Agent List   │  │ Workflow     │  │ Analytics    │          │   │
│  │  │ & Chat       │  │ Execution    │  │ & Reports    │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                    HTTP/REST │ WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          API LAYER                                       │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Backend (Python)                       │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │ Agent API    │  │ Workflow API │  │ Monitoring   │          │   │
│  │  │ /api/v1/     │  │ /api/v1/     │  │ API          │          │   │
│  │  │ agents/      │  │ workflows/   │  │ /api/v1/     │          │   │
│  │  └──────────────┘  └──────────────┘  │ monitoring/  │          │   │
│  │  ┌──────────────┐  ┌──────────────┐  └──────────────┘          │   │
│  │  │ Knowledge    │  │ Tools API   │  ┌──────────────┐          │   │
│  │  │ Base API     │  │ /api/v1/    │  │ Enhanced     │          │   │
│  │  │ /api/v1/kb/  │  │ agents/     │  │ Monitoring   │          │   │
│  │  └──────────────┘  │ tools/      │  │ API          │          │   │
│  │                     └──────────────┘  └──────────────┘          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       SERVICE LAYER                                      │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │ Agent        │  │ Workflow     │  │ Monitoring   │          │   │
│  │  │ Service      │  │ Service      │  │ Service      │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │ Knowledge    │  │ Tools        │  │ Memory       │          │   │
│  │  │ Base Service │  │ Service      │  │ Service      │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │ SQLite/      │  │ Qdrant      │  │ External     │          │   │
│  │  │ PostgreSQL   │  │ (Vector DB)  │  │ Services     │          │   │
│  │  │              │  │             │  │              │          │   │
│  │  │ - Agents     │  │ - Memory    │  │ - LLM APIs   │          │   │
│  │  │ - Workflows  │  │ - Embeddings│  │ - Tools APIs │          │   │
│  │  │ - Executions │  │             │  │              │          │   │
│  │  │ - Logs       │  │             │  │              │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Agent Execution Flow

```
┌─────────────┐
│   User      │
│   Input     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Agent Service  │
│  - Get Agent    │
│  - Decrypt Key  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  PII Filtering  │
│  (if enabled)   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Memory Service │
│  - Search       │
│  - Retrieve     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Knowledge Base  │
│  - Query        │
│  - Retrieve     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Create Agent   │
│  - LLM Init     │
│  - Tools Load   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  LangGraph      │
│  Execution      │
│  - ReAct        │
│  - Plan-Execute │
│  - Reflection   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Tool Execution │
│  (if needed)    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  PII Filtering   │
│  (output)       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Store Memory   │
│  (if enabled)   │
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│   Response  │
└─────────────┘
```

## Workflow Execution Flow

```
┌─────────────┐
│  Workflow   │
│  Execution  │
│  Request    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Create Execution│
│ Record          │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Parse Workflow  │
│ Definition      │
│ - Steps         │
│ - Dependencies  │
│ - Conditions    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Find Starting   │
│ Steps           │
│ (no deps)       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Execute Ready   │
│ Steps in        │
│ Parallel        │
│                 │
│  ┌───┐  ┌───┐  │
│  │ S1│  │ S2│  │
│  └───┘  └───┘  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Check           │
│ Dependencies    │
│ & Conditions    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ More Steps?     │
│  Yes ──┐        │
│  No  ──┼───┐    │
└──────┘    │    │
            │    │
            ▼    │
┌─────────────────┐│
│ Execute Next    ││
│ Batch           ││
└─────────────────┘│
            │      │
            └──────┘
       │
       ▼
┌─────────────────┐
│ Update          │
│ Execution       │
│ Status          │
│ - Metrics       │
│ - Results       │
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│   Return    │
│   Results   │
└─────────────┘
```

## Data Model Relationships

```
┌─────────────┐
│   Agents     │
│             │
│ - agent_id  │
│ - name      │
│ - config    │
└──────┬──────┘
       │
       │ 1:N
       │
       ▼
┌─────────────┐
│  Workflows  │
│             │
│ - workflow_ │
│   id        │
│ - steps[]   │
│ - deps      │
└──────┬──────┘
       │
       │ 1:N
       │
       ▼
┌─────────────┐      ┌─────────────┐
│ Workflow    │ 1:N  │ Step        │
│ Executions  │◄─────┤ Executions  │
│             │      │             │
│ - exec_id   │      │ - step_id   │
│ - status    │      │ - status    │
│ - metrics   │      │ - metrics   │
└──────┬──────┘      └─────────────┘
       │
       │ 1:N
       │
       ▼
┌─────────────┐
│ Execution   │
│ Logs        │
│             │
│ - log_id    │
│ - level     │
│ - message   │
└─────────────┘

┌─────────────┐
│ Knowledge   │
│ Bases       │
│             │
│ - kb_id     │
│ - agent_id  │
└──────┬──────┘
       │
       │ 1:N
       │
       ▼
┌─────────────┐
│ Documents   │
│             │
│ - doc_id    │
│ - content   │
│ - chunks    │
└─────────────┘
```

## Monitoring Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Monitoring Components                      │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Execution    │  │ Resource     │  │ Analytics    │ │
│  │ Tracking     │  │ Monitoring   │  │ Engine      │ │
│  │              │  │              │  │             │ │
│  │ - Status     │  │ - CPU        │  │ - Bottlenecks│ │
│  │ - Timing     │  │ - Memory     │  │ - Trends     │ │
│  │ - Results    │  │ - I/O        │  │ - Predictions│ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Logging      │  │ Alerting     │  │ Reporting    │ │
│  │ System       │  │ System        │  │ System       │ │
│  │              │  │              │  │             │ │
│  │ - Logs       │  │ - Rules       │  │ - Reports   │ │
│  │ - Levels     │  │ - Channels    │  │ - Dashboards│ │
│  │ - Metadata   │  │ - History     │  │ - Exports   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │   Database   │
                    │   Storage    │
                    └──────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Security Layers                             │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │  API Key Encryption                                │ │
│  │  - Fernet Encryption                               │ │
│  │  - Secure Storage                                 │ │
│  │  - Decrypt on Use                                 │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │  PII Filtering Middleware                         │ │
│  │  - Input Filtering                                │ │
│  │  - Output Filtering                               │ │
│  │  - Tool Result Filtering                          │ │
│  │  - Multiple Strategies                            │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Access Control (Future)                          │ │
│  │  - Authentication                                 │ │
│  │  - Authorization (RBAC)                            │ │
│  │  - Audit Logging                                  │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Tool Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Tools Service                               │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Search Tools │  │ API Tools    │  │ Browser Tools│ │
│  │              │  │              │  │              │ │
│  │ - DuckDuckGo │  │ - GitHub     │  │ - PlayWright │ │
│  │ - Brave      │  │ - Gmail      │  │              │ │
│  │ - Wikipedia  │  │ - FireCrawl  │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Research     │  │ Database     │  │ Custom       │ │
│  │ Tools        │  │ Tools        │  │ Tools        │ │
│  │              │  │              │  │              │ │
│  │ - Arxiv      │  │ - MCP DB     │  │ - Extensible │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Tool Configuration Management                    │ │
│  │  - API Key Management                            │ │
│  │  - Tool-specific Settings                        │ │
│  │  - Validation                                    │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

**Note**: These diagrams represent the current architecture. Future enhancements will add:
- User management layer
- Scheduling system
- Queue management
- Real-time dashboards
- Microservices (optional)

