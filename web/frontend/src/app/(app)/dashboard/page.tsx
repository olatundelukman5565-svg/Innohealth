"use client";

import Link from "next/link";
import { useMemo } from "react";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Activity, CheckCircle2, FolderKanban, Gauge, Plus } from "lucide-react";

import { ProjectsTable } from "@/components/projects/ProjectsTable";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState, LoadingState } from "@/components/ui/states";
import { useProjects } from "@/hooks/use-projects";
import { useAuth } from "@/lib/auth-context";
import { CHART_ACCENT, CHART_AXIS_TICK, CHART_DANGER, CHART_GRID_STROKE, CHART_NEUTRAL, CHART_TOOLTIP_STYLE, CHART_WARNING } from "@/lib/chart-theme";
import { formatPercent } from "@/lib/utils";

export default function DashboardPage() {
  const { user } = useAuth();
  const { data: projects = [], isLoading } = useProjects();

  const active = projects.filter((p) => ["QUEUED", "PROCESSING", "UPLOADING", "VALIDATING"].includes(p.status)).length;
  const completed = projects.filter((p) => p.status === "COMPLETED").length;
  const withCoverage = projects.filter((p) => p.coverage_percent !== null);
  const avgCoverage = withCoverage.reduce((sum, p) => sum + (p.coverage_percent ?? 0), 0) / (withCoverage.length || 1);

  const statusBreakdown = useMemo(() => {
    const failed = projects.filter((p) => p.status === "FAILED").length;
    return [
      { status: "Completed", count: completed, color: CHART_ACCENT },
      { status: "Processing", count: active, color: CHART_WARNING },
      { status: "Failed", count: failed, color: CHART_DANGER },
    ];
  }, [projects, completed, active]);

  const coverageByProject = useMemo(
    () =>
      projects
        .filter((p) => p.coverage_percent !== null)
        .slice(0, 8)
        .map((p) => ({ name: p.name.length > 14 ? `${p.name.slice(0, 14)}…` : p.name, coverage: Number((p.coverage_percent ?? 0).toFixed(1)) })),
    [projects]
  );

  const temperatureRangeByProject = useMemo(
    () =>
      projects
        .filter((p) => p.min_temperature !== null && p.max_temperature !== null)
        .slice(0, 8)
        .map((p) => ({
          name: p.name.length > 14 ? `${p.name.slice(0, 14)}…` : p.name,
          min: Number((p.min_temperature ?? 0).toFixed(1)),
          range: Number(((p.max_temperature ?? 0) - (p.min_temperature ?? 0)).toFixed(1)),
        })),
    [projects]
  );

  if (isLoading) return <LoadingState label="Loading your workspace..." />;

  const recentProjects = [...projects].sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()).slice(0, 5);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Dashboard</h1>
          <p className="mt-1 text-muted-foreground">Overview of your thermal mesh processing projects.</p>
        </div>
        <Button asChild>
          <Link href="/projects/new">
            <Plus className="h-4 w-4" /> New Project
          </Link>
        </Button>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <KpiCard icon={FolderKanban} label="Projects" value={projects.length} />
        <KpiCard icon={Activity} label="Processing Jobs" value={active} />
        <KpiCard icon={CheckCircle2} label="Completed Analyses" value={completed} />
        <KpiCard icon={Gauge} label="Thermal Coverage" value={formatPercent(avgCoverage)} />
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Projects</CardTitle>
          <Link href="/projects" className="text-sm text-brand hover:underline">
            View all
          </Link>
        </CardHeader>
        <CardContent className="p-0">
          {recentProjects.length === 0 ? (
            <div className="p-5">
              <EmptyState
                title="No thermal projects have been created."
                description="Every scan you process will show up here."
                action={
                  <Button asChild size="sm">
                    <Link href="/projects/new">Create your first project</Link>
                  </Button>
                }
              />
            </div>
          ) : (
            <ProjectsTable projects={recentProjects} variant="dashboard" />
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Processing Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={statusBreakdown}>
              <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID_STROKE} vertical={false} />
              <XAxis dataKey="status" tick={CHART_AXIS_TICK} axisLine={{ stroke: CHART_GRID_STROKE }} tickLine={false} />
              <YAxis tick={CHART_AXIS_TICK} allowDecimals={false} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={CHART_TOOLTIP_STYLE} cursor={{ fill: "rgba(15,23,42,0.03)" }} />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {statusBreakdown.map((entry) => (
                  <Cell key={entry.status} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Thermal Coverage by Project</CardTitle>
          </CardHeader>
          <CardContent>
            {coverageByProject.length === 0 ? (
              <p className="py-10 text-center text-sm text-muted-foreground">No processed projects yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={coverageByProject}>
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID_STROKE} vertical={false} />
                  <XAxis dataKey="name" tick={CHART_AXIS_TICK} axisLine={{ stroke: CHART_GRID_STROKE }} tickLine={false} interval={0} angle={-20} textAnchor="end" height={50} />
                  <YAxis tick={CHART_AXIS_TICK} unit="%" axisLine={false} tickLine={false} domain={[0, 100]} />
                  <Tooltip contentStyle={CHART_TOOLTIP_STYLE} cursor={{ fill: "rgba(15,23,42,0.03)" }} formatter={(v: number) => `${v}%`} />
                  <Bar dataKey="coverage" fill={CHART_ACCENT} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Temperature Range by Project</CardTitle>
          </CardHeader>
          <CardContent>
            {temperatureRangeByProject.length === 0 ? (
              <p className="py-10 text-center text-sm text-muted-foreground">No processed projects yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={temperatureRangeByProject}>
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART_GRID_STROKE} vertical={false} />
                  <XAxis dataKey="name" tick={CHART_AXIS_TICK} axisLine={{ stroke: CHART_GRID_STROKE }} tickLine={false} interval={0} angle={-20} textAnchor="end" height={50} />
                  <YAxis tick={CHART_AXIS_TICK} unit="°C" axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={CHART_TOOLTIP_STYLE} cursor={{ fill: "rgba(15,23,42,0.03)" }} />
                  <Bar dataKey="min" stackId="range" fill="transparent" legendType="none" />
                  <Bar dataKey="range" stackId="range" fill={CHART_NEUTRAL} radius={[4, 4, 0, 0]} name="Range above min (°C)" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function KpiCard({ icon: Icon, label, value }: { icon: typeof FolderKanban; label: string; value: number | string }) {
  return (
    <Card>
      <CardContent className="p-4">
        <Icon className="mb-2 h-4 w-4 text-brand" />
        <p className="tabular-data text-xl font-semibold text-foreground">{value}</p>
        <p className="text-xs text-muted-foreground">{label}</p>
      </CardContent>
    </Card>
  );
}
