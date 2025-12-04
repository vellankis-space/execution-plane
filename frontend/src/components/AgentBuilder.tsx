import { useState, useRef, useEffect, useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Sparkles, Cpu, Database, GitBranch, Settings2, Thermometer, Hash, Layers, Box, FileText, Key, MessageSquare, Upload, Link2, Type, Brain, Wrench, Shield, Plus, X, Home, Loader2, RefreshCw, Server, CheckCircle, Trash2 } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { ThemeToggle } from "@/components/ThemeToggle";
import { ToolConfigDialog } from "@/components/ToolConfigDialog";
import { MCPServerModal } from "@/components/MCPServerModal";
import MCPToolSelector from "@/components/MCPToolSelector";

const LLM_PROVIDERS = [
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
  { value: "google", label: "Google" },
  { value: "groq", label: "Groq" },
  { value: "openrouter", label: "OpenRouter" },
  { value: "together", label: "Together AI" },
  { value: "fireworks", label: "Fireworks AI" },
  { value: "cohere", label: "Cohere" },
  { value: "meta", label: "Meta" },
  { value: "mistral", label: "Mistral AI" },
];

// Models will be fetched dynamically from the API

const AGENT_TYPES = [
  { value: "react", label: "ReAct" },
  { value: "plan-execute", label: "Plan & Execute" },
  { value: "reflection", label: "Reflection" },
  { value: "custom", label: "Custom Graph" },
];

const MEMORY_TYPES = [
  { value: "memory-saver", label: "MemorySaver (SQLite)" },
  { value: "postgres", label: "PostgreSQL" },
  { value: "redis", label: "Redis" },
  { value: "none", label: "No Persistence" },
];

const AGENT_FRAMEWORKS = [
  { value: "langgraph", label: "LangGraph" },
  { value: "crewai", label: "CrewAI" },
  { value: "autogen", label: "AutoGen" },
  { value: "google-adk", label: "Google ADK" },
  { value: "semantic-kernel", label: "Semantic Kernel" },
];

const TOOLS = [
  // New LangChain Tools (6 tools from documentation)
  { id: "duckduckgo_search", label: "DuckDuckGo Search", requiresConfig: true, icon: "🦆" },
  { id: "brave_search", label: "Brave Search", requiresConfig: true, icon: "🦁" },
  { id: "github_toolkit", label: "GitHub Toolkit", requiresConfig: true, icon: "🐙" },
  { id: "gmail_toolkit", label: "Gmail Toolkit", requiresConfig: true, icon: "📧" },
  { id: "playwright_browser", label: "PlayWright Browser", requiresConfig: false, icon: "🎭" },
  { id: "mcp_database", label: "MCP Database Toolbox", requiresConfig: true, icon: "🗄️" },
  { id: "firecrawl", label: "FireCrawl", requiresConfig: true, icon: "🔥" },
  { id: "arxiv", label: "Arxiv", requiresConfig: false, icon: "📚" },
  { id: "wikipedia", label: "Wikipedia", requiresConfig: false, icon: "🌐" },
];

const PII_CATEGORIES = [
  { id: "pii_email", label: "Email Addresses", description: "User email addresses" },
  { id: "pii_phone", label: "Phone Numbers", description: "Phone contact information" },
  { id: "pii_name", label: "Full Names", description: "First and last names" },
  { id: "pii_address", label: "Physical Address", description: "Street, city, state, ZIP" },
  { id: "pii_ssn", label: "SSN/Tax ID", description: "Social security numbers" },
  { id: "pii_dob", label: "Date of Birth", description: "Birth dates and age" },
  { id: "pii_financial", label: "Financial Data", description: "Credit cards, bank accounts" },
  { id: "pii_medical", label: "Medical Records", description: "Health information" },
  { id: "pii_ip", label: "IP Addresses", description: "Network identifiers" },
  { id: "pii_biometric", label: "Biometric Data", description: "Fingerprints, facial data" },
];

export function AgentBuilder() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const editAgentId = searchParams.get('id');
  const [isEditMode, setIsEditMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [agentName, setAgentName] = useState("");
  const [agentType, setAgentType] = useState("react");
  const [agentFramework, setAgentFramework] = useState("langgraph");
  const [llmProvider, setLlmProvider] = useState("anthropic");
  const [llmModel, setLlmModel] = useState("claude-sonnet-4-5");
  const [temperature, setTemperature] = useState([0.7]);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [selectedTools, setSelectedTools] = useState<string[]>([]);
  const [maxIterations, setMaxIterations] = useState("15");
  const [memoryType, setMemoryType] = useState("memory-saver");
  const [streamingEnabled, setStreamingEnabled] = useState(true);
  const [humanInLoop, setHumanInLoop] = useState(false);
  const [recursionLimit, setRecursionLimit] = useState("25");
  const [knowledgeText, setKnowledgeText] = useState("");
  const [knowledgeLinks, setKnowledgeLinks] = useState("");
  const [knowledgeMode, setKnowledgeMode] = useState<"upload" | "links" | "text">("text");
  const [knowledgeFiles, setKnowledgeFiles] = useState<File[]>([]);
  const [selectedToolsList, setSelectedToolsList] = useState<string[]>([]);
  const [blockedPII, setBlockedPII] = useState<string[]>([]);
  const [customPII, setCustomPII] = useState<Array<{ id: string; label: string; description: string }>>([]);
  const [newPIILabel, setNewPIILabel] = useState("");
  const [newPIIDescription, setNewPIIDescription] = useState("");
  const [newPIIPattern, setNewPIIPattern] = useState("");
  const [showCustomPIIForm, setShowCustomPIIForm] = useState(false);
  const [piiStrategy, setPIIStrategy] = useState<"redact" | "mask" | "hash" | "block">("redact");
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Tool configurations
  const [toolConfigs, setToolConfigs] = useState<Record<string, any>>({});
  const [showToolConfig, setShowToolConfig] = useState<string | null>(null);

  // Dynamic models state
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [loadingModels, setLoadingModels] = useState(false);
  const [providerApiKey, setProviderApiKey] = useState<string>("");
  const [isUsingApiKey, setIsUsingApiKey] = useState(false);
  const [modelSearch, setModelSearch] = useState("");

  // MCP Servers state
  const [mcpServers, setMcpServers] = useState<any[]>([]);
  const [selectedMcpServers, setSelectedMcpServers] = useState<string[]>([]);
  const [mcpServerConfigs, setMcpServerConfigs] = useState<Record<string, string[] | null>>({});
  const [loadingMcpServers, setLoadingMcpServers] = useState(false);
  const [deletingServerId, setDeletingServerId] = useState<string | null>(null);
  const [reconnectingServerId, setReconnectingServerId] = useState<string | null>(null);


  // Fetch agent data if in edit mode
  useEffect(() => {
    const fetchAgentData = async () => {
      if (editAgentId) {
        setLoading(true);
        try {
          const response = await fetch(`http://localhost:8000/api/v1/agents/${editAgentId}`);
          if (response.ok) {
            const agent = await response.json();
            setIsEditMode(true);
            setAgentName(agent.name || "");
            setAgentType(agent.agent_type || "react");
            setAgentFramework(agent.agent_framework || "langgraph");
            setLlmProvider(agent.llm_provider || "anthropic");
            setLlmModel(agent.llm_model || "claude-sonnet-4-5");
            setTemperature([agent.temperature || 0.7]);
            setSystemPrompt(agent.system_prompt || "");
            setSelectedTools(agent.tools || []);
            setSelectedToolsList(agent.tools || []);
            setMaxIterations(agent.max_iterations?.toString() || "15");
            setMemoryType(agent.memory_type || "memory-saver");
            setStreamingEnabled(agent.streaming_enabled !== false);
            setHumanInLoop(agent.human_in_loop || false);
            setRecursionLimit(agent.recursion_limit?.toString() || "25");
            if (agent.tool_configs) {
              setToolConfigs(agent.tool_configs);
            }
            if (agent.pii_config) {
              setBlockedPII(agent.pii_config.blocked_pii_types || []);
              setPIIStrategy(agent.pii_config.strategy || "redact");
              if (agent.pii_config.custom_pii_categories) {
                setCustomPII(agent.pii_config.custom_pii_categories);
              }
            }

            // Load MCP server configurations
            try {
              const mcpResponse = await fetch(`http://localhost:8000/api/v1/agents/${editAgentId}/mcp-servers`);
              if (mcpResponse.ok) {
                const mcpData = await mcpResponse.json();
                if (mcpData.mcp_servers && mcpData.mcp_servers.length > 0) {
                  const serverIds = mcpData.mcp_servers.map((s: any) => s.server_id);
                  setSelectedMcpServers(serverIds);

                  // Build mcpServerConfigs from selected_tools
                  const configs: Record<string, string[] | null> = {};
                  mcpData.mcp_servers.forEach((s: any) => {
                    configs[s.server_id] = s.selected_tools;
                  });
                  setMcpServerConfigs(configs);
                }
              }
            } catch (error) {
              console.error("Error fetching MCP server configurations:", error);
            }
          } else {
            toast({
              title: "Error",
              description: "Failed to load agent data",
              variant: "destructive",
            });
          }
        } catch (error) {
          console.error("Error fetching agent:", error);
          toast({
            title: "Error",
            description: "Failed to load agent data",
            variant: "destructive",
          });
        } finally {
          setLoading(false);
        }
      }
    };
    fetchAgentData();
  }, [editAgentId]);

  // Fetch models function
  const fetchModels = async () => {
    if (!llmProvider) return;
    if (!providerApiKey.trim()) {
      toast({
        title: "API key required",
        description: `Enter your ${llmProvider} API key to fetch models`,
        variant: "destructive",
      });
      return;
    }

    setLoadingModels(true);
    setIsUsingApiKey(false);

    try {
      const url = `http://localhost:8000/api/v1/models/${llmProvider}?api_key=${encodeURIComponent(providerApiKey.trim())}`;
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setAvailableModels(data.models || []);

        setIsUsingApiKey(true);
        toast({
          title: "Models updated",
          description: `Fetched real-time models from ${llmProvider}`,
        });

        // Set first model as default if current model is not in the list
        if (data.models && data.models.length > 0 && !data.models.includes(llmModel)) {
          setLlmModel(data.models[0]);
        }
      } else {
        console.error("Failed to fetch models for provider:", llmProvider);
        setAvailableModels([]);
        toast({
          title: "API error",
          description: "Unable to fetch models with the provided API key",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Error fetching models:", error);
      setAvailableModels([]);
      toast({
        title: "Network error",
        description: "Failed to connect to provider API",
        variant: "destructive",
      });
    } finally {
      setLoadingModels(false);
    }
  };

  // Fetch models when provider changes (without API key)
  useEffect(() => {
    setAvailableModels([]);
    setLlmModel("");
    setProviderApiKey("");
    setIsUsingApiKey(false);
    setModelSearch("");
  }, [llmProvider]);

  useEffect(() => {
    setModelSearch("");
  }, [availableModels]);

  const filteredModels = useMemo(() => {
    if (!modelSearch.trim()) return availableModels;
    const query = modelSearch.trim().toLowerCase();
    return availableModels.filter((model) => model.toLowerCase().includes(query));
  }, [availableModels, modelSearch]);

  // Fetch MCP servers
  useEffect(() => {
    fetchMcpServers();
  }, []);

  const fetchMcpServers = async () => {
    try {
      setLoadingMcpServers(true);
      const response = await fetch('http://localhost:8000/api/v1/mcp-servers');
      if (response.ok) {
        const data = await response.json();
        setMcpServers(data);
      }
    } catch (error) {
      console.error('Error fetching MCP servers:', error);
    } finally {
      setLoadingMcpServers(false);
    }
  };

  const handleMcpServerToggle = (serverId: string) => {
    setSelectedMcpServers(prev => {
      const isCurrentlySelected = prev.includes(serverId);

      if (isCurrentlySelected) {
        // Remove server and its tool config
        setMcpServerConfigs(configs => {
          const newConfigs = { ...configs };
          delete newConfigs[serverId];
          return newConfigs;
        });
        return prev.filter(id => id !== serverId);
      } else {
        // Add server with "all tools" by default
        setMcpServerConfigs(configs => ({
          ...configs,
          [serverId]: null // null = all tools
        }));
        return [...prev, serverId];
      }
    });
  };

  const handleMcpToolsChange = (serverId: string, selectedTools: string[] | null) => {
    setMcpServerConfigs(prev => ({
      ...prev,
      [serverId]: selectedTools
    }));
  };

  const handleDeleteMcpServer = async (serverId: string, serverName: string) => {
    if (!confirm(`Are you sure you want to delete "${serverName}"? This action cannot be undone.`)) {
      return;
    }

    setDeletingServerId(serverId);

    try {
      const response = await fetch(`http://localhost:8000/api/v1/mcp-servers/${serverId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        toast({
          title: 'Server Deleted',
          description: `${serverName} has been deleted successfully`,
        });
        // Remove from selected servers if it was selected
        setSelectedMcpServers(prev => prev.filter(id => id !== serverId));
        // Refresh the server list
        fetchMcpServers();
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete server');
      }
    } catch (error: any) {
      console.error('Error deleting MCP server:', error);
      toast({
        title: 'Error',
        description: error.message || 'Failed to delete MCP server',
        variant: 'destructive',
      });
    } finally {
      setDeletingServerId(null);
    }
  };

  const handleReconnectMcpServer = async (serverId: string, serverName: string) => {
    setReconnectingServerId(serverId);

    try {
      toast({
        title: 'Connecting...',
        description: `Attempting to connect to ${serverName}`,
      });

      const response = await fetch(`http://localhost:8000/api/v1/mcp-servers/${serverId}/connect`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: 'Connected!',
          description: `Successfully connected to ${serverName}. Found ${data.tools_count || 0} tools.`,
        });
        // Refresh the server list to show updated status
        fetchMcpServers();
      } else {
        const error = await response.json();
        toast({
          title: 'Connection Failed',
          description: error.detail || 'Failed to connect to MCP server',
          variant: 'destructive',
        });
      }
    } catch (error: any) {
      console.error('Error reconnecting to MCP server:', error);
      toast({
        title: 'Connection Error',
        description: error.message || 'Failed to connect to MCP server',
        variant: 'destructive',
      });
    } finally {
      setReconnectingServerId(null);
    }
  };

  const handleProviderChange = (provider: string) => {
    setLlmProvider(provider);
    // Model will be set automatically by the useEffect above
  };

  const handleToolToggle = (toolId: string) => {
    setSelectedTools(prev =>
      prev.includes(toolId)
        ? prev.filter(id => id !== toolId)
        : [...prev, toolId]
    );
  };

  const handleToolsToggle = (toolId: string) => {
    setSelectedToolsList(prev => {
      const isSelected = prev.includes(toolId);

      if (isSelected) {
        // Deselecting - remove from list and configs
        const newConfigs = { ...toolConfigs };
        delete newConfigs[toolId];
        setToolConfigs(newConfigs);
        return prev.filter(id => id !== toolId);
      } else {
        // Selecting - add to list and show config if needed
        const tool = TOOLS.find(t => t.id === toolId);
        if (tool?.requiresConfig) {
          setShowToolConfig(toolId);
        }
        return [...prev, toolId];
      }
    });
  };

  const handleToolConfigSave = (toolId: string, config: any) => {
    setToolConfigs(prev => ({
      ...prev,
      [toolId]: config
    }));
    setShowToolConfig(null);
  };

  const handlePIIToggle = (piiId: string) => {
    setBlockedPII(prev =>
      prev.includes(piiId)
        ? prev.filter(id => id !== piiId)
        : [...prev, piiId]
    );
  };

  const handleAddCustomPII = () => {
    if (!newPIILabel.trim()) {
      toast({
        title: "Label required",
        description: "Please provide a label for the custom PII category",
        variant: "destructive",
      });
      return;
    }

    const customId = `pii_custom_${Date.now()}`;
    setCustomPII(prev => [
      ...prev,
      {
        id: customId,
        label: newPIILabel.trim(),
        description: newPIIDescription.trim() || "Custom PII category",
        pattern: newPIIPattern.trim() || generatePatternFromLabel(newPIILabel.trim())
      }
    ]);
    setNewPIILabel("");
    setNewPIIDescription("");
    setNewPIIPattern("");
    setShowCustomPIIForm(false);
    toast({
      title: "Custom PII Added",
      description: `${newPIILabel} has been added to PII controls`,
    });
  };

  const generatePatternFromLabel = (label: string): string => {
    const patterns: Record<string, string> = {
      "employee id": "EMP-\\d{5}",
      "badge number": "BDG-\\d{5}",
      "customer id": "CUST-\\d{6}",
      "order number": "ORD-\\d{8}",
      "ticket number": "TKT-\\d{6}",
      "license plate": "[A-Z]{3}-\\d{4}",
      "patient id": "PAT-\\d{7}",
      "student id": "STU-\\d{7}",
      "member number": "MBR-\\d{9}",
      "invoice number": "INV-\\d{6}",
      "account number": "ACC-\\d{8}",
      "policy number": "POL-\\d{9}",
      "claim number": "CLM-\\d{7}",
      "reference number": "REF-\\d{10}",
      "tracking number": "TRK-\\d{12}"
    };

    const normalizedLabel = label.toLowerCase().trim();
    return patterns[normalizedLabel] || `${label.replace(/\s+/g, '-').toUpperCase()}-\\d{5}`;
  };

  const handleGenerateAgent = async () => {
    if (!agentName.trim()) {
      toast({
        title: "Agent name required",
        description: "Please provide a name for your agent",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);

    // Build PII configuration only if user selected something
    let pii_config = null;
    if (blockedPII.length > 0 || customPII.length > 0) {
      pii_config = {
        blocked_pii_types: blockedPII,
        custom_pii_categories: customPII.map(pii => ({
          id: pii.id,
          label: pii.label,
          description: pii.description,
          pattern: (pii as any).pattern || generatePatternFromLabel(pii.label)
        })),
        strategy: piiStrategy,
        apply_to_output: true,  // Always enable output filtering when PII types are selected
        apply_to_tool_results: false
      };
    }

    const config = {
      name: agentName,
      agent_type: agentType,
      agent_framework: agentFramework,
      llm_provider: llmProvider,
      llm_model: llmModel,
      temperature: temperature[0],
      system_prompt: systemPrompt,
      tools: selectedToolsList.length > 0 ? selectedToolsList : selectedTools,
      tool_configs: Object.keys(toolConfigs).length > 0 ? toolConfigs : null,
      max_iterations: parseInt(maxIterations),
      memory_type: memoryType,
      streaming_enabled: streamingEnabled,
      human_in_loop: humanInLoop,
      recursion_limit: parseInt(recursionLimit),
      pii_config: pii_config,
      mcp_server_configs: selectedMcpServers.length > 0
        ? selectedMcpServers.map(serverId => ({
          server_id: serverId,
          selected_tools: mcpServerConfigs[serverId] || null
        }))
        : null,
      api_key: providerApiKey || ""  // Include API key if provided, empty string otherwise
    };

    try {
      const url = isEditMode
        ? `http://localhost:8000/api/v1/agents/${editAgentId}`
        : 'http://localhost:8000/api/v1/agents/';
      const method = isEditMode ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (response.ok) {
        const agent = await response.json();
        console.log(isEditMode ? "Agent updated successfully:" : "Agent created successfully:", agent);

        // Create knowledge base if any knowledge is provided (text, links, or files)
        if (knowledgeText || knowledgeLinks || knowledgeFiles.length > 0) {
          try {
            // Create knowledge base
            const kbResponse = await fetch('http://localhost:8000/api/v1/knowledge-bases/', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                agent_id: agent.agent_id,
                name: `${agentName} Knowledge Base`,
                description: `Knowledge base for ${agentName}`,
              }),
            });

            if (kbResponse.ok) {
              const kb = await kbResponse.json();

              // Add text documents (if provided)
              if (knowledgeText) {
                const formData = new FormData();
                formData.append('text', knowledgeText);

                await fetch(`http://localhost:8000/api/v1/knowledge-bases/${kb.kb_id}/documents/text`, {
                  method: 'POST',
                  body: formData,
                });
              }

              // Add URL documents (if provided)
              if (knowledgeLinks) {
                const urls = knowledgeLinks.split('\n').filter(url => url.trim());
                for (const url of urls) {
                  const formData = new FormData();
                  formData.append('url', url.trim());

                  await fetch(`http://localhost:8000/api/v1/knowledge-bases/${kb.kb_id}/documents/url`, {
                    method: 'POST',
                    body: formData,
                  });
                }
              }

              // Upload files (if provided)
              if (knowledgeFiles.length > 0) {
                for (const file of knowledgeFiles) {
                  const formData = new FormData();
                  formData.append('file', file);
                  await fetch(`http://localhost:8000/api/v1/knowledge-bases/${kb.kb_id}/documents/file`, {
                    method: 'POST',
                    body: formData,
                  });
                }
              }

              console.log("Knowledge base created successfully:", kb);
            }
          } catch (kbError) {
            console.error("Error creating knowledge base:", kbError);
          }
        }

        toast({
          title: isEditMode ? "Agent Updated! 🎉" : "Agent Created! 🎉",
          description: isEditMode
            ? `${agentName} has been updated successfully`
            : `${agentName} configured with ${agentType} architecture and ID: ${agent.agent_id}`,
        });
        // Reset form after successful creation or navigate back after update
        if (isEditMode) {
          navigate('/');
        } else {
          setAgentName("");
          setSystemPrompt("");
          setSelectedTools([]);
          setKnowledgeText("");
          setKnowledgeLinks("");
          setKnowledgeFiles([]);
          setBlockedPII([]);
          setCustomPII([]);
          setPIIStrategy("redact");
        }
      } else {
        const errorData = await response.json();
        const errorMessage = typeof errorData.detail === 'string'
          ? errorData.detail
          : JSON.stringify(errorData.detail || errorData);
        throw new Error(errorMessage);
      }
    } catch (error: any) {
      console.error(isEditMode ? "Error updating agent:" : "Error creating agent:", error);

      // Extract a meaningful error message
      let errorMessage = isEditMode ? "Failed to update agent. Please try again." : "Failed to create agent. Please try again.";

      if (error.message) {
        // If it's a string, use it directly
        if (typeof error.message === 'string') {
          errorMessage = error.message;
        } else {
          // If it's an object, try to stringify it
          try {
            errorMessage = JSON.stringify(error.message);
          } catch {
            errorMessage = String(error.message);
          }
        }
      }

      toast({
        title: isEditMode ? "Error Updating Agent" : "Error Creating Agent",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-background pb-24">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">{isEditMode ? 'Edit Agent' : 'New Agent'}</h1>
            <p className="text-muted-foreground mt-1 text-lg">
              {isEditMode ? 'Refine your agent\'s capabilities' : 'Design your custom AI agent'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" onClick={() => navigate('/')}>
              Cancel
            </Button>
          </div>
        </div>

        <Tabs defaultValue="general" className="w-full space-y-8">
          <div className="sticky top-0 z-10 bg-background/95 backdrop-blur py-4 -mx-4 px-4 border-b mb-8">
            <TabsList className="w-full justify-start h-auto p-1 bg-muted/50 rounded-full">
              <TabsTrigger value="general" className="rounded-full px-6 py-2.5 data-[state=active]:bg-background data-[state=active]:shadow-sm">
                <Brain className="w-4 h-4 mr-2" />
                General
              </TabsTrigger>
              <TabsTrigger value="capabilities" className="rounded-full px-6 py-2.5 data-[state=active]:bg-background data-[state=active]:shadow-sm">
                <Wrench className="w-4 h-4 mr-2" />
                Capabilities
              </TabsTrigger>
              <TabsTrigger value="knowledge" className="rounded-full px-6 py-2.5 data-[state=active]:bg-background data-[state=active]:shadow-sm">
                <Database className="w-4 h-4 mr-2" />
                Knowledge
              </TabsTrigger>
              <TabsTrigger value="settings" className="rounded-full px-6 py-2.5 data-[state=active]:bg-background data-[state=active]:shadow-sm">
                <Settings2 className="w-4 h-4 mr-2" />
                Settings
              </TabsTrigger>
            </TabsList>
          </div>

          {/* General Tab */}
          <TabsContent value="general" className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="grid gap-6">
              <div className="space-y-2">
                <Label htmlFor="agent-name" className="text-base font-medium">Name & Identity</Label>
                <Input
                  id="agent-name"
                  placeholder="e.g. Research Assistant"
                  value={agentName}
                  onChange={(e) => setAgentName(e.target.value)}
                  className="h-12 text-lg px-4 bg-muted/30 border-transparent focus:border-primary focus:bg-background transition-all"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="system-prompt" className="text-base font-medium">System Instructions</Label>
                <Textarea
                  id="system-prompt"
                  placeholder="You are a helpful AI assistant that..."
                  value={systemPrompt}
                  onChange={(e) => setSystemPrompt(e.target.value)}
                  className="min-h-[200px] bg-muted/30 border-transparent focus:border-primary focus:bg-background resize-none text-base leading-relaxed p-4 transition-all"
                />
              </div>

              <div className="p-6 rounded-xl bg-muted/30 border border-border/50 space-y-6">
                <div className="flex items-center gap-2 mb-4">
                  <Cpu className="w-5 h-5 text-primary" />
                  <h3 className="font-medium text-lg">Model Configuration</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>Provider</Label>
                    <Select value={llmProvider} onValueChange={handleProviderChange}>
                      <SelectTrigger className="h-10 bg-background border-border/50">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {LLM_PROVIDERS.map(p => (
                          <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <Label>Model</Label>
                      {isUsingApiKey && (
                        <span className="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-2 py-0.5 rounded">
                          Live API
                        </span>
                      )}
                    </div>
                    <Select value={llmModel} onValueChange={setLlmModel} disabled={loadingModels || availableModels.length === 0}>
                      <SelectTrigger className="h-10 bg-background border-border/50">
                        <SelectValue placeholder={loadingModels ? "Loading..." : "Select model"} />
                      </SelectTrigger>
                      <SelectContent>
                        {availableModels.length > 0 ? (
                          <>
                            <div className="px-2 pb-1">
                              <Input
                                type="text"
                                placeholder="Search models..."
                                value={modelSearch}
                                onChange={(e) => setModelSearch(e.target.value)}
                                onKeyDown={(e) => e.stopPropagation()}
                                className="h-8 text-xs"
                              />
                            </div>
                            {filteredModels.length > 0 ? (
                              filteredModels.map((model) => (
                                <SelectItem key={model} value={model}>
                                  {model}
                                </SelectItem>
                              ))
                            ) : (
                              <SelectItem value="no-results" disabled>
                                No models match "{modelSearch}"
                              </SelectItem>
                            )}
                          </>
                        ) : (
                          <SelectItem value="loading" disabled>
                            {loadingModels ? "Fetching models..." : "Enter API key to fetch models"}
                          </SelectItem>
                        )}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Real-time Model Fetching Section */}
                <div className="p-4 bg-background/50 rounded-lg border border-border/50 space-y-3">
                  <div className="flex items-center gap-2">
                    <RefreshCw className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm font-medium">Fetch Real-Time Models</span>
                  </div>
                  <div className="flex gap-2">
                    <Input
                      type="password"
                      placeholder={`Enter ${llmProvider} API key`}
                      value={providerApiKey}
                      onChange={(e) => setProviderApiKey(e.target.value)}
                      className="h-9 bg-background text-sm flex-1"
                    />
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={fetchModels}
                      disabled={loadingModels}
                    >
                      {loadingModels ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <RefreshCw className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Enter your API key to fetch the latest available models from {llmProvider}.
                  </p>
                </div>

                <div className="space-y-4 pt-2">
                  <div className="flex items-center justify-between">
                    <Label>Creativity (Temperature): {temperature[0]}</Label>
                  </div>
                  <Slider
                    value={temperature}
                    onValueChange={setTemperature}
                    max={2}
                    step={0.1}
                    className="py-2"
                  />
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Capabilities Tab */}
          <TabsContent value="capabilities" className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
                  <Wrench className="w-5 h-5 text-primary" />
                  Built-in Tools
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {TOOLS.map(tool => (
                    <div
                      key={tool.id}
                      onClick={() => handleToolsToggle(tool.id)}
                      className={`
                        relative group cursor-pointer p-4 rounded-xl border transition-all duration-200
                        ${selectedToolsList.includes(tool.id)
                          ? 'bg-primary/5 border-primary shadow-sm'
                          : 'bg-card border-border hover:border-primary/50 hover:shadow-sm'}
                      `}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <span className="text-2xl">{tool.icon}</span>
                        <Checkbox
                          checked={selectedToolsList.includes(tool.id)}
                          className="data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                        />
                      </div>
                      <p className="font-medium text-sm">{tool.label}</p>

                      {tool.requiresConfig && selectedToolsList.includes(tool.id) && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="absolute top-2 right-2 h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                          onClick={(e) => {
                            e.stopPropagation();
                            setShowToolConfig(tool.id);
                          }}
                        >
                          <Settings2 className="w-3 h-3" />
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-6 border-t">
                <h3 className="text-lg font-medium mb-4 flex items-center gap-2">
                  <Server className="w-5 h-5 text-primary" />
                  MCP Servers
                </h3>

                {mcpServers.length === 0 ? (
                  <div className="text-center py-12 bg-muted/30 rounded-xl border border-dashed">
                    <Server className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-50" />
                    <p className="text-muted-foreground mb-4">Connect external tools via MCP</p>
                    <MCPServerModal onServerAdded={fetchMcpServers} />
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Active Servers */}
                    <div className="grid gap-4">
                      {mcpServers.filter(s => s.status === 'active').map(server => (
                        <div key={server.server_id} className="bg-card border rounded-xl overflow-hidden">
                          <div className="flex items-center gap-4 p-4">
                            <Checkbox
                              checked={selectedMcpServers.includes(server.server_id)}
                              onCheckedChange={() => handleMcpServerToggle(server.server_id)}
                            />
                            <div className="flex-1">
                              <h4 className="font-medium">{server.name}</h4>
                              <p className="text-sm text-muted-foreground">{server.description}</p>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="px-2 py-1 rounded text-xs bg-green-100 text-green-700">Active</span>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-muted-foreground hover:text-destructive"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDeleteMcpServer(server.server_id, server.name);
                                }}
                                disabled={deletingServerId === server.server_id}
                              >
                                {deletingServerId === server.server_id ? (
                                  <Loader2 className="w-4 h-4 animate-spin" />
                                ) : (
                                  <Trash2 className="w-4 h-4" />
                                )}
                              </Button>
                            </div>
                          </div>

                          {/* Tool Selector for Active Server */}
                          {selectedMcpServers.includes(server.server_id) && (
                            <div className="border-t bg-muted/10 p-4">
                              <MCPToolSelector
                                serverId={server.server_id}
                                serverName={server.name}
                                initialSelectedTools={mcpServerConfigs[server.server_id]}
                                onToolsChange={(tools) => handleMcpToolsChange(server.server_id, tools)}
                              />
                            </div>
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Inactive Servers */}
                    {mcpServers.filter(s => s.status !== 'active').length > 0 && (
                      <div className="pt-4 border-t">
                        <h4 className="text-sm font-medium text-muted-foreground mb-3">Inactive Servers</h4>
                        <div className="grid gap-3">
                          {mcpServers.filter(s => s.status !== 'active').map(server => (
                            <div key={server.server_id} className="flex items-center justify-between p-3 rounded-lg bg-muted/30 border border-yellow-200/50">
                              <div className="flex items-center gap-3">
                                <span className="font-medium text-sm">{server.name}</span>
                                <span className="px-2 py-0.5 rounded text-xs bg-yellow-100 text-yellow-700">{server.status}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleReconnectMcpServer(server.server_id, server.name)}
                                  disabled={reconnectingServerId === server.server_id}
                                >
                                  {reconnectingServerId === server.server_id ? (
                                    <Loader2 className="w-3 h-3 animate-spin mr-2" />
                                  ) : (
                                    <RefreshCw className="w-3 h-3 mr-2" />
                                  )}
                                  Reconnect
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8 text-muted-foreground hover:text-destructive"
                                  onClick={() => handleDeleteMcpServer(server.server_id, server.name)}
                                  disabled={deletingServerId === server.server_id}
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex justify-center mt-4">
                      <MCPServerModal onServerAdded={fetchMcpServers} />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </TabsContent>

          {/* Knowledge Tab */}
          <TabsContent value="knowledge" className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="grid gap-6">
              <div className="flex gap-2 p-1 bg-muted/30 rounded-lg w-fit">
                <Button
                  variant={knowledgeMode === "text" ? "secondary" : "ghost"}
                  onClick={() => setKnowledgeMode("text")}
                  size="sm"
                >
                  <Type className="w-4 h-4 mr-2" />
                  Text
                </Button>
                <Button
                  variant={knowledgeMode === "links" ? "secondary" : "ghost"}
                  onClick={() => setKnowledgeMode("links")}
                  size="sm"
                >
                  <Link2 className="w-4 h-4 mr-2" />
                  Links
                </Button>
                <Button
                  variant={knowledgeMode === "upload" ? "secondary" : "ghost"}
                  onClick={() => setKnowledgeMode("upload")}
                  size="sm"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Files
                </Button>
              </div>

              <div className="bg-card border rounded-xl p-6 min-h-[300px]">
                {knowledgeMode === "text" && (
                  <div className="space-y-4">
                    <Label>Knowledge Text</Label>
                    <Textarea
                      placeholder="Paste documentation or context here..."
                      value={knowledgeText}
                      onChange={(e) => setKnowledgeText(e.target.value)}
                      className="min-h-[200px] resize-none"
                    />
                  </div>
                )}

                {knowledgeMode === "links" && (
                  <div className="space-y-4">
                    <Label>External URLs</Label>
                    <Textarea
                      placeholder="https://..."
                      value={knowledgeLinks}
                      onChange={(e) => setKnowledgeLinks(e.target.value)}
                      className="min-h-[200px] font-mono text-sm"
                    />
                  </div>
                )}

                {knowledgeMode === "upload" && (
                  <div
                    className="border-2 border-dashed rounded-xl h-[200px] flex flex-col items-center justify-center cursor-pointer hover:bg-muted/50 transition-colors"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      multiple
                      className="hidden"
                      onChange={(e) => setKnowledgeFiles(Array.from(e.target.files || []))}
                    />
                    <Upload className="w-10 h-10 text-muted-foreground mb-4" />
                    <p className="font-medium">Drop files or click to upload</p>
                    <p className="text-sm text-muted-foreground mt-1">PDF, TXT, MD, JSON</p>
                    {knowledgeFiles.length > 0 && (
                      <div className="mt-4 flex gap-2 flex-wrap justify-center">
                        {knowledgeFiles.map((f, i) => (
                          <span key={i} className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                            {f.name}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </TabsContent>

          {/* Settings Tab */}
          <TabsContent value="settings" className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="grid gap-6">
              <div className="p-6 rounded-xl border bg-card space-y-6">
                <h3 className="font-medium text-lg flex items-center gap-2">
                  <Shield className="w-5 h-5 text-primary" />
                  Guardrails & Privacy
                </h3>

                <div className="space-y-4">
                  <Label>PII Handling</Label>
                  <Select value={piiStrategy} onValueChange={(v: any) => setPIIStrategy(v)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="redact">Redact (Replace with placeholder)</SelectItem>
                      <SelectItem value="mask">Mask (****1234)</SelectItem>
                      <SelectItem value="hash">Hash (SHA-256)</SelectItem>
                      <SelectItem value="block">Block Request</SelectItem>
                    </SelectContent>
                  </Select>

                  <div className="grid grid-cols-2 gap-3 pt-2">
                    {PII_CATEGORIES.map(pii => (
                      <div key={pii.id} className="flex items-center gap-2 p-3 border rounded-lg hover:bg-muted/50 transition-colors">
                        <Checkbox
                          checked={blockedPII.includes(pii.id)}
                          onCheckedChange={() => handlePIIToggle(pii.id)}
                        />
                        <div className="text-sm">
                          <p className="font-medium">{pii.label}</p>
                          <p className="text-xs text-muted-foreground">{pii.description}</p>
                        </div>
                      </div>
                    ))}
                    {/* Custom PII Categories */}
                    {customPII.map(pii => (
                      <div key={pii.id} className="flex items-center gap-2 p-3 border border-primary/30 bg-primary/5 rounded-lg">
                        <Checkbox
                          checked={blockedPII.includes(pii.id)}
                          onCheckedChange={() => handlePIIToggle(pii.id)}
                        />
                        <div className="flex-1 text-sm">
                          <p className="font-medium">{pii.label}</p>
                          <p className="text-xs text-muted-foreground">{pii.description}</p>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6 text-muted-foreground hover:text-destructive"
                          onClick={() => {
                            setCustomPII(prev => prev.filter(p => p.id !== pii.id));
                            setBlockedPII(prev => prev.filter(id => id !== pii.id));
                          }}
                        >
                          <X className="w-3 h-3" />
                        </Button>
                      </div>
                    ))}
                  </div>

                  {/* Add Custom PII Form */}
                  <div className="pt-4 border-t">
                    {showCustomPIIForm ? (
                      <div className="p-4 bg-muted/30 rounded-lg space-y-3">
                        <div className="grid grid-cols-2 gap-3">
                          <div className="space-y-1">
                            <Label className="text-xs">Category Name</Label>
                            <Input
                              value={newPIILabel}
                              onChange={(e) => setNewPIILabel(e.target.value)}
                              placeholder="e.g. License Plate"
                              className="h-8"
                            />
                          </div>
                          <div className="space-y-1">
                            <Label className="text-xs">Description</Label>
                            <Input
                              value={newPIIDescription}
                              onChange={(e) => setNewPIIDescription(e.target.value)}
                              placeholder="Optional description"
                              className="h-8"
                            />
                          </div>
                          <div className="space-y-1 col-span-2">
                            <Label className="text-xs">Regex Pattern (Optional)</Label>
                            <Input
                              value={newPIIPattern}
                              onChange={(e) => setNewPIIPattern(e.target.value)}
                              placeholder="e.g. ^[A-Z]{3}-\d{3}$ (Leave empty to auto-generate)"
                              className="h-8 font-mono text-xs"
                            />
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button size="sm" onClick={handleAddCustomPII} className="flex-1">Add Category</Button>
                          <Button size="sm" variant="ghost" onClick={() => setShowCustomPIIForm(false)}>Cancel</Button>
                        </div>
                      </div>
                    ) : (
                      <Button variant="outline" size="sm" className="w-full" onClick={() => setShowCustomPIIForm(true)}>
                        <Plus className="w-3 h-3 mr-2" />
                        Add Custom PII Category
                      </Button>
                    )}
                  </div>
                </div>
              </div>

              <div className="p-6 rounded-xl border bg-card space-y-6">
                <h3 className="font-medium text-lg flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-primary" />
                  Advanced Execution
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>Architecture</Label>
                    <Select value={agentType} onValueChange={setAgentType}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {AGENT_TYPES.map(t => (
                          <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Framework</Label>
                    <Select value={agentFramework} onValueChange={setAgentFramework}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {AGENT_FRAMEWORKS.map(f => (
                          <SelectItem key={f.value} value={f.value}>{f.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Memory Type</Label>
                    <Select value={memoryType} onValueChange={setMemoryType}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {MEMORY_TYPES.map(t => (
                          <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Max Iterations</Label>
                    <Input
                      type="number"
                      value={maxIterations}
                      onChange={(e) => setMaxIterations(e.target.value)}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Recursion Limit</Label>
                    <Input
                      type="number"
                      value={recursionLimit}
                      onChange={(e) => setRecursionLimit(e.target.value)}
                    />
                  </div>

                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <Label>Human in the Loop</Label>
                    <Switch checked={humanInLoop} onCheckedChange={setHumanInLoop} />
                  </div>

                  <div className="flex items-center justify-between p-3 border rounded-lg">
                    <Label>Enable Streaming</Label>
                    <Switch checked={streamingEnabled} onCheckedChange={setStreamingEnabled} />
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Floating Action Bar */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
        <div className="bg-background/80 backdrop-blur-xl border shadow-2xl rounded-full p-2 pl-6 flex items-center gap-4">
          <span className="text-sm font-medium text-muted-foreground hidden sm:inline-block">
            {isEditMode ? 'Unsaved changes' : 'Ready to create'}
          </span>
          <Button
            size="lg"
            className="rounded-full px-8 shadow-lg hover:shadow-primary/25 transition-all"
            onClick={handleGenerateAgent}
            disabled={loading}
          >
            {loading ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4 mr-2" />
            )}
            {isEditMode ? 'Update Agent' : 'Create Agent'}
          </Button>
        </div>
      </div>

      {/* Tool Config Dialog */}
      {showToolConfig && (
        <ToolConfigDialog
          toolId={showToolConfig}
          toolLabel={TOOLS.find(t => t.id === showToolConfig)?.label || "Tool"}
          onSave={handleToolConfigSave}
          onClose={() => setShowToolConfig(null)}
          existingConfig={toolConfigs[showToolConfig]}
        />
      )}
    </div>
  );
}
