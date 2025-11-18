import { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Play, Pause, RotateCcw, ZoomIn, ZoomOut } from "lucide-react";

interface WorkflowStep {
  id: string;
  name: string;
  agent_id: string;
  description: string;
  position?: { x: number; y: number };
}

interface WorkflowVisualizationProps {
  steps: WorkflowStep[];
  dependencies?: Record<string, string[]>;
  executionStatus?: Record<string, "pending" | "running" | "completed" | "failed">;
  onStepClick?: (stepId: string) => void;
}

export function WorkflowVisualization({
  steps,
  dependencies = {},
  executionStatus = {},
  onStepClick
}: WorkflowVisualizationProps) {
  const [scale, setScale] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const svgRef = useRef<SVGSVGElement>(null);

  // Auto-layout steps if no positions are provided
  const layoutSteps = () => {
    if (steps.length === 0) return [];

    // Simple tree layout algorithm
    const positionedSteps = [...steps];
    const stepMap = Object.fromEntries(steps.map(step => [step.id, step]));
    
    // Assign positions based on dependencies
    const visited = new Set<string>();
    let currentY = 50;
    
    // Find root nodes (no dependencies)
    const rootSteps = steps.filter(step => 
      !Object.values(dependencies).some(deps => deps.includes(step.id))
    );
    
    // Position root nodes
    rootSteps.forEach((step, index) => {
      if (!step.position) {
        stepMap[step.id] = {
          ...step,
          position: { x: 100 + index * 200, y: currentY }
        };
      }
      visited.add(step.id);
    });
    
    currentY += 150;
    
    // Position dependent nodes
    let currentLevel = [...rootSteps.map(s => s.id)];
    while (currentLevel.length > 0 && visited.size < steps.length) {
      const nextLevel = new Set<string>();
      
      currentLevel.forEach(stepId => {
        // Find steps that depend on this step
        Object.entries(dependencies).forEach(([dependentId, deps]) => {
          if (deps.includes(stepId) && !visited.has(dependentId)) {
            // Check if all dependencies are satisfied
            const allDepsSatisfied = deps.every(dep => visited.has(dep));
            if (allDepsSatisfied) {
              nextLevel.add(dependentId);
            }
          }
        });
      });
      
      // Position next level steps
      const nextLevelArray = Array.from(nextLevel);
      nextLevelArray.forEach((stepId, index) => {
        if (!stepMap[stepId].position) {
          stepMap[stepId] = {
            ...stepMap[stepId],
            position: { x: 100 + index * 200, y: currentY }
          };
        }
        visited.add(stepId);
      });
      
      currentLevel = nextLevelArray;
      currentY += 150;
    }
    
    // Position any remaining steps
    steps.forEach(step => {
      if (!stepMap[step.id].position) {
        stepMap[step.id] = {
          ...step,
          position: { x: 100 + Math.random() * 400, y: currentY }
        };
      }
    });
    
    return Object.values(stepMap);
  };

  const positionedSteps = layoutSteps();

  const handleZoomIn = () => {
    setScale(prev => Math.min(prev * 1.2, 3));
  };

  const handleZoomOut = () => {
    setScale(prev => Math.max(prev / 1.2, 0.5));
  };

  const handleResetView = () => {
    setScale(1);
    setPan({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsPanning(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  // Get status color for a step
  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending": return "bg-gray-200";
      case "running": return "bg-blue-500";
      case "completed": return "bg-green-500";
      case "failed": return "bg-red-500";
      default: return "bg-gray-200";
    }
  };

  // Get status text for a step
  const getStatusText = (status: string) => {
    switch (status) {
      case "pending": return "Pending";
      case "running": return "Running";
      case "completed": return "Completed";
      case "failed": return "Failed";
      default: return "Unknown";
    }
  };

  return (
    <Card className="p-4 h-full flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Workflow Visualization</h3>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleZoomIn}>
            <ZoomIn className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={handleZoomOut}>
            <ZoomOut className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="sm" onClick={handleResetView}>
            <RotateCcw className="w-4 h-4" />
          </Button>
        </div>
      </div>
      
      <div className="flex-1 border rounded-lg overflow-hidden relative bg-slate-50 dark:bg-slate-950/60">
        <svg
          ref={svgRef}
          className="w-full h-full"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          <g transform={`translate(${pan.x}, ${pan.y}) scale(${scale})`}>
            {/* Render edges (dependencies) */}
            {Object.entries(dependencies).map(([dependentId, deps]) => {
              const dependentStep = positionedSteps.find(s => s.id === dependentId);
              if (!dependentStep?.position) return null;
              
              return deps.map(depId => {
                const depStep = positionedSteps.find(s => s.id === depId);
                if (!depStep?.position) return null;
                
                return (
                  <line
                    key={`${depId}-${dependentId}`}
                    x1={depStep.position.x + 75}
                    y1={depStep.position.y + 30}
                    x2={dependentStep.position.x + 75}
                    y2={dependentStep.position.y + 30}
                    stroke="#94a3b8"
                    strokeWidth="2"
                    markerEnd="url(#arrowhead)"
                  />
                );
              });
            })}
            
            {/* Render steps as nodes */}
            {positionedSteps.map((step) => {
              const status = executionStatus[step.id] || "pending";
              return (
                <g 
                  key={step.id}
                  transform={`translate(${step.position?.x || 0}, ${step.position?.y || 0})`}
                  onClick={() => onStepClick?.(step.id)}
                  className="cursor-pointer"
                >
                  <rect
                    width="150"
                    height="60"
                    rx="8"
                    className={`${getStatusColor(status)} stroke-2 stroke-gray-300`}
                    fill="white"
                  />
                  <text
                    x="75"
                    y="25"
                    textAnchor="middle"
                    className="text-sm font-medium fill-gray-800"
                  >
                    {step.name}
                  </text>
                  <text
                    x="75"
                    y="45"
                    textAnchor="middle"
                    className="text-xs fill-gray-600"
                  >
                    {step.agent_id || "No agent"}
                  </text>
                  <foreignObject x="5" y="5" width="140" height="20">
                    <div className="flex justify-end">
                      <Badge 
                        className={`text-xs ${status === "completed" ? "bg-green-100 text-green-800" : 
                          status === "running" ? "bg-blue-100 text-blue-800" : 
                          status === "failed" ? "bg-red-100 text-red-800" : 
                          "bg-gray-100 text-gray-800"}`}
                      >
                        {getStatusText(status)}
                      </Badge>
                    </div>
                  </foreignObject>
                </g>
              );
            })}
            
            {/* Arrow marker definition */}
            <defs>
              <marker
                id="arrowhead"
                markerWidth="10"
                markerHeight="7"
                refX="9"
                refY="3.5"
                orient="auto"
              >
                <polygon
                  points="0 0, 10 3.5, 0 7"
                  className="fill-gray-400"
                />
              </marker>
            </defs>
          </g>
        </svg>
      </div>
      
      <div className="mt-4 text-xs text-muted-foreground">
        <p>Click and drag to pan · Use zoom controls to adjust the view</p>
      </div>
    </Card>
  );
}