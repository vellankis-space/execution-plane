import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DollarSign, Zap } from 'lucide-react';

interface ModelCostTableProps {
    costs: Array<{ name: string; cost: number; tokens: number }>;
}

export function ModelCostTable({ costs }: ModelCostTableProps) {
    const totalCost = costs.reduce((sum, model) => sum + model.cost, 0);
    const totalTokens = costs.reduce((sum, model) => sum + model.tokens, 0);

    return (
        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
            <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-green-500" />
                    Cost Breakdown by Model
                </CardTitle>
            </CardHeader>
            <CardContent>
                {costs && costs.length > 0 ? (
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Model</TableHead>
                                <TableHead className="text-right">Cost</TableHead>
                                <TableHead className="text-right">Tokens</TableHead>
                                <TableHead className="text-right">% of Total</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {costs.map((model) => {
                                const percentage = totalCost > 0 ? (model.cost / totalCost) * 100 : 0;
                                return (
                                    <TableRow key={model.name}>
                                        <TableCell className="font-mono text-xs">
                                            {model.name}
                                        </TableCell>
                                        <TableCell className="text-right font-medium">
                                            ${model.cost.toFixed(4)}
                                        </TableCell>
                                        <TableCell className="text-right text-muted-foreground">
                                            <div className="flex items-center justify-end gap-1">
                                                <Zap className="w-3 h-3" />
                                                {model.tokens.toLocaleString()}
                                            </div>
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <Badge variant="outline" className="font-mono">
                                                {percentage.toFixed(1)}%
                                            </Badge>
                                        </TableCell>
                                    </TableRow>
                                );
                            })}
                        </TableBody>
                    </Table>
                ) : (
                    <div className="text-center text-muted-foreground py-8 text-sm">
                        No cost data available
                    </div>
                )}
                {costs && costs.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-border/50 flex justify-between text-sm">
                        <span className="text-muted-foreground">Total</span>
                        <div className="flex gap-6">
                            <span className="font-medium">
                                ${totalCost.toFixed(4)}
                            </span>
                            <span className="text-muted-foreground">
                                {totalTokens.toLocaleString()} tokens
                            </span>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
