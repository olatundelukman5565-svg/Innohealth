"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { MoreVertical, Play, Trash2 } from "lucide-react";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";

import { CamerasTab } from "@/components/projects/CamerasTab";
import { DataTab } from "@/components/projects/DataTab";
import { OverviewTab } from "@/components/projects/OverviewTab";
import { ReportsTab } from "@/components/projects/ReportsTab";
import { StatusBadge } from "@/components/projects/StatusBadge";
import { TemperatureTab } from "@/components/projects/TemperatureTab";
import { ThermalTab } from "@/components/projects/ThermalTab";
import { Button } from "@/components/ui/button";
import { ErrorState, LoadingState } from "@/components/ui/states";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "@/components/ui/toast";
import {
  useDeleteProject,
  useProject,
  useProjectCameras,
  useProjectReports,
  useProjectResults,
  useProjectThermalImages,
} from "@/hooks/use-projects";
import { ApiError } from "@/lib/api/client";
import * as projectsApi from "@/lib/api/projects";
import { formatDateTime } from "@/lib/utils";

const ThermalMeshViewer = dynamic(() => import("@/components/three/ThermalMeshViewer").then((m) => m.ThermalMeshViewer), {
  ssr: false,
  loading: () => <LoadingState label="Loading 3D viewer..." />,
});

export default function ProjectDetailPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const router = useRouter();
  const { data: project, isLoading, error } = useProject(id);
  const { data: results } = useProjectResults(id, project?.has_result);
  const { data: cameras = [] } = useProjectCameras(id, project?.has_result);
  const { data: thermalImages = [] } = useProjectThermalImages(id, project?.has_result);
  const { data: reports = [] } = useProjectReports(id, project?.has_result);
  const deleteProject = useDeleteProject();

  if (isLoading) return <LoadingState label="Loading project..." />;
  if (error || !project) {
    return <ErrorState title="Could not load this project" reason={error instanceof ApiError ? error.message : undefined} />;
  }

  const handleStart = async () => {
    try {
      await projectsApi.startProcessing(id);
      router.push(`/projects/${id}/processing`);
    } catch (err) {
      toast({ title: "Could not start processing", description: err instanceof ApiError ? err.message : undefined, tone: "danger" });
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Delete "${project.name}"? This cannot be undone.`)) return;
    await deleteProject.mutateAsync(id);
    router.push("/projects");
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-semibold">{project.name}</h1>
            <StatusBadge status={project.status} />
          </div>
          <p className="mt-1 text-sm text-muted">
            {project.last_processed_at ? `Last processed ${formatDateTime(project.last_processed_at)}` : "Not processed yet"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {project.status === "PROCESSING" || project.status === "QUEUED" ? (
            <Button asChild variant="secondary">
              <Link href={`/projects/${id}/processing`}>View Progress</Link>
            </Button>
          ) : (
            <Button onClick={handleStart}>
              <Play className="h-4 w-4" /> {project.has_result ? "Reprocess" : "Start Processing"}
            </Button>
          )}
          <DropdownMenu.Root>
            <DropdownMenu.Trigger asChild>
              <Button variant="secondary" size="icon">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenu.Trigger>
            <DropdownMenu.Portal>
              <DropdownMenu.Content align="end" className="glass-panel z-50 min-w-40 rounded-lg p-1 shadow-panel">
                <DropdownMenu.Item
                  onSelect={handleDelete}
                  className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-sm text-danger hover:bg-danger/10"
                >
                  <Trash2 className="h-3.5 w-3.5" /> Delete project
                </DropdownMenu.Item>
              </DropdownMenu.Content>
            </DropdownMenu.Portal>
          </DropdownMenu.Root>
        </div>
      </div>

      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="viewer">3D Viewer</TabsTrigger>
          <TabsTrigger value="thermal">Thermal</TabsTrigger>
          <TabsTrigger value="cameras">Cameras</TabsTrigger>
          <TabsTrigger value="temperature">Temperature</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
          <TabsTrigger value="data">Data</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <OverviewTab project={project} results={results} />
        </TabsContent>
        <TabsContent value="viewer">
          <div className="h-[560px]">
            <ThermalMeshViewer
              projectId={id}
              modelUrl={results?.model_url ? projectsApi.getModelUrl(id) : null}
              cameras={cameras}
              minTemperature={results?.min_temperature ?? null}
              maxTemperature={results?.max_temperature ?? null}
            />
          </div>
        </TabsContent>
        <TabsContent value="thermal">
          <ThermalTab images={thermalImages} />
        </TabsContent>
        <TabsContent value="cameras">
          <CamerasTab cameras={cameras} />
        </TabsContent>
        <TabsContent value="temperature">
          {project.has_result ? <TemperatureTab projectId={id} /> : <p className="text-sm text-muted">Not available yet.</p>}
        </TabsContent>
        <TabsContent value="reports">
          <ReportsTab reports={reports} />
        </TabsContent>
        <TabsContent value="data">
          <DataTab projectId={id} results={results} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
