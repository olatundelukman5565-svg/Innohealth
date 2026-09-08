"use client";

import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Activity, CheckCircle2, Database, FolderKanban, Users, XCircle } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingState } from "@/components/ui/states";
import { useAdminOverview } from "@/hooks/use-admin";
import { CHART_ACCENT, CHART_AXIS_TICK, CHART_GRID_STROKE, CHART_TOOLTIP_STYLE } from "@/lib/chart-theme";
import { formatDateTime } from "@/lib/utils";

export default function AdminOverviewPage() {
  const { data, isLoading } = useAdminOverview();

  if (isLoading || !data) return <LoadingState label="Loading admin overview..." />;

  const tiles = [
    { label: "Total Users", value: data.total_users, icon: Users },
    { label: "Active Projects", value: data.active_projects, icon: FolderKanban },
    { label: "Processing Jobs", value: data.processing_jobs, icon: Activity },
    { label: "Completed Jobs", value: data.completed_jobs, icon: CheckCircle2 },
    { label: "Failed Jobs", value: data.failed_jobs, icon: XCircle },
    { label: "Storage Used", value: `${data.storage_usage_mb} MB`, icon: Database },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Admin Overview</h1>
        <p className="mt-1 text-muted-foreground">System-wide status across every user and project.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        {tiles.map((tile) => (
          <Card key={tile.label}>
            <CardContent className="p-4">
              <tile.icon className="mb-2 h-4 w-4 text-brand" />
              <p className="tabular-data text-xl font-semibold text-foreground">{tile.value}</p>
              <p className="text-xs text-muted-foreground">{tile.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Projects created (last 14 days)</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={data.projects_over_time}>
                <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID_STROKE} vertical={false} />
                <XAxis dataKey="date" tick={CHART_AXIS_TICK} tickFormatter={(v) => v.slice(5)} axisLine={{ stroke: CHART_GRID_STROKE }} tickLine={false} />
                <YAxis tick={CHART_AXIS_TICK} allowDecimals={false} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} cursor={{ stroke: CHART_GRID_STROKE }} />
                <Line type="monotone" dataKey="count" stroke={CHART_ACCENT} strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Processing jobs by status</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={data.jobs_by_status}>
                <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID_STROKE} vertical={false} />
                <XAxis dataKey="status" tick={CHART_AXIS_TICK} axisLine={{ stroke: CHART_GRID_STROKE }} tickLine={false} />
                <YAxis tick={CHART_AXIS_TICK} allowDecimals={false} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={CHART_TOOLTIP_STYLE} cursor={{ fill: "rgba(15,23,42,0.03)" }} />
                <Bar dataKey="count" fill={CHART_ACCENT} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent activity</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3">
            {data.recent_activity.map((log) => (
              <li key={log.id} className="flex items-center justify-between border-b border-border pb-3 text-sm last:border-0 last:pb-0">
                <div>
                  <span className="font-medium text-foreground">{log.user_email ?? "System"}</span>{" "}
                  <span className="text-muted-foreground">{log.action.replaceAll("_", " ").toLowerCase()}</span>
                </div>
                <span className="text-xs text-muted-foreground">{formatDateTime(log.created_at)}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
