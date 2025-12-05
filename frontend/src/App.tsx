import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "next-themes";
import { AuthProvider, useAuth } from "@/hooks/use-auth";
import { MainLayout } from "@/components/layout";
import Index from "./pages/Index";
import Chat from "./pages/Chat";
import Agents from "./pages/Agents";
import Workflows from "./pages/Workflows";
import Monitoring from "./pages/Monitoring";
import Observability from "./pages/Observability";
import Audit from "./pages/Audit";
import MCPServers from "./pages/MCPServers";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import { AgentBuilder } from "./components/AgentBuilder";
import { WorkflowBuilder } from "./components/workflow/WorkflowBuilder";
import { ErrorBoundary } from "./components/ErrorBoundary";

const queryClient = new QueryClient();

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return <>{children}</>;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <MainLayout>
                      <Index />
                    </MainLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/chat"
                element={
                  <ProtectedRoute>
                    <MainLayout>
                      <Chat />
                    </MainLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/agents"
                element={
                  <ProtectedRoute>
                    <MainLayout>
                      <Agents />
                    </MainLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/workflows"
                element={
                  <ProtectedRoute>
                    <MainLayout>
                      <Workflows />
                    </MainLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/monitoring"
                element={
                  <ProtectedRoute>
                    <MainLayout>
                      <Monitoring />
                    </MainLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/observability"
                element={
                  <ProtectedRoute>
                    <MainLayout>
                      <ErrorBoundary>
                        <Observability />
                      </ErrorBoundary>
                    </MainLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/audit"
                element={
                  <ProtectedRoute>
                    <MainLayout>
                      <Audit />
                    </MainLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/mcp-servers"
                element={
                  <ProtectedRoute>
                    <MainLayout>
                      <MCPServers />
                    </MainLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/playground"
                element={
                  <ProtectedRoute>
                    <MainLayout>
                      <AgentBuilder />
                    </MainLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/workflow-builder"
                element={
                  <ProtectedRoute>
                    <WorkflowBuilder />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/production-workflow"
                element={
                  <Navigate to="/workflow-builder" replace />
                }
              />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;