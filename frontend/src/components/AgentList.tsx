import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Trash2, Brain, RefreshCw, MessageSquare, Plus, Edit } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { useNavigate } from "react-router-dom";

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

interface AgentListProps {
  onAgentDeleted?: () => void;
}

export function AgentList({ onAgentDeleted }: AgentListProps) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/agents');
      if (response.ok) {
        const data = await response.json();
        console.log("Fetched agents:", data); // Debug log
        setAgents(data);
        // Additional debug log to check if agents have names
        if (data.length > 0) {
          console.log("First agent:", data[0]);
        }
      } else {
        console.error("Failed to fetch agents, status:", response.status);
        // Show error to user
        toast({
          title: "Error",
          description: `Failed to load agents. Status: ${response.status}`,
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Error fetching agents:", error);
      toast({
        title: "Error",
        description: "Failed to load agents. Please check if the backend is running.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleDeleteAgent = async (agentId: string, agentName: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/agents/${agentId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // Remove the agent from the local state
        setAgents(agents.filter(agent => agent.agent_id !== agentId));
        toast({
          title: "Agent Deleted",
          description: `${agentName} has been successfully deleted.`,
        });
        // Call the callback if provided
        if (onAgentDeleted) {
          onAgentDeleted();
        }
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

  const handleRefresh = () => {
    setRefreshing(true);
    fetchAgents();
  };

  if (loading && !refreshing) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-4">
        <div>
          <p className="text-sm text-muted-foreground">
            {agents.length} {agents.length === 1 ? 'agent' : 'agents'} configured
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
            className="gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </Button>
        </div>
      </div>
      {agents.length === 0 ? (
        <Card className="border-dashed border-border/50 bg-card/50">
          <div className="p-12 text-center">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500/20 to-blue-600/20 mx-auto mb-4 flex items-center justify-center">
              <Brain className="w-8 h-8 text-blue-500" />
            </div>
            <h3 className="font-semibold text-lg mb-2">No agents yet</h3>
            <p className="text-muted-foreground text-sm mb-6">
              Create your first AI agent to get started
            </p>
            <Button onClick={() => navigate('/playground')} className="shine-effect">
              <Plus className="w-4 h-4 mr-2" />
              Create Agent
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent) => (
            <Card 
              key={agent.agent_id} 
              className="group relative overflow-hidden border-border/50 bg-gradient-to-br from-card to-card/50 hover:shadow-2xl transition-all duration-300 hover:scale-[1.02] h-full"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="p-6 relative">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-blue-500/25 group-hover:scale-110 transition-transform">
                      <Brain className="w-6 h-6 text-white" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h3 className="font-semibold text-lg group-hover:text-primary transition-colors truncate">
                        {agent.name || "Unnamed Agent"}
                      </h3>
                      <p className="text-xs text-muted-foreground capitalize mt-1 truncate">
                        {agent.agent_type || "Unknown Type"}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteAgent(agent.agent_id, agent.name);
                    }}
                    className="text-muted-foreground hover:text-destructive hover:bg-destructive/10 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 h-8 w-8"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
                
                {/* Agent Metadata */}
                <div className="space-y-2 mb-4 text-xs">
                  <div className="flex items-center justify-between py-2 px-3 rounded-lg bg-muted/50">
                    <span className="text-muted-foreground">Model</span>
                    <span className="font-medium">{agent.llm_model}</span>
                  </div>
                  <div className="flex items-center justify-between py-2 px-3 rounded-lg bg-muted/50">
                    <span className="text-muted-foreground">Tools</span>
                    <span className="font-medium">{agent.tools?.length || 0}</span>
                  </div>
                </div>

                <div className="flex gap-2 pt-4 border-t border-border/50">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 gap-2 hover:bg-primary/10 hover:border-primary/50"
                    onClick={() => navigate(`/playground?id=${agent.agent_id}`)}
                  >
                    <Edit className="w-4 h-4" />
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    className="flex-1 gap-2 bg-gradient-to-r from-primary to-primary/90 shine-effect"
                    onClick={() => navigate('/chat')}
                  >
                    <MessageSquare className="w-4 h-4" />
                    Chat
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}