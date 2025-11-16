import { AuditLogViewer } from "@/components/audit/AuditLogViewer";
import { FileText } from "lucide-react";

export default function Audit() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Header Section */}
      <div className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-30">
        <div className="container mx-auto px-8 py-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center shadow-lg shadow-green-500/25">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Orchestration Audit Logs</h1>
              <p className="text-sm text-muted-foreground">
                Comprehensive audit trail of all agent and workflow activities
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-8 py-8">
        <AuditLogViewer />
      </div>
    </div>
  );
}

