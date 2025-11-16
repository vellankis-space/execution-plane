import { WorkflowList } from "@/components/workflow/WorkflowList";
import { Button } from "@/components/ui/button";
import { Plus, Network, GitBranch } from "lucide-react";
import { Link } from "react-router-dom";

export default function Workflows() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Header Section */}
      <div className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-30">
        <div className="container mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/25">
                <Network className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">Workflow Orchestration</h1>
                <p className="text-sm text-muted-foreground">
                  Design and orchestrate complex multi-agent workflows
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <Button variant="outline" size="sm" asChild className="shine-effect">
                <Link to="/workflow-builder">
                  <GitBranch className="w-4 h-4 mr-2" />
                  Builder
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

      <div className="container mx-auto px-8 py-8">
        <WorkflowList />
      </div>
    </div>
  );
}