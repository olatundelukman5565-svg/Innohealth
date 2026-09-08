"use client";

import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Activity, CheckCircle2, Database, FolderKanban, Users, XCircle } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { LoadingState } from "@/components/ui/states";
import { useAdminOverview } from "@/hooks/use-admin";
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
        <h1 className="text-2xl font-semibold">Admin Overview</h1>
        <p className="mt-1 text-muted">System-wide status across every user and project.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        {tiles.map((tile) => (
          <Card key={tile.label}>
            <CardContent className="p-4">
              <tile.icon className="mb-2 h-4 w-4 text-brand" />
              <p className="font-mono text-xl font-semibold">{tile.value}</p>
              <p className="text-xs text-muted">{tile.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardContent className="p-6">
            <p className="mb-4 text-sm font-medium">Projects created (last 14 days)</p>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={data.projects_over_time}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#8b95a7" }} tickFormatter={(v) => v.slice(5)} />
                <YAxis tick={{ fontSize: 10, fill: "#8b95a7" }} allowDecimals={false} />
                <Tooltip contentStyle={{ background: "#0c111d", border: "1px solid rgba(255,255,255,0.1)", fontSize: 12 }} />
                <Line type="monotone" dataKey="count" stroke="#22d3ee" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <p className="mb-4 text-sm font-medium">Processing jobs by status</p>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={data.jobs_by_status}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="status" tick={{ fontSize: 10, fill: "#8b95a7" }} />
                <YAxis tick={{ fontSize: 10, fill: "#8b95a7" }} allowDecimals={false} />
                <Tooltip contentStyle={{ background: "#0c111d", border: "1px solid rgba(255,255,255,0.1)", fontSize: 12 }} />
                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="p-6">
          <p className="mb-4 text-sm font-medium">Recent activity</p>
          <ul className="space-y-3">
            {data.recent_activity.map((log) => (
              <li key={log.id} className="flex items-center justify-between border-b border-border pb-3 text-sm last:border-0 last:pb-0">
                <div>
                  <span className="font-medium">{log.user_email ?? "System"}</span>{" "}
                  <span className="text-muted">{log.action.replaceAll("_", " ").toLowerCase()}</span>
                </div>
                <span className="text-xs text-muted">{formatDateTime(log.created_at)}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
