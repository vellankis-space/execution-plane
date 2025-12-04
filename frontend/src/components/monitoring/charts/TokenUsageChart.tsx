import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface TokenUsageChartProps {
    promptTokens: number;
    completionTokens: number;
}

export function TokenUsageChart({ promptTokens, completionTokens }: TokenUsageChartProps) {
    const data = [
        {
            name: 'Token Usage',
            Prompt: promptTokens,
            Completion: completionTokens
        }
    ];

    const total = promptTokens + completionTokens;

    return (
        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
            <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center justify-between">
                    <span>Token Usage Breakdown</span>
                    <span className="text-muted-foreground font-normal">
                        Total: {total.toLocaleString()}
                    </span>
                </CardTitle>
            </CardHeader>
            <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={data} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                        <XAxis type="number" />
                        <YAxis dataKey="name" type="category" hide />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'hsl(var(--card))',
                                border: '1px solid hsl(var(--border))',
                                borderRadius: '8px'
                            }}
                            formatter={(value: number) => value.toLocaleString()}
                        />
                        <Legend />
                        <Bar dataKey="Prompt" fill="#8b5cf6" radius={[0, 8, 8, 0]} />
                        <Bar dataKey="Completion" fill="#06b6d4" radius={[0, 8, 8, 0]} />
                    </BarChart>
                </ResponsiveContainer>
                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                        <span className="text-muted-foreground">Prompt:</span>
                        <span className="font-medium">{promptTokens.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded-full bg-cyan-500"></div>
                        <span className="text-muted-foreground">Completion:</span>
                        <span className="font-medium">{completionTokens.toLocaleString()}</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
