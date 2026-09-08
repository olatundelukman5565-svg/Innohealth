"use client";

import { useEffect, useRef, useState } from "react";

import { sseUrl } from "@/lib/api/client";
import * as projectsApi from "@/lib/api/projects";
import type { ProcessingJob } from "@/types";

export function useProcessingStream(projectId: string) {
  const [job, setJob] = useState<ProcessingJob | null>(null);
  const [connected, setConnected] = useState(false);
  const [errored, setErrored] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!projectId) return;
    let source: EventSource | null = null;
    let cancelled = false;

    const startPolling = () => {
      if (pollRef.current) return;
      pollRef.current = setInterval(async () => {
        try {
          const status = await projectsApi.getProcessingStatus(projectId);
          if (!cancelled) setJob(status);
        } catch {
          // keep polling -- transient errors are expected between stage writes
        }
      }, 2000);
    };

    try {
      source = new EventSource(sseUrl(`/api/projects/${projectId}/processing/stream`));
      source.addEventListener("update", (event) => {
        if (cancelled) return;
        setConnected(true);
        setJob(JSON.parse((event as MessageEvent).data));
      });
      source.addEventListener("done", (event) => {
        if (cancelled) return;
        setJob(JSON.parse((event as MessageEvent).data));
        source?.close();
      });
      source.onerror = () => {
        setConnected(false);
        source?.close();
        if (!cancelled) startPolling();
      };
    } catch {
      setErrored(true);
      startPolling();
    }

    return () => {
      cancelled = true;
      source?.close();
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [projectId]);

  return { job, connected, errored };
}
