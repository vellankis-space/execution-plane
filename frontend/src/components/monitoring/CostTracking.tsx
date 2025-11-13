import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, DollarSign, TrendingUp, AlertTriangle } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { format } from "date-fns";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from "recharts";

interface CostSummary {
  total_cost: number;
  total_tokens: number;
  total_calls: number;
  by_provider: Record<string, { cost: number; tokens: number; calls: number }>;
  by_model: Record<string, { cost: number; tokens: number; calls: number }>;
}

interface CostTrend {
  date: string;
  cost: number;
  tokens: number;
  calls: number;
}

interface Budget {
  budget_id: string;
  name: string;
  budget_type: string;
  amount: number;
  enabled: boolean;
}

export function CostTracking() {
  const [selectedPeriod, setSelectedPeriod] = useState<number>(30);
  const [isBudgetDialogOpen, setIsBudgetDialogOpen] = useState(false);
  const queryClient = useQueryClient();

  // Fetch cost summary
  const { data: costSummary } = useQuery<CostSummary>({
    queryKey: ["cost-summary", selectedPeriod],
    queryFn: async () => {
      const response = await fetch(
        `http://localhost:8000/api/v1/cost-tracking/summary?days=${selectedPeriod}`
      );
      if (!response.ok) throw new Error("Failed to fetch cost summary");
      return response.json();
    },
    refetchInterval: 60000, // Refresh every minute
  });

  // Fetch cost trends
  const { data: costTrends } = useQuery<CostTrend[]>({
    queryKey: ["cost-trends", selectedPeriod],
    queryFn: async () => {
      const response = await fetch(
        `http://localhost:8000/api/v1/cost-tracking/trends?days=${selectedPeriod}`
      );
      if (!response.ok) throw new Error("Failed to fetch cost trends");
      return response.json();
    },
    refetchInterval: 60000,
  });

  // Fetch budgets
  const { data: budgets } = useQuery<Budget[]>({
    queryKey: ["cost-budgets"],
    queryFn: async () => {
      const response = await fetch("http://localhost:8000/api/v1/cost-tracking/budgets");
      if (!response.ok) throw new Error("Failed to fetch budgets");
      return response.json();
    },
  });

  // Fetch cost alerts
  const { data: costAlerts } = useQuery({
    queryKey: ["cost-alerts"],
    queryFn: async () => {
      const response = await fetch("http://localhost:8000/api/v1/cost-tracking/alerts?status=active");
      if (!response.ok) throw new Error("Failed to fetch cost alerts");
      return response.json();
    },
    refetchInterval: 30000,
  });

  return (
    <div className="space-y-6">
      {/* Cost Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Cost</p>
              <p className="text-2xl font-bold mt-2">
                ${costSummary?.total_cost?.toFixed(2) || "0.00"}
              </p>
            </div>
            <DollarSign className="h-8 w-8 text-green-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Total Tokens</p>
              <p className="text-2xl font-bold mt-2">
                {costSummary?.total_tokens?.toLocaleString() || "0"}
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-blue-500" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">API Calls</p>
              <p className="text-2xl font-bold mt-2">
                {costSummary?.total_calls?.toLocaleString() || "0"}
              </p>
            </div>
            <AlertTriangle className="h-8 w-8 text-purple-500" />
          </div>
        </Card>
      </div>

      {/* Cost Trends Chart */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Cost Trends</h3>
          <Select value={selectedPeriod.toString()} onValueChange={(v) => setSelectedPeriod(parseInt(v))}>
            <SelectTrigger className="w-[150px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={costTrends || []}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="cost"
              stroke="#8884d8"
              name="Cost ($)"
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Cost by Provider */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Cost by Provider</h3>
          {costSummary?.by_provider && Object.keys(costSummary.by_provider).length > 0 ? (
            <div className="space-y-2">
              {Object.entries(costSummary.by_provider).map(([provider, data]) => (
                <div
                  key={provider}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div>
                    <p className="font-medium">{provider}</p>
                    <p className="text-sm text-muted-foreground">
                      {data.calls} calls • {data.tokens.toLocaleString()} tokens
                    </p>
                  </div>
                  <p className="font-semibold">${data.cost.toFixed(2)}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">No cost data available</p>
          )}
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Budgets</h3>
            <Dialog open={isBudgetDialogOpen} onOpenChange={setIsBudgetDialogOpen}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Budget
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Budget</DialogTitle>
                  <DialogDescription>
                    Set up a cost budget with alerts
                  </DialogDescription>
                </DialogHeader>
                <BudgetForm
                  onSuccess={() => {
                    setIsBudgetDialogOpen(false);
                    queryClient.invalidateQueries({ queryKey: ["cost-budgets"] });
                  }}
                />
              </DialogContent>
            </Dialog>
          </div>
          {budgets && budgets.length > 0 ? (
            <div className="space-y-2">
              {budgets.map((budget) => (
                <BudgetCard key={budget.budget_id} budget={budget} />
              ))}
            </div>
          ) : (
            <p className="text-center text-muted-foreground py-8">No budgets configured</p>
          )}
        </Card>
      </div>

      {/* Cost Alerts */}
      {costAlerts && costAlerts.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Cost Alerts</h3>
          <div className="space-y-2">
            {costAlerts.map((alert: any) => (
              <div
                key={alert.alert_id}
                className="flex items-center justify-between p-3 border rounded-lg bg-yellow-50"
              >
                <div>
                  <p className="font-medium">{alert.message}</p>
                  <p className="text-sm text-muted-foreground">
                    {alert.percentage_used.toFixed(1)}% of budget used
                  </p>
                </div>
                <Badge variant="destructive">{alert.alert_type}</Badge>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}

function BudgetCard({ budget }: { budget: Budget }) {
  const { data: status } = useQuery({
    queryKey: ["budget-status", budget.budget_id],
    queryFn: async () => {
      const response = await fetch(
        `http://localhost:8000/api/v1/cost-tracking/budgets/${budget.budget_id}/status`
      );
      if (!response.ok) throw new Error("Failed to fetch budget status");
      return response.json();
    },
    refetchInterval: 60000,
  });

  const percentageUsed = status?.percentage_used || 0;
  const isOverBudget = percentageUsed >= 100;

  return (
    <div className="p-4 border rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <div>
          <p className="font-medium">{budget.name}</p>
          <p className="text-sm text-muted-foreground">{budget.budget_type}</p>
        </div>
        <Badge variant={isOverBudget ? "destructive" : "default"}>
          {percentageUsed.toFixed(1)}%
        </Badge>
      </div>
      <div className="mt-2">
        <div className="flex justify-between text-sm mb-1">
          <span>${status?.current_cost?.toFixed(2) || "0.00"}</span>
          <span>${budget.amount.toFixed(2)}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${
              isOverBudget ? "bg-red-500" : percentageUsed > 80 ? "bg-yellow-500" : "bg-green-500"
            }`}
            style={{ width: `${Math.min(percentageUsed, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
}

function BudgetForm({ onSuccess }: { onSuccess: () => void }) {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    budget_type: "monthly",
    amount: 100,
    alert_threshold: 0.8,
  });

  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await fetch("http://localhost:8000/api/v1/cost-tracking/budgets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error("Failed to create budget");
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Budget created",
        description: "Your budget has been created successfully.",
      });
      onSuccess();
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to create budget",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="budget-name">Budget Name</Label>
        <Input
          id="budget-name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />
      </div>

      <div>
        <Label htmlFor="budget-type">Budget Type</Label>
        <Select
          value={formData.budget_type}
          onValueChange={(value) => setFormData({ ...formData, budget_type: value })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="daily">Daily</SelectItem>
            <SelectItem value="weekly">Weekly</SelectItem>
            <SelectItem value="monthly">Monthly</SelectItem>
            <SelectItem value="total">Total</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <Label htmlFor="budget-amount">Budget Amount ($)</Label>
        <Input
          id="budget-amount"
          type="number"
          step="0.01"
          min="0"
          value={formData.amount}
          onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) })}
          required
        />
      </div>

      <div className="flex justify-end gap-2 pt-4">
        <Button type="submit" disabled={createMutation.isPending}>
          Create Budget
        </Button>
      </div>
    </form>
  );
}

