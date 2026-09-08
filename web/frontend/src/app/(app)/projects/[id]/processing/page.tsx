"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { CheckCircle2, Circle, Loader2, XCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ErrorState, LoadingState } from "@/components/ui/states";
import { useProcessingStream } from "@/hooks/use-processing-stream";
import { cn, formatDuration } from "@/lib/utils";
import { PROCESSING_STAGE_META } from "@/types";

export default function ProcessingPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const router = useRouter();
  const { job, connected } = useProcessingStream(id);
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    if (job?.status !== "RUNNING") return;
    const interval = setInterval(() => setNow(Date.now()), 500);
    return () => clearInterval(interval);
  }, [job?.status]);

  if (!job) return <LoadingState label="Connecting to the processing engine..." />;

  if (job.status === "FAILED") {
    return (
      <div className="mx-auto max-w-2xl space-y-4">
        <ErrorState
          title="Processing could not be completed."
          reason={job.error_message ?? "An unknown error occurred."}
          action="Back to project"
          onAction={() => router.push(`/projects/${id}`)}
        />
      </div>
    );
  }

  const completedCount = job.stages.filter((s) => s.status === "COMPLETED").length;
  const overallElapsed = job.started_at ? (now - new Date(job.started_at).getTime()) / 1000 : 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Processing</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            {connected ? "Live connection to the ThermalMesh engine" : "Reconnecting..."}
          </p>
        </div>
        {job.status === "COMPLETED" && <Button onClick={() => router.push(`/projects/${id}`)}>View Results</Button>}
      </div>

      <Card>
        <CardContent className="space-y-3 p-5">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-foreground">
              {job.current_stage ? PROCESSING_STAGE_META[job.current_stage].label : job.status === "COMPLETED" ? "Complete" : "Starting..."}
            </span>
            <span className="tabular-data text-muted-foreground">{job.progress_percent.toFixed(0)}%</span>
          </div>
          <Progress value={job.progress_percent} />
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{job.current_stage && PROCESSING_STAGE_META[job.current_stage].description}</span>
            <span className="tabular-data">{formatDuration(overallElapsed)} elapsed</span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            Pipeline Stages ({completedCount}/{job.stages.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <ol>
            {job.stages.map((stage, i) => {
              const meta = PROCESSING_STAGE_META[stage.name];
              const started = stage.started_at ? new Date(stage.started_at).getTime() : null;
              const completed = stage.completed_at ? new Date(stage.completed_at).getTime() : null;
              const durationSeconds =
                started && completed ? (completed - started) / 1000 : started && stage.status === "RUNNING" ? (now - started) / 1000 : null;

              return (
                <li
                  key={stage.name}
                  className={cn("flex items-start gap-3 border-b border-border px-5 py-3.5 last:border-b-0", stage.status === "RUNNING" && "bg-brand-muted")}
                >
                  <span className="tabular-data mt-0.5 w-5 shrink-0 text-xs text-muted-foreground">{String(i + 1).padStart(2, "0")}</span>
                  <div className="mt-0.5 shrink-0">
                    {stage.status === "COMPLETED" && <CheckCircle2 className="h-4 w-4 text-success" />}
                    {stage.status === "RUNNING" && <Loader2 className="h-4 w-4 animate-spin text-brand" />}
                    {stage.status === "PENDING" && <Circle className="h-4 w-4 text-muted-foreground" />}
                    {stage.status === "FAILED" && <XCircle className="h-4 w-4 text-danger" />}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-baseline justify-between gap-x-3">
                      <span className={cn("text-sm", stage.status === "PENDING" ? "text-muted-foreground" : "font-medium text-foreground")}>
                        {meta.label}
                      </span>
                      {durationSeconds !== null && <span className="tabular-data text-xs text-muted-foreground">{formatDuration(durationSeconds)}</span>}
                    </div>
                    <p className="mt-0.5 text-xs text-muted-foreground">{meta.description}</p>
                  </div>
                </li>
              );
            })}
          </ol>
        </CardContent>
      </Card>

      {job.status === "COMPLETED" && (
        <div className="flex items-center justify-between rounded-lg border border-success/20 bg-success-bg p-5">
          <div>
            <p className="font-medium text-success">Processing completed successfully</p>
            <p className="text-sm text-muted-foreground">Your 3D thermal model is ready to explore.</p>
          </div>
          <Button asChild>
            <Link href={`/projects/${id}`}>Open Project</Link>
          </Button>
        </div>
      )}
    </div>
  );
}
