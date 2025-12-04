import { API_ENDPOINTS } from '@/lib/api-config';
import axios from 'axios';
import { useQuery } from '@tanstack/react-query';

export interface Workflow {
    workflow_id: string;
    name: string;
    description: string;
    created_at: string;
    updated_at: string;
    is_active: boolean;
}

export const workflowService = {
    getAllWorkflows: async (): Promise<Workflow[]> => {
        const response = await axios.get(API_ENDPOINTS.WORKFLOWS.LIST);
        return response.data;
    },

    getWorkflow: async (id: string): Promise<Workflow> => {
        const response = await axios.get(API_ENDPOINTS.WORKFLOWS.GET(id));
        return response.data;
    }
};

export const useWorkflows = () => {
    return useQuery({
        queryKey: ['workflows'],
        queryFn: workflowService.getAllWorkflows,
    });
};
