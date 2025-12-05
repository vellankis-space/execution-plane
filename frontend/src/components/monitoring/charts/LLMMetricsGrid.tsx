import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Brain, Clock, Zap, TrendingUp } from 'lucide-react';
import type { AgentMetrics } from '@/services/observabilityService';

interface LLMMetricsGridProps {
    metrics: AgentMetrics;
}

interface MetricCardProps {
    title: string;
    value: string | number;
    icon: React.ReactNode;
    description?: string;
    trend?: 'up' | 'down' | 'neutral';
}

function MetricCard({ title, value, icon, description, trend }: MetricCardProps) {
    return (
        <Card className="bg-gradient-to-br from-card/50 to-card/30 backdrop-blur-sm border-border/50 hover:border-primary/50 transition-all">
            <CardContent className="p-6">
                <div className="flex items-start justify-between">
                    <div className="space-y-2">
                        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                            {title}
                        </p>
                        <p className="text-3xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                            {value}
                        </p>
                        {description && (
                            <p className="text-xs text-muted-foreground">{description}</p>
                        )}
                    </div>
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center">
                        {icon}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

export function LLMMetricsGrid({ metrics }: LLMMetricsGridProps) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
                title="Total LLM Calls"
                value={metrics.traffic.llm_calls.toLocaleString()}
                icon={<Brain className="w-6 h-6 text-purple-500" />}
                description="Successful completions"
            />
            <MetricCard
                title="Avg Latency"
                value={`${metrics.latency.avg.toFixed(0)}ms`}
                icon={<Clock className="w-6 h-6 text-blue-500" />}
                description="Mean response time"
            />
            <MetricCard
                title="P99 Latency"
                value={`${metrics.latency.p99.toFixed(0)}ms`}
                icon={<TrendingUp className="w-6 h-6 text-cyan-500" />}
                description="99th percentile"
            />
            <MetricCard
                title="TTFT"
                value={`${metrics.latency.ttft.toFixed(0)}ms`}
                icon={<Zap className="w-6 h-6 text-yellow-500" />}
                description="Time to first token"
            />
        </div>
    );
}
