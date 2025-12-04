import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Eye, Server, GitBranch } from "lucide-react";
import { ObservabilityAgentView } from "@/components/monitoring/views/ObservabilityAgentView";
import { ObservabilityWorkflowView } from "@/components/monitoring/views/ObservabilityWorkflowView";

export default function Observability() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
            {/* Header Section */}
            <div className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-30">
                <div className="container mx-auto px-8 py-6">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-purple-500/25">
                            <Eye className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold">Observability</h1>
                            <p className="text-sm text-muted-foreground">
                                Deep insights, traces, and debugging for agents and workflows
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="container mx-auto px-8 py-8">
                <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

                    <Tabs defaultValue="agent-level" className="w-full">
                        <TabsList className="w-auto inline-flex bg-muted/50 border border-border/50">
                            <TabsTrigger value="agent-level" className="gap-2">
                                <Server className="w-4 h-4" />
                                Agent Level
                            </TabsTrigger>
                            <TabsTrigger value="workflow-level" className="gap-2">
                                <GitBranch className="w-4 h-4" />
                                Workflow Level
                            </TabsTrigger>
                        </TabsList>

                        <TabsContent value="agent-level" className="mt-6">
                            <ObservabilityAgentView />
                        </TabsContent>

                        <TabsContent value="workflow-level" className="mt-6">
                            <ObservabilityWorkflowView />
                        </TabsContent>
                    </Tabs>
                </div>
            </div>
        </div>
    );
}
