"use client";

import { Badge } from "@/components/ui/badge";
import { LoadingState } from "@/components/ui/states";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useAdminAuditLogs } from "@/hooks/use-admin";
import { formatDateTime } from "@/lib/utils";

export default function AdminAuditPage() {
  const { data: logs = [], isLoading } = useAdminAuditLogs(200);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Audit Logs</h1>
        <p className="mt-1 text-muted-foreground">Every recorded action across the platform.</p>
      </div>

      {isLoading ? (
        <LoadingState label="Loading audit logs..." />
      ) : (
        <div className="overflow-hidden rounded-lg border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Timestamp</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {logs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell>{log.user_email ?? "System"}</TableCell>
                  <TableCell className="tabular-data text-xs">{log.action}</TableCell>
                  <TableCell>
                    <Badge tone={log.status === "SUCCESS" ? "success" : "danger"}>{log.status}</Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{formatDateTime(log.created_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
