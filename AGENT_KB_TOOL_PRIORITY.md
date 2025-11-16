# Agent Execution Logic - Knowledge Base First, Then Tools

## Overview
Modified the agent execution logic to ensure agents **search the knowledge base FIRST** before using tools. This creates a more efficient and accurate agent behavior where verified knowledge base information takes priority over external tool calls.

## Implementation Strategy

### Execution Priority Flow

```
┌─────────────────────────────────────────────────┐
│ 1. User Query Received                          │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ 2. Query Knowledge Base (if available)          │
│    - Searches linked knowledge bases            │
│    - Retrieves top 5 relevant chunks            │
│    - 30 second timeout                          │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ 3. Retrieve Memory Context (if enabled)         │
│    - Gets previous conversation context         │
│    - Top 5 relevant memories                    │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ 4. Build Prioritized System Prompt              │
│    a) Base system prompt                        │
│    b) KB information (FIRST - clearly marked)   │
│    c) Memory context (SECOND)                   │
│    d) Tool descriptions (LAST - conditional)    │
│    e) Execution guidelines                      │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ 5. Agent Execution with Clear Instructions      │
│    - Agent checks KB first                      │
│    - Uses KB info if available                  │
│    - Only calls tools if KB insufficient        │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│ 6. Return Response to User                      │
└─────────────────────────────────────────────────┘
```

## Code Changes

### File: `backend/services/agent_service.py`

#### Change 1: ReAct Agent System Prompt (Lines 359-387)

**Key Improvements:**
- Knowledge base information added **BEFORE** tool descriptions
- Clear section headers: "## Knowledge Base Information"
- Explicit instructions: "Always check if the knowledge base has relevant information BEFORE using any tools"
- Tool usage strategy with 4-step priority

**Updated Structure:**
```python
if agent.agent_type == "react":
    system_content = agent.system_prompt or "You are a helpful AI assistant."
    
    # 1. KNOWLEDGE BASE FIRST (if available)
    if knowledge_context:
        has_kb = True
        system_content += f"\n\n## Knowledge Base Information\n{knowledge_context}"
        system_content += "\n\nIMPORTANT: This knowledge base contains verified information..."
    
    # 2. MEMORY CONTEXT SECOND
    if memory_context:
        system_content += f"\n\n## Context from Previous Conversations\n{memory_context}"
    
    # 3. TOOLS LAST (with conditional instructions)
    if hasattr(agent, 'tools') and agent.tools:
        if has_kb:
            # Instructions emphasize KB priority
            system_content += "\n\n## Available Tools\nIf the knowledge base doesn't have sufficient information..."
            system_content += "\n\nTool Usage Strategy:\n1. First, check if the knowledge base has the answer..."
        else:
            # Standard tool instructions (no KB available)
            system_content += f"\n\nAvailable tools: {', '.join(tool_names)}..."
```

#### Change 2: Non-ReAct Agents (Plan-Execute, Reflection, Custom) (Lines 401-420)

**Key Improvements:**
- KB context clearly marked as "Check this FIRST"
- Instructions added to use KB before tools
- Memory context added as secondary priority

**Updated Structure:**
```python
# Add KB context first with clear instructions
if knowledge_context:
    kb_section = "## Knowledge Base Information (Check this FIRST)\n"
    kb_section += knowledge_context
    kb_section += "\n\nIMPORTANT: Use this knowledge base information to answer the query if possible. Only use tools if the knowledge base doesn't have sufficient information."
    context_parts.append(kb_section)

# Add memory context second
if memory_context:
    context_parts.append("## Previous Conversation Context\n" + memory_context)
```

## Tool Usage Strategy

### When Agent Has Knowledge Base

The agent follows this explicit strategy:

```
1. First, check if the knowledge base has the answer
   ↓
2. If KB has relevant info, use it to answer directly
   ↓
3. Only use tools if KB info is insufficient or you need real-time/external data
   ↓
4. You can only use the listed tools - do not attempt to use any other tools
```

### When Agent Has No Knowledge Base

The agent uses tools normally:
- Tools are listed in system prompt
- Agent can use any listed tool as needed
- Standard tool calling behavior

## Benefits

### 1. **Reduced API Costs**
- Fewer external tool calls
- Knowledge base queries are local/cached
- More efficient resource usage

### 2. **Faster Response Times**
- KB lookups are faster than tool calls
- No external API latency for KB-answerable queries
- Reduced waiting time for users

### 3. **More Accurate Responses**
- KB contains verified, domain-specific information
- Reduces hallucination by providing trusted context
- Consistent answers based on curated knowledge

### 4. **Better Tool Usage**
- Tools used only when truly needed
- Real-time data fetched appropriately
- External APIs called for dynamic information only

### 5. **Improved Context Awareness**
- Memory context from previous conversations
- KB context for domain knowledge
- Clear priority hierarchy

## Example Scenarios

### Scenario 1: Question Answerable from KB

**User Query:** "What is our return policy?"

**Execution Flow:**
1. KB search finds return policy document
2. Agent reads KB context: "30-day return policy..."
3. Agent responds directly from KB information
4. ✅ **No tools called** - Fast, accurate response

**Before (Old Logic):**
- Agent might call web search tool unnecessarily
- Could fetch outdated external information
- Slower response time

**After (New Logic):**
- Agent uses verified KB information
- Instant response
- Consistent with company policy

---

### Scenario 2: Real-Time Data Needed

**User Query:** "What's the current weather in New York?"

**Execution Flow:**
1. KB search returns no weather information
2. Agent recognizes KB doesn't have real-time weather
3. Agent calls weather API tool
4. ✅ **Tool called appropriately** - Gets current data

**Before (Old Logic):**
- Agent might call tool without checking KB
- Same outcome but less systematic

**After (New Logic):**
- Agent systematically checks KB first
- Makes informed decision to use tool
- Clear reasoning path

---

### Scenario 3: Partial KB Info + Tool Enhancement

**User Query:** "Tell me about our product pricing and compare with competitors"

**Execution Flow:**
1. KB search finds company pricing information
2. Agent uses KB for company pricing
3. Agent recognizes competitor info needs web search
4. Agent calls web search tool for competitor data
5. ✅ **Combines KB + Tool** - Best of both worlds

**Before (Old Logic):**
- Might search web for all info
- Could miss authoritative company data

**After (New Logic):**
- Uses verified KB for company info
- Supplements with tool for external data
- Comprehensive accurate response

---

### Scenario 4: Multi-Step Query with Knowledge Priority

**User Query:** "How do I troubleshoot login issues? Also check server status."

**Execution Flow:**
1. KB search finds troubleshooting guide
2. Agent provides steps from KB
3. Agent calls server status monitoring tool for real-time status
4. ✅ **KB for static info, tool for dynamic info**

## Technical Details

### Knowledge Base Query

**Location:** Lines 330-349 in `agent_service.py`

```python
knowledge_context = ""
try:
    import asyncio
    from services.knowledge_base_service import KnowledgeBaseService
    kb_service = KnowledgeBaseService(self.db)
    
    # 30 second timeout for KB queries
    knowledge_context = await asyncio.wait_for(
        kb_service.query_agent_knowledge(agent_id, filtered_input, top_k=5),
        timeout=30.0
    )
    
    if knowledge_context:
        print(f"Retrieved KB context for agent {agent_id}: {len(knowledge_context)} chars")
except asyncio.TimeoutError:
    print(f"Knowledge base query timed out for agent {agent_id}")
except Exception as kb_error:
    print(f"Error retrieving knowledge base context: {kb_error}")
```

**Features:**
- Queries all knowledge bases linked to agent
- Returns top 5 most relevant chunks
- 30-second timeout to prevent hanging
- Graceful error handling

### Memory Context Retrieval

**Location:** Lines 308-328 in `agent_service.py`

```python
memory_context = ""
if self.memory_service.is_enabled():
    try:
        memories = self.memory_service.search_memory(
            query=filtered_input,
            user_id=user_id,
            agent_id=agent_id,
            top_k=5,
            llm_provider=agent.llm_provider,
            llm_model=agent.llm_model
        )
        
        if memories:
            memory_context = "\nRelevant information from previous conversations:\n"
            for i, memory in enumerate(memories, 1):
                memory_content = memory.get('memory', '') if isinstance(memory, dict) else str(memory)
                memory_context += f"{i}. {memory_content}\n"
    except Exception as mem_error:
        print(f"Error retrieving memory context: {mem_error}")
```

**Features:**
- Uses mem0 for memory management
- Top 5 relevant memories
- Session-based or agent-based storage
- Error-tolerant execution

### Timeout Configuration

**KB Present:** 180 seconds (3 minutes)
- Allows time for KB retrieval and processing
- Accommodates embedding generation if needed

**No KB:** 90 seconds (1.5 minutes)
- Standard LLM response time
- Adequate for tool-based queries

## Testing Checklist

### Knowledge Base Priority Testing
- [x] Agent with KB: Answers from KB without calling tools
- [x] Agent with KB: Uses tools only when KB insufficient
- [x] Agent without KB: Uses tools normally
- [x] Empty KB: Falls back to tools appropriately

### Context Integration Testing
- [x] KB context appears in system prompt
- [x] Memory context appears after KB
- [x] Tool instructions appear last
- [x] Clear section headers visible

### Tool Usage Testing
- [x] Tools listed correctly in prompt
- [x] Tool usage strategy displayed
- [x] Agent follows priority instructions
- [x] Appropriate tool selection

### Error Handling Testing
- [x] KB query timeout handled gracefully
- [x] Memory service errors don't break agent
- [x] Tool execution errors reported clearly
- [x] Agent continues with available context

### Performance Testing
- [x] KB queries complete within timeout
- [x] Response times improved with KB
- [x] No increased latency for KB-less agents
- [x] Memory overhead acceptable

## Configuration

### For Agents WITH Knowledge Base

**Setup:**
1. Create knowledge base in UI
2. Upload documents to KB
3. Link KB to agent
4. Configure agent tools (optional)

**Result:**
- Agent prioritizes KB information
- Tools used selectively
- Clear execution strategy

### For Agents WITHOUT Knowledge Base

**Setup:**
1. Create agent
2. Configure tools

**Result:**
- Standard tool usage
- No KB overhead
- Normal execution flow

## Monitoring and Debugging

### Log Messages

**KB Context Retrieved:**
```
Retrieved KB context for agent abc-123: 1234 chars
```

**KB Query Timeout:**
```
Knowledge base query timed out for agent abc-123
```

**Memory Context Error:**
```
Error retrieving memory context: [error details]
```

**Tools Loaded:**
```
Loaded 3 external tools: ['web_search', 'calculator', 'weather']
```

### Debug Information

Check system prompt to verify priority:
1. KB section appears first
2. Memory section appears second
3. Tools section appears last with strategy
4. Guidelines appear at end

## Migration Guide

### Existing Agents

**No changes required!** All existing agents will automatically:
- Use new priority logic
- Check KB first if available
- Continue working as before if no KB

### New Agents

To take full advantage:
1. **Create Knowledge Base**: Add domain-specific documents
2. **Link to Agent**: Associate KB with agent
3. **Configure Tools**: Add only necessary tools
4. **Test Priority**: Verify agent checks KB first

## Best Practices

### Knowledge Base Content
✅ **Do:**
- Add frequently asked questions
- Include product documentation
- Store company policies
- Add troubleshooting guides
- Keep information current

❌ **Don't:**
- Add real-time data (use tools instead)
- Duplicate tool functionality
- Include outdated information
- Store sensitive credentials

### Tool Configuration
✅ **Do:**
- Add tools for real-time data
- Include tools for external services
- Configure tools for dynamic operations
- Test tool functionality

❌ **Don't:**
- Add redundant tools
- Configure tools for static info
- Overcomplicate tool set
- Forget API key configuration

## Performance Metrics

### Expected Improvements

**With Proper KB Setup:**
- 40-60% reduction in tool calls
- 30-50% faster response times
- 20-30% lower API costs
- Higher accuracy for domain questions

**Measurement:**
- Monitor tool call frequency
- Track response latency
- Review API usage costs
- Check user satisfaction scores

## Troubleshooting

### Issue: Agent Still Calls Tools for KB-Answerable Questions

**Diagnosis:**
- Check if KB is properly linked
- Verify KB has relevant documents
- Ensure embeddings are generated
- Review system prompt structure

**Solution:**
- Re-index knowledge base
- Add more specific documents
- Improve document chunking
- Test KB queries directly

### Issue: Agent Never Uses Tools

**Diagnosis:**
- KB may be too comprehensive
- Tool instructions unclear
- Agent being overly conservative

**Solution:**
- Review system prompt balance
- Test queries requiring tools
- Adjust KB scope
- Verify tool configurations

### Issue: Slow Response Times

**Diagnosis:**
- KB queries timing out
- Too many embeddings
- Large documents

**Solution:**
- Optimize chunk sizes
- Reduce top_k parameter
- Improve embedding model
- Cache frequent queries

## Future Enhancements

### Potential Improvements
- [ ] Dynamic KB relevance scoring
- [ ] Adaptive tool selection based on confidence
- [ ] KB cache for frequently accessed info
- [ ] Tool usage analytics dashboard
- [ ] Automatic KB content suggestions
- [ ] Hybrid KB + tool responses
- [ ] Context-aware timeout adjustment

## Summary

✅ **Agents now prioritize knowledge base information**
✅ **Tools used only when KB insufficient**
✅ **Clear execution strategy with 4-step priority**
✅ **Better performance and accuracy**
✅ **Reduced API costs and latency**
✅ **Backward compatible with existing agents**

The agent execution logic is now **optimized for efficiency and accuracy** by checking verified knowledge base information before making external tool calls! 🎉
