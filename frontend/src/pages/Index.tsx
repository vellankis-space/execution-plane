import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Brain, Network, Plus, ArrowRight, Activity, Sparkles, Zap, TrendingUp } from "lucide-react";
import { Link } from "react-router-dom";
import { AgentList } from "@/components/AgentList";
import { WorkflowList } from "@/components/workflow/WorkflowList";

export default function Index() {
  const [activeTab, setActiveTab] = useState<"agents" | "workflows">("agents");

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Header Section */}
      <div className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-30">
        <div className="container mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center shadow-lg shadow-primary/25">
                <Sparkles className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">Orchestration Dashboard</h1>
                <p className="text-sm text-muted-foreground">
                  Manage and monitor your AI agents and workflows
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <Button variant="outline" size="sm" asChild className="shine-effect">
                <Link to="/playground">
                  <Plus className="w-4 h-4 mr-2" />
                  New Agent
                </Link>
              </Button>
              <Button size="sm" asChild className="shine-effect bg-gradient-to-r from-primary to-primary/90">
                <Link to="/production-workflow">
                  <Plus className="w-4 h-4 mr-2" />
                  New Workflow
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-8 py-8 space-y-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="group relative overflow-hidden border-border/50 bg-gradient-to-br from-card to-card/50 hover:shadow-xl transition-all duration-300 hover:scale-[1.02]">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="p-6 relative">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Agents</p>
                  <p className="text-3xl font-bold mt-2 bg-gradient-to-br from-foreground to-foreground/70 bg-clip-text text-transparent">
                    12
                  </p>
                  <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3 text-green-500" />
                    <span className="text-green-500">+3</span> this week
                  </p>
                </div>
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/20 to-blue-600/20 flex items-center justify-center">
                  <Brain className="w-6 h-6 text-blue-500" />
                </div>
              </div>
            </div>
          </Card>

          <Card className="group relative overflow-hidden border-border/50 bg-gradient-to-br from-card to-card/50 hover:shadow-xl transition-all duration-300 hover:scale-[1.02]">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="p-6 relative">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Active Workflows</p>
                  <p className="text-3xl font-bold mt-2 bg-gradient-to-br from-foreground to-foreground/70 bg-clip-text text-transparent">
                    8
                  </p>
                  <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3 text-green-500" />
                    <span className="text-green-500">+2</span> this week
                  </p>
                </div>
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500/20 to-purple-600/20 flex items-center justify-center">
                  <Network className="w-6 h-6 text-purple-500" />
                </div>
              </div>
            </div>
          </Card>

          <Card className="group relative overflow-hidden border-border/50 bg-gradient-to-br from-card to-card/50 hover:shadow-xl transition-all duration-300 hover:scale-[1.02]">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
            <div className="p-6 relative">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Executions Today</p>
                  <p className="text-3xl font-bold mt-2 bg-gradient-to-br from-foreground to-foreground/70 bg-clip-text text-transparent">
                    156
                  </p>
                  <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                    <Zap className="w-3 h-3 text-amber-500" />
                    <span className="text-amber-500">Real-time</span>
                  </p>
                </div>
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500/20 to-amber-600/20 flex items-center justify-center">
                  <Activity className="w-6 h-6 text-amber-500" />
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link to="/agents">
            <Card className="group p-6 hover:shadow-2xl transition-all duration-300 border-border/50 hover:border-primary/50 bg-gradient-to-br from-card to-card/50 cursor-pointer relative overflow-hidden h-full">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="relative">
                <div className="flex items-start gap-4">
                  <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-blue-500/20 to-blue-600/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Brain className="w-7 h-7 text-blue-500" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xl font-semibold">Agents</h3>
                      <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                    </div>
                    <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                      Create and manage individual AI agents with specific capabilities and tools
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          </Link>

          <Link to="/workflows">
            <Card className="group p-6 hover:shadow-2xl transition-all duration-300 border-border/50 hover:border-primary/50 bg-gradient-to-br from-card to-card/50 cursor-pointer relative overflow-hidden h-full">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="relative">
                <div className="flex items-start gap-4">
                  <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-purple-500/20 to-purple-600/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Network className="w-7 h-7 text-purple-500" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xl font-semibold">Workflows</h3>
                      <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                    </div>
                    <p className="text-sm text-muted-foreground mt-2 leading-relaxed">
                      Orchestrate multiple agents to collaborate on complex multi-step tasks
                    </p>
                  </div>
                </div>
              </div>
            </Card>
          </Link>
        </div>

        {/* Tabs Section */}
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <div className="border-b border-border/50">
            <div className="flex gap-1 p-2">
              <Button
                variant={activeTab === "agents" ? "default" : "ghost"}
                onClick={() => setActiveTab("agents")}
                className="gap-2 flex-1 md:flex-none"
              >
                <Brain className="w-4 h-4" />
                Agents
              </Button>
              <Button
                variant={activeTab === "workflows" ? "default" : "ghost"}
                onClick={() => setActiveTab("workflows")}
                className="gap-2 flex-1 md:flex-none"
              >
                <Network className="w-4 h-4" />
                Workflows
              </Button>
            </div>
          </div>

          <div className="p-6">
            {activeTab === "agents" && <AgentList />}
            {activeTab === "workflows" && <WorkflowList />}
          </div>
        </Card>
      </div>
    </div>
  );
}