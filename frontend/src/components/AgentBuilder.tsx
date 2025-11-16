import { useState, useRef, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Sparkles, Cpu, Database, GitBranch, Settings2, Thermometer, Hash, Layers, Box, FileText, Key, MessageSquare, Upload, Link2, Type, Brain, Wrench, Shield, Plus, X, Home, Loader2 } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { ThemeToggle } from "@/components/ThemeToggle";
import { ToolConfigDialog } from "@/components/ToolConfigDialog";

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

const MODELS = {
  openai: [
    "gpt-4o",
    "gpt-4o-mini", 
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
    "o1-preview",
    "o1-mini"
  ],
  anthropic: [
    "claude-sonnet-4-5",
    "claude-opus-4-1",
    "claude-3-7-sonnet",
    "claude-3-5-sonnet",
    "claude-3-5-haiku",
    "claude-3-opus",
    "claude-3-sonnet",
    "claude-3-haiku"
  ],
  google: [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b"
  ],
  groq: [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma-2-9b-it",
    "llama-guard-3-8b"
  ],
  openrouter: [
    "anthropic/claude-sonnet-4-5",
    "openai/gpt-4o",
    "google/gemini-2.5-pro",
    "meta-llama/llama-3.3-70b-instruct",
    "anthropic/claude-3-5-haiku",
    "deepseek/deepseek-chat",
    "qwen/qwen-2.5-72b-instruct",
    "mistralai/mistral-large"
  ],
  together: [
    "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
    "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
    "mistralai/Mixtral-8x22B-Instruct-v0.1",
    "deepseek-ai/DeepSeek-V3",
    "Qwen/Qwen2.5-72B-Instruct-Turbo"
  ],
  fireworks: [
    "accounts/fireworks/models/llama-v3p3-70b-instruct",
    "accounts/fireworks/models/llama-v3p1-405b-instruct",
    "accounts/fireworks/models/mixtral-8x22b-instruct",
    "accounts/fireworks/models/qwen2p5-72b-instruct",
    "accounts/fireworks/models/deepseek-v3"
  ],
  cohere: [
    "command-r-plus",
    "command-r",
    "command",
    "command-light",
    "command-r-08-2024",
    "command-r-plus-08-2024"
  ],
  meta: [
    "llama-3.3-70b",
    "llama-3.2-90b-vision",
    "llama-3.1-405b",
    "llama-3.1-70b",
    "llama-3.1-8b"
  ],
  mistral: [
    "mistral-large-2411",
    "mistral-large-2407",
    "mistral-medium",
    "mistral-small",
    "mixtral-8x7b",
    "pixtral-large-2411"
  ],
};

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

const MCP_SERVERS = [
  { id: "mcp_filesystem", label: "Filesystem" },
  { id: "mcp_github", label: "GitHub" },
  { id: "mcp_postgres", label: "PostgreSQL" },
  { id: "mcp_web_search", label: "Web Search" },
  { id: "mcp_slack", label: "Slack" },
  { id: "mcp_brave_search", label: "Brave Search" },
  { id: "mcp_google_maps", label: "Google Maps" },
  { id: "mcp_memory", label: "Memory" },
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
  const [apiKey, setApiKey] = useState("");
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
  const [showCustomPIIForm, setShowCustomPIIForm] = useState(false);
  const [piiStrategy, setPIIStrategy] = useState<"redact" | "mask" | "hash" | "block">("redact");
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  
  // Tool configurations
  const [toolConfigs, setToolConfigs] = useState<Record<string, any>>({});
  const [showToolConfig, setShowToolConfig] = useState<string | null>(null);

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

  const handleProviderChange = (provider: string) => {
    setLlmProvider(provider);
    setLlmModel(MODELS[provider as keyof typeof MODELS][0]);
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
        description: newPIIDescription.trim() || "Custom PII category"
      }
    ]);
    setNewPIILabel("");
    setNewPIIDescription("");
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
          pattern: generatePatternFromLabel(pii.label)
        })),
        strategy: piiStrategy,
        apply_to_output: true,  // Always enable output filtering when PII types are selected
        apply_to_tool_results: false
      };
    }

    const config = {
      name: agentName,
      agent_type: agentType,
      llm_provider: llmProvider,
      llm_model: llmModel,
      api_key: apiKey,
      temperature: temperature[0],
      system_prompt: systemPrompt,
      tools: selectedToolsList.length > 0 ? selectedToolsList : selectedTools,
      tool_configs: Object.keys(toolConfigs).length > 0 ? toolConfigs : null,
      max_iterations: parseInt(maxIterations),
      memory_type: memoryType,
      streaming_enabled: streamingEnabled,
      human_in_loop: humanInLoop,
      recursion_limit: parseInt(recursionLimit),
      pii_config: pii_config
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
        const error = await response.json();
        throw new Error(error.detail || (isEditMode ? 'Failed to update agent' : 'Failed to create agent'));
      }
    } catch (error) {
      console.error(isEditMode ? "Error updating agent:" : "Error creating agent:", error);
      toast({
        title: isEditMode ? "Error Updating Agent" : "Error Creating Agent",
        description: error.message || (isEditMode ? "Failed to update agent. Please try again." : "Failed to create agent. Please try again."),
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-background">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">{isEditMode ? 'Edit Agent' : 'Agent Playground'}</h1>
            <p className="text-sm text-muted-foreground mt-1">{isEditMode ? 'Update your agent configuration' : 'Configure and orchestrate your AI agents'}</p>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Button variant="outline" size="default" onClick={() => navigate('/')}>
              <Home className="w-4 h-4 mr-2" />
              Home
            </Button>
            <Button variant="outline" size="default" onClick={() => navigate('/chat')}>
              <MessageSquare className="w-4 h-4 mr-2" />
              Chat
            </Button>
            <Button variant="default" size="default" onClick={handleGenerateAgent} disabled={loading}>
              {loading ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Sparkles className="w-4 h-4 mr-2" />
              )}
              {loading ? 'Creating...' : (isEditMode ? 'Update Agent' : 'Generate Agent')}
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - System & Model Configuration */}
          <div className="lg:col-span-2 space-y-6">
            {/* Model Selection - Clean horizontal layout */}
            <div className="border border-border rounded-lg p-5 bg-card">
              <div className="flex items-center gap-2 mb-4">
                <Cpu className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-sm font-medium">Model</h3>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="provider" className="text-xs text-muted-foreground mb-2 block">Provider</Label>
                  <Select value={llmProvider} onValueChange={handleProviderChange}>
                    <SelectTrigger id="provider" className="h-9 bg-background">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {LLM_PROVIDERS.map(provider => (
                        <SelectItem key={provider.value} value={provider.value}>
                          {provider.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="model" className="text-xs text-muted-foreground mb-2 block">Model</Label>
                  <Select value={llmModel} onValueChange={setLlmModel}>
                    <SelectTrigger id="model" className="h-9 bg-background">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="max-h-[300px]">
                      {MODELS[llmProvider as keyof typeof MODELS].map(model => (
                        <SelectItem key={model} value={model}>
                          {model}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <div className="flex items-center gap-1.5 mb-2">
                    <Thermometer className="w-3.5 h-3.5 text-muted-foreground" />
                    <Label htmlFor="temperature" className="text-xs text-muted-foreground">
                      Temperature: {temperature[0].toFixed(1)}
                    </Label>
                  </div>
                  <Slider
                    id="temperature"
                    min={0}
                    max={2}
                    step={0.1}
                    value={temperature}
                    onValueChange={setTemperature}
                    className="mt-2"
                  />
                </div>
              </div>
              
              <div className="mt-4">
                <div className="flex items-center gap-1.5 mb-2">
                  <Key className="w-3.5 h-3.5 text-muted-foreground" />
                  <Label htmlFor="api-key" className="text-xs text-muted-foreground">API Key</Label>
                </div>
                <Input
                  id="api-key"
                  type="password"
                  placeholder="sk-..."
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="h-9 bg-background"
                />
              </div>
            </div>

            {/* System Prompt */}
            <div className="border border-border rounded-lg p-5 bg-card">
              <div className="flex items-center gap-2 mb-3">
                <FileText className="w-4 h-4 text-muted-foreground" />
                <Label htmlFor="system-prompt" className="text-sm font-medium">System Instructions</Label>
              </div>
              <Textarea
                id="system-prompt"
                placeholder="You are a helpful AI assistant that..."
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                className="min-h-[120px] bg-background resize-none text-sm"
              />
            </div>

            {/* Agent Configuration */}
            <div className="border border-border rounded-lg p-5 bg-card">
              <div className="flex items-center gap-2 mb-4">
                <Settings2 className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-sm font-medium">Agent Configuration</h3>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <div className="flex items-center gap-1.5 mb-2">
                    <Box className="w-3.5 h-3.5 text-muted-foreground" />
                    <Label htmlFor="agent-name" className="text-xs text-muted-foreground">Agent Name</Label>
                  </div>
                  <Input
                    id="agent-name"
                    placeholder="ResearchAssistant"
                    value={agentName}
                    onChange={(e) => setAgentName(e.target.value)}
                    className="h-9 bg-background"
                  />
                </div>
                <div>
                  <div className="flex items-center gap-1.5 mb-2">
                    <Layers className="w-3.5 h-3.5 text-muted-foreground" />
                    <Label htmlFor="agent-type" className="text-xs text-muted-foreground">Architecture</Label>
                  </div>
                  <Select value={agentType} onValueChange={setAgentType}>
                    <SelectTrigger id="agent-type" className="h-9 bg-background">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {AGENT_TYPES.map(type => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <div className="flex items-center gap-1.5 mb-2">
                    <Brain className="w-3.5 h-3.5 text-muted-foreground" />
                    <Label htmlFor="agent-framework" className="text-xs text-muted-foreground">Framework</Label>
                  </div>
                  <Select value={agentFramework} onValueChange={setAgentFramework}>
                    <SelectTrigger id="agent-framework" className="h-9 bg-background">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {AGENT_FRAMEWORKS.map(framework => (
                        <SelectItem key={framework.value} value={framework.value}>
                          {framework.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            {/* MCP Servers */}
            <div className="border border-border rounded-lg p-5 bg-card">
              <div className="flex items-center gap-2 mb-4">
                <GitBranch className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-sm font-medium">MCP Servers</h3>
                <span className="text-xs text-muted-foreground ml-auto">Model Context Protocol</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {MCP_SERVERS.map(server => (
                  <div
                    key={server.id}
                    className="flex items-center space-x-2 p-2.5 rounded-md border border-border bg-background hover:bg-muted transition-colors cursor-pointer"
                    onClick={() => handleToolToggle(server.id)}
                  >
                    <Checkbox
                      id={server.id}
                      checked={selectedTools.includes(server.id)}
                      onCheckedChange={() => handleToolToggle(server.id)}
                    />
                    <label htmlFor={server.id} className="text-xs cursor-pointer flex-1 leading-tight">
                      {server.label}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Tools */}
            <div className="border border-border rounded-lg p-5 bg-card">
              <div className="flex items-center gap-2 mb-4">
                <Wrench className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-sm font-medium">Tools</h3>
                <span className="text-xs text-muted-foreground ml-auto">Agent Capabilities</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {TOOLS.map(tool => (
                  <div
                    key={tool.id}
                    className="flex items-center space-x-2 p-2.5 rounded-md border border-border bg-background hover:bg-muted transition-colors cursor-pointer relative"
                    onClick={() => handleToolsToggle(tool.id)}
                  >
                    <Checkbox
                      id={tool.id}
                      checked={selectedToolsList.includes(tool.id)}
                      onCheckedChange={() => handleToolsToggle(tool.id)}
                    />
                    <label htmlFor={tool.id} className="text-xs cursor-pointer flex-1 leading-tight">
                      {tool.icon && <span className="mr-1">{tool.icon}</span>}
                      {tool.label}
                    </label>
                    {tool.requiresConfig && selectedToolsList.includes(tool.id) && (
                      <Settings2 
                        className="w-3.5 h-3.5 text-primary cursor-pointer hover:text-primary/80" 
                        onClick={(e) => {
                          e.stopPropagation();
                          setShowToolConfig(tool.id);
                        }}
                      />
                    )}
                    {tool.requiresConfig && !selectedToolsList.includes(tool.id) && (
                      <Key className="w-3 h-3 text-muted-foreground" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Knowledge Base */}
            <div className="border border-border rounded-lg p-5 bg-card">
              <div className="flex items-center gap-2 mb-4">
                <Database className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-sm font-medium">Knowledge Base</h3>
              </div>
              
              <div className="flex gap-2 mb-4">
                <Button
                  type="button"
                  variant={knowledgeMode === "text" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setKnowledgeMode("text")}
                  className="flex-1"
                >
                  <Type className="w-3.5 h-3.5 mr-1.5" />
                  Text
                </Button>
                <Button
                  type="button"
                  variant={knowledgeMode === "links" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setKnowledgeMode("links")}
                  className="flex-1"
                >
                  <Link2 className="w-3.5 h-3.5 mr-1.5" />
                  Links
                </Button>
                <Button
                  type="button"
                  variant={knowledgeMode === "upload" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setKnowledgeMode("upload")}
                  className="flex-1"
                >
                  <Upload className="w-3.5 h-3.5 mr-1.5" />
                  Upload
                </Button>
              </div>

              {knowledgeMode === "text" && (
                <div>
                  <Label htmlFor="knowledge-text" className="text-xs text-muted-foreground mb-2 block">
                    Paste your text or documentation
                  </Label>
                  <Textarea
                    id="knowledge-text"
                    placeholder="Add context, documentation, or any information the agent should know..."
                    value={knowledgeText}
                    onChange={(e) => setKnowledgeText(e.target.value)}
                    className="min-h-[100px] bg-background resize-none text-sm"
                  />
                </div>
              )}

              {knowledgeMode === "links" && (
                <div>
                  <Label htmlFor="knowledge-links" className="text-xs text-muted-foreground mb-2 block">
                    Add URLs (one per line)
                  </Label>
                  <Textarea
                    id="knowledge-links"
                    placeholder="https://docs.example.com&#x0A;https://github.com/repo&#x0A;https://blog.example.com/article"
                    value={knowledgeLinks}
                    onChange={(e) => setKnowledgeLinks(e.target.value)}
                    className="min-h-[100px] bg-background resize-none text-sm font-mono"
                  />
                </div>
              )}

              {knowledgeMode === "upload" && (
                <div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".pdf,.docx,.txt,.md,.html,.htm,.json"
                    className="hidden"
                    onChange={(e) => {
                      const files = e.target.files ? Array.from(e.target.files) : [];
                      setKnowledgeFiles(files);
                    }}
                  />
                  <div
                    className="border-2 border-dashed border-border rounded-lg p-6 bg-background hover:bg-muted/50 transition-colors cursor-pointer"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <div className="flex flex-col items-center justify-center gap-2 text-center">
                      <Upload className="w-8 h-8 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">Click to select files</p>
                        <p className="text-xs text-muted-foreground mt-1">PDF, DOCX, TXT, MD, HTML, JSON</p>
                      </div>
                    </div>
                  </div>
                  {knowledgeFiles.length > 0 && (
                    <div className="mt-3 text-xs text-muted-foreground">
                      {knowledgeFiles.length} file(s) selected: {knowledgeFiles.map(f => f.name).join(", ")}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* PII Configuration */}
            <div className="border border-border rounded-lg p-5 bg-card">
              <div className="flex items-center gap-2 mb-4">
                <Shield className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-sm font-medium">PII Controls</h3>
                <span className="text-xs text-muted-foreground ml-auto">Privacy Settings</span>
              </div>
              <p className="text-xs text-muted-foreground mb-4">
                Select which Personally Identifiable Information (PII) categories should be blocked/filtered from agent interactions. When PII types are selected, they will be filtered from user input, knowledge base content, conversation memory, and agent responses.
              </p>
              
              {/* PII Strategy Selection */}
              <div className="mb-4 p-3 border border-border rounded-lg bg-background space-y-3">
                <Label className="text-xs text-muted-foreground font-medium">PII Handling Strategy</Label>
                <Select value={piiStrategy} onValueChange={(val) => setPIIStrategy(val as any)}>
                  <SelectTrigger className="h-9 bg-card">
                    <SelectValue placeholder="Select strategy" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="redact">Redact - Replace with [REDACTED_TYPE]</SelectItem>
                    <SelectItem value="mask">Mask - Show last 4 characters (****1234)</SelectItem>
                    <SelectItem value="hash">Hash - Deterministic hash</SelectItem>
                    <SelectItem value="block">Block - Prevent request if PII detected</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2 max-h-[280px] overflow-y-auto pr-1">
                {PII_CATEGORIES.map(pii => (
                  <div
                    key={pii.id}
                    className="flex items-start space-x-3 p-3 rounded-md border border-border bg-background hover:bg-muted transition-colors cursor-pointer"
                    onClick={() => handlePIIToggle(pii.id)}
                  >
                    <Checkbox
                      id={pii.id}
                      checked={blockedPII.includes(pii.id)}
                      onCheckedChange={() => handlePIIToggle(pii.id)}
                      className="mt-0.5"
                    />
                    <div className="flex-1 min-w-0">
                      <label htmlFor={pii.id} className="text-xs font-medium cursor-pointer block">
                        {pii.label}
                      </label>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {pii.description}
                      </p>
                    </div>
                  </div>
                ))}
                
                {customPII.map(pii => (
                  <div
                    key={pii.id}
                    className="flex items-start space-x-3 p-3 rounded-md border border-primary/50 bg-primary/5 hover:bg-primary/10 transition-colors cursor-pointer"
                    onClick={() => handlePIIToggle(pii.id)}
                  >
                    <Checkbox
                      id={pii.id}
                      checked={blockedPII.includes(pii.id)}
                      onCheckedChange={() => handlePIIToggle(pii.id)}
                      className="mt-0.5"
                    />
                    <div className="flex-1 min-w-0">
                      <label htmlFor={pii.id} className="text-xs font-medium cursor-pointer block">
                        {pii.label}
                      </label>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {pii.description}
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setCustomPII(prev => prev.filter(p => p.id !== pii.id));
                        setBlockedPII(prev => prev.filter(id => id !== pii.id));
                      }}
                      className="text-muted-foreground hover:text-destructive transition-colors"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>

              {showCustomPIIForm ? (
                <div className="mt-4 p-4 border border-border rounded-lg bg-background space-y-3">
                  <div>
                    <Label htmlFor="custom-pii-label" className="text-xs text-muted-foreground mb-1.5 block">
                      PII Category Name
                    </Label>
                    <Input
                      id="custom-pii-label"
                      placeholder="e.g., License Number"
                      value={newPIILabel}
                      onChange={(e) => setNewPIILabel(e.target.value)}
                      className="h-9 bg-card"
                    />
                  </div>
                  <div>
                    <Label htmlFor="custom-pii-desc" className="text-xs text-muted-foreground mb-1.5 block">
                      Description (Optional)
                    </Label>
                    <Input
                      id="custom-pii-desc"
                      placeholder="e.g., Driver's license numbers"
                      value={newPIIDescription}
                      onChange={(e) => setNewPIIDescription(e.target.value)}
                      className="h-9 bg-card"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      size="sm"
                      onClick={handleAddCustomPII}
                      className="flex-1"
                    >
                      Add Category
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setShowCustomPIIForm(false);
                        setNewPIILabel("");
                        setNewPIIDescription("");
                      }}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowCustomPIIForm(true)}
                  className="mt-4 w-full"
                >
                  <Plus className="w-3.5 h-3.5 mr-1.5" />
                  Add Custom PII Category
                </Button>
              )}
            </div>
          </div>

          {/* Right Panel - Advanced Settings and Agent List */}
          <div className="space-y-6">
            <div className="border border-border rounded-lg p-5 bg-card">
              <div className="flex items-center gap-2 mb-4">
                <Hash className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-sm font-medium">Execution Settings</h3>
              </div>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="max-iter" className="text-xs text-muted-foreground mb-2 block">Max Iterations</Label>
                  <Input
                    id="max-iter"
                    type="number"
                    min="1"
                    value={maxIterations}
                    onChange={(e) => setMaxIterations(e.target.value)}
                    className="h-9 bg-background"
                  />
                </div>
                <div>
                  <Label htmlFor="recursion" className="text-xs text-muted-foreground mb-2 block">Recursion Limit</Label>
                  <Input
                    id="recursion"
                    type="number"
                    min="1"
                    value={recursionLimit}
                    onChange={(e) => setRecursionLimit(e.target.value)}
                    className="h-9 bg-background"
                  />
                </div>
              </div>
            </div>

            <div className="border border-border rounded-lg p-5 bg-card">
              <div className="flex items-center gap-2 mb-4">
                <Database className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-sm font-medium">Memory & State</h3>
              </div>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="memory" className="text-xs text-muted-foreground mb-2 block">Checkpoint Storage</Label>
                  <Select value={memoryType} onValueChange={setMemoryType}>
                    <SelectTrigger id="memory" className="h-9 bg-background">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {MEMORY_TYPES.map(type => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center justify-between pt-2">
                  <Label htmlFor="streaming" className="text-xs">Enable Streaming</Label>
                  <Switch
                    id="streaming"
                    checked={streamingEnabled}
                    onCheckedChange={setStreamingEnabled}
                  />
                </div>
                <div className="flex items-center justify-between pt-2">
                  <Label htmlFor="human" className="text-xs">Human-in-the-Loop</Label>
                  <Switch
                    id="human"
                    checked={humanInLoop}
                    onCheckedChange={setHumanInLoop}
                  />
                </div>
              </div>
            </div>

            {/* Agent List */}
            {/* Removed AgentList component as requested - it will be moved to the Chat page */}
          </div>
        </div>
      </div>
      
      {/* Tool Configuration Dialog */}
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
