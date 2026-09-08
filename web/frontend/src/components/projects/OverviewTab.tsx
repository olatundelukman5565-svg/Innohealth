import { Card, CardContent } from "@/components/ui/card";
import { formatPercent, formatTemperature } from "@/lib/utils";
import type { ProcessingResult, ProjectDetail } from "@/types";

export function OverviewTab({ project, results }: { project: ProjectDetail; results?: ProcessingResult }) {
  if (!results) {
    return (
      <div className="glass-panel rounded-2xl p-8 text-center text-muted">
        This project has not been fully processed yet -- start processing to see thermal statistics here.
      </div>
    );
  }

  const stats = [
    { label: "Vertices", value: results.num_vertices.toLocaleString() },
    { label: "Faces", value: results.num_faces.toLocaleString() },
    { label: "Views", value: results.num_views },
    { label: "Coverage", value: formatPercent(results.coverage_percent) },
    { label: "Alignment Confidence", value: results.alignment_confidence !== null ? formatPercent(results.alignment_confidence * 100) : "--" },
    { label: "Mean Temperature", value: formatTemperature(results.mean_temperature) },
    { label: "Min / Max", value: `${formatTemperature(results.min_temperature)} / ${formatTemperature(results.max_temperature)}` },
    { label: "Std. Deviation", value: results.std_temperature !== null ? `±${results.std_temperature.toFixed(2)}°C` : "--" },
  ];

  return (
    <div className="space-y-6">
      {results.is_synthetic && (
        <div className="rounded-lg border border-warning/30 bg-warning/10 px-4 py-2 text-xs text-warning">
          This project uses synthetic validation data generated for demonstration -- not a real Innohealth measurement.
        </div>
      )}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-4">
              <p className="text-xs text-muted">{stat.label}</p>
              <p className="mt-1 font-mono text-lg font-semibold">{stat.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>
      <p className="text-sm text-muted">{project.description}</p>
    </div>
  );
}
