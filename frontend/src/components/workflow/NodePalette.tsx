import { Card } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Input } from "@/components/ui/input";
import {
  Bot,
  GitBranch,
  Repeat,
  Play,
  Square,
  AlertCircle,
  MessageSquare,
  Monitor,
  Zap,
  Search,
  GripVertical,
  Clock,
  Database,
  Code2,
  Layers,
} from "lucide-react";
import { useState } from "react";

interface NodeTypeConfig {
  type: string;
  label: string;
  icon: React.ElementType;
  description: string;
  category: "trigger" | "agent" | "logic" | "tool" | "human";
}

const nodeTypeConfigs: NodeTypeConfig[] = [
  // Triggers
  {
    type: "startNode",
    label: "Manual Trigger",
    icon: Play,
    description: "Starts the workflow manually",
    category: "trigger",
  },
  {
    type: "chatNode",
    label: "Chat Input",
    icon: MessageSquare,
    description: "Waits for user input",
    category: "trigger",
  },

  // Agents
  {
    type: "agentNode",
    label: "AI Agent",
    icon: Bot,
    description: "Executes an AI task",
    category: "agent",
  },

  // Logic
  {
    type: "groupNode",
    label: "Group",
    icon: Layers,
    description: "Visual container for nodes",
    category: "logic",
  },
  {
    type: "conditionNode",
    label: "Condition / Switch",
    icon: GitBranch,
    description: "If/Else or multi-branch routing",
    category: "logic",
  },
  {
    type: "loopNode",
    label: "Loop",
    icon: Repeat,
    description: "Iterate over items",
    category: "logic",
  },
  {
    type: "errorHandlerNode",
    label: "Error Handler",
    icon: AlertCircle,
    description: "Catch errors",
    category: "logic",
  },

  // Tools
  {
    type: "actionNode",
    label: "Custom Action",
    icon: Zap,
    description: "Run custom script/API",
    category: "tool",
  },
  {
    type: "httpRequestNode",
    label: "HTTP Request",
    icon: Zap,
    description: "Make API calls",
    category: "tool",
  },
  {
    type: "databaseNode",
    label: "Database",
    icon: Database,
    description: "Query database",
    category: "tool",
  },
  {
    type: "transformNode",
    label: "Transform",
    icon: Code2,
    description: "Map & transform data",
    category: "tool",
  },
  {
    type: "filterNode",
    label: "Filter",
    icon: GitBranch,
    description: "Filter data by rules",
    category: "tool",
  },
  {
    type: "mergeNode",
    label: "Merge",
    icon: GitBranch,
    description: "Combine data streams",
    category: "tool",
  },
  {
    type: "delayNode",
    label: "Delay",
    icon: Clock,
    description: "Wait or schedule",
    category: "tool",
  },
  {
    type: "displayNode",
    label: "Display Data",
    icon: Monitor,
    description: "View output data",
    category: "tool",
  },
  {
    type: "endNode",
    label: "End Workflow",
    icon: Square,
    description: "Terminates execution",
    category: "tool",
  },
];

export function NodePalette() {
  const [searchQuery, setSearchQuery] = useState("");

  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData("application/reactflow", nodeType);
    event.dataTransfer.effectAllowed = "move";
  };

  const filteredNodes = nodeTypeConfigs.filter(node =>
    node.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
    node.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderNodeItem = (config: NodeTypeConfig) => {
    const Icon = config.icon;
    return (
      <div
        key={config.type}
        className="flex items-center gap-3 p-2 rounded-md border border-transparent hover:border-border hover:bg-muted/50 cursor-grab active:cursor-grabbing group transition-all"
        draggable
        onDragStart={(e) => onDragStart(e, config.type)}
      >
        <div className="flex items-center justify-center w-8 h-8 rounded bg-background border border-border shadow-sm group-hover:scale-105 transition-transform">
          <Icon className="w-4 h-4 text-muted-foreground group-hover:text-foreground" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium leading-none">{config.label}</div>
          <div className="text-[10px] text-muted-foreground mt-1 truncate">{config.description}</div>
        </div>
        <GripVertical className="w-4 h-4 text-muted-foreground/30 opacity-0 group-hover:opacity-100" />
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-card border-r border-border/50">
      <div className="p-4 border-b border-border/50">
        <h2 className="font-semibold text-sm mb-3">Components</h2>
        <div className="relative">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search nodes..."
            className="pl-8 h-9 bg-muted/30"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2">
          {searchQuery ? (
            <div className="space-y-1">
              {filteredNodes.map(renderNodeItem)}
              {filteredNodes.length === 0 && (
                <div className="p-4 text-center text-xs text-muted-foreground">
                  No components found
                </div>
              )}
            </div>
          ) : (
            <Accordion type="multiple" defaultValue={["trigger", "agent", "logic", "tool"]} className="w-full">
              <AccordionItem value="trigger" className="border-none">
                <AccordionTrigger className="py-2 px-2 hover:bg-muted/30 rounded-md text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Triggers
                </AccordionTrigger>
                <AccordionContent className="pt-1 pb-2 space-y-1">
                  {nodeTypeConfigs.filter(n => n.category === "trigger").map(renderNodeItem)}
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="agent" className="border-none">
                <AccordionTrigger className="py-2 px-2 hover:bg-muted/30 rounded-md text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Agents
                </AccordionTrigger>
                <AccordionContent className="pt-1 pb-2 space-y-1">
                  {nodeTypeConfigs.filter(n => n.category === "agent").map(renderNodeItem)}
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="logic" className="border-none">
                <AccordionTrigger className="py-2 px-2 hover:bg-muted/30 rounded-md text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Logic & Flow
                </AccordionTrigger>
                <AccordionContent className="pt-1 pb-2 space-y-1">
                  {nodeTypeConfigs.filter(n => n.category === "logic").map(renderNodeItem)}
                </AccordionContent>
              </AccordionItem>

              <AccordionItem value="tool" className="border-none">
                <AccordionTrigger className="py-2 px-2 hover:bg-muted/30 rounded-md text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Tools & Utilities
                </AccordionTrigger>
                <AccordionContent className="pt-1 pb-2 space-y-1">
                  {nodeTypeConfigs.filter(n => n.category === "tool" || n.category === "human").map(renderNodeItem)}
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
