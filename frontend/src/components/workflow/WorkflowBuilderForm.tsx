import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Plus, Trash2, Play } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { WorkflowVisualization } from "./WorkflowVisualization";

interface WorkflowStep {
  id: string;
  name: string;
  agent_id: string;
  description: string;
}

export function WorkflowBuilderForm() {
  const [workflowName, setWorkflowName] = useState("");
  const [workflowDescription, setWorkflowDescription] = useState("");
  const [steps, setSteps] = useState<WorkflowStep[]>([
    { id: "step-1", name: "Initial Step", agent_id: "", description: "" }
  ]);

  const addStep = () => {
    const newStep: WorkflowStep = {
      id: `step-${steps.length + 1}`,
      name: `Step ${steps.length + 1}`,
      agent_id: "",
      description: ""
    };
    setSteps([...steps, newStep]);
  };

  const removeStep = (id: string) => {
    if (steps.length > 1) {
      setSteps(steps.filter(step => step.id !== id));
    }
  };

  const updateStep = (id: string, field: keyof WorkflowStep, value: string) => {
    setSteps(steps.map(step => 
      step.id === id ? { ...step, [field]: value } : step
    ));
  };

  const handleSaveWorkflow = async () => {
    try {
      // Create workflow definition
      const workflowDefinition = {
        steps: steps.map(step => ({
          id: step.id,
          name: step.name,
          agent_id: step.agent_id,
          description: step.description
        }))
      };

      // Send to backend
      const response = await fetch('http://localhost:8000/api/v1/workflows', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: workflowName,
          description: workflowDescription,
          definition: workflowDefinition
        }),
      });

      if (response.ok) {
        toast({
          title: "Workflow Saved",
          description: "Your workflow has been saved successfully.",
        });
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to save workflow');
      }
    } catch (error: any) {
      console.error("Error saving workflow:", error);
      toast({
        title: "Error Saving Workflow",
        description: error.message || "Failed to save workflow. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Workflow Name</label>
            <Input
              placeholder="Enter workflow name"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              className="mt-1"
            />
          </div>
          
          <div>
            <label className="text-sm font-medium">Description</label>
            <Textarea
              placeholder="Describe what this workflow does"
              value={workflowDescription}
              onChange={(e) => setWorkflowDescription(e.target.value)}
              className="mt-1"
            />
          </div>
        </div>
      </Card>

      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Workflow Steps</h3>
        <Button onClick={addStep} variant="outline" size="sm">
          <Plus className="w-4 h-4 mr-2" />
          Add Step
        </Button>
      </div>

      <div className="space-y-4">
        {steps.map((step, index) => (
          <Card key={step.id} className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-medium">Step {index + 1}: {step.name}</h4>
              {steps.length > 1 && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeStep(step.id)}
                  className="text-muted-foreground hover:text-destructive"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              )}
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Step Name</label>
                <Input
                  placeholder="Enter step name"
                  value={step.name}
                  onChange={(e) => updateStep(step.id, 'name', e.target.value)}
                  className="mt-1"
                />
              </div>
              
              <div>
                <label className="text-sm font-medium">Agent ID</label>
                <Input
                  placeholder="Enter agent ID to use for this step"
                  value={step.agent_id}
                  onChange={(e) => updateStep(step.id, 'agent_id', e.target.value)}
                  className="mt-1"
                />
              </div>
              
              <div>
                <label className="text-sm font-medium">Description</label>
                <Textarea
                  placeholder="Describe what this step does"
                  value={step.description}
                  onChange={(e) => updateStep(step.id, 'description', e.target.value)}
                  className="mt-1"
                />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Workflow Visualization */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Workflow Preview</h3>
        <div className="h-96">
          <WorkflowVisualization 
            steps={steps} 
            dependencies={{}} 
          />
        </div>
      </Card>

      <div className="flex justify-end gap-2">
        <Button variant="outline">Cancel</Button>
        <Button onClick={handleSaveWorkflow}>
          <Play className="w-4 h-4 mr-2" />
          Save Workflow
        </Button>
      </div>
    </div>
  );
}

