import { AuditLogViewer } from "@/components/audit/AuditLogViewer";

export default function Audit() {
  return (
    <div className="container py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Audit Logs</h1>
        <p className="text-muted-foreground mt-2">
          Comprehensive audit trail of all system activities
        </p>
      </div>
      <AuditLogViewer />
    </div>
  );
}

