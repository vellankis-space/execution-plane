import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MonitoringDashboard } from "@/components/monitoring/MonitoringDashboard";
import { ExecutionTimeline } from "@/components/monitoring/ExecutionTimeline";
import { MetricsChart } from "@/components/monitoring/MetricsChart";
import { SystemHealth } from "@/components/monitoring/SystemHealth";
import { AlertManagement } from "@/components/monitoring/AlertManagement";
import { CostTracking } from "@/components/monitoring/CostTracking";
import { Activity } from "lucide-react";

export default function Monitoring() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Header Section */}
      <div className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-30">
        <div className="container mx-auto px-8 py-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center shadow-lg shadow-amber-500/25">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Orchestration Monitoring</h1>
              <p className="text-sm text-muted-foreground">
                Real-time monitoring, metrics, and analytics for agents and workflows
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-8 py-8">
        <Tabs defaultValue="dashboard" className="w-full">
          <TabsList className="grid w-full grid-cols-6 bg-card/50 border border-border/50">
            <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
            <TabsTrigger value="executions">Executions</TabsTrigger>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
            <TabsTrigger value="health">Health</TabsTrigger>
            <TabsTrigger value="alerts">Alerts</TabsTrigger>
            <TabsTrigger value="costs">Costs</TabsTrigger>
          </TabsList>
          
          <TabsContent value="dashboard" className="mt-6">
            <MonitoringDashboard />
          </TabsContent>
          
          <TabsContent value="executions" className="mt-6">
            <ExecutionTimeline />
          </TabsContent>
          
          <TabsContent value="metrics" className="mt-6">
            <MetricsChart />
          </TabsContent>
          
          <TabsContent value="health" className="mt-6">
            <SystemHealth />
          </TabsContent>
          
          <TabsContent value="alerts" className="mt-6">
            <AlertManagement />
          </TabsContent>
          
          <TabsContent value="costs" className="mt-6">
            <CostTracking />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

