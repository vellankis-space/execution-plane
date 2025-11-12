import { useState } from "react";
import { WorkflowList } from "@/components/workflow/WorkflowList";
import { WorkflowBuilder } from "@/components/workflow/WorkflowBuilder";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Workflows() {
  const [view, setView] = useState<"list" | "builder">("list");
  const navigate = useNavigate();

  return (
    <div className="container py-8">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={() => navigate("/")}
            className="h-8 w-8"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <h1 className="text-3xl font-bold tracking-tight">Workflows</h1>
        </div>
        {view === "list" && (
          <Button onClick={() => setView("builder")}>
            Create Workflow
          </Button>
        )}
        {view === "builder" && (
          <Button variant="outline" onClick={() => setView("list")}>
            Cancel
          </Button>
        )}
      </div>

      {view === "list" && <WorkflowList />}
      {view === "builder" && <WorkflowBuilder />}
    </div>
  );
}