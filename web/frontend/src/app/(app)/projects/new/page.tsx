"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Check } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input, Textarea } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { UploadZone, type UploadZoneFile } from "@/components/ui/upload-zone";
import { toast } from "@/components/ui/toast";
import { useCreateProject, useProjectFiles } from "@/hooks/use-projects";
import * as projectsApi from "@/lib/api/projects";
import { ApiError } from "@/lib/api/client";
import { cn, formatBytes } from "@/lib/utils";

const STEPS = ["Project Info", "Geometry", "Thermal Data", "Cameras", "Review"];

export default function NewProjectPage() {
  const router = useRouter();
  const createProject = useCreateProject();
  const [step, setStep] = useState(0);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [starting, setStarting] = useState(false);

  const [finalMeshFile, setFinalMeshFile] = useState<UploadZoneFile[]>([]);
  const [initialMeshFile, setInitialMeshFile] = useState<UploadZoneFile[]>([]);
  const [thermalFiles, setThermalFiles] = useState<UploadZoneFile[]>([]);
  const [cameraFile, setCameraFile] = useState<UploadZoneFile[]>([]);

  const { data: uploadedFiles = [], refetch: refetchFiles } = useProjectFiles(projectId ?? "");

  const upload = async (file: File, type: Parameters<typeof projectsApi.uploadFile>[2], setStatus: (f: UploadZoneFile[]) => void, existing: UploadZoneFile[]) => {
    if (!projectId) return;
    const pending: UploadZoneFile = { name: file.name, size: file.size, status: "uploading" };
    setStatus([...existing.filter((f) => f.name !== file.name), pending]);
    try {
      await projectsApi.uploadFile(projectId, file, type);
      setStatus([...existing.filter((f) => f.name !== file.name), { name: file.name, size: file.size, status: "done" }]);
      refetchFiles();
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Upload failed";
      setStatus([...existing.filter((f) => f.name !== file.name), { name: file.name, size: file.size, status: "error", error: message }]);
    }
  };

  const handleNext = async () => {
    if (step === 0) {
      if (!name.trim()) {
        toast({ title: "Project name is required", tone: "danger" });
        return;
      }
      try {
        const project = await createProject.mutateAsync({ name, description });
        setProjectId(project.id);
        setStep(1);
      } catch (err) {
        toast({ title: "Could not create project", description: err instanceof ApiError ? err.message : undefined, tone: "danger" });
      }
      return;
    }
    setStep((s) => Math.min(s + 1, STEPS.length - 1));
  };

  const handleStartProcessing = async () => {
    if (!projectId) return;
    setStarting(true);
    try {
      await projectsApi.startProcessing(projectId);
      router.push(`/projects/${projectId}/processing`);
    } catch (err) {
      toast({ title: "Could not start processing", description: err instanceof ApiError ? err.message : undefined, tone: "danger" });
      setStarting(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">New Project</h1>
        <p className="mt-1 text-muted">Set up a thermal-mapped 3D reconstruction in a few steps.</p>
      </div>

      <ol className="flex items-center gap-2">
        {STEPS.map((label, index) => (
          <li key={label} className="flex flex-1 items-center gap-2">
            <div
              className={cn(
                "flex h-7 w-7 shrink-0 items-center justify-center rounded-full border text-xs font-medium",
                index < step && "border-brand bg-brand text-brand-foreground",
                index === step && "border-brand text-brand",
                index > step && "border-border text-muted"
              )}
            >
              {index < step ? <Check className="h-3.5 w-3.5" /> : index + 1}
            </div>
            {index < STEPS.length - 1 && <div className={cn("h-px flex-1", index < step ? "bg-brand" : "bg-border")} />}
          </li>
        ))}
      </ol>
      <p className="-mt-4 text-sm font-medium text-muted">{STEPS[step]}</p>

      <div className="glass-panel rounded-2xl p-6">
        {step === 0 && (
          <div className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="name">Project name</Label>
              <Input id="name" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Thermal Scan 004" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="description">Description</Label>
              <Textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="What does this scan capture?" />
            </div>
          </div>
        )}

        {step === 1 && (
          <div className="space-y-6">
            <div>
              <p className="mb-2 text-sm font-medium">Final reconstructed mesh (required)</p>
              <p className="mb-3 text-xs text-muted">The final PLY mesh your thermal data will be mapped onto.</p>
              <UploadZone
                label="Drop final PLY mesh here"
                hint=".ply files only"
                accept=".ply"
                files={finalMeshFile}
                onFilesSelected={(files) => files[0] && upload(files[0], "FINAL_MESH", setFinalMeshFile, finalMeshFile)}
                onRemove={() => setFinalMeshFile([])}
              />
            </div>
            <div>
              <p className="mb-2 text-sm font-medium">Initial acquisition mesh (optional)</p>
              <p className="mb-3 text-xs text-muted">Used to automatically align if it&apos;s in a different coordinate space than the final mesh.</p>
              <UploadZone
                label="Drop initial mesh/point cloud here"
                hint=".ply files only"
                accept=".ply"
                files={initialMeshFile}
                onFilesSelected={(files) => files[0] && upload(files[0], "INITIAL_MESH", setInitialMeshFile, initialMeshFile)}
                onRemove={() => setInitialMeshFile([])}
              />
            </div>
          </div>
        )}

        {step === 2 && (
          <div>
            <p className="mb-2 text-sm font-medium">Thermal data (required)</p>
            <p className="mb-3 text-xs text-muted">One raw temperature file per camera view -- CSV or numeric text.</p>
            <UploadZone
              label="Drop thermal data files here"
              hint="CSV or numeric files, one per camera view"
              accept=".csv,.txt,.dat"
              multiple
              files={thermalFiles}
              onFilesSelected={(files) => files.forEach((f) => upload(f, "THERMAL_DATA", setThermalFiles, thermalFiles))}
              onRemove={(fname) => setThermalFiles((prev) => prev.filter((f) => f.name !== fname))}
            />
          </div>
        )}

        {step === 3 && (
          <div>
            <p className="mb-2 text-sm font-medium">Camera metadata (required)</p>
            <p className="mb-3 text-xs text-muted">Camera locations for every view -- orientation is estimated automatically if not provided.</p>
            <UploadZone
              label="Drop camera metadata here"
              hint="JSON or CSV"
              accept=".json,.csv"
              files={cameraFile}
              onFilesSelected={(files) => files[0] && upload(files[0], "CAMERA_METADATA", setCameraFile, cameraFile)}
              onRemove={() => setCameraFile([])}
            />
          </div>
        )}

        {step === 4 && (
          <div className="space-y-4">
            <p className="text-sm font-medium">Review</p>
            <div className="rounded-lg border border-border">
              {uploadedFiles.length === 0 && <p className="p-4 text-sm text-muted">No files uploaded yet.</p>}
              {uploadedFiles.map((file) => (
                <div key={file.id} className="flex items-center justify-between border-b border-border px-4 py-2 text-sm last:border-0">
                  <span>{file.filename}</span>
                  <span className="text-xs text-muted">
                    {file.type} · {formatBytes(file.size)}
                  </span>
                </div>
              ))}
            </div>
            <p className="text-xs text-muted">
              Once processing starts, the real ThermalMesh engine will validate, align, project, and blend your data into an
              interactive 3D model.
            </p>
          </div>
        )}
      </div>

      <div className="flex justify-between">
        <Button variant="secondary" disabled={step === 0} onClick={() => setStep((s) => Math.max(0, s - 1))}>
          Back
        </Button>
        {step < STEPS.length - 1 ? (
          <Button onClick={handleNext} disabled={createProject.isPending}>
            {createProject.isPending ? "Creating..." : "Next"}
          </Button>
        ) : (
          <Button onClick={handleStartProcessing} disabled={starting}>
            {starting ? "Starting..." : "Start Processing"}
          </Button>
        )}
      </div>
    </div>
  );
}
