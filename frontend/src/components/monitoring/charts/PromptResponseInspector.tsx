import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, Sparkles } from 'lucide-react';
import type { AgentMetrics } from '@/services/observabilityService';

interface PromptResponseInspectorProps {
    metrics: AgentMetrics;
}

export function PromptResponseInspector({ metrics }: PromptResponseInspectorProps) {
    const recentPrompts = metrics.recent_prompts || [];
    const recentResponses = metrics.recent_responses || [];

    if (recentPrompts.length === 0 && recentResponses.length === 0) {
        return (
            <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                <CardHeader>
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <MessageSquare className="w-4 h-4 text-purple-500" />
                        Recent Prompts & Responses
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center text-muted-foreground py-8 text-sm">
                        No recent prompt/response data available
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
            <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-purple-500" />
                    Recent Prompts & Responses
                </CardTitle>
            </CardHeader>
            <CardContent>
                <Tabs defaultValue="prompts" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="prompts" className="gap-2">
                            <Sparkles className="w-4 h-4" />
                            Prompts ({recentPrompts.length})
                        </TabsTrigger>
                        <TabsTrigger value="responses" className="gap-2">
                            <MessageSquare className="w-4 h-4" />
                            Responses ({recentResponses.length})
                        </TabsTrigger>
                    </TabsList>

                    <TabsContent value="prompts" className="mt-4">
                        <ScrollArea className="h-[400px] pr-4">
                            <div className="space-y-3">
                                {recentPrompts.map((item, idx) => (
                                    <Card
                                        key={idx}
                                        className="bg-gradient-to-br from-purple-500/5 to-indigo-500/5 border-purple-500/20 hover:border-purple-500/40 transition-colors"
                                    >
                                        <CardContent className="p-4">
                                            <div className="flex justify-between items-start text-xs text-muted-foreground mb-2">
                                                <span>{new Date(item.timestamp).toLocaleString()}</span>
                                                <Badge variant="outline" className="font-mono text-xs">
                                                    {item.model}
                                                </Badge>
                                            </div>
                                            <p className="text-sm leading-relaxed">
                                                {item.prompt}
                                            </p>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        </ScrollArea>
                    </TabsContent>

                    <TabsContent value="responses" className="mt-4">
                        <ScrollArea className="h-[400px] pr-4">
                            <div className="space-y-3">
                                {recentResponses.map((item, idx) => (
                                    <Card
                                        key={idx}
                                        className="bg-gradient-to-br from-cyan-500/5 to-blue-500/5 border-cyan-500/20 hover:border-cyan-500/40 transition-colors"
                                    >
                                        <CardContent className="p-4">
                                            <div className="flex justify-between items-start text-xs text-muted-foreground mb-2">
                                                <span>{new Date(item.timestamp).toLocaleString()}</span>
                                                <Badge variant="outline" className="font-mono text-xs">
                                                    {item.model}
                                                </Badge>
                                            </div>
                                            <p className="text-sm leading-relaxed">
                                                {item.response}
                                            </p>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        </ScrollArea>
                    </TabsContent>
                </Tabs>
            </CardContent>
        </Card>
    );
}
