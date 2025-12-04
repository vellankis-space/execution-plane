import { OBSERVABILITY_ENDPOINTS } from '@/lib/api-config';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

// Types
// Types
export interface AgentMetrics {
    traffic: {
        total_requests: number;
        active_users: number;
        llm_calls: number;
        tool_calls: number;
    };
    latency: {
        avg: number;
        p99: number;
        ttft: number;
    };
    errors: {
        rate: number;
        count: number;
    };
    cost: {
        total: number;
        tokens: number;
        by_model?: Array<{ name: string; cost: number; tokens: number }>;
        token_breakdown?: { prompt: number; completion: number };
    };
    charts?: {
        requests_over_time: Array<{ time: string; requests: number }>;
    };
    // NEW: Enhanced metrics from Phase 2
    finish_reasons?: Record<string, number>;
    recent_prompts?: Array<{
        timestamp: string;
        prompt: string;
        model: string;
    }>;
    recent_responses?: Array<{
        timestamp: string;
        response: string;
        model: string;
    }>;
    tool_usage?: Array<{
        name: string;
        count: number;
        avg_latency: number;
        failures: number;
        success_rate: number;
    }>;
    mcp_servers_used?: string[];
}

export interface WorkflowMetrics {
    executions: {
        total: number;
        success_rate: number;
        failure_rate: number;
    };
    latency: {
        avg_duration: number;
        p95: number;
    };
    cost: {
        total: number;
        by_model?: Array<{ name: string; cost: number }>;
    };
    tokens: {
        total: number;
        prompt: number;
        completion: number;
    };
    charts?: {
        executions_over_time: Array<{ time: string; executions: number }>;
    };
}

export interface Trace {
    id: string;
    timestamp: string;
    status: 'success' | 'failed';
    latency: string;
    tokens: number;
    cost: string;
    name?: string;
}

export interface TraceSpan {
    span_id: string;
    parent_id?: string;
    name: string;
    type: 'chain' | 'llm' | 'tool' | 'agent';
    start_time: string;
    end_time?: string;
    status: 'success' | 'failed';
    input?: any;
    output?: any;
    metadata?: Record<string, any>;
    metrics?: {
        tokens?: { prompt: number; completion: number; total: number };
        cost?: number;
    };
    error?: string;
}

export interface TraceDetail extends Trace {
    spans: TraceSpan[];
    metadata?: Record<string, any>;
}

// API Service
export const observabilityService = {
    getAgentMetrics: async (agentId: string, timeRange: string = '24h'): Promise<AgentMetrics> => {
        const token = localStorage.getItem('access_token');
        const response = await axios.get(OBSERVABILITY_ENDPOINTS.AGENT_METRICS(agentId), {
            params: { time_range: timeRange },
            headers: token ? { Authorization: `Bearer ${token}` } : {},
        });

        const data = response.data;
        // Map backend metrics to frontend structure with all OpenTelemetry data
        return {
            traffic: {
                total_requests: data.total_runs || 0,
                active_users: data.active_users || 0,
                llm_calls: data.llm_calls || 0,
                tool_calls: data.tool_calls || 0
            },
            latency: {
                avg: data.avg_latency || 0,
                p99: data.p99_latency || 0,
                ttft: data.ttft || 0
            },
            errors: {
                rate: (data.error_rate || 0) / 100, // Convert percentage to decimal
                count: Math.round((data.total_runs || 0) * (data.error_rate || 0) / 100)
            },
            cost: {
                total: data.total_cost || 0,
                tokens: data.total_tokens || 0,
                by_model: data.model_costs || [],
                token_breakdown: {
                    prompt: data.prompt_tokens || 0,
                    completion: data.completion_tokens || 0
                }
            },
            charts: {
                requests_over_time: data.chart_data || []
            },
            // NEW: Enhanced metrics from Phase 2
            finish_reasons: data.finish_reasons || {},
            recent_prompts: data.recent_prompts || [],
            recent_responses: data.recent_responses || [],
            tool_usage: data.tool_usage || [],
            mcp_servers_used: data.mcp_servers_used || []
        };
    },

    getWorkflowMetrics: async (workflowId: string, timeRange: string = '24h'): Promise<WorkflowMetrics> => {
        const token = localStorage.getItem('access_token');
        console.log(`[ObservabilityService] Fetching workflow metrics for ${workflowId}, token: ${token ? 'present' : 'missing'}`);
        
        try {
            const response = await axios.get(OBSERVABILITY_ENDPOINTS.WORKFLOW_METRICS(workflowId), {
                params: { time_range: timeRange },
                headers: token ? { Authorization: `Bearer ${token}` } : {},
            });
            console.log(`[ObservabilityService] Workflow metrics response:`, response.data);
            const data = response.data;
        return {
            executions: {
                total: data.total_runs || 0,
                success_rate: (data.success_rate || 0) / 100, // Convert percentage to decimal
                failure_rate: (data.error_rate || 0) / 100 // Convert percentage to decimal
            },
            latency: {
                avg_duration: data.avg_latency || 0,
                p95: data.p95_latency || 0
            },
            cost: {
                total: data.total_cost || 0,
                by_model: data.model_costs || []
            },
            tokens: {
                total: data.total_tokens || 0,
                prompt: data.prompt_tokens || 0,
                completion: data.completion_tokens || 0
            },
            charts: {
                executions_over_time: data.chart_data || []
            }
        };
        } catch (error) {
            console.error(`[ObservabilityService] Error fetching workflow metrics:`, error);
            throw error;
        }
    },

    getTraces: async (filters: { agentId?: string; workflowId?: string; status?: string; limit?: number; offset?: number } = {}): Promise<Trace[]> => {
        const token = localStorage.getItem('access_token');
        const response = await axios.get(OBSERVABILITY_ENDPOINTS.TRACES, {
            params: {
                agent_id: filters.agentId,
                workflow_id: filters.workflowId,
                status: filters.status,
                limit: filters.limit || 10,
                offset: filters.offset || 0,
            },
            headers: token ? { Authorization: `Bearer ${token}` } : {},
        });

        // Map Jaeger traces to frontend Trace interface
        // Backend returns { data: [...], total: ... }
        const jaegerTraces = response.data.data || [];

        return jaegerTraces.map((trace: any) => {
            // Find root span (usually the one without references or the first one)
            // Jaeger spans usually have a 'references' array. Root has empty references.
            const rootSpan = trace.spans.find((s: any) => !s.references || s.references.length === 0) || trace.spans[0];

            // Calculate duration (latency)
            // Jaeger duration is in microseconds
            const durationMs = rootSpan.duration / 1000;
            const latencyStr = durationMs > 1000 ? `${(durationMs / 1000).toFixed(2)}s` : `${Math.round(durationMs)}ms`;

            // Check status (look for error tag)
            const hasError = trace.spans.some((s: any) =>
                s.tags.some((t: any) => t.key === 'error' && t.value === true)
            );

            // Try to find token usage from span attributes/tags
            // OpenLLMetry uses gen_ai.usage.* attributes
            let tokens = 0;
            trace.spans.forEach((s: any) => {
                const tokenTag = s.tags.find((t: any) => 
                    t.key === 'gen_ai.usage.total_tokens' || 
                    t.key === 'llm.usage.total_tokens' ||
                    t.key === 'gen_ai.usage.input_tokens' ||
                    t.key === 'gen_ai.usage.output_tokens'
                );
                if (tokenTag) tokens += Number(tokenTag.value);
            });

            // Estimate cost based on tokens (using average pricing)
            // Average cost ~$0.002 per 1K tokens for GPT-3.5 level models
            const estimatedCost = tokens > 0 ? (tokens * 0.002 / 1000).toFixed(4) : '0.0000';

            return {
                id: trace.traceID,
                timestamp: new Date(rootSpan.startTime / 1000).toISOString(), // Jaeger time is microseconds
                status: hasError ? 'failed' : 'success',
                latency: latencyStr,
                tokens: tokens,
                cost: `$${estimatedCost}`,
                name: rootSpan.operationName
            };
        });
    },

    getTraceDetails: async (traceId: string): Promise<TraceDetail> => {
        const token = localStorage.getItem('access_token');
        const response = await axios.get(`${OBSERVABILITY_ENDPOINTS.TRACES}/${traceId}`, {
            headers: token ? { Authorization: `Bearer ${token}` } : {},
        });

        const jaegerTrace = response.data;
        if (!jaegerTrace || !jaegerTrace.spans) {
            throw new Error("Invalid trace data");
        }

        // Map to TraceDetail
        const rootSpan = jaegerTrace.spans.find((s: any) => !s.references || s.references.length === 0) || jaegerTrace.spans[0];
        const durationMs = rootSpan.duration / 1000;
        const latencyStr = durationMs > 1000 ? `${(durationMs / 1000).toFixed(2)}s` : `${Math.round(durationMs)}ms`;
        const hasError = jaegerTrace.spans.some((s: any) =>
            s.tags.some((t: any) => t.key === 'error' && t.value === true)
        );

        // Map spans
        const spans: TraceSpan[] = jaegerTrace.spans.map((s: any) => {
            // Determine type based on tags/attributes
            let type: 'chain' | 'llm' | 'tool' | 'agent' = 'chain';

            const tags = s.tags || [];
            const hasTag = (key: string) => tags.some((t: any) => t.key === key);

            if (hasTag('gen_ai.system')) {
                type = 'llm';
            } else if (hasTag('tool.name') || s.operationName.startsWith('tool:')) {
                type = 'tool';
            } else if (hasTag('agent.name') || s.operationName.startsWith('agent:')) {
                type = 'agent';
            }

            // Extract tokens if available - OpenLLMetry uses gen_ai.usage.* attributes
            let tokens = undefined;
            const promptTokens = tags.find((t: any) => t.key === 'gen_ai.usage.prompt_tokens' || t.key === 'gen_ai.usage.input_tokens' || t.key === 'llm.usage.prompt_tokens');
            const completionTokens = tags.find((t: any) => t.key === 'gen_ai.usage.completion_tokens' || t.key === 'gen_ai.usage.output_tokens' || t.key === 'llm.usage.completion_tokens');
            const totalTokens = tags.find((t: any) => t.key === 'gen_ai.usage.total_tokens' || t.key === 'llm.usage.total_tokens');

            if (promptTokens || completionTokens || totalTokens) {
                tokens = {
                    prompt: promptTokens ? Number(promptTokens.value) : 0,
                    completion: completionTokens ? Number(completionTokens.value) : 0,
                    total: totalTokens ? Number(totalTokens.value) : 0
                };
            }

            return {
                span_id: s.spanID,
                parent_id: s.references && s.references.length > 0 ? s.references[0].spanID : undefined,
                name: s.operationName,
                type: type,
                start_time: new Date(s.startTime / 1000).toISOString(),
                end_time: new Date((s.startTime + s.duration) / 1000).toISOString(),
                status: tags.some((t: any) => t.key === 'error' && t.value === true) ? 'failed' : 'success',
                metadata: tags.reduce((acc: any, t: any) => ({ ...acc, [t.key]: t.value }), {}),
                // Input/Output extraction
                input: tags.find((t: any) => t.key === 'gen_ai.prompt' || t.key === 'input.value')?.value,
                output: tags.find((t: any) => t.key === 'gen_ai.completion' || t.key === 'output.value')?.value,
                metrics: {
                    tokens: tokens
                }
            };
        });

        return {
            id: jaegerTrace.traceID,
            timestamp: new Date(rootSpan.startTime / 1000).toISOString(),
            status: hasError ? 'failed' : 'success',
            latency: latencyStr,
            tokens: 0, // Aggregate if needed
            cost: 'N/A',
            name: rootSpan.operationName,
            spans: spans,
            metadata: {
                traceID: jaegerTrace.traceID,
                processes: jaegerTrace.processes // Jaeger process info
            }
        };
    }
};

// React Query Hooks
export const useAgentMetrics = (agentId: string, timeRange: string = '24h') => {
    return useQuery({
        queryKey: ['agentMetrics', agentId, timeRange],
        queryFn: () => observabilityService.getAgentMetrics(agentId, timeRange),
        enabled: !!agentId,
        refetchInterval: 30000, // Refresh every 30s
    });
};

export const useWorkflowMetrics = (workflowId: string, timeRange: string = '24h') => {
    return useQuery({
        queryKey: ['workflowMetrics', workflowId, timeRange],
        queryFn: () => observabilityService.getWorkflowMetrics(workflowId, timeRange),
        enabled: !!workflowId,
        refetchInterval: 30000,
    });
};

export const useTraces = (filters: { agentId?: string; workflowId?: string; status?: string; limit?: number; offset?: number } = {}) => {
    return useQuery({
        queryKey: ['traces', filters],
        queryFn: () => observabilityService.getTraces(filters),
        refetchInterval: 10000, // Refresh every 10s for live traces
    });
};

export const useTraceDetails = (traceId: string | null) => {
    return useQuery({
        queryKey: ['traceDetails', traceId],
        queryFn: () => observabilityService.getTraceDetails(traceId!),
        enabled: !!traceId,
    });
};
