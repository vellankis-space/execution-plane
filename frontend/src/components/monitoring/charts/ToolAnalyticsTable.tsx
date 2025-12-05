import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Wrench, TrendingUp, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface ToolAnalyticsTableProps {
    toolUsage: Array<{
        name: string;
        count: number;
        avg_latency: number;
        failures: number;
        success_rate: number;
    }>;
    mcpServersUsed: string[];
}

export function ToolAnalyticsTable({ toolUsage, mcpServersUsed }: ToolAnalyticsTableProps) {
    if (!toolUsage || toolUsage.length === 0) {
        return (
            <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                <CardHeader>
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <Wrench className="w-4 h-4 text-orange-500" />
                        Tool Usage Analytics
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center text-muted-foreground py-8 text-sm">
                        No tool usage data yet
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
            <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Wrench className="w-4 h-4 text-orange-500" />
                        Tool Usage Analytics
                    </div>
                    <Badge variant="outline" className="font-normal">
                        {toolUsage.length} tool{toolUsage.length !== 1 ? 's' : ''}
                    </Badge>
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Tool Name</TableHead>
                            <TableHead className="text-right">Calls</TableHead>
                            <TableHead className="text-right">Avg Latency</TableHead>
                            <TableHead className="text-right">Success Rate</TableHead>
                            <TableHead className="text-right">Failures</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {toolUsage.map((tool) => (
                            <TableRow key={tool.name}>
                                <TableCell className="font-medium">
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-orange-500"></div>
                                        {tool.name}
                                    </div>
                                </TableCell>
                                <TableCell className="text-right">
                                    <Badge variant="secondary" className="font-mono">
                                        {tool.count}
                                    </Badge>
                                </TableCell>
                                <TableCell className="text-right text-muted-foreground">
                                    <div className="flex items-center justify-end gap-1">
                                        <TrendingUp className="w-3 h-3" />
                                        {tool.avg_latency.toFixed(0)}ms
                                    </div>
                                </TableCell>
                                <TableCell className="text-right">
                                    <Badge
                                        variant={tool.success_rate >= 90 ? 'default' : tool.success_rate >= 70 ? 'secondary' : 'destructive'}
                                        className="gap-1"
                                    >
                                        {tool.success_rate >= 90 ? (
                                            <CheckCircle2 className="w-3 h-3" />
                                        ) : (
                                            <AlertTriangle className="w-3 h-3" />
                                        )}
                                        {tool.success_rate.toFixed(1)}%
                                    </Badge>
                                </TableCell>
                                <TableCell className="text-right">
                                    {tool.failures > 0 ? (
                                        <Badge variant="destructive" className="font-mono">
                                            {tool.failures}
                                        </Badge>
                                    ) : (
                                        <span className="text-muted-foreground text-xs">0</span>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>

                {/* MCP Servers Used */}
                {mcpServersUsed && mcpServersUsed.length > 0 && (
                    <div className="pt-4 border-t border-border/50">
                        <div className="text-sm font-medium mb-2">MCP Servers Used</div>
                        <div className="flex flex-wrap gap-2">
                            {mcpServersUsed.map((server) => (
                                <Badge
                                    key={server}
                                    variant="outline"
                                    className="bg-gradient-to-r from-purple-500/10 to-indigo-500/10 border-purple-500/20"
                                >
                                    <Server className="w-3 h-3 mr-1" />
                                    {server}
                                </Badge>
                            ))}
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}

function Server({ className }: { className?: string }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
        >
            <rect width="20" height="8" x="2" y="2" rx="2" ry="2" />
            <rect width="20" height="8" x="2" y="14" rx="2" ry="2" />
            <line x1="6" x2="6.01" y1="6" y2="6" />
            <line x1="6" x2="6.01" y1="18" y2="18" />
        </svg>
    );
}
