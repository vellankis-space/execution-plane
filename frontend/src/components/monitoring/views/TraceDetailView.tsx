import React, { useState } from 'react';
import { useTraceDetails, TraceSpan } from '@/services/observabilityService';
import {
    Loader2,
    AlertCircle,
    Clock,
    DollarSign,
    Zap,
    ChevronRight,
    ChevronDown,
    Braces,
    Database,
    Bot,
    Wrench,
    Layers
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

interface TraceDetailViewProps {
    traceId: string;
    onClose?: () => void;
}

export function TraceDetailView({ traceId, onClose }: TraceDetailViewProps) {
    const { data: trace, isLoading, error } = useTraceDetails(traceId);
    const [selectedSpanId, setSelectedSpanId] = useState<string | null>(null);

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-full min-h-[400px]">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
        );
    }

    if (error || !trace) {
        return (
            <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-muted-foreground">
                <AlertCircle className="w-8 h-8 mb-2 text-destructive" />
                <p>Failed to load trace details</p>
            </div>
        );
    }

    // Calculate timeline bounds
    const startTime = new Date(trace.timestamp).getTime();
    // Find max end time from spans or default to trace start + latency
    const endTime = trace.spans?.length
        ? Math.max(...trace.spans.map(s => s.end_time ? new Date(s.end_time).getTime() : startTime))
        : startTime + (parseFloat(trace.latency) * 1000);

    const totalDuration = endTime - startTime;

    const getSpanIcon = (type: string) => {
        switch (type) {
            case 'llm': return <Bot className="w-4 h-4" />;
            case 'tool': return <Wrench className="w-4 h-4" />;
            case 'chain': return <Layers className="w-4 h-4" />;
            default: return <Clock className="w-4 h-4" />;
        }
    };

    const getSpanColor = (type: string) => {
        switch (type) {
            case 'llm': return 'bg-blue-500/20 text-blue-500 border-blue-500/30';
            case 'tool': return 'bg-amber-500/20 text-amber-500 border-amber-500/30';
            case 'chain': return 'bg-purple-500/20 text-purple-500 border-purple-500/30';
            default: return 'bg-slate-500/20 text-slate-500 border-slate-500/30';
        }
    };

    const selectedSpan = trace.spans?.find(s => s.span_id === selectedSpanId) || trace.spans?.[0];

    return (
        <div className="flex flex-col h-full space-y-4 animate-in fade-in duration-300">
            {/* Header Stats - Responsive grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <Card className="bg-card/50 backdrop-blur-sm">
                    <CardContent className="p-3 flex items-center gap-2">
                        <div className="p-1.5 rounded-full bg-primary/10 text-primary shrink-0">
                            <Clock className="w-3.5 h-3.5" />
                        </div>
                        <div className="min-w-0">
                            <p className="text-[10px] text-muted-foreground">Duration</p>
                            <p className="text-sm font-semibold truncate">{trace.latency}</p>
                        </div>
                    </CardContent>
                </Card>
                <Card className="bg-card/50 backdrop-blur-sm">
                    <CardContent className="p-3 flex items-center gap-2">
                        <div className="p-1.5 rounded-full bg-green-500/10 text-green-500 shrink-0">
                            <DollarSign className="w-3.5 h-3.5" />
                        </div>
                        <div className="min-w-0">
                            <p className="text-[10px] text-muted-foreground">Cost</p>
                            <p className="text-sm font-semibold truncate">{trace.cost}</p>
                        </div>
                    </CardContent>
                </Card>
                <Card className="bg-card/50 backdrop-blur-sm">
                    <CardContent className="p-3 flex items-center gap-2">
                        <div className="p-1.5 rounded-full bg-purple-500/10 text-purple-500 shrink-0">
                            <Zap className="w-3.5 h-3.5" />
                        </div>
                        <div className="min-w-0">
                            <p className="text-[10px] text-muted-foreground">Tokens</p>
                            <p className="text-sm font-semibold truncate">{trace.tokens.toLocaleString()}</p>
                        </div>
                    </CardContent>
                </Card>
                <Card className="bg-card/50 backdrop-blur-sm">
                    <CardContent className="p-3 flex items-center gap-2">
                        <div className={cn("p-1.5 rounded-full shrink-0", trace.status === 'success' ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500")}>
                            {trace.status === 'success' ? <Zap className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
                        </div>
                        <div className="min-w-0">
                            <p className="text-[10px] text-muted-foreground">Status</p>
                            <p className="text-sm font-semibold capitalize truncate">{trace.status}</p>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <div className="flex flex-col lg:grid lg:grid-cols-3 gap-4 flex-1 min-h-0">
                {/* Waterfall Visualization */}
                <Card className="lg:col-span-2 bg-card/50 backdrop-blur-sm flex flex-col overflow-hidden min-h-[300px] lg:min-h-0">
                    <CardHeader className="py-3 px-4">
                        <CardTitle className="text-base flex items-center gap-2">
                            <Layers className="w-4 h-4" />
                            Execution Flow
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-auto p-0">
                        <ScrollArea className="h-full">
                            <div className="p-3 space-y-1.5">
                                {trace.spans?.map((span) => {
                                    const spanStart = new Date(span.start_time).getTime();
                                    const spanEnd = span.end_time ? new Date(span.end_time).getTime() : spanStart;
                                    const offset = ((spanStart - startTime) / totalDuration) * 100;
                                    const width = Math.max(((spanEnd - spanStart) / totalDuration) * 100, 1); // Min 1% width

                                    return (
                                        <div
                                            key={span.span_id}
                                            className={cn(
                                                "group relative flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2 p-2 rounded-md cursor-pointer transition-colors hover:bg-accent/50",
                                                selectedSpanId === span.span_id && "bg-accent"
                                            )}
                                            onClick={() => setSelectedSpanId(span.span_id)}
                                        >
                                            <div className="flex items-center gap-2 sm:w-36 md:w-44 shrink-0">
                                                {getSpanIcon(span.type)}
                                                <span className="text-xs sm:text-sm truncate flex-1" title={span.name}>{span.name}</span>
                                                <span className="text-[10px] text-muted-foreground sm:hidden">
                                                    {Math.round(spanEnd - spanStart)}ms
                                                </span>
                                            </div>

                                            <div className="flex-1 relative h-5 bg-secondary/20 rounded overflow-hidden">
                                                <div
                                                    className={cn("absolute h-full rounded opacity-80 transition-all", getSpanColor(span.type))}
                                                    style={{
                                                        left: `${offset}%`,
                                                        width: `${width}%`
                                                    }}
                                                />
                                            </div>

                                            <div className="hidden sm:block w-16 shrink-0 text-xs text-right text-muted-foreground">
                                                {Math.round(spanEnd - spanStart)}ms
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </ScrollArea>
                    </CardContent>
                </Card>

                {/* Details Panel */}
                <Card className="bg-card/50 backdrop-blur-sm flex flex-col overflow-hidden min-h-[250px] lg:min-h-0">
                    <CardHeader className="py-3 px-4 border-b border-border/50">
                        <CardTitle className="text-base flex items-center gap-2">
                            <Braces className="w-4 h-4" />
                            Step Details
                        </CardTitle>
                        <CardDescription className="text-xs truncate">
                            {selectedSpan ? selectedSpan.name : "Select a step to view details"}
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-hidden p-0">
                        {selectedSpan ? (
                            <Tabs defaultValue="io" className="h-full flex flex-col">
                                <div className="px-3 pt-2">
                                    <TabsList className="w-full grid grid-cols-2 h-8">
                                        <TabsTrigger value="io" className="text-xs">I/O</TabsTrigger>
                                        <TabsTrigger value="meta" className="text-xs">Meta</TabsTrigger>
                                    </TabsList>
                                </div>

                                <TabsContent value="io" className="flex-1 overflow-hidden mt-0 p-0">
                                    <ScrollArea className="h-full p-3">
                                        <div className="space-y-3">
                                            <div>
                                                <h4 className="text-[10px] font-semibold uppercase text-muted-foreground mb-1.5">Input</h4>
                                                <pre className="bg-muted/50 p-2 rounded-md text-[11px] font-mono overflow-x-auto whitespace-pre-wrap break-all max-h-[150px] overflow-y-auto">
                                                    {JSON.stringify(selectedSpan.input, null, 2) || "No input"}
                                                </pre>
                                            </div>
                                            <Separator />
                                            <div>
                                                <h4 className="text-[10px] font-semibold uppercase text-muted-foreground mb-1.5">Output</h4>
                                                <pre className="bg-muted/50 p-2 rounded-md text-[11px] font-mono overflow-x-auto whitespace-pre-wrap break-all max-h-[150px] overflow-y-auto">
                                                    {JSON.stringify(selectedSpan.output, null, 2) || "No output"}
                                                </pre>
                                            </div>
                                            {selectedSpan.error && (
                                                <>
                                                    <Separator />
                                                    <div>
                                                        <h4 className="text-xs font-semibold uppercase text-destructive mb-2">Error</h4>
                                                        <pre className="bg-destructive/10 text-destructive p-3 rounded-md text-xs font-mono overflow-x-auto">
                                                            {selectedSpan.error}
                                                        </pre>
                                                    </div>
                                                </>
                                            )}
                                        </div>
                                    </ScrollArea>
                                </TabsContent>

                                <TabsContent value="meta" className="flex-1 overflow-hidden mt-0 p-0">
                                    <ScrollArea className="h-full p-3">
                                        <div className="space-y-3">
                                            <div className="grid grid-cols-2 gap-3">
                                                <div className="space-y-0.5">
                                                    <p className="text-[10px] text-muted-foreground">Type</p>
                                                    <Badge variant="outline" className="text-[10px] h-5">{selectedSpan.type}</Badge>
                                                </div>
                                                <div className="space-y-0.5">
                                                    <p className="text-[10px] text-muted-foreground">Status</p>
                                                    <Badge variant={selectedSpan.status === 'success' ? 'default' : 'destructive'} className="text-[10px] h-5">
                                                        {selectedSpan.status}
                                                    </Badge>
                                                </div>
                                                <div className="space-y-0.5">
                                                    <p className="text-[10px] text-muted-foreground">Start</p>
                                                    <p className="text-xs font-mono">{new Date(selectedSpan.start_time).toLocaleTimeString()}</p>
                                                </div>
                                                <div className="space-y-0.5">
                                                    <p className="text-[10px] text-muted-foreground">End</p>
                                                    <p className="text-xs font-mono">{selectedSpan.end_time ? new Date(selectedSpan.end_time).toLocaleTimeString() : '-'}</p>
                                                </div>
                                            </div>

                                            {selectedSpan.metrics && (
                                                <>
                                                    <Separator />
                                                    <h4 className="text-[10px] font-semibold uppercase text-muted-foreground">Metrics</h4>
                                                    <div className="grid grid-cols-2 gap-3">
                                                        {selectedSpan.metrics.tokens && (
                                                            <>
                                                                <div className="space-y-0.5">
                                                                    <p className="text-[10px] text-muted-foreground">Prompt</p>
                                                                    <p className="text-xs">{selectedSpan.metrics.tokens.prompt}</p>
                                                                </div>
                                                                <div className="space-y-0.5">
                                                                    <p className="text-[10px] text-muted-foreground">Completion</p>
                                                                    <p className="text-xs">{selectedSpan.metrics.tokens.completion}</p>
                                                                </div>
                                                            </>
                                                        )}
                                                        {selectedSpan.metrics.cost !== undefined && (
                                                            <div className="space-y-0.5">
                                                                <p className="text-[10px] text-muted-foreground">Cost</p>
                                                                <p className="text-xs">${selectedSpan.metrics.cost.toFixed(6)}</p>
                                                            </div>
                                                        )}
                                                    </div>
                                                </>
                                            )}

                                            {selectedSpan.metadata && (
                                                <>
                                                    <Separator />
                                                    <h4 className="text-[10px] font-semibold uppercase text-muted-foreground">Metadata</h4>
                                                    <pre className="bg-muted/50 p-2 rounded-md text-[11px] font-mono overflow-x-auto whitespace-pre-wrap break-all max-h-[120px] overflow-y-auto">
                                                        {JSON.stringify(selectedSpan.metadata, null, 2)}
                                                    </pre>
                                                </>
                                            )}
                                        </div>
                                    </ScrollArea>
                                </TabsContent>
                            </Tabs>
                        ) : (
                            <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-4 text-center">
                                <Layers className="w-8 h-8 mb-2 opacity-50" />
                                <p>Select a step from the execution flow to view its details</p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
