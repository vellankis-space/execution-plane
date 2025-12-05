import { API_ENDPOINTS } from '@/lib/api-config';
import axios from 'axios';
import { useQuery } from '@tanstack/react-query';

export interface Agent {
    agent_id: string;
    name: string;
    agent_type: string;
    llm_provider: string;
    llm_model: string;
    created_at: string;
    updated_at: string;
}

export const agentService = {
    getAllAgents: async (): Promise<Agent[]> => {
        const response = await axios.get(API_ENDPOINTS.AGENTS.LIST);
        return response.data;
    },

    getAgent: async (id: string): Promise<Agent> => {
        const response = await axios.get(API_ENDPOINTS.AGENTS.GET(id));
        return response.data;
    }
};

export const useAgents = () => {
    return useQuery({
        queryKey: ['agents'],
        queryFn: agentService.getAllAgents,
    });
};
