import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle } from 'lucide-react';

interface FinishReasonsChartProps {
    reasons: Record<string, number>;
}

const COLORS = ['#8b5cf6', '#06b6d4', '#f59e0b', '#ef4444', '#10b981'];

export function FinishReasonsChart({ reasons }: FinishReasonsChartProps) {
    const data = Object.entries(reasons || {}).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1), // Capitalize
        value
    }));

    const total = data.reduce((sum, item) => sum + item.value, 0);

    if (data.length === 0) {
        return (
            <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                <CardHeader>
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-blue-500" />
                        Finish Reasons
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center text-muted-foreground py-8 text-sm">
                        No finish reason data available
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card className="bg-card/50 backdrop-blur-sm border-border/50">
            <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-blue-500" />
                    Finish Reasons
                </CardTitle>
            </CardHeader>
            <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="value"
                        >
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'hsl(var(--card))',
                                border: '1px solid hsl(var(--border))',
                                borderRadius: '8px'
                            }}
                        />
                        <Legend />
                    </PieChart>
                </ResponsiveContainer>
                <div className="mt-4 text-center text-sm text-muted-foreground">
                    Total Completions: {total}
                </div>
            </CardContent>
        </Card>
    );
}
