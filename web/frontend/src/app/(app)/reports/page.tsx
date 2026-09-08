"use client";

import { useQueries } from "@tanstack/react-query";
import { Download, Eye } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { EmptyState, LoadingState } from "@/components/ui/states";
import { useProjects } from "@/hooks/use-projects";
import * as projectsApi from "@/lib/api/projects";
import { formatDateTime } from "@/lib/utils";
import type { Report } from "@/types";

const REPORT_LABEL: Record<string, string> = {
  THERMAL_ANALYSIS: "Thermal Mapping Report",
  PROCESSING: "Processing Report",
  QUALITY: "Quality Report",
};

export default function ReportsPage() {
  const { data: projects = [], isLoading: projectsLoading } = useProjects();
  const processed = projects.filter((p) => p.has_result);
  const [open, setOpen] = useState<{ report: Report; projectName: string } | null>(null);

  const results = useQueries({
    queries: processed.map((project) => ({
      queryKey: ["project-reports", project.id],
      queryFn: () => projectsApi.listReports(project.id),
      enabled: processed.length > 0,
    })),
  });

  const isLoading = projectsLoading || results.some((r) => r.isLoading);
  const rows = processed
    .flatMap((project, index) => (results[index]?.data ?? []).map((report) => ({ project, report })))
    .sort((a, b) => new Date(b.report.generated_at).getTime() - new Date(a.report.generated_at).getTime());

  const download = (report: Report) => {
    const blob = new Blob([JSON.stringify(report.summary, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${report.type.toLowerCase()}_report.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Reports</h1>
        <p className="mt-1 text-muted-foreground">Every quality, processing, and thermal analysis report across your projects.</p>
      </div>

      {isLoading ? (
        <LoadingState label="Loading reports..." />
      ) : rows.length === 0 ? (
        <EmptyState title="Reports will appear here after processing is complete." />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {rows.map(({ project, report }) => (
            <Card key={report.id}>
              <CardContent className="space-y-3 p-5">
                <div className="flex items-start justify-between gap-2">
                  <p className="font-medium text-foreground">{REPORT_LABEL[report.type] ?? report.type}</p>
                  <Badge tone="success">Generated</Badge>
                </div>
                <div className="space-y-1 text-xs text-muted-foreground">
                  <p>
                    Project:{" "}
                    <Link href={`/projects/${project.id}?tab=reports`} className="text-foreground hover:text-brand">
                      {project.name}
                    </Link>
                  </p>
                  <p>Created {formatDateTime(report.generated_at)}</p>
                </div>
                <div className="flex gap-2 border-t border-border pt-3">
                  <Button size="sm" variant="secondary" onClick={() => setOpen({ report, projectName: project.name })}>
                    <Eye className="h-3.5 w-3.5" /> View
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => download(report)}>
                    <Download className="h-3.5 w-3.5" /> Download
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={Boolean(open)} onOpenChange={(v) => !v && setOpen(null)}>
        <DialogContent className="max-h-[80vh] max-w-2xl overflow-y-auto">
          {open && (
            <>
              <DialogHeader>
                <DialogTitle>
                  {REPORT_LABEL[open.report.type] ?? open.report.type} -- {open.projectName}
                </DialogTitle>
              </DialogHeader>
              <pre className="custom-scrollbar max-h-[60vh] overflow-auto rounded-md border border-border bg-surface-secondary p-4 text-xs text-foreground">
                {JSON.stringify(open.report.summary, null, 2)}
              </pre>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
