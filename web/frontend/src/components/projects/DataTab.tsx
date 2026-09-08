"use client";

import { Download, FileJson, FileSpreadsheet, FileType } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { toast } from "@/components/ui/toast";
import { apiDownload } from "@/lib/api/client";
import { getDownloadUrl, type DownloadArtifact } from "@/lib/api/projects";
import type { ProcessingResult } from "@/types";

const FILES: { artifact: DownloadArtifact; label: string; description: string; filename: string; icon: typeof FileJson }[] = [
  { artifact: "temperatures_csv", label: "temperatures.csv", description: "Per-vertex position + temperature + confidence", filename: "temperatures.csv", icon: FileSpreadsheet },
  { artifact: "vertex_temperature", label: "vertex_temperature.npy", description: "Raw NumPy array of blended vertex temperatures", filename: "vertex_temperature.npy", icon: FileType },
  { artifact: "face_temperature", label: "face_temperature.npy", description: "Per-face temperature (mean of vertices)", filename: "face_temperature.npy", icon: FileType },
  { artifact: "results_json", label: "results.json", description: "Camera poses, alignment diagnostics, temperature statistics", filename: "results.json", icon: FileJson },
];

export function DataTab({ projectId, results }: { projectId: string; results?: ProcessingResult }) {
  const handleDownload = async (artifact: DownloadArtifact, filename: string) => {
    try {
      await apiDownload(getDownloadUrl(projectId, artifact), filename);
    } catch {
      toast({ title: "Download failed", description: "This file may not be available for this project.", tone: "danger" });
    }
  };

  if (!results) {
    return <p className="text-sm text-muted-foreground">Numerical data will be available once processing completes.</p>;
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {FILES.map((file) => {
        const Icon = file.icon;
        return (
          <Card key={file.artifact}>
            <CardContent className="flex items-center justify-between gap-4 p-5">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-border text-muted-foreground">
                  <Icon className="h-4 w-4" />
                </div>
                <div>
                  <p className="tabular-data text-sm font-medium text-foreground">{file.label}</p>
                  <p className="text-xs text-muted-foreground">{file.description}</p>
                </div>
              </div>
              <Button size="sm" variant="secondary" onClick={() => handleDownload(file.artifact, file.filename)}>
                <Download className="h-3.5 w-3.5" />
              </Button>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
