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
import { Sparkles, Cpu, MessageSquare, Zap } from "lucide-react";
import { toast } from "@/hooks/use-toast";

const LLM_PROVIDERS = [
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
  { value: "google", label: "Google" },
  { value: "cohere", label: "Cohere" },
];

const MODELS = {
  openai: ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
  anthropic: ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
  google: ["gemini-pro", "gemini-pro-vision"],
  cohere: ["command", "command-light"],
};

const AVAILABLE_TOOLS = [
  { id: "web_search", label: "Web Search", description: "Search the web for information" },
  { id: "calculator", label: "Calculator", description: "Perform mathematical calculations" },
  { id: "code_interpreter", label: "Code Interpreter", description: "Execute and analyze code" },
  { id: "file_reader", label: "File Reader", description: "Read and process files" },
  { id: "data_analysis", label: "Data Analysis", description: "Analyze datasets and generate insights" },
  { id: "image_generation", label: "Image Generation", description: "Generate images from text" },
];

export function AgentBuilder() {
  const [agentName, setAgentName] = useState("");
  const [llmProvider, setLlmProvider] = useState("openai");
  const [llmModel, setLlmModel] = useState("gpt-4");
  const [temperature, setTemperature] = useState([0.7]);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [selectedTools, setSelectedTools] = useState<string[]>([]);
  const [maxIterations, setMaxIterations] = useState("10");
  const [enableCheckpointing, setEnableCheckpointing] = useState(true);
  const [streamingEnabled, setStreamingEnabled] = useState(true);

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
      llmProvider,
      llmModel,
      temperature: temperature[0],
      systemPrompt,
      tools: selectedTools,
      maxIterations: parseInt(maxIterations),
      enableCheckpointing,
      streamingEnabled,
    };

    console.log("Generated Agent Configuration:", config);
    
    toast({
      title: "Agent Generated! 🎉",
      description: `${agentName} is ready to go with ${selectedTools.length} tools enabled`,
    });
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-background via-background to-background/95 relative overflow-hidden">
      {/* Background gradient overlay */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_hsl(263_40%_10%)_0%,_hsl(240_10%_3.9%)_50%)] pointer-events-none" />
      
      <div className="relative z-10 container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="text-center mb-12 pt-8">
          <div className="inline-flex items-center gap-2 mb-4 px-4 py-2 rounded-full bg-primary/10 border border-primary/20">
            <Sparkles className="w-4 h-4 text-accent" />
            <span className="text-sm font-medium text-accent">AI Agent Builder</span>
          </div>
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-foreground via-accent to-primary bg-clip-text text-transparent">
            Build Your Custom Agent
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Configure and deploy powerful AI agents with advanced LangGraph capabilities
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Configuration */}
          <div className="lg:col-span-2 space-y-6">
            {/* Agent Identity */}
            <Card className="p-6 bg-card/50 backdrop-blur-sm border-border shadow-[var(--shadow-card)] hover:shadow-[var(--shadow-glow)] transition-shadow duration-300">
              <div className="flex items-center gap-2 mb-4">
                <Cpu className="w-5 h-5 text-primary" />
                <h2 className="text-xl font-semibold">Agent Identity</h2>
              </div>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="agent-name">Agent Name</Label>
                  <Input
                    id="agent-name"
                    placeholder="e.g., ResearchAssistant"
                    value={agentName}
                    onChange={(e) => setAgentName(e.target.value)}
                    className="mt-2 bg-secondary/50 border-border"
                  />
                </div>
              </div>
            </Card>

            {/* LLM Configuration */}
            <Card className="p-6 bg-card/50 backdrop-blur-sm border-border shadow-[var(--shadow-card)] hover:shadow-[var(--shadow-glow)] transition-shadow duration-300">
              <div className="flex items-center gap-2 mb-4">
                <MessageSquare className="w-5 h-5 text-primary" />
                <h2 className="text-xl font-semibold">LLM Configuration</h2>
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="provider">Provider</Label>
                    <Select value={llmProvider} onValueChange={handleProviderChange}>
                      <SelectTrigger id="provider" className="mt-2 bg-secondary/50 border-border">
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
                    <Label htmlFor="model">Model</Label>
                    <Select value={llmModel} onValueChange={setLlmModel}>
                      <SelectTrigger id="model" className="mt-2 bg-secondary/50 border-border">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {MODELS[llmProvider as keyof typeof MODELS].map(model => (
                          <SelectItem key={model} value={model}>
                            {model}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label htmlFor="temperature">Temperature: {temperature[0].toFixed(2)}</Label>
                  <Slider
                    id="temperature"
                    min={0}
                    max={2}
                    step={0.1}
                    value={temperature}
                    onValueChange={setTemperature}
                    className="mt-2"
                  />
                  <div className="flex justify-between text-xs text-muted-foreground mt-1">
                    <span>Focused</span>
                    <span>Creative</span>
                  </div>
                </div>
              </div>
            </Card>

            {/* System Prompt */}
            <Card className="p-6 bg-card/50 backdrop-blur-sm border-border shadow-[var(--shadow-card)] hover:shadow-[var(--shadow-glow)] transition-shadow duration-300">
              <div className="flex items-center gap-2 mb-4">
                <MessageSquare className="w-5 h-5 text-primary" />
                <h2 className="text-xl font-semibold">System Prompt</h2>
              </div>
              <Textarea
                placeholder="You are a helpful AI assistant that..."
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                className="min-h-[120px] bg-secondary/50 border-border resize-none"
              />
            </Card>

            {/* Tools Selection */}
            <Card className="p-6 bg-card/50 backdrop-blur-sm border-border shadow-[var(--shadow-card)] hover:shadow-[var(--shadow-glow)] transition-shadow duration-300">
              <div className="flex items-center gap-2 mb-4">
                <Zap className="w-5 h-5 text-primary" />
                <h2 className="text-xl font-semibold">Available Tools</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {AVAILABLE_TOOLS.map(tool => (
                  <div
                    key={tool.id}
                    className="flex items-start space-x-3 p-3 rounded-lg border border-border bg-secondary/30 hover:bg-secondary/50 transition-colors cursor-pointer"
                    onClick={() => handleToolToggle(tool.id)}
                  >
                    <Checkbox
                      id={tool.id}
                      checked={selectedTools.includes(tool.id)}
                      onCheckedChange={() => handleToolToggle(tool.id)}
                    />
                    <div className="flex-1">
                      <label htmlFor={tool.id} className="text-sm font-medium cursor-pointer">
                        {tool.label}
                      </label>
                      <p className="text-xs text-muted-foreground mt-1">{tool.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Sidebar - Execution Settings & Generate */}
          <div className="lg:col-span-1 space-y-6">
            {/* Execution Settings */}
            <Card className="p-6 bg-card/50 backdrop-blur-sm border-border shadow-[var(--shadow-card)] sticky top-6">
              <div className="flex items-center gap-2 mb-4">
                <Zap className="w-5 h-5 text-primary" />
                <h2 className="text-xl font-semibold">Execution</h2>
              </div>
              <div className="space-y-6">
                <div>
                  <Label htmlFor="max-iterations">Max Iterations</Label>
                  <Input
                    id="max-iterations"
                    type="number"
                    min="1"
                    value={maxIterations}
                    onChange={(e) => setMaxIterations(e.target.value)}
                    className="mt-2 bg-secondary/50 border-border"
                  />
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="checkpointing">Checkpointing</Label>
                      <p className="text-xs text-muted-foreground">Enable MemorySaver</p>
                    </div>
                    <Switch
                      id="checkpointing"
                      checked={enableCheckpointing}
                      onCheckedChange={setEnableCheckpointing}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="streaming">Streaming</Label>
                      <p className="text-xs text-muted-foreground">Real-time responses</p>
                    </div>
                    <Switch
                      id="streaming"
                      checked={streamingEnabled}
                      onCheckedChange={setStreamingEnabled}
                    />
                  </div>
                </div>

                <div className="pt-6 border-t border-border">
                  <Button
                    variant="hero"
                    size="xl"
                    className="w-full"
                    onClick={handleGenerateAgent}
                  >
                    <Sparkles className="w-5 h-5 mr-2" />
                    Generate Agent
                  </Button>
                </div>
              </div>
            </Card>

            {/* Quick Stats */}
            <Card className="p-6 bg-card/50 backdrop-blur-sm border-border shadow-[var(--shadow-card)]">
              <h3 className="text-sm font-medium text-muted-foreground mb-4">Configuration Summary</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Provider</span>
                  <span className="font-medium">{llmProvider}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Model</span>
                  <span className="font-medium">{llmModel}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Tools Enabled</span>
                  <span className="font-medium">{selectedTools.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Temperature</span>
                  <span className="font-medium">{temperature[0].toFixed(2)}</span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
