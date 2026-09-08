"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { CheckCircle2, Circle, Loader2, XCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ErrorState, LoadingState } from "@/components/ui/states";
import { useProcessingStream } from "@/hooks/use-processing-stream";
import { cn, formatDuration } from "@/lib/utils";
import { PROCESSING_STAGE_META } from "@/types";

const ProcessingScene = dynamic(() => import("@/components/three/ProcessingScene").then((m) => m.ProcessingScene), { ssr: false });

export default function ProcessingPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const router = useRouter();
  const { job, connected } = useProcessingStream(id);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!job?.started_at || job.status !== "RUNNING") return;
    const start = new Date(job.started_at).getTime();
    const interval = setInterval(() => setElapsed((Date.now() - start) / 1000), 500);
    return () => clearInterval(interval);
  }, [job?.started_at, job?.status]);

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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Processing</h1>
          <p className="mt-1 text-sm text-muted">{connected ? "Live connection to the ThermalMesh engine" : "Reconnecting..."}</p>
        </div>
        {job.status === "COMPLETED" && (
          <Button onClick={() => router.push(`/projects/${id}`)}>View Results</Button>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.3fr_1fr]">
        <Card className="overflow-hidden">
          <div className="h-80 bg-black/40">
            <ProcessingScene currentStage={job.current_stage} progressPercent={job.progress_percent} />
          </div>
          <CardContent className="space-y-3 p-6">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">
                {job.current_stage ? PROCESSING_STAGE_META[job.current_stage].label : job.status === "COMPLETED" ? "Complete" : "Starting..."}
              </span>
              <span className="font-mono text-muted">{job.progress_percent.toFixed(0)}%</span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/[0.06]">
              <div className="h-full bg-brand-gradient transition-all duration-500" style={{ width: `${job.progress_percent}%` }} />
            </div>
            <div className="flex items-center justify-between text-xs text-muted">
              <span>{job.current_stage && PROCESSING_STAGE_META[job.current_stage].description}</span>
              <span className="font-mono">{formatDuration(elapsed)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <p className="mb-4 text-xs font-medium uppercase tracking-wide text-muted">
              Pipeline Stages ({completedCount}/{job.stages.length})
            </p>
            <ol className="space-y-2">
              {job.stages.map((stage) => {
                const meta = PROCESSING_STAGE_META[stage.name];
                return (
                  <li key={stage.name} className="flex items-center gap-3 rounded-lg px-2 py-1.5">
                    <span className="font-mono text-xs text-muted">{String(stage.sequence + 1).padStart(2, "0")}</span>
                    {stage.status === "COMPLETED" && <CheckCircle2 className="h-4 w-4 text-success" />}
                    {stage.status === "RUNNING" && <Loader2 className="h-4 w-4 animate-spin text-brand" />}
                    {stage.status === "PENDING" && <Circle className="h-4 w-4 text-muted" />}
                    {stage.status === "FAILED" && <XCircle className="h-4 w-4 text-danger" />}
                    <span className={cn("text-sm", stage.status === "PENDING" && "text-muted", stage.status === "RUNNING" && "font-medium")}>
                      {meta.label}
                    </span>
                  </li>
                );
              })}
            </ol>
          </CardContent>
        </Card>
      </div>

      {job.status === "COMPLETED" && (
        <div className="glass-panel flex items-center justify-between rounded-2xl p-6">
          <div>
            <p className="font-medium text-success">Processing completed successfully</p>
            <p className="text-sm text-muted">Your 3D thermal model is ready to explore.</p>
          </div>
          <Button asChild>
            <Link href={`/projects/${id}`}>Open Project</Link>
          </Button>
        </div>
      )}
    </div>
  );
}
