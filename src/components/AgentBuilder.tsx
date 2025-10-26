import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Sparkles, Cpu, Database, GitBranch, Settings2, Thermometer, Hash, Layers, Box, FileText } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { ThemeToggle } from "@/components/ThemeToggle";

const LLM_PROVIDERS = [
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
  { value: "google", label: "Google" },
  { value: "cohere", label: "Cohere" },
  { value: "meta", label: "Meta" },
  { value: "mistral", label: "Mistral AI" },
];

const MODELS = {
  openai: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
  anthropic: [
    "claude-sonnet-4-5",
    "claude-opus-4-1",
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
    "gemini-1.5-flash"
  ],
  cohere: ["command-r-plus", "command-r", "command", "command-light"],
  meta: ["llama-3.3-70b", "llama-3.1-405b", "llama-3.1-70b", "llama-3.1-8b"],
  mistral: ["mistral-large", "mistral-medium", "mistral-small", "mixtral-8x7b"],
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

const AVAILABLE_TOOLS = [
  { id: "tavily_search", label: "Tavily Search" },
  { id: "python_repl", label: "Python REPL" },
  { id: "arxiv", label: "arXiv Papers" },
  { id: "wikipedia", label: "Wikipedia" },
  { id: "duckduckgo", label: "DuckDuckGo" },
  { id: "human_approval", label: "Human Approval" },
];

export function AgentBuilder() {
  const [agentName, setAgentName] = useState("");
  const [agentType, setAgentType] = useState("react");
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

  const handleGenerateAgent = () => {
    if (!agentName.trim()) {
      toast({
        title: "Agent name required",
        description: "Please provide a name for your agent",
        variant: "destructive",
      });
      return;
    }

    const config = {
      agentName,
      agentType,
      llmProvider,
      llmModel,
      temperature: temperature[0],
      systemPrompt,
      tools: selectedTools,
      maxIterations: parseInt(maxIterations),
      memoryType,
      streamingEnabled,
      humanInLoop,
      recursionLimit: parseInt(recursionLimit),
    };

    console.log("Generated LangGraph Agent Configuration:", config);
    
    toast({
      title: "Agent Generated! 🎉",
      description: `${agentName} configured with ${agentType} architecture`,
    });
  };

  return (
    <div className="min-h-screen w-full bg-background">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Playground</h1>
            <p className="text-sm text-muted-foreground mt-1">Configure and test your LangGraph agent</p>
          </div>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Button variant="default" size="default" onClick={handleGenerateAgent}>
              <Sparkles className="w-4 h-4 mr-2" />
              Generate Agent
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
              <div className="grid grid-cols-2 gap-4">
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
              </div>
            </div>

            {/* Tools */}
            <div className="border border-border rounded-lg p-5 bg-card">
              <div className="flex items-center gap-2 mb-4">
                <GitBranch className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-sm font-medium">Tools</h3>
              </div>
              <div className="grid grid-cols-3 gap-3">
                {AVAILABLE_TOOLS.map(tool => (
                  <div
                    key={tool.id}
                    className="flex items-center space-x-2 p-2.5 rounded-md border border-border bg-background hover:bg-muted transition-colors cursor-pointer"
                    onClick={() => handleToolToggle(tool.id)}
                  >
                    <Checkbox
                      id={tool.id}
                      checked={selectedTools.includes(tool.id)}
                      onCheckedChange={() => handleToolToggle(tool.id)}
                    />
                    <label htmlFor={tool.id} className="text-xs cursor-pointer flex-1">
                      {tool.label}
                    </label>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Panel - Advanced Settings */}
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
          </div>
        </div>
      </div>
    </div>
  );
}
