"use client";

import dynamic from "next/dynamic";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LoadingState } from "@/components/ui/states";
import * as projectsApi from "@/lib/api/projects";
import { formatDateTime, formatPercent, formatTemperature } from "@/lib/utils";
import type { Camera, ProcessingResult, ProjectDetail } from "@/types";

const ThermalMeshViewer = dynamic(() => import("@/components/three/ThermalMeshViewer").then((m) => m.ThermalMeshViewer), {
  ssr: false,
  loading: () => <LoadingState label="Loading 3D preview..." />,
});

interface OverviewTabProps {
  project: ProjectDetail;
  results?: ProcessingResult;
  cameras: Camera[];
}

export function OverviewTab({ project, results, cameras }: OverviewTabProps) {
  const summaryStats = results
    ? [
        { label: "Vertices", value: results.num_vertices.toLocaleString() },
        { label: "Faces", value: results.num_faces.toLocaleString() },
        { label: "Views", value: results.num_views },
        { label: "Coverage", value: formatPercent(results.coverage_percent) },
        { label: "Alignment Confidence", value: results.alignment_confidence !== null ? formatPercent(results.alignment_confidence * 100) : "--" },
        { label: "Mean Temperature", value: formatTemperature(results.mean_temperature) },
        { label: "Min / Max", value: `${formatTemperature(results.min_temperature)} / ${formatTemperature(results.max_temperature)}` },
        { label: "Std. Deviation", value: results.std_temperature !== null ? `±${results.std_temperature.toFixed(2)}°C` : "--" },
      ]
    : [];

  return (
    <div className="space-y-6">
      {results?.is_synthetic && (
        <div className="rounded-md border border-warning/20 bg-warning-bg px-4 py-2 text-xs text-warning">
          This project uses synthetic validation data generated for demonstration -- not a real Innohealth measurement.
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_1.2fr]">
        <Card>
          <CardHeader>
            <CardTitle>Project Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <InfoRow label="Description" value={project.description || "No description provided."} />
            <InfoRow label="Created" value={formatDateTime(project.created_at)} />
            <InfoRow label="Last updated" value={formatDateTime(project.updated_at)} />
            <InfoRow label="Last processed" value={project.last_processed_at ? formatDateTime(project.last_processed_at) : "Not processed yet"} />
            <InfoRow label="Type" value={project.is_demo ? "Synthetic demo project" : "Project"} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Processing Summary</CardTitle>
          </CardHeader>
          <CardContent>
            {results ? (
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                {summaryStats.map((stat) => (
                  <div key={stat.label}>
                    <p className="text-xs text-muted-foreground">{stat.label}</p>
                    <p className="mt-1 tabular-data text-base font-semibold text-foreground">{stat.value}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">This project has not been fully processed yet -- start processing to see thermal statistics here.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>3D Thermal Model Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[420px]">
            <ThermalMeshViewer
              projectId={project.id}
              modelUrl={results?.model_url ? projectsApi.getModelUrl(project.id) : null}
              cameras={cameras}
              minTemperature={results?.min_temperature ?? null}
              maxTemperature={results?.max_temperature ?? null}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-0.5 text-foreground">{value}</p>
    </div>
  );
}
