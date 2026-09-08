"use client";

import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { LoadingState } from "@/components/ui/states";
import { useAdminSystemHealth } from "@/hooks/use-admin";
import { cn, formatDateTime } from "@/lib/utils";

const STATUS_STYLES = {
  healthy: { icon: CheckCircle2, color: "text-success" },
  warning: { icon: AlertTriangle, color: "text-warning" },
  error: { icon: XCircle, color: "text-danger" },
} as const;

export default function AdminSystemPage() {
  const { data, isLoading } = useAdminSystemHealth();

  if (isLoading || !data) return <LoadingState label="Checking system health..." />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">System Health</h1>
        <p className="mt-1 text-muted-foreground">Last checked {formatDateTime(data.checked_at)}</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {data.components.map((component) => {
          const style = STATUS_STYLES[component.status];
          const Icon = style.icon;
          return (
            <Card key={component.name}>
              <CardContent className="flex items-center gap-4 p-5">
                <Icon className={cn("h-6 w-6", style.color)} />
                <div>
                  <p className="font-medium">{component.name}</p>
                  <p className="text-xs text-muted-foreground">{component.detail}</p>
                </div>
                <span className={cn("ml-auto text-xs font-medium uppercase", style.color)}>{component.status}</span>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
