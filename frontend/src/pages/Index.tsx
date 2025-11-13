import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Bot, Workflow, Plus, ArrowRight, Activity } from "lucide-react";
import { Link } from "react-router-dom";
import { AgentList } from "@/components/AgentList";
import { UserMenu } from "@/components/auth/UserMenu";

export default function Index() {
  const [activeTab, setActiveTab] = useState<"agents" | "workflows">("agents");

  return (
    <div className="container py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Orchestration Platform</h1>
          <p className="text-muted-foreground mt-2">
            Build and manage agentic AI workflows
          </p>
        </div>
        <div className="flex gap-2 items-center">
          <Button variant="outline" asChild>
            <Link to="/monitoring">
              <Activity className="w-4 h-4 mr-2" />
              Monitoring
            </Link>
          </Button>
          <Button asChild>
            <Link to="/workflows">
              <Plus className="w-4 h-4 mr-2" />
              Create Workflow
            </Link>
          </Button>
          <UserMenu />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
              <Bot className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Agents</h3>
              <p className="text-muted-foreground text-sm mt-1">
                Create and manage individual AI agents with specific capabilities
              </p>
              <Button variant="link" className="p-0 mt-2 h-auto" asChild>
                <Link to="/" onClick={(e) => { e.preventDefault(); setActiveTab("agents"); }}>
                  Manage Agents <ArrowRight className="w-4 h-4 ml-1" />
                </Link>
              </Button>
            </div>
          </div>
        </Card>

        <Card className="p-6 hover:shadow-lg transition-shadow">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center">
              <Workflow className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-lg">Workflows</h3>
              <p className="text-muted-foreground text-sm mt-1">
                Orchestrate multiple agents to work together on complex tasks
              </p>
              <Button variant="link" className="p-0 mt-2 h-auto" asChild>
                <Link to="/workflows">
                  Manage Workflows <ArrowRight className="w-4 h-4 ml-1" />
                </Link>
              </Button>
            </div>
          </div>
        </Card>
      </div>

      <div className="border-b mb-6">
        <div className="flex gap-6">
          <Button
            variant={activeTab === "agents" ? "default" : "ghost"}
            onClick={() => setActiveTab("agents")}
            className="px-4"
          >
            <Bot className="w-4 h-4 mr-2" />
            Agents
          </Button>
          <Button
            variant={activeTab === "workflows" ? "default" : "ghost"}
            onClick={() => setActiveTab("workflows")}
            className="px-4"
          >
            <Workflow className="w-4 h-4 mr-2" />
            Workflows
          </Button>
        </div>
      </div>

      {activeTab === "agents" && <AgentList />}
    </div>
  );
}