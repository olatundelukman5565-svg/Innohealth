"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useMemo } from "react";
import { ArrowUpRight, FolderKanban, Gauge, Layers, Plus } from "lucide-react";

import { ProjectCard } from "@/components/projects/ProjectCard";
import { StatusBadge } from "@/components/projects/StatusBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { EmptyState, LoadingState } from "@/components/ui/states";
import { useProjectResults, useProjects } from "@/hooks/use-projects";
import { useAuth } from "@/lib/auth-context";
import { formatPercent, formatTemperature } from "@/lib/utils";
import * as projectsApi from "@/lib/api/projects";

const ThermalMeshViewer = dynamic(() => import("@/components/three/ThermalMeshViewer").then((m) => m.ThermalMeshViewer), {
  ssr: false,
  loading: () => <LoadingState label="Loading 3D preview..." />,
});

function greeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

export default function DashboardPage() {
  const { user } = useAuth();
  const { data: projects = [], isLoading } = useProjects();

  const latest = useMemo(() => projects.find((p) => p.has_result) ?? projects[0], [projects]);
  const { data: results } = useProjectResults(latest?.id ?? "", Boolean(latest?.has_result));

  const active = projects.filter((p) => ["QUEUED", "PROCESSING", "UPLOADING", "VALIDATING"].includes(p.status)).length;
  const completed = projects.filter((p) => p.status === "COMPLETED").length;
  const avgCoverage =
    projects.filter((p) => p.coverage_percent !== null).reduce((sum, p) => sum + (p.coverage_percent ?? 0), 0) /
    (projects.filter((p) => p.coverage_percent !== null).length || 1);

  if (isLoading) return <LoadingState label="Loading your workspace..." />;

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">
            {greeting()}, {user?.full_name.split(" ")[0]}
          </h1>
          <p className="mt-1 text-muted">Here&apos;s your thermal intelligence overview.</p>
        </div>
        <Button asChild>
          <Link href="/projects/new">
            <Plus className="h-4 w-4" /> New Project
          </Link>
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.5fr_1fr]">
        <div className="h-[420px]">
          {latest?.has_result ? (
            <ThermalMeshViewer
              projectId={latest.id}
              modelUrl={results?.model_url ? projectsApi.getModelUrl(latest.id) : null}
              cameras={[]}
              minTemperature={results?.min_temperature ?? latest.min_temperature}
              maxTemperature={results?.max_temperature ?? latest.max_temperature}
            />
          ) : (
            <Card className="flex h-full items-center justify-center">
              <EmptyState
                icon={<Layers className="h-8 w-8 text-muted" />}
                title="No processed projects yet"
                description="Create a project and run the pipeline to see your latest 3D thermal reconstruction here."
                action={
                  <Button asChild size="sm">
                    <Link href="/projects/new">Create your first project</Link>
                  </Button>
                }
              />
            </Card>
          )}
        </div>

        <div className="space-y-4">
          <Card>
            <CardContent className="space-y-4 p-5">
              <p className="text-xs font-medium uppercase tracking-wide text-muted">Latest Project</p>
              {latest ? (
                <>
                  <div className="flex items-center justify-between">
                    <Link href={`/projects/${latest.id}`} className="font-medium hover:text-brand">
                      {latest.name}
                    </Link>
                    <StatusBadge status={latest.status} />
                  </div>
                  {results && (
                    <div className="grid grid-cols-2 gap-3 border-t border-border pt-3 text-sm">
                      <div>
                        <p className="text-xs text-muted">Coverage</p>
                        <p className="font-mono font-medium">{formatPercent(results.coverage_percent)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted">Views</p>
                        <p className="font-mono font-medium">{results.num_views}</p>
                      </div>
                      <div className="col-span-2">
                        <p className="text-xs text-muted">Temperature range</p>
                        <p className="font-mono font-medium">
                          {formatTemperature(results.min_temperature)} - {formatTemperature(results.max_temperature)}
                        </p>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <p className="text-sm text-muted">No projects yet.</p>
              )}
            </CardContent>
          </Card>

          <div className="grid grid-cols-3 gap-3">
            <StatTile icon={FolderKanban} label="Projects" value={projects.length} />
            <StatTile icon={Gauge} label="Active" value={active} />
            <StatTile icon={Layers} label="Completed" value={completed} />
          </div>

          <Card>
            <CardContent className="p-5">
              <p className="text-xs font-medium uppercase tracking-wide text-muted">Average Thermal Coverage</p>
              <p className="mt-2 font-mono text-3xl font-semibold">{formatPercent(avgCoverage)}</p>
              <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-white/[0.06]">
                <div className="h-full bg-brand-gradient" style={{ width: `${Math.min(avgCoverage, 100)}%` }} />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Recent Projects</h2>
          <Link href="/projects" className="flex items-center gap-1 text-sm text-brand hover:underline">
            View all <ArrowUpRight className="h-3.5 w-3.5" />
          </Link>
        </div>
        {projects.length === 0 ? (
          <EmptyState
            title="No thermal projects have been created."
            description="Every scan you process will show up here."
            action={
              <Button asChild size="sm">
                <Link href="/projects/new">Create your first project</Link>
              </Button>
            }
          />
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.slice(0, 6).map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatTile({ icon: Icon, label, value }: { icon: typeof FolderKanban; label: string; value: number }) {
  return (
    <Card>
      <CardContent className="p-4">
        <Icon className="mb-2 h-4 w-4 text-brand" />
        <p className="font-mono text-xl font-semibold">{value}</p>
        <p className="text-xs text-muted">{label}</p>
      </CardContent>
    </Card>
  );
}
