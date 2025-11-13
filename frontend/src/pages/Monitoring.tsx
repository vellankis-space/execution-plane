import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MonitoringDashboard } from "@/components/monitoring/MonitoringDashboard";
import { ExecutionTimeline } from "@/components/monitoring/ExecutionTimeline";
import { MetricsChart } from "@/components/monitoring/MetricsChart";
import { SystemHealth } from "@/components/monitoring/SystemHealth";
import { AlertManagement } from "@/components/monitoring/AlertManagement";
import { CostTracking } from "@/components/monitoring/CostTracking";

export default function Monitoring() {
  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Monitoring & Observability</h1>
        <p className="text-muted-foreground mt-2">
          Real-time monitoring, metrics, and analytics for your AI agents and workflows
        </p>
      </div>

      <Tabs defaultValue="dashboard" className="w-full">
        <TabsList>
          <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
          <TabsTrigger value="executions">Executions</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
          <TabsTrigger value="health">System Health</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="costs">Cost Tracking</TabsTrigger>
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
  );
}

