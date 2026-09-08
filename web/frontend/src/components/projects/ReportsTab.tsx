"use client";

import { useState } from "react";
import { Download, Eye } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { EmptyState } from "@/components/ui/states";
import { formatDateTime } from "@/lib/utils";
import type { Report } from "@/types";

const REPORT_LABEL: Record<Report["type"], string> = {
  THERMAL_ANALYSIS: "Thermal Analysis Report",
  PROCESSING: "Processing Report",
  QUALITY: "Quality Report",
};

export function ReportsTab({ reports }: { reports: Report[] }) {
  const [open, setOpen] = useState<Report | null>(null);

  if (reports.length === 0) {
    return <EmptyState title="Reports will appear here after processing is complete." />;
  }

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
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {reports.map((report) => (
          <Card key={report.id}>
            <CardContent className="space-y-3 p-5">
              <p className="font-medium">{REPORT_LABEL[report.type]}</p>
              <p className="text-xs text-muted-foreground">Generated {formatDateTime(report.generated_at)}</p>
              <div className="flex gap-2">
                <Button size="sm" variant="secondary" onClick={() => setOpen(report)}>
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

      <Dialog open={Boolean(open)} onOpenChange={(v) => !v && setOpen(null)}>
        <DialogContent className="max-h-[80vh] max-w-2xl overflow-y-auto">
          {open && (
            <>
              <DialogHeader>
                <DialogTitle>{REPORT_LABEL[open.type]}</DialogTitle>
              </DialogHeader>
              <pre className="custom-scrollbar max-h-[60vh] overflow-auto rounded-md border border-border bg-surface-secondary p-4 text-xs text-foreground">
                {JSON.stringify(open.summary, null, 2)}
              </pre>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
