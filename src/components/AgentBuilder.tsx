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
import { Sparkles, Cpu, Database, GitBranch, Settings2 } from "lucide-react";
import { toast } from "@/hooks/use-toast";

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
      <div className="container mx-auto px-4 py-6 max-w-7xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <Sparkles className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h1 className="text-xl font-semibold">Agent Builder</h1>
              <p className="text-xs text-muted-foreground">Configure your LangGraph agent</p>
            </div>
          </div>
          <Button variant="hero" size="lg" onClick={handleGenerateAgent}>
            <Cpu className="w-4 h-4 mr-2" />
            Generate Agent
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - System & Model Configuration */}
          <div className="lg:col-span-2 space-y-4">
            {/* System Prompt - Most prominent like ChatGPT */}
            <div>
              <Label htmlFor="system-prompt" className="text-sm font-medium mb-2 block">System</Label>
              <Textarea
                id="system-prompt"
                placeholder="You are a helpful AI assistant that..."
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                className="min-h-[140px] bg-card border-border resize-none font-mono text-sm"
              />
            </div>

            {/* Model Selection - Clean Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="provider" className="text-sm font-medium mb-2 block">Provider</Label>
                <Select value={llmProvider} onValueChange={handleProviderChange}>
                  <SelectTrigger id="provider" className="bg-card border-border">
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
                <Label htmlFor="model" className="text-sm font-medium mb-2 block">Model</Label>
                <Select value={llmModel} onValueChange={setLlmModel}>
                  <SelectTrigger id="model" className="bg-card border-border">
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
                <Label htmlFor="agent-type" className="text-sm font-medium mb-2 block">Architecture</Label>
                <Select value={agentType} onValueChange={setAgentType}>
                  <SelectTrigger id="agent-type" className="bg-card border-border">
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

            {/* Settings Sections */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Parameters */}
              <Card className="p-4 bg-card border-border">
                <div className="flex items-center gap-2 mb-4">
                  <Settings2 className="w-4 h-4 text-muted-foreground" />
                  <h3 className="text-sm font-medium">Parameters</h3>
                </div>
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <Label htmlFor="temperature" className="text-xs text-muted-foreground">Temperature</Label>
                      <span className="text-xs font-medium">{temperature[0].toFixed(1)}</span>
                    </div>
                    <Slider
                      id="temperature"
                      min={0}
                      max={2}
                      step={0.1}
                      value={temperature}
                      onValueChange={setTemperature}
                    />
                  </div>
                  <div>
                    <Label htmlFor="max-iter" className="text-xs text-muted-foreground mb-2 block">Max Iterations</Label>
                    <Input
                      id="max-iter"
                      type="number"
                      min="1"
                      value={maxIterations}
                      onChange={(e) => setMaxIterations(e.target.value)}
                      className="h-9 bg-secondary/50 border-border"
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
                      className="h-9 bg-secondary/50 border-border"
                    />
                  </div>
                </div>
              </Card>

              {/* Memory & State */}
              <Card className="p-4 bg-card border-border">
                <div className="flex items-center gap-2 mb-4">
                  <Database className="w-4 h-4 text-muted-foreground" />
                  <h3 className="text-sm font-medium">Memory & State</h3>
                </div>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="memory" className="text-xs text-muted-foreground mb-2 block">Checkpoint Storage</Label>
                    <Select value={memoryType} onValueChange={setMemoryType}>
                      <SelectTrigger id="memory" className="bg-secondary/50 border-border">
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
                  <div className="flex items-center justify-between py-2 border-t border-border">
                    <Label htmlFor="streaming" className="text-xs text-muted-foreground">Enable Streaming</Label>
                    <Switch
                      id="streaming"
                      checked={streamingEnabled}
                      onCheckedChange={setStreamingEnabled}
                    />
                  </div>
                  <div className="flex items-center justify-between py-2 border-t border-border">
                    <Label htmlFor="human" className="text-xs text-muted-foreground">Human-in-the-Loop</Label>
                    <Switch
                      id="human"
                      checked={humanInLoop}
                      onCheckedChange={setHumanInLoop}
                    />
                  </div>
                </div>
              </Card>
            </div>

            {/* Tools */}
            <Card className="p-4 bg-card border-border">
              <div className="flex items-center gap-2 mb-4">
                <GitBranch className="w-4 h-4 text-muted-foreground" />
                <h3 className="text-sm font-medium">Tools</h3>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {AVAILABLE_TOOLS.map(tool => (
                  <div
                    key={tool.id}
                    className="flex items-center space-x-2 p-2.5 rounded-md border border-border bg-secondary/30 hover:bg-secondary/50 transition-colors cursor-pointer"
                    onClick={() => handleToolToggle(tool.id)}
                  >
                    <Checkbox
                      id={tool.id}
                      checked={selectedTools.includes(tool.id)}
                      onCheckedChange={() => handleToolToggle(tool.id)}
                    />
                    <label htmlFor={tool.id} className="text-xs font-medium cursor-pointer flex-1">
                      {tool.label}
                    </label>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Right Panel - Configuration */}
          <div className="space-y-4">
            <Card className="p-4 bg-card border-border">
              <h3 className="text-sm font-medium mb-4">Agent Configuration</h3>
              <div className="space-y-3">
                <div>
                  <Label htmlFor="agent-name" className="text-xs text-muted-foreground mb-2 block">Agent Name</Label>
                  <Input
                    id="agent-name"
                    placeholder="ResearchAssistant"
                    value={agentName}
                    onChange={(e) => setAgentName(e.target.value)}
                    className="bg-secondary/50 border-border"
                  />
                </div>
                
                <div className="pt-3 border-t border-border">
                  <h4 className="text-xs font-medium text-muted-foreground mb-3">Summary</h4>
                  <div className="space-y-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Provider</span>
                      <span className="font-medium capitalize">{llmProvider}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Model</span>
                      <span className="font-medium">{llmModel}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Architecture</span>
                      <span className="font-medium">{AGENT_TYPES.find(t => t.value === agentType)?.label}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Tools</span>
                      <span className="font-medium">{selectedTools.length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Temperature</span>
                      <span className="font-medium">{temperature[0].toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Memory</span>
                      <span className="font-medium text-[10px]">{memoryType}</span>
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            <Card className="p-4 bg-muted/30 border-border">
              <h4 className="text-xs font-medium text-muted-foreground mb-2">Ready to Build?</h4>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Your agent will be generated with the selected configuration. All settings can be adjusted after creation.
              </p>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
