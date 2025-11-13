import { AgentList } from "@/components/AgentList";
import { Button } from "@/components/ui/button";
import { Plus, Brain } from "lucide-react";
import { Link } from "react-router-dom";

export default function Agents() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Header Section */}
      <div className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-30">
        <div className="container mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/25">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">Agents</h1>
                <p className="text-sm text-muted-foreground">
                  Manage your AI agents and their capabilities
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <Button size="sm" asChild className="shine-effect bg-gradient-to-r from-primary to-primary/90">
                <Link to="/playground">
                  <Plus className="w-4 h-4 mr-2" />
                  New Agent
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-8 py-8">
        <AgentList />
      </div>
    </div>
  );
}
