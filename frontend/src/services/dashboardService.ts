import { API_ENDPOINTS } from "@/lib/api-config";

export interface DashboardStats {
    total_agents: number;
    active_workflows: number;
    executions_today: number;
}

export const DashboardService = {
    getStats: async (): Promise<DashboardStats> => {
        const response = await fetch(API_ENDPOINTS.DASHBOARD.STATS);
        if (!response.ok) {
            throw new Error(`Failed to fetch dashboard stats: ${response.statusText}`);
        }
        return response.json();
    },
};
