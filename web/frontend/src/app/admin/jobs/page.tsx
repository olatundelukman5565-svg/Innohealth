"use client";

import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LoadingState } from "@/components/ui/states";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useAdminJobs } from "@/hooks/use-admin";
import { cn, formatDateTime, formatDuration } from "@/lib/utils";
import type { AdminJob, JobStatus } from "@/types";

const STATUS_TONE: Record<JobStatus, "neutral" | "info" | "success" | "danger" | "warning"> = {
  QUEUED: "warning",
  RUNNING: "info",
  COMPLETED: "success",
  FAILED: "danger",
  CANCELLED: "neutral",
};

export default function AdminJobsPage() {
  const [status, setStatus] = useState<string>("ALL");
  const { data: jobs = [], isLoading } = useAdminJobs(status === "ALL" ? undefined : status);
  const [selected, setSelected] = useState<AdminJob | null>(null);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Processing Jobs</h1>
          <p className="mt-1 text-muted">Every pipeline run, across every project.</p>
        </div>
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All statuses</SelectItem>
            <SelectItem value="QUEUED">Queued</SelectItem>
            <SelectItem value="RUNNING">Running</SelectItem>
            <SelectItem value="COMPLETED">Completed</SelectItem>
            <SelectItem value="FAILED">Failed</SelectItem>
            <SelectItem value="CANCELLED">Cancelled</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <LoadingState label="Loading jobs..." />
      ) : (
        <div className="overflow-hidden rounded-2xl border border-border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Project</TableHead>
                <TableHead>Stage</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Progress</TableHead>
                <TableHead>Started</TableHead>
                <TableHead>Duration</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {jobs.map((job) => (
                <TableRow key={job.id} className="cursor-pointer" onClick={() => setSelected(job)}>
                  <TableCell>{job.project_name}</TableCell>
                  <TableCell className="text-xs text-muted">{job.current_stage ?? "--"}</TableCell>
                  <TableCell>
                    <Badge tone={STATUS_TONE[job.status]}>{job.status}</Badge>
                  </TableCell>
                  <TableCell className="w-32">
                    <Progress value={job.progress_percent} />
                  </TableCell>
                  <TableCell className="text-muted">{job.started_at ? formatDateTime(job.started_at) : "--"}</TableCell>
                  <TableCell className="font-mono">{job.duration_seconds !== null ? formatDuration(job.duration_seconds) : "--"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      <Dialog open={Boolean(selected)} onOpenChange={(v) => !v && setSelected(null)}>
        <DialogContent className="max-w-lg">
          {selected && (
            <>
              <DialogHeader>
                <DialogTitle>{selected.project_name}</DialogTitle>
              </DialogHeader>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted">Status</span>
                  <Badge tone={STATUS_TONE[selected.status]}>{selected.status}</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Current stage</span>
                  <span>{selected.current_stage ?? "--"}</span>
                </div>
                {selected.error_message && (
                  <div className="rounded-lg border border-danger/30 bg-danger/10 p-3">
                    <p className="font-medium text-danger">{selected.error_message}</p>
                    {selected.error_detail && (
                      <pre className={cn("mt-2 max-h-40 overflow-auto whitespace-pre-wrap text-[10px] text-white/60")}>
                        {selected.error_detail}
                      </pre>
                    )}
                  </div>
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
