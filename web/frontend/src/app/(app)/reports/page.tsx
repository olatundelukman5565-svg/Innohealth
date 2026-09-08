"use client";

import { useQueries } from "@tanstack/react-query";
import Link from "next/link";

import { EmptyState, LoadingState } from "@/components/ui/states";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useProjects } from "@/hooks/use-projects";
import * as projectsApi from "@/lib/api/projects";
import { formatDateTime } from "@/lib/utils";

const REPORT_LABEL: Record<string, string> = {
  THERMAL_ANALYSIS: "Thermal Analysis",
  PROCESSING: "Processing",
  QUALITY: "Quality",
};

export default function ReportsPage() {
  const { data: projects = [], isLoading: projectsLoading } = useProjects();
  const processed = projects.filter((p) => p.has_result);

  const results = useQueries({
    queries: processed.map((project) => ({
      queryKey: ["project-reports", project.id],
      queryFn: () => projectsApi.listReports(project.id),
      enabled: processed.length > 0,
    })),
  });

  const isLoading = projectsLoading || results.some((r) => r.isLoading);
  const rows = processed.flatMap((project, index) => (results[index]?.data ?? []).map((report) => ({ project, report })));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Reports</h1>
        <p className="mt-1 text-muted">Every quality, processing, and thermal analysis report across your projects.</p>
      </div>

      {isLoading ? (
        <LoadingState label="Loading reports..." />
      ) : rows.length === 0 ? (
        <EmptyState title="Reports will appear here after processing is complete." />
      ) : (
        <div className="overflow-hidden rounded-2xl border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Project</TableHead>
                <TableHead>Report Type</TableHead>
                <TableHead>Generated</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.map(({ project, report }) => (
                <TableRow key={report.id}>
                  <TableCell>
                    <Link href={`/projects/${project.id}?tab=reports`} className="hover:text-brand">
                      {project.name}
                    </Link>
                  </TableCell>
                  <TableCell>{REPORT_LABEL[report.type] ?? report.type}</TableCell>
                  <TableCell className="text-muted">{formatDateTime(report.generated_at)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
