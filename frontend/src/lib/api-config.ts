/**
 * API Configuration
 * Centralized configuration for API endpoints
 */

// Get API URL from environment variable or use default
const getApiUrl = (): string => {
  // In production, use environment variable
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // In development, detect from window location
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;

    // If running in Docker or production, use same host
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
      return `${protocol}//${hostname}:8000`;
    }
  }

  // Default to localhost for local development
  return 'http://localhost:8000';
};

// Get WebSocket URL
const getWebSocketUrl = (path: string): string => {
  const apiUrl = getApiUrl();
  const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
  const host = apiUrl.replace(/^https?:\/\//, '').replace(/:\d+$/, '');

  // Extract port from API URL or use default
  const portMatch = apiUrl.match(/:(\d+)/);
  const port = portMatch ? portMatch[1] : '8000';

  return `${wsProtocol}://${host}:${port}${path}`;
};

export const API_BASE_URL = getApiUrl();
export const API_V1_URL = `${API_BASE_URL}/api/v1`;

// Helper function to get WebSocket URL
export const getWSUrl = (path: string): string => {
  return getWebSocketUrl(path);
};

// API endpoint helpers
export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: `${API_V1_URL}/auth/login`,
    REGISTER: `${API_V1_URL}/auth/register`,
    LOGOUT: `${API_V1_URL}/auth/logout`,
    ME: `${API_V1_URL}/auth/me`,
  },

  // Agents
  AGENTS: {
    LIST: `${API_V1_URL}/agents/`,
    GET: (id: string) => `${API_V1_URL}/agents/${id}`,
    CREATE: `${API_V1_URL}/agents/`,
    UPDATE: (id: string) => `${API_V1_URL}/agents/${id}`,
    DELETE: (id: string) => `${API_V1_URL}/agents/${id}`,
    EXECUTE: (id: string) => `${API_V1_URL}/agents/${id}/execute`,
    CHAT: (id: string) => `${API_V1_URL}/agents/${id}/chat`,
    STREAM: (id: string) => getWSUrl(`/api/v1/agents/${id}/stream`),
    MEMORY: {
      SESSION: (sessionId: string) => `${API_V1_URL}/agents/memory/session/${sessionId}`,
    },
  },

  // Workflows
  WORKFLOWS: {
    LIST: `${API_V1_URL}/workflows/`,
    GET: (id: string) => `${API_V1_URL}/workflows/${id}`,
    CREATE: `${API_V1_URL}/workflows/`,
    UPDATE: (id: string) => `${API_V1_URL}/workflows/${id}`,
    DELETE: (id: string) => `${API_V1_URL}/workflows/${id}`,
    EXECUTE: (id: string) => `${API_V1_URL}/workflows/${id}/execute`,
    EXECUTION: (executionId: string) => `${API_V1_URL}/workflow-executions/${executionId}`,
  },

  // Monitoring
  MONITORING: {
    HEALTH: `${API_V1_URL}/monitoring/health`,
    RECENT_EXECUTIONS: `${API_V1_URL}/monitoring/recent-executions`,
    METRICS: {
      WORKFLOW_EXECUTIONS: `${API_V1_URL}/monitoring/metrics/workflow-executions`,
      STEP_EXECUTIONS: `${API_V1_URL}/monitoring/metrics/step-executions`,
    },
  },

  // Enhanced Monitoring
  ENHANCED_MONITORING: {
    WORKFLOW_METRICS: `${API_V1_URL}/enhanced-monitoring/enhanced-metrics/workflow-executions`,
    STEP_METRICS: `${API_V1_URL}/enhanced-monitoring/enhanced-metrics/step-executions`,
    BOTTLENECKS: (workflowId: string) => `${API_V1_URL}/enhanced-monitoring/analytics/bottlenecks/${workflowId}`,
    RESOURCE_TRENDS: (workflowId: string) => `${API_V1_URL}/enhanced-monitoring/analytics/resource-trends/${workflowId}`,
  },

  // Alerting
  ALERTING: {
    RULES: `${API_V1_URL}/alerting/rules`,
    RULE: (id: string) => `${API_V1_URL}/alerting/rules/${id}`,
    ALERTS: `${API_V1_URL}/alerting/alerts`,
    ALERT: (id: string) => `${API_V1_URL}/alerting/alerts/${id}`,
    ACKNOWLEDGE: (id: string) => `${API_V1_URL}/alerting/alerts/${id}/acknowledge`,
    RESOLVE: (id: string) => `${API_V1_URL}/alerting/alerts/${id}/resolve`,
  },

  // Cost Tracking
  COST_TRACKING: {
    SUMMARY: `${API_V1_URL}/cost-tracking/summary`,
    TRENDS: `${API_V1_URL}/cost-tracking/trends`,
    BUDGETS: `${API_V1_URL}/cost-tracking/budgets`,
    BUDGET: (id: string) => `${API_V1_URL}/cost-tracking/budgets/${id}`,
    BUDGET_STATUS: (id: string) => `${API_V1_URL}/cost-tracking/budgets/${id}/status`,
    ALERTS: `${API_V1_URL}/cost-tracking/alerts`,
  },

  // Audit
  AUDIT: {
    LOGS: `${API_V1_URL}/audit/logs`,
    SEARCH: `${API_V1_URL}/audit/search`,
    SUMMARY: `${API_V1_URL}/audit/summary`,
  },

  // Knowledge Bases
  KNOWLEDGE_BASES: {
    LIST: `${API_V1_URL}/knowledge-bases`,
    GET: (id: string) => `${API_V1_URL}/knowledge-bases/${id}`,
    CREATE: `${API_V1_URL}/knowledge-bases`,
    DOCUMENTS: {
      TEXT: (id: string) => `${API_V1_URL}/knowledge-bases/${id}/documents/text`,
      URL: (id: string) => `${API_V1_URL}/knowledge-bases/${id}/documents/url`,
      FILE: (id: string) => `${API_V1_URL}/knowledge-bases/${id}/documents/file`,
    },
  },

  // Dashboard
  DASHBOARD: {
    STATS: `${API_V1_URL}/dashboard/stats`,
  },
};

// Observability endpoints (may not be available if router is removed)
export const OBSERVABILITY_ENDPOINTS = {
  AGENT_METRICS: (agentId: string) => `${API_V1_URL}/observability/agents/${agentId}/metrics`,
  WORKFLOW_METRICS: (workflowId: string) => `${API_V1_URL}/observability/workflows/${workflowId}/metrics`,
  TRACES: `${API_V1_URL}/observability/traces`,
};

